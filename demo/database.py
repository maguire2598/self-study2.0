"""Versioned SQLite storage with transactional, non-destructive seeding."""
import hashlib
import json
import sqlite3
from pathlib import Path
from scripts.generate_collision_pi_c_questions import build_bank

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content/courses/collision-pi'

def connect(db_path):
    db = sqlite3.connect(str(db_path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db

def public_question(q, section):
    fields = ('id', 'node_id', 'node_title', 'question_type', 'question_style', 'difficulty', 'prompt')
    out = {k: q[k] for k in fields}
    out.update(section_id=section, revision=q.get('revision', 0), presentation_mode=q.get('presentation_mode', 'text_only'), figure_refs=q.get('figure_refs', []))
    if 'options' in q:
        out['options'] = [{k: o[k] for k in ('id', 'text', 'figure_ref') if k in o} for o in q['options']]
    if 'blanks' in q:
        out['blanks'] = [{'id': b['id']} for b in q['blanks']]
    return out

DDL = [
    'CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY)',
    'CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY,title TEXT NOT NULL)',
    'CREATE TABLE IF NOT EXISTS sections(id TEXT PRIMARY KEY,course_id TEXT REFERENCES courses(id),title TEXT,status TEXT)',
    'CREATE TABLE IF NOT EXISTS nodes(id TEXT PRIMARY KEY,section_id TEXT REFERENCES sections(id),parent_id TEXT REFERENCES nodes(id),title TEXT,summary TEXT,depth INTEGER)',
    'CREATE TABLE IF NOT EXISTS diagrams(id TEXT PRIMARY KEY,path TEXT NOT NULL,sha256 TEXT)',
    'CREATE TABLE IF NOT EXISTS questions(id TEXT PRIMARY KEY,node_id TEXT REFERENCES nodes(id),section_id TEXT REFERENCES sections(id),sort_order INTEGER,public_json TEXT NOT NULL,enabled INTEGER NOT NULL CHECK(enabled IN (0,1)),revision INTEGER NOT NULL,source_fingerprint TEXT)',
    'CREATE TABLE IF NOT EXISTS answer_keys(question_id TEXT PRIMARY KEY REFERENCES questions(id),source_json TEXT NOT NULL)',
    'CREATE TABLE IF NOT EXISTS learners(id TEXT PRIMARY KEY,created_at TEXT DEFAULT CURRENT_TIMESTAMP)',
    'CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,learner_id TEXT REFERENCES learners(id),question_id TEXT REFERENCES questions(id),node_id TEXT REFERENCES nodes(id),answers_json TEXT,correct INTEGER,revision INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP)',
    'CREATE TABLE IF NOT EXISTS reflections(id INTEGER PRIMARY KEY,attempt_id INTEGER REFERENCES attempts(id),learner_id TEXT REFERENCES learners(id),text TEXT,stage INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP)',
    'CREATE TABLE IF NOT EXISTS author_changes(id INTEGER PRIMARY KEY,question_id TEXT REFERENCES questions(id),enabled INTEGER,revision INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP)',
]

def initialize(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    puzzle = json.loads((CONTENT / 'knowledge-puzzle.json').read_text(encoding='utf-8'))
    banks = [json.loads((CONTENT / f'question-bank-{s}.json').read_text(encoding='utf-8')) for s in ('a', 'b')] + [build_bank()]
    if len(puzzle['nodes']) != 136 or [len(b['questions']) for b in banks] != [140, 168, 180]:
        raise ValueError('Unexpected source counts')
    manifest = json.loads((CONTENT / 'diagram-manifest-c.json').read_text(encoding='utf-8'))
    db = connect(db_path)
    try:
        db.execute('PRAGMA journal_mode=WAL')
        with db:
            for sql in DDL:
                db.execute(sql)
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(1)')
            db.execute("INSERT OR IGNORE INTO courses VALUES('collision-pi','碰撞与π')")
            for s in 'ABCD':
                db.execute('INSERT OR IGNORE INTO sections VALUES(?,?,?,?)', (s, 'collision-pi', f'{s} 板块', 'pending' if s == 'D' else 'available'))
            for n in sorted(puzzle['nodes'], key=lambda n: n['depth']):
                db.execute('INSERT OR IGNORE INTO nodes VALUES(?,?,?,?,?,?)', (n['id'], n['board'], n.get('parent'), n['title'], n['summary'], n['depth']))
            for diagram in manifest['diagrams']:
                path = (ROOT / diagram['path']).resolve()
                if not path.is_relative_to((CONTENT / 'diagrams/c').resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != diagram['sha256']:
                    raise ValueError('Invalid diagram asset')
                db.execute('INSERT OR IGNORE INTO diagrams VALUES(?,?,?)', (diagram['diagram_id'], diagram['path'], diagram['sha256']))
            for bank in banks:
                for order, q in enumerate(bank['questions']):
                    source = json.dumps(q, ensure_ascii=False)
                    db.execute('INSERT OR IGNORE INTO questions VALUES(?,?,?,?,?,?,?,?)', (q['id'], q['node_id'], bank['section_id'], order, json.dumps(public_question(q, bank['section_id']), ensure_ascii=False), int(q.get('enabled', True)), q.get('revision', 0), hashlib.sha256(source.encode()).hexdigest()))
                    db.execute('INSERT OR IGNORE INTO answer_keys VALUES(?,?)', (q['id'], source))
    finally:
        db.close()
