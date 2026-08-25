const assert = require('assert');
const state = require('./collision_pi_question_editor_state.js');
const bankA = require('../content/courses/collision-pi/question-bank-a.json');

const clone = value => JSON.parse(JSON.stringify(value));

function storageWith(entries = {}) {
  const values = new Map(Object.entries(entries));
  return {
    getItem(key) {
      return values.has(key) ? values.get(key) : null;
    },
    setItem(key, value) {
      values.set(key, value);
    }
  };
}

function loadA(storage) {
  return state.loadDraft({
    sectionId: 'A',
    banks: { A: bankA },
    getItem: storage.getItem,
    setItem: storage.setItem,
    clone
  });
}

const validLegacy = clone(bankA);
validLegacy.questions[0].author_notes = 'legacy A migration';
const legacyKey = 'collision-pi-a-question-draft';
const scopedKey = state.draftKey('A');
const validLegacyRaw = JSON.stringify(validLegacy);
const migrationStorage = storageWith({ [legacyKey]: validLegacyRaw });
const migrated = loadA(migrationStorage);
assert.equal(migrated.questions[0].author_notes, 'legacy A migration');
assert.equal(migrationStorage.getItem(legacyKey), validLegacyRaw);
assert.equal(
  JSON.parse(migrationStorage.getItem(scopedKey)).questions[0].author_notes,
  'legacy A migration'
);

const malformedStorage = storageWith({ [legacyKey]: '{not json' });
assert.equal(loadA(malformedStorage).questions[0].author_notes, '');
assert.equal(malformedStorage.getItem(scopedKey), null);

const rejectedLegacyDrafts = [];
const crossSection = clone(bankA);
crossSection.section_id = 'B';
rejectedLegacyDrafts.push(crossSection);
const movedNode = clone(bankA);
movedNode.questions[0].node_id = 'B1.1';
rejectedLegacyDrafts.push(movedNode);
const extraQuota = clone(bankA);
extraQuota.question_count_by_node.EXTRA = 1;
rejectedLegacyDrafts.push(extraQuota);
const missingQuota = clone(bankA);
delete missingQuota.question_count_by_node[Object.keys(missingQuota.question_count_by_node)[0]];
rejectedLegacyDrafts.push(missingQuota);
const duplicateQuestion = clone(bankA);
duplicateQuestion.questions[duplicateQuestion.questions.length - 1] = clone(duplicateQuestion.questions[0]);
rejectedLegacyDrafts.push(duplicateQuestion);
const missingQuestion = clone(bankA);
missingQuestion.questions.pop();
rejectedLegacyDrafts.push(missingQuestion);
const extraQuestion = clone(bankA);
extraQuestion.questions.push(clone(extraQuestion.questions[0]));
rejectedLegacyDrafts.push(extraQuestion);

for (const invalidLegacy of rejectedLegacyDrafts) {
  const storage = storageWith({ [legacyKey]: JSON.stringify(invalidLegacy) });
  assert.equal(loadA(storage).questions[0].author_notes, '');
  assert.equal(storage.getItem(scopedKey), null);
}

assert.deepEqual(state.nodeActionState('all'), {
  disableNodeOnlyActions: true,
  canApplyNodeAction: false
});
assert.deepEqual(state.nodeActionState('A1.1'), {
  disableNodeOnlyActions: false,
  canApplyNodeAction: true
});
assert.deepEqual(state.nodeQuestionIds('all', bankA.questions), []);
assert.equal(state.nodeQuestionIds('A1.1', bankA.questions).length, 5);

const nodes = ['A1.1', 'A1.2', 'A1.3'];
assert.equal(state.moveNodeId('all', nodes, 1), 'A1.1');
assert.equal(state.moveNodeId('all', nodes, -1), 'A1.3');
assert.equal(state.moveNodeId('A1.1', nodes, -1), 'A1.3');
assert.equal(state.moveNodeId('A1.3', nodes, 1), 'A1.1');

const outgoingAction = state.sectionAction('A', 3);
assert.deepEqual(outgoingAction, { sectionId: 'A', activationId: 3 });
assert.equal(state.isCurrentSectionAction(outgoingAction, 'A', 3), true);
assert.equal(state.isCurrentSectionAction(outgoingAction, 'B', 4), false);
assert.equal(state.isCurrentSectionAction(outgoingAction, 'A', 5), false);

console.log('question editor state validation OK');
