"""Generate the validated, deterministic section C formal bank."""
import hashlib
from pathlib import Path
if __package__:
    from .collision_pi_question_bank import build_bank_from_paths, content_fingerprint, write_bank
else:
    from collision_pi_question_bank import build_bank_from_paths, content_fingerprint, write_bank
ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content/courses/collision-pi'
OUTPUT = CONTENT / 'question-bank-c.json'

def build_bank():
    bank = build_bank_from_paths(CONTENT / 'question-source-c.json', CONTENT / 'knowledge-puzzle.json', section_id='C', title='碰撞与π · C板块客观题库')
    bank['diagram_manifest_fingerprint'] = hashlib.sha256((CONTENT / 'diagram-manifest-c.json').read_bytes()).hexdigest()
    bank['content_fingerprint'] = content_fingerprint(bank)
    return bank

if __name__ == '__main__':
    bank = build_bank()
    write_bank(bank, OUTPUT)
    print(f"generated {len(bank['questions'])} questions -> {OUTPUT}")
