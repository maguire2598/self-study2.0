const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const appPath = path.join(__dirname, '../demo/web/app.js');
test('frontend encodes filters and zero-based pagination without mixing nodes', () => {
  assert.ok(fs.existsSync(appPath), 'Learning application must exist');
  const { queryFor } = require(appPath);
  assert.equal(queryFor({ section: 'C', node: 'C1.1', type: 'multi_blank', offset: 20 }, 20), 'section=C&node_id=C1.1&type=multi_blank&offset=20&limit=20');
});
test('answer payload preserves blank IDs and choice selection', () => {
  assert.ok(fs.existsSync(appPath), 'Learning application must exist');
  const { answerPayload } = require(appPath);
  assert.deepEqual(answerPayload({ question_type: 'single_choice' }, [['answer', 'B']]), ['B']);
  assert.deepEqual(answerPayload({ question_type: 'multiple_choice' }, [['answer', 'A'], ['answer', 'C']]), ['A', 'C']);
  assert.deepEqual(answerPayload({ question_type: 'multi_blank' }, [['blank:one', '-1/2'], ['blank:two', '2']]), {one:'-1/2', two:'2'});
});
test('knowledge directory follows parent-child natural order, not insertion depth', () => {
  assert.ok(fs.existsSync(appPath), 'Learning application must exist');
  const { orderedNodes } = require(appPath);
  assert.deepEqual(orderedNodes([{id:'C10',section_id:'C'}, {id:'C2.1',section_id:'C'}, {id:'C2',section_id:'C'}, {id:'A1',section_id:'A'}], 'C').map(n => n.id), ['C2','C2.1','C10']);
});
