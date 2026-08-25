const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const editorPath = path.join(root, 'authoring', 'collision-pi-question-editor.html');
const source = fs.readFileSync(editorPath, 'utf8');
const scripts = [...source.matchAll(/<script(?: [^>]*)?>([\s\S]*?)<\/script>/g)];

if (!source.startsWith('<meta charset="utf-8">')) {
  throw new Error('editor must declare UTF-8 before its Chinese content');
}

if (scripts.length < 3) {
  throw new Error(`expected embedded data and application scripts, found ${scripts.length}`);
}

const banks = JSON.parse(scripts[0][1]);
if (banks.A.questions.length !== 140 || banks.B.questions.length !== 168) {
  throw new Error('expected A=140 and B=168 questions');
}

if (!source.includes('id="questionSectionFilter"')) {
  throw new Error('section filter is missing');
}

if (!source.includes("new Option('全部知识点', 'all')")) {
  throw new Error('node filter must allow cross-node scenario filtering');
}

if (!source.includes('get("section")')) {
  throw new Error('section=B URL handling is missing');
}

if (!source.includes('collision-pi-question-editor:${sectionId}:draft-v1')) {
  throw new Error('section-qualified draft key is missing');
}

if (!source.includes('id="questionScenarioFilter"')) {
  throw new Error('scenario filter is missing');
}

if (!source.includes('question.scenario_id') || !source.includes('question.question_style')) {
  throw new Error('scenario metadata rendering is missing');
}

new Function(scripts[1][1]);
new Function(scripts.at(-1)[1]);
const stateValidation = spawnSync(process.execPath, [path.join(__dirname, 'validate_question_editor_state.js')], {
  encoding: 'utf8'
});
if (stateValidation.status !== 0) {
  throw new Error(`question editor state validation failed:\n${stateValidation.stdout}${stateValidation.stderr}`);
}
console.log(`question editor validation OK: A=${banks.A.questions.length}, B=${banks.B.questions.length} questions, ${scripts.length} script blocks`);
