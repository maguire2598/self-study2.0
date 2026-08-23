const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const editorPath = path.join(root, 'authoring', 'collision-pi-question-editor.html');
const source = fs.readFileSync(editorPath, 'utf8');
const scripts = [...source.matchAll(/<script(?: [^>]*)?>([\s\S]*?)<\/script>/g)];

if (scripts.length < 2) {
  throw new Error(`expected embedded data and application scripts, found ${scripts.length}`);
}

const bank = JSON.parse(scripts[0][1]);
if (bank.questions.length !== 140) {
  throw new Error(`expected 140 questions, found ${bank.questions.length}`);
}

if (!source.includes('id="questionScenarioFilter"')) {
  throw new Error('scenario filter is missing');
}

if (!source.includes('question.scenario_id') || !source.includes('question.question_style')) {
  throw new Error('scenario metadata rendering is missing');
}

new Function(scripts.at(-1)[1]);
console.log(`question editor validation OK: ${bank.questions.length} questions, ${scripts.length} script blocks`);
