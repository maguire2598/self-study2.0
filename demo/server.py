"""Loopback-only HTTP application. Repository files are never a static root."""
import argparse
import hmac
import json
import secrets
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from .database import ROOT, connect, initialize
from .grading import grade

class APIError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, value, mime='application/json; charset=utf-8'):
        data = json.dumps(value, ensure_ascii=False).encode() if mime.startswith('application/json') else value
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; frame-ancestors 'none'")
        for cookie in self.new_cookies:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(data)

    def cookie(self, name, value, expire=False):
        self.new_cookies.append(f'{name}={value}; Path=/; HttpOnly; SameSite=Strict' + ('; Max-Age=0' if expire else '; Max-Age=31536000' if name == 'selfstudy_learner' else ''))

    def body(self):
        if self.headers.get('Transfer-Encoding'):
            raise APIError(400, '不支持分块请求。')
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 0 or size > 65536:
                raise ValueError()
            raw = self.rfile.read(size)
            if self.headers.get('X-SelfStudy-Request') != '1' or self.headers.get_content_type() != 'application/json':
                raise APIError(400, '写请求需要 JSON 与 X-SelfStudy-Request。')
            data = json.loads(raw.decode('utf-8'), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
            if not isinstance(data, dict):
                raise ValueError()
            return data
        except (ValueError, UnicodeError):
            raise APIError(400, '请求体非法或超过 64 KiB。')

    def dispatch(self):
        self.new_cookies = []
        db = None
        try:
            host = self.headers.get('Host', '')
            if host not in self.server.allowed_hosts or (self.headers.get('Origin') and self.headers['Origin'] != 'http://' + host):
                raise APIError(400, '仅允许本站本地请求。')
            self.cookies = SimpleCookie()
            self.cookies.load(self.headers.get('Cookie', ''))
            self.path_only = unquote(urlsplit(self.path).path)
            self.query = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            self.data = self.body() if self.command in {'POST', 'PATCH'} else {}
            db = connect(self.server.db_path)
            self.db = db
            with db:
                response = self.route()
            self.send(*response)
        except APIError as e:
            self.send(e.status, {'error': e.message})
        except (ValueError, TypeError, KeyError, OverflowError):
            self.send(400, {'error': '输入格式无效。'})
        except Exception:
            self.send(500, {'error': '本地服务处理失败。'})
        finally:
            if db is not None:
                db.close()

    do_GET = do_POST = do_PATCH = do_OPTIONS = dispatch

    def learner(self):
        token = self.cookies.get('selfstudy_learner')
        learner = token.value if token else ''
        if not self.db.execute('SELECT 1 FROM learners WHERE id=?', (learner,)).fetchone():
            learner = secrets.token_urlsafe(32)
            self.db.execute('INSERT INTO learners(id) VALUES(?)', (learner,))
            self.cookie('selfstudy_learner', learner)
        return learner

    def author(self):
        token = self.cookies.get('selfstudy_author')
        if not token or token.value not in self.server.author_sessions:
            raise APIError(401, '请先登录作者端。')

    def question(self, qid, author=False):
        row = self.db.execute('SELECT q.*,a.source_json FROM questions q JOIN answer_keys a ON a.question_id=q.id WHERE q.id=?' + ('' if author else ' AND q.enabled=1'), (qid,)).fetchone()
        if row is None:
            raise APIError(404, '题目不存在或已停用。')
        result = json.loads(row['source_json'] if author else row['public_json'])
        result['revision'] = row['revision']
        if author:
            result.update(enabled=bool(row['enabled']), section_id=row['section_id'])
        return result

    def listing(self, author=False):
        where, values = ([] if author else ['enabled=1']), []
        for query, column in [('section', 'section_id'), ('node_id', 'node_id'), ('type', "json_extract(public_json,'$.question_type')")]:
            val = self.query.get(query, [''])[0]
            if val:
                where.append(column + '=?')
                values.append(val)
        offset, limit = int(self.query.get('offset', ['0'])[0]), int(self.query.get('limit', ['20'])[0])
        if offset < 0 or not 1 <= limit <= 200:
            raise ValueError()
        clause = ' WHERE ' + ' AND '.join(where) if where else ''
        total = self.db.execute('SELECT COUNT(*) FROM questions' + clause, values).fetchone()[0]
        rows = self.db.execute('SELECT id FROM questions' + clause + " ORDER BY section_id,CAST(substr(node_id,2) AS INTEGER),CAST(substr(node_id,instr(node_id,'.')+1) AS INTEGER),sort_order LIMIT ? OFFSET ?", values + [limit, offset])
        return {'items': [self.question(r['id'], author) for r in rows], 'total': total}

    def route(self):
        path, method, db = self.path_only, self.command, self.db
        if method == 'GET' and path == '/api/health':
            counts = {s: db.execute('SELECT COUNT(*) FROM questions WHERE section_id=?', (s,)).fetchone()[0] for s in 'ABCD'}
            return 200, dict(status='ok', database='ok', question_count=sum(counts.values()), sections=counts)
        if method == 'GET' and path == '/api/course':
            sections = [dict(r) for r in db.execute('SELECT id,title,status,(SELECT COUNT(*) FROM questions q WHERE q.section_id=s.id AND enabled=1) question_count FROM sections s ORDER BY id')]
            nodes = [dict(r) for r in db.execute('SELECT n.*,(SELECT COUNT(*) FROM questions q WHERE q.node_id=n.id AND enabled=1) question_count FROM nodes n ORDER BY rowid')]
            return 200, dict(id='collision-pi', title='碰撞与π', sections=sections, nodes=nodes, video_available=False)
        if method == 'GET' and path == '/api/questions':
            return 200, self.listing()
        if method == 'GET' and path.startswith('/api/questions/'):
            return 200, self.question(path.removeprefix('/api/questions/'))
        if path == '/api/attempts' and method == 'POST':
            if not isinstance(self.data.get('question_id'), str):
                raise ValueError()
            learner = self.learner()
            q = self.question(self.data['question_id'])
            source = json.loads(db.execute('SELECT source_json FROM answer_keys WHERE question_id=?', (q['id'],)).fetchone()[0])
            correct = grade(source, self.data['answers'])
            cursor = db.execute('INSERT INTO attempts(learner_id,question_id,node_id,answers_json,correct,revision) VALUES(?,?,?,?,?,?)', (learner, q['id'], q['node_id'], json.dumps(self.data['answers'], ensure_ascii=False), int(correct), q['revision']))
            return 200, dict(attempt_id=cursor.lastrowid, correct=correct, next_action='next_question' if correct else 'reflection', message='已记录，可以继续学习。' if correct else '先检查依据：回看条件与自己的推理。')
        if path == '/api/progress' and method == 'GET':
            learner = self.learner()
            aggregates = 'COUNT(*) attempts,COALESCE(SUM(correct),0) correct_attempts,COUNT(DISTINCT CASE WHEN correct=1 THEN question_id END) completed_questions'
            out = dict(db.execute('SELECT ' + aggregates + ' FROM attempts WHERE learner_id=?', (learner,)).fetchone())
            out['nodes'] = [dict(r) for r in db.execute('SELECT node_id,' + aggregates + ' FROM attempts WHERE learner_id=? GROUP BY node_id', (learner,))]
            out['recent'] = [dict(r) for r in db.execute('SELECT question_id,node_id,correct,created_at FROM attempts WHERE learner_id=? ORDER BY id DESC LIMIT 20', (learner,))]
            for r in out['recent']:
                r['correct'] = bool(r['correct'])
            out['last_question_id'] = out['recent'][0]['question_id'] if out['recent'] else None
            return 200, out
        if path == '/api/reflections' and method == 'POST':
            learner = self.learner()
            attempt = self.data['attempt_id']
            if type(attempt) is not int or not db.execute('SELECT 1 FROM attempts WHERE id=? AND learner_id=?', (attempt, learner)).fetchone():
                raise APIError(404, '学习记录不存在。')
            text = self.data['text']
            if not isinstance(text, str) or not text.strip() or len(text) > 4000:
                raise ValueError()
            stage = min(3, db.execute('SELECT COUNT(*) FROM reflections WHERE attempt_id=?', (attempt,)).fetchone()[0] + 1)
            if db.execute('SELECT COUNT(*) FROM reflections WHERE attempt_id=?', (attempt,)).fetchone()[0] < 3:
                db.execute('INSERT INTO reflections(attempt_id,learner_id,text,stage) VALUES(?,?,?,?)', (attempt, learner, text, stage))
            prompts = ['演示引导，非 AI：写下题目给出的条件，检查你是否遗漏了方向或单位。', '演示引导，非 AI：选出你推理中最不确定的一步，说明它的依据。', '演示引导，非 AI：总结你准备修改的一步。现在可以重试，也可以跳过。']
            return 200, dict(stage=stage, prompt=prompts[stage - 1], can_retry=True, mode='rule_demo')
        if path == '/api/author/login' and method == 'POST':
            token = self.data.get('token')
            if not isinstance(token, str) or not hmac.compare_digest(token.encode('utf-8'), self.server.author_token.encode('utf-8')):
                raise APIError(401, '作者令牌无效。')
            session = secrets.token_urlsafe(32)
            self.server.author_sessions.add(session)
            self.cookie('selfstudy_author', session)
            return 200, {'authenticated': True}
        if path == '/api/author/logout' and method == 'POST':
            token = self.cookies.get('selfstudy_author')
            if token:
                self.server.author_sessions.discard(token.value)
            self.cookie('selfstudy_author', '', True)
            return 200, {'authenticated': False}
        if path == '/api/author/questions' and method == 'GET':
            self.author()
            return 200, self.listing(True)
        if path.startswith('/api/author/questions/') and method == 'PATCH':
            self.author()
            q = self.question(path.removeprefix('/api/author/questions/'), True)
            enabled, revision = self.data['enabled'], self.data['revision']
            if type(enabled) is not bool or type(revision) is not int:
                raise ValueError()
            cursor = db.execute('UPDATE questions SET enabled=?,revision=revision+1 WHERE id=? AND revision=?', (int(enabled), q['id'], revision))
            if cursor.rowcount != 1:
                db.execute('INSERT INTO author_changes(question_id,enabled,revision,outcome) VALUES(?,?,?,?)', (q['id'], int(enabled), revision, 'conflict'))
                return 409, {'error': '题目版本已更新，请刷新后重试。'}
            db.execute('INSERT INTO author_changes(question_id,enabled,revision) VALUES(?,?,?)', (q['id'], int(enabled), revision + 1))
            return 200, dict(id=q['id'], enabled=enabled, revision=revision + 1)
        if method == 'GET' and path.startswith('/api/diagrams/') and path.endswith('.svg'):
            diagram = db.execute('SELECT path FROM diagrams WHERE id=?', (path.removeprefix('/api/diagrams/').removesuffix('.svg'),)).fetchone()
            if diagram:
                return 200, (ROOT / diagram['path']).read_bytes(), 'image/svg+xml'
        static = {'/': 'index.html', '/index.html': 'index.html', '/app.js': 'app.js', '/styles.css': 'styles.css', '/author': 'author.html', '/author.html': 'author.html', '/author.js': 'author.js'}
        if method == 'GET' and path in static:
            file = ROOT / 'demo/web' / static[path]
            if file.is_file():
                mime = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8'}[file.suffix]
                return 200, file.read_bytes(), mime
        raise APIError(404, '路径不存在。')

def create_server(host, port, db_path):
    if host != '127.0.0.1':
        raise ValueError('Demo must bind to 127.0.0.1')
    initialize(db_path)
    token_path = Path(db_path).resolve().parent / 'author-token.txt'
    try:
        with token_path.open('x', encoding='utf-8') as file:
            file.write(secrets.token_urlsafe(32) + '\n')
    except FileExistsError:
        pass
    server = ThreadingHTTPServer((host, port), Handler)
    server.db_path = str(Path(db_path).resolve())
    server.author_token = token_path.read_text(encoding='utf-8').strip()
    if not server.author_token:
        server.server_close()
        raise ValueError('Empty author token file')
    server.author_sessions = set()
    server.allowed_hosts = {f'127.0.0.1:{server.server_port}', f'localhost:{server.server_port}'}
    return server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--db', default=str(ROOT / '.local/selfstudy-demo.sqlite3'))
    args = parser.parse_args()
    server = create_server('127.0.0.1', args.port, args.db)
    print(f'SelfStudy: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
