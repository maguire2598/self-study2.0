import hashlib
from contextlib import closing
import http.cookiejar
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from demo.database import CONTENT, connect, initialize
from demo.grading import grade
from demo.server import create_server
from scripts.generate_collision_pi_c_questions import build_bank
from scripts.collision_pi_question_bank import content_fingerprint

class DemoTests(unittest.TestCase):
    def test_questions_follow_knowledge_order_and_reject_oversized_offset(self):
        status, data = self.request('/api/questions?section=A&limit=6')
        self.assertEqual(status, 200)
        self.assertEqual([q['node_id'] for q in data['items']], ['A1.1'] * 5 + ['A1.2'])
        self.assertEqual(self.request('/api/questions?offset=999999999999999999999999')[0], 400)

    def test_conflict_is_audited_without_changing_enabled_state(self):
        self.request('/api/author/login', {'token': self.server.author_token})
        q = self.request('/api/author/questions?limit=1')[1]['items'][0]
        self.assertEqual(self.request('/api/author/questions/' + q['id'], {'enabled': False, 'revision': q['revision'] + 2}, 'PATCH')[0], 409)
        with closing(connect(self.path)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM author_changes WHERE question_id=?', (q['id'],)).fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT enabled FROM questions WHERE id=?', (q['id'],)).fetchone()[0], 1)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'demo.sqlite3'
        self.server = create_server('127.0.0.1', 0, self.path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.other = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, data=None, method=None, client=None, headers=None):
        request = urllib.request.Request(f'http://127.0.0.1:{self.server.server_port}' + path, data=json.dumps(data).encode() if data is not None else None, method=method, headers=headers or {'Content-Type': 'application/json', 'X-SelfStudy-Request': '1'})
        try:
            response = (client or self.client).open(request)
        except urllib.error.HTTPError as e:
            response = e
        with response:
            self.last_headers = response.headers
            raw = response.read()
            return response.status, json.loads(raw) if response.headers.get_content_type() == 'application/json' else raw

    def test_counts_idempotence_foreign_keys_and_no_source_mutation(self):
        bank = build_bank()
        self.assertEqual(bank, json.loads((CONTENT / 'question-bank-c.json').read_text(encoding='utf-8')))
        self.assertEqual(bank['content_fingerprint'], content_fingerprint(bank))
        hashes = [hashlib.sha256((CONTENT / f'question-bank-{s}.json').read_bytes()).hexdigest() for s in 'ab']
        initialize(self.path)
        status, health = self.request('/api/health')
        self.assertEqual((status, health['question_count'], health['sections']), (200, 488, {'A': 140, 'B': 168, 'C': 180, 'D': 0}))
        db = connect(self.path)
        try:
            self.assertEqual(db.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM nodes').fetchone()[0], 136)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM diagrams').fetchone()[0], 36)
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
        finally:
            db.close()
        self.assertEqual(hashes, [hashlib.sha256((CONTENT / f'question-bank-{s}.json').read_bytes()).hexdigest() for s in 'ab'])
        self.assertEqual(self.request('/api/questions?section=D')[1], {'items': [], 'total': 0})

    def test_public_dto_and_routes_have_no_private_data(self):
        forbidden = {'correct_answers', 'accepted_answers', 'explanation', 'answer_contract', 'visible_physics_contract', 'author_notes'}
        def inspect(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden & value.keys())
                for v in value.values(): inspect(v)
            elif isinstance(value, list):
                for v in value: inspect(v)
        for section in 'ABC':
            status, data = self.request(f'/api/questions?section={section}&limit=200')
            self.assertEqual(status, 200)
            inspect(data)
        for path in ['/content/courses/collision-pi/question-bank-a.json', '/.local/author-token.txt', '/demo/database.py', '/api/diagrams/../../question-bank-c.json', '/%2e%2e/.local/author-token.txt']:
            self.assertEqual(self.request(path)[0], 404)
        db = connect(self.path)
        try:
            diagram = db.execute('SELECT id FROM diagrams LIMIT 1').fetchone()[0]
        finally: db.close()
        self.assertEqual(self.request('/api/diagrams/' + diagram + '.svg')[0], 200)

    def test_attempts_reflections_isolation_and_persistence(self):
        for kind in ['single_choice', 'multiple_choice', 'multi_blank']:
            items = self.request('/api/questions?type=' + kind)[1]['items']
            self.assertTrue(items)
            q = items[0]
            db = connect(self.path)
            try: source = json.loads(db.execute('SELECT source_json FROM answer_keys WHERE question_id=?', (q['id'],)).fetchone()[0])
            finally: db.close()
            answers = {b['id']: b['accepted_answers'][0] for b in source['blanks']} if kind == 'multi_blank' else source['correct_answers']
            status, result = self.request('/api/attempts', {'question_id': q['id'], 'answers': answers})
            self.assertEqual(status, 200)
            self.assertTrue(result['correct'])
        q = self.request('/api/questions?type=single_choice')[1]['items'][0]
        bad = self.request('/api/attempts', {'question_id': q['id'], 'answers': ['A', 'A']})
        self.assertEqual(bad[0], 400)
        for option in q['options']:
            result = self.request('/api/attempts', {'question_id': q['id'], 'answers': [option['id']]})[1]
            if not result['correct']: break
        self.assertEqual(set(result), {'attempt_id', 'correct', 'next_action', 'message'})
        self.assertEqual(self.request('/api/reflections', {'attempt_id': result['attempt_id'], 'text': '方向'}, client=self.other)[0], 404)
        for index in range(5):
            status, reflection = self.request('/api/reflections', {'attempt_id': result['attempt_id'], 'text': '检查方向'})
            self.assertEqual((status, reflection['stage']), (200, min(3, index + 1)))
        progress = self.request('/api/progress')[1]
        self.assertGreater(progress['attempts'], 1)
        self.assertEqual(self.request('/api/progress', client=self.other)[1]['attempts'], 0)
        initialize(self.path)
        self.assertEqual(self.request('/api/progress')[1], progress)
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.server = create_server('127.0.0.1', 0, self.path)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.assertEqual(self.request('/api/progress')[1], progress)

    def test_author_auth_revision_and_enable_persistence(self):
        self.assertEqual(self.request('/api/author/questions')[0], 401)
        self.assertEqual(self.request('/api/author/login', {'token': 'wrong'})[0], 401)
        self.assertEqual(self.request('/api/author/login', {'token': '错误'})[0], 401)
        token = (self.path.parent / 'author-token.txt').read_text().strip()
        self.assertEqual(self.request('/api/author/login', {'token': token})[0], 200)
        self.assertNotIn('Max-Age', self.last_headers['Set-Cookie'])
        q = self.request('/api/author/questions')[1]['items'][0]
        self.assertIn('explanation', q)
        path = '/api/author/questions/' + q['id']
        self.assertEqual(self.request(path, {'enabled': False, 'revision': q['revision']}, 'PATCH')[0], 200)
        self.assertEqual(self.request(path, {'enabled': True, 'revision': q['revision']}, 'PATCH')[0], 409)
        initialize(self.path)
        self.assertEqual(self.request('/api/questions/' + q['id'])[0], 404)
        self.assertEqual(self.request(path, {'enabled': True, 'revision': q['revision'] + 1}, 'PATCH')[0], 200)
        self.request('/api/author/logout', {})
        self.assertEqual(self.request('/api/author/questions')[0], 401)

    def test_request_boundaries(self):
        self.request('/api/progress')
        cookie = self.last_headers['Set-Cookie']
        for attribute in ['HttpOnly', 'SameSite=Strict', 'Max-Age=31536000']:
            self.assertIn(attribute, cookie)
        self.assertEqual(self.request('/api/attempts', {}, headers={'Content-Type': 'application/json'})[0], 400)
        self.assertEqual(self.request('/api/health', headers={'Host': 'evil.example'})[0], 400)
        self.assertEqual(self.request('/api/health', headers={'Origin': 'https://evil.example'})[0], 400)
        self.assertEqual(self.request('/api/attempts', {'large': 'x' * 65536})[0], 400)
        self.assertEqual(self.request('/api/attempts', {'question_id': [], 'answers': []})[0], 400)
        self.assertEqual(self.request('/api/questions?limit=-1')[0], 400)
        with self.assertRaises(ValueError): create_server('0.0.0.0', 0, self.path)

class GradingTests(unittest.TestCase):
    def test_numeric_normalization_and_rejection(self):
        q = {'question_type': 'multi_blank', 'blanks': [{'id': 'x', 'accepted_answers': ['-0.5']}, {'id': 'y', 'accepted_answers': ['2']}]}
        self.assertTrue(grade(q, {'x': ' −１/２ ', 'y': '2.0'}))
        self.assertFalse(grade(q, {'x': '-0.5 kg', 'y': '2'}))
        self.assertFalse(grade(q, {'x': '__import__("os")', 'y': '2'}))
        for answers in [{'x': 'NaN', 'y': '2'}, {'x': '-0.5'}, {'x': 0.5, 'y': '2'}]:
            with self.assertRaises(ValueError): grade(q, answers)
    def test_choice_sets(self):
        q = {'question_type': 'multiple_choice', 'options': [{'id': 'A'}, {'id': 'B'}, {'id': 'C'}], 'correct_answers': ['A', 'C']}
        self.assertTrue(grade(q, ['C', 'A']))
        self.assertFalse(grade(q, ['A']))
        for answers in [['A', 'A'], [], ['D'], {'A': True}]:
            with self.assertRaises(ValueError): grade(q, answers)

if __name__ == '__main__': unittest.main()
