/* Public learning UI: never imports the author bank or answer keys. */
function queryFor(state, limit = 20) {
  return new URLSearchParams({section: state.section, node_id: state.node || '', type: state.type || '', offset: String(state.offset || 0), limit: String(limit)}).toString();
}
function orderedNodes(nodes, section) {
  return nodes.filter(n => n.section_id === section).sort((a,b) => a.id.localeCompare(b.id, 'en', {numeric:true}));
}
function answerPayload(question, entries) {
  return question.question_type === 'multi_blank' ? Object.fromEntries(entries.filter(([k]) => k.startsWith('blank:')).map(([k,v]) => [k.slice(6), v])) : entries.filter(([k]) => k === 'answer').map(([,v]) => v);
}
if (typeof module !== 'undefined') module.exports = {queryFor, orderedNodes, answerPayload};
if (typeof document !== 'undefined') {
  const $ = id => document.getElementById(id);
  const state = {section:'A', node:'', type:'', offset:0, index:0, items:[], total:0, course:null, attempt:null, loading:false, submitting:false, sequence:0};
  const names = {A:'观察碰撞', B:'建立方程', C:'理解图像', D:'走近 π · 待定'};
  const types = {single_choice:'单选题',multiple_choice:'多选题',multi_blank:'填空题'};
  function el(tag, text, className) { const e=document.createElement(tag); if(text !== undefined)e.textContent=text; if(className)e.className=className; return e; }
  async function api(path, body) {
    const response=await fetch(path, body === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-SelfStudy-Request':'1'},body:JSON.stringify(body)});
    const data=await response.json(); if(!response.ok) throw new Error(data.error || '请求失败，请重试。'); return data;
  }
  function status(message, error=false) { $('status').textContent=message; $('reload').hidden=!error; }
  function busy(value) {
    state.loading=value;
    document.querySelectorAll('[data-filter]').forEach(e => {e.disabled=value || state.submitting;});
    $('previous').disabled=value || state.submitting || state.offset+state.index===0;
    $('next').disabled=value || state.submitting || state.offset+state.index>=state.total-1;
    $('skip').disabled=$('next').disabled;
  }
  function directory() {
    $('sections').replaceChildren();
    state.course.sections.forEach(s => {
      const button=el('button'); button.type='button'; button.dataset.filter=''; button.setAttribute('aria-pressed',String(state.section===s.id));
      button.append(el('b',s.id),el('span',names[s.id]),el('small',s.status==='pending'?'待定':`${s.question_count}题`));
      button.onclick=()=>{state.section=s.id;state.node='';state.offset=0;state.index=0;directory();load();}; $('sections').append(button);
    });
    $('node').replaceChildren(new Option('全部知识点',''));
    orderedNodes(state.course.nodes,state.section).forEach(n=>{
      const option=new Option(`${n.depth>1?'　':''}${n.id} ${n.title}${n.question_count?' · '+n.question_count+'题':''}`,n.id);
      option.disabled=n.question_count===0; $('node').append(option);
    });
    $('node').value=state.node; $('type').value=state.type;
    $('section-label').textContent=`${state.section} / ${names[state.section]}`;
    $('node-summary').textContent=state.course.nodes.find(n=>n.id===state.node)?.summary || '按知识点顺序练习，也可以选择想加强的部分。';
  }
  function figure(ref, label) {
    const id=typeof ref==='string'?ref:ref.diagram_id;
    const url='/api/diagrams/'+encodeURIComponent(id)+'.svg';
    const box=el('figure'); const image=el('img'); image.src=url; image.alt=label; image.width=720; image.height=480;
    image.onerror=()=>{image.replaceWith(el('p','图像加载失败，请刷新后重试。','error'));};
    const link=el('a','查看大图 ↗','figure-link'); link.href=url;link.target='_blank';link.rel='noopener';link.setAttribute('aria-label',label+'，查看大图');
    box.append(image,link);return box;
  }
  function render() {
    state.attempt=null; const q=state.items[state.index];
    $('question').hidden=!q; $('feedback').hidden=true; $('reflection').hidden=true;
    $('answer-error').textContent='';$('reflection-error').textContent='';$('answers').disabled=false;$('submit').disabled=false;
    if(!q) { status(state.section==='D'?'D 板块出题待定，目前仅保留知识目录。':'没有符合筛选条件的题目，请调整知识点或题型。');busy(false);return; }
    status(`共 ${state.total} 道题`);$('question-type').textContent=types[q.question_type];$('position').textContent=`${state.offset+state.index+1} / ${state.total}`;
    $('question-node').textContent=`${q.node_id} · ${q.node_title}`;$('prompt').textContent=q.prompt;
    $('figures').replaceChildren(); (q.figure_refs||[]).forEach((ref,i)=>$('figures').append(figure(ref,`题干图 ${i+1}`)));
    $('answer-fields').replaceChildren();$('answer-fields').className=q.presentation_mode==='option_figures'?'option-grid':'';
    if(q.question_type==='multi_blank') {
      q.blanks.forEach((b,i)=>{const label=el('label',`第 ${i+1} 空`,'blank');const input=el('input');input.type='text';input.name='blank:'+b.id;input.required=true;input.maxLength=1000;input.autocomplete='off';label.append(input);$('answer-fields').append(label);});
    } else {
      q.options.forEach(o=>{
        const row=el('div',undefined,'option-wrap');const label=el('label',undefined,'option');const input=el('input');input.type=q.question_type==='single_choice'?'radio':'checkbox';input.name='answer';input.value=o.id;
        label.append(input,el('span',o.id,'option-letter'),el('span',o.text));row.append(label);
        if(o.figure_ref)row.append(figure(o.figure_ref,`选项 ${o.id} 的图`));$('answer-fields').append(row);
      });
    }
    busy(false);
  }
  async function load() {
    const seq=++state.sequence;busy(true);$('question').hidden=true;status('正在载入题目…');
    try { const data=await api('/api/questions?'+queryFor(state));if(seq!==state.sequence)return;state.items=data.items;state.total=data.total;state.index=Math.min(state.index,Math.max(0,data.items.length-1));render(); }
    catch(e){if(seq!==state.sequence)return;status(e.message,true);busy(false);}
  }
  async function progress() {
    const p=await api('/api/progress');$('completed').textContent=p.completed_questions;$('attempt-count').textContent=`累计 ${p.attempts} 次作答 · ${p.correct_attempts} 次通过`;
    $('recent').replaceChildren();p.recent.slice(0,5).forEach(r=>{const item=el('li');item.append(el('span',r.node_id),el('span',r.correct?'已通过':'待检查',r.correct?'passed':'quiet'));$('recent').append(item);});
    if(!p.recent.length)$('recent').append(el('li','从第一题开始，记录会保存在这里。','quiet'));return p;
  }
  function move(delta) {
    if(state.loading||state.submitting)return;const absolute=state.offset+state.index+delta;if(absolute<0||absolute>=state.total)return;
    const offset=Math.floor(absolute/20)*20;state.index=absolute%20;if(offset===state.offset)render();else{state.offset=offset;load();}
  }
  function openReflection() {$('reflection').hidden=false;$('reflection-text').value='';$('reflection-text').disabled=false;$('reflection-submit').disabled=false;$('stage').textContent='演示引导，非 AI · 最多3轮';$('reflection-prompt').textContent='题目给出了哪些条件？你是怎样作出判断的？';$('reflect-open').hidden=true;}
  $('answer-form').onsubmit=async event=>{
    event.preventDefault();if(state.submitting||state.attempt||state.loading)return;
    const q=state.items[state.index];const answers=answerPayload(q,[...new FormData(event.currentTarget)]);
    if(Array.isArray(answers)&&!answers.length){$('answer-error').textContent='请先选择选项。';return;}
    state.submitting=true;busy(false);$('submit').disabled=true;$('answers').disabled=true;$('answer-error').textContent='';
    try {
      const result=await api('/api/attempts',{question_id:q.id,answers});state.attempt=result.attempt_id;
      $('answers').disabled=true;$('feedback').hidden=false;$('feedback-title').textContent=result.correct?'这次检查已通过':'先检查依据';$('feedback-message').textContent=result.message;$('reflect-open').hidden=false;
      if(!result.correct)openReflection();
      try{await progress();}catch(e){status('作答已保存，但进度暂未刷新。'+e.message,true);}
    } catch(e){$('answer-error').textContent=e.message+' 如果网络中断，请先刷新查看记录，避免重复提交。';$('submit').disabled=false;$('answers').disabled=false;}
    finally {state.submitting=false;busy(false);}
  };
  $('reflection-form').onsubmit=async event=>{
    event.preventDefault();if(!state.attempt||state.submitting)return;state.submitting=true;busy(false);$('reflection-submit').disabled=true;$('retry').disabled=true;$('reflection-error').textContent='';
    try {const r=await api('/api/reflections',{attempt_id:state.attempt,text:$('reflection-text').value});$('reflection-prompt').textContent=r.prompt;$('stage').textContent=`演示引导，非 AI · ${r.stage}/3`;$('reflection-text').value='';$('reflection-text').disabled=r.stage>=3;$('reflection-submit').disabled=r.stage>=3;}
    catch(e){$('reflection-error').textContent=e.message;$('reflection-submit').disabled=false;}
    finally{state.submitting=false;$('retry').disabled=false;busy(false);}
  };
  $('node').onchange=()=>{state.node=$('node').value;state.offset=0;state.index=0;directory();load();};
  $('type').onchange=()=>{state.type=$('type').value;state.offset=0;state.index=0;load();};
  $('previous').onclick=()=>move(-1);$('next').onclick=()=>move(1);$('skip').onclick=()=>move(1);$('retry').onclick=render;$('reflect-open').onclick=openReflection;
  async function start() {
    busy(true);status('正在载入课程…');
    try {
      state.course=await api('/api/course');const p=await progress();
      if(p.last_question_id){try{const last=await api('/api/questions/'+encodeURIComponent(p.last_question_id));state.section=last.section_id;const list=await api('/api/questions?section='+state.section+'&limit=200');const index=list.items.findIndex(q=>q.id===last.id);if(index>=0){state.offset=Math.floor(index/20)*20;state.index=index%20;}}catch{/* A disabled last question is intentionally not restored. */}}
      directory();await load();
    }catch(e){status('无法载入课程：'+e.message,true);busy(false);}
  }
  $('reload').onclick=()=>state.course?load():start();start();
}
