const $=id=>document.getElementById(id);
const authorState={offset:0,total:0,nodes:[],sequence:0,busy:false};
function element(tag,text,className){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(className)e.className=className;return e;}
async function request(path,method='GET',body){const r=await fetch(path,{method,...(body===undefined?{}:{headers:{'Content-Type':'application/json','X-SelfStudy-Request':'1'},body:JSON.stringify(body)})});const data=await r.json();if(!r.ok){const e=new Error(data.error||'请求失败');e.status=r.status;throw e;}return data;}
function lock(value){authorState.busy=value;['author-section','author-node','author-type','author-reload','logout'].forEach(id=>$(id).disabled=value);$('author-prev').disabled=value||authorState.offset===0;$('author-next').disabled=value||authorState.offset+20>=authorState.total;}
function loginView(){++authorState.sequence;$('login').hidden=false;$('author-workspace').hidden=true;$('author-questions').replaceChildren();$('author-status').textContent='请使用本地令牌登录。';}
function nodeOptions(){$('author-node').replaceChildren(new Option('全部知识点',''));authorState.nodes.filter(n=>n.section_id===$('author-section').value).sort((a,b)=>a.id.localeCompare(b.id,'en',{numeric:true})).forEach(n=>{const option=new Option(`${n.depth>1?'　':''}${n.id} ${n.title}`,n.id);option.disabled=n.depth===1;$('author-node').append(option);});}
function addFigure(container,ref,label){const figure=element('figure');const img=element('img');img.src='/api/diagrams/'+encodeURIComponent(typeof ref==='string'?ref:ref.diagram_id)+'.svg';img.alt=label;img.width=720;img.height=480;img.loading='lazy';const link=element('a','查看大图 ↗','figure-link');link.href=img.src;link.target='_blank';link.rel='noopener';figure.append(img,link);container.append(figure);}
function renderQuestion(q){
  const article=element('article',undefined,'author-question');const meta=element('div',undefined,'question-meta');meta.append(element('span',`${q.node_id} · ${q.node_title}`),element('span',`修订 ${q.revision}`));article.append(meta,element('h2',q.prompt));
  const figures=element('div',undefined,'figures');(q.figure_refs||[]).forEach((ref,i)=>addFigure(figures,ref,`题干图 ${i+1}`));article.append(figures);
  if(q.options){const list=element('div');q.options.forEach(o=>{list.append(element('p',`${o.id}. ${o.text}`));if(o.figure_ref)addFigure(list,o.figure_ref,`选项 ${o.id} 的图`);});article.append(list);}
  const answer=q.correct_answers?q.correct_answers.join('、'):q.blanks.map((b,i)=>`第${i+1}空：${b.accepted_answers.join(' / ')}`).join('\n');
  article.append(element('p','标准答案：'+answer,'author-answer'),element('p',q.explanation||'暂无解析。'));
  const actions=element('div',undefined,'actions');const info=element('span',q.enabled?'已启用 · 学习端可见':'已停用 · 学习端隐藏','author-status');const button=element('button',q.enabled?'停用题目':'启用题目','subtle');
  button.onclick=async()=>{if(authorState.busy)return;lock(true);button.disabled=true;try{await request('/api/author/questions/'+encodeURIComponent(q.id),'PATCH',{enabled:!q.enabled,revision:q.revision});await load();}catch(e){if(e.status===401)loginView();else{info.textContent=e.message+(e.status===409?' 请点击“刷新题目”获取最新状态。':'');info.className='error';}button.disabled=false;}finally{lock(false);}};
  actions.append(info,button);article.append(actions);return article;
}
async function load(){
  const sequence=++authorState.sequence;lock(true);$('author-status').textContent='正在载入作者题目…';$('author-questions').replaceChildren();
  try{const query=new URLSearchParams({section:$('author-section').value,node_id:$('author-node').value,type:$('author-type').value,offset:authorState.offset,limit:20});const data=await request('/api/author/questions?'+query);if(sequence!==authorState.sequence)return;
    $('login').hidden=true;$('author-workspace').hidden=false;authorState.total=data.total;$('author-status').textContent=data.total?`共 ${data.total} 题（包含停用题）`:$('author-section').value==='D'?'D 板块出题待定。':'当前筛选没有题目。';$('author-questions').replaceChildren(...data.items.map(renderQuestion));$('author-page').textContent=data.total?`${Math.floor(authorState.offset/20)+1} / ${Math.ceil(data.total/20)}`:'0 / 0';
  }catch(e){if(sequence!==authorState.sequence)return;if(e.status===401)loginView();else $('author-status').textContent='加载失败：'+e.message;}finally{if(sequence===authorState.sequence)lock(false);}
}
$('login').onsubmit=async e=>{e.preventDefault();$('login-button').disabled=true;$('login-error').textContent='';try{await request('/api/author/login','POST',{token:$('token').value.trim()});$('token').value='';await load();}catch(error){$('login-error').textContent=error.message;}finally{$('login-button').disabled=false;}};
$('logout').onclick=async()=>{lock(true);try{await request('/api/author/logout','POST',{});loginView();}catch(e){$('author-status').textContent=e.message;}finally{lock(false);}};
['author-section','author-node','author-type'].forEach(id=>$(id).onchange=()=>{authorState.offset=0;if(id==='author-section')nodeOptions();load();});
$('author-prev').onclick=()=>{authorState.offset=Math.max(0,authorState.offset-20);load();};$('author-next').onclick=()=>{authorState.offset+=20;load();};$('author-reload').onclick=load;
(async()=>{try{authorState.nodes=(await request('/api/course')).nodes;nodeOptions();await load();}catch(e){loginView();$('login-error').textContent=e.message;}})();
