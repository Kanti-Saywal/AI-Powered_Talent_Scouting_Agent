const S={sessionId:null,jdParsed:null,candidates:[],shortlist:[],mode:'builtin',jobId:null};
let activeCid=null,activeCname=null,selectedFiles=[];

const SAMPLES={
  de:"We are looking for a Senior Data Engineer with 4-6 years of experience.\n\nRequirements:\n- Python and SQL\n- Apache Spark for large-scale data processing\n- AWS (S3, Glue, Redshift, Lambda)\n- Kafka for real-time streaming\n- Airflow for orchestration\n- dbt is a plus",
  ml:"Hiring a Machine Learning Engineer with 3-5 years experience.\n\nMust Have:\n- Python, PyTorch or TensorFlow\n- MLflow, Docker, Kubernetes\n- AWS SageMaker\n\nNice to Have:\n- LLM fine-tuning experience\n- CI/CD for ML pipelines",
  ops:"Data Operations Manager - Remote (5-8 years)\n\nRequired:\n- Data Governance and quality management\n- SQL\n- HubSpot, Salesforce, or Zoho CRM\n- ETL oversight\n- Python for automation",
  hubspot:"HubSpot Specialist - 2-4 years\n\nRequired:\n- HubSpot CRM, Marketing Hub, Sales Hub\n- Workflow automation and sequences\n- Email automation\n- HubSpot reporting\n\nNice to Have:\n- HubSpot CMS\n- Salesforce integration",
  revops:"RevOps Manager - 5-8 years\n\nRequired:\n- Salesforce CRM administration\n- HubSpot Marketing Operations\n- SQL for revenue analytics\n- Process automation\n- Clari or similar forecasting tool",
  ta:"Talent Acquisition Specialist - 2-5 years\n\nRequired:\n- LinkedIn Recruiter and Boolean Search\n- ATS management\n- End-to-end sourcing and interviewing\n- Stakeholder management",
  csm:"Customer Success Manager - 3-6 years\n\nRequired:\n- Customer onboarding and QBR management\n- Salesforce or Gainsight\n- Churn management and NPS tracking",
  sdr:"SDR - 0-2 years\n\nRequired:\n- Cold calling and email outreach\n- LinkedIn Sales Navigator\n- Salesforce or HubSpot CRM\n- Prospecting and pipeline building"
};

function loadSample(t){document.getElementById('jdText').value=SAMPLES[t]||'';}
function setStep(n){for(let i=1;i<=4;i++){const e=document.getElementById('step'+i);e.classList.remove('active','done');if(i<n)e.classList.add('done');else if(i===n)e.classList.add('active');}}
function showLoad(msg){document.getElementById('loadingMsg').textContent=msg;document.getElementById('loadingOverlay').classList.remove('hidden');}
function hideLoad(){document.getElementById('loadingOverlay').classList.add('hidden');}

async function parseJD(){
  const jd=document.getElementById('jdText').value.trim();
  if(!jd){alert('Please paste a job description first.');return;}
  showLoad('Parsing Job Description...');const btn=document.getElementById('parseBtn');btn.disabled=true;
  try{
    const r=await fetch('/api/parse-jd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({jd_text:jd})});
    const d=await r.json();if(d.error)throw new Error(d.error);
    S.sessionId=d.session_id;S.jdParsed=d.jd_parsed;
    document.getElementById('parsedResult').innerHTML=`<div class="parsed-box"><h3>&#10003; JD Parsed Successfully</h3>
      <div class="parsed-grid">
        <div class="parsed-item"><label>Role Title</label><p>${d.jd_parsed.role_title||'&mdash;'}</p></div>
        <div class="parsed-item"><label>Experience</label><p>${d.jd_parsed.experience_min||0}&ndash;${d.jd_parsed.experience_max||'?'} years</p></div>
        <div class="parsed-item" style="grid-column:span 2"><label>Required Skills</label>
          <div class="tag-list">${(d.jd_parsed.required_skills||[]).map(s=>`<span class="tag">${s}</span>`).join('')}</div></div>
        <div class="parsed-item" style="grid-column:span 2"><label>Preferred Skills</label>
          <div class="tag-list">${(d.jd_parsed.preferred_skills||[]).map(s=>`<span class="tag green">${s}</span>`).join('')}</div></div>
      </div></div>`;
    document.getElementById('parsedResult').classList.remove('hidden');
    document.getElementById('panel-discover').classList.remove('hidden');
    setStep(2);document.getElementById('panel-discover').scrollIntoView({behavior:'smooth'});
  }catch(e){alert('Error: '+e.message);}finally{hideLoad();btn.disabled=false;}
}

function switchMode(m){
  S.mode=m;
  document.getElementById('tab-builtin').classList.toggle('active',m==='builtin');
  document.getElementById('tab-upload').classList.toggle('active',m==='upload');
  document.getElementById('mode-builtin').classList.toggle('hidden',m!=='builtin');
  document.getElementById('mode-upload').classList.toggle('hidden',m!=='upload');
}

// ── BUILTIN ────────────────────────────────────────────────────────────────────
async function discoverBuiltin(){
  showLoad('Scanning 240 candidate profiles...');
  try{
    const r=await fetch('/api/discover-candidates',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({session_id:S.sessionId,mode:'builtin'})});
    const d=await r.json();if(d.error)throw new Error(d.error);
    S.candidates=d.candidates;
    document.getElementById('candidateSubtitle').textContent='Sourced from built-in database. Top '+d.candidates.length+' matches ranked by Match Score.';
    renderCandidateGrid(d.candidates);
    document.getElementById('panel-candidates').classList.remove('hidden');
    setStep(3);document.getElementById('panel-candidates').scrollIntoView({behavior:'smooth'});
  }catch(e){alert('Error: '+e.message);}finally{hideLoad();}
}

// ── FILE UPLOAD ────────────────────────────────────────────────────────────────
function handleDragOver(e){e.preventDefault();document.getElementById('uploadZone').classList.add('drag-over');}
function handleDrop(e){e.preventDefault();document.getElementById('uploadZone').classList.remove('drag-over');handleFileSelect(e.dataTransfer.files);}
function handleFileSelect(files){
  const v=Array.from(files).filter(f=>f.name.match(/\.(pdf|docx|doc)$/i));
  if(!v.length){alert('Please upload PDF or DOCX files only.');return;}
  selectedFiles=v;
  document.getElementById('fileListTitle').textContent=v.length+' file(s) ready to parse';
  document.getElementById('fileList').innerHTML=v.map(f=>`<div class="file-item">
    <span class="file-icon">&#128196;</span>
    <span class="file-name">${f.name}</span>
    <span class="file-size">${(f.size/1024).toFixed(1)} KB</span></div>`).join('');
  document.getElementById('fileListBox').classList.remove('hidden');
  document.getElementById('uploadText').textContent=v.length+' file(s) selected';
}
function clearFiles(){
  selectedFiles=[];
  ['fileListBox','parseProgressBox','parsedCVBox'].forEach(id=>document.getElementById(id).classList.add('hidden'));
  document.getElementById('uploadText').textContent='Click to upload or drag & drop CV files here';
  document.getElementById('cvFiles').value='';
}

// ── PARSE CVs ─────────────────────────────────────────────────────────────────
async function startCVParsing(){
  if(!selectedFiles.length){alert('No files selected.');return;}
  const btn=document.getElementById('parseStartBtn');btn.disabled=true;
  const fd=new FormData();selectedFiles.forEach(f=>fd.append('files',f));
  let jobId;
  try{
    const r=await fetch('/api/upload-cvs',{method:'POST',body:fd});
    const d=await r.json();if(d.error)throw new Error(d.error);
    jobId=d.job_id;S.jobId=jobId;
  }catch(e){alert('Upload error: '+e.message);btn.disabled=false;return;}
  document.getElementById('fileListBox').classList.add('hidden');
  document.getElementById('parseProgressBox').classList.remove('hidden');
  document.getElementById('progressCount').textContent='0 / '+selectedFiles.length;
  document.getElementById('progressFill').style.width='0%';
  document.getElementById('parseLog').innerHTML='';
  const parsed=[];
  const es=new EventSource('/api/parse-cvs-stream/'+jobId);
  es.onmessage=(e)=>{
    const data=JSON.parse(e.data);
    const pct=Math.round((data.done/data.total)*100);
    document.getElementById('progressFill').style.width=pct+'%';
    document.getElementById('progressCount').textContent=data.done+' / '+data.total;
    document.getElementById('progressLabel').textContent=data.complete
      ?'Done! '+data.count+' candidates extracted & ready to score.'
      :'Parsing '+data.done+' of '+data.total+'...';
    const log=document.getElementById('parseLog');
    const entry=document.createElement('div');
    entry.className='log-entry '+(data.success?'log-ok':'log-err');
    entry.textContent=data.complete?'All done! '+data.count+' extracted. Click Score & Match below.'
      :(data.success?'✓ ':'⚠ ')+data.filename
        +(data.success&&data.candidate?' → '+data.candidate.name+' ('+data.candidate.title+')':' → Could not extract text');
    log.appendChild(entry);log.scrollTop=log.scrollHeight;
    if(data.success&&data.candidate)parsed.push(data.candidate);
    if(data.complete){es.close();renderParsedCVs(parsed);btn.disabled=false;}
  };
  es.onerror=()=>{es.close();
    fetch('/api/cv-parse-result/'+jobId).then(r=>r.json()).then(d=>{renderParsedCVs(d.candidates);btn.disabled=false;});
  };
}

function renderParsedCVs(candidates){
  document.getElementById('parsedCVCount').innerHTML='<strong>'+candidates.length+' candidates</strong> extracted — click Score & Match to run the full funnel';
  document.getElementById('parsedCVGrid').innerHTML=candidates.map(c=>`
    <div class="mini-cv-card">
      <div class="mini-cv-name">${c.name}</div>
      <div class="mini-cv-title">${c.title}</div>
      <div class="mini-cv-meta">&#128205; ${c.location} &middot; &#128188; ${c.experience_years}y exp</div>
      <div class="mini-cv-skills">${(c.skills||[]).slice(0,6).map(s=>`<span class="skill-tag">${s}</span>`).join('')}</div>
    </div>`).join('');
  document.getElementById('parsedCVBox').classList.remove('hidden');
  document.getElementById('parsedCVBox').scrollIntoView({behavior:'smooth'});
}

// ── DISCOVER FROM UPLOADED CVs → FULL FUNNEL ──────────────────────────────────
async function discoverUploaded(){
  if(!S.jobId){alert('Please parse CVs first.');return;}
  showLoad('Scoring your CVs against the JD...');
  try{
    const r=await fetch('/api/discover-candidates',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({session_id:S.sessionId,mode:'uploaded',job_id:S.jobId})});
    const d=await r.json();if(d.error)throw new Error(d.error);
    S.candidates=d.candidates;
    document.getElementById('candidateSubtitle').textContent=
      'Sourced from your uploaded CVs. Top '+d.candidates.length+' matches ranked by Match Score.';
    renderCandidateGrid(d.candidates);
    document.getElementById('panel-candidates').classList.remove('hidden');
    setStep(3);document.getElementById('panel-candidates').scrollIntoView({behavior:'smooth'});
  }catch(e){alert('Error: '+e.message);}finally{hideLoad();}
}

// ── CANDIDATE GRID (IDENTICAL FOR BOTH MODES) ─────────────────────────────────
function renderCandidateGrid(candidates){
  document.getElementById('candidateGrid').innerHTML=candidates.map(c=>{
    const matched=c.explanation?.required_matched||[];
    const up=c.source==='uploaded_cv';
    return `<div class="candidate-card" id="card-${c.id}">
      <div class="card-header">
        <div>
          <div class="card-name">${c.name}${up?'<span class="source-badge">Your CV</span>':''}</div>
          <div class="card-title">${c.title}</div>
        </div>
        <div class="match-badge">${c.match_score}%</div>
      </div>
      <div class="card-meta">&#128205; ${c.location} &nbsp;&middot;&nbsp; &#128188; ${c.experience_years} yrs</div>
      ${up&&c.filename?`<div class="cv-filename">&#128206; ${c.filename}</div>`:''}
      <div class="skill-tags">${(c.skills||[]).map(s=>{
        const h=matched.some(m=>m.toLowerCase().includes(s.toLowerCase())||s.toLowerCase().includes(m.toLowerCase()));
        return `<span class="skill-tag ${h?'hit':''}">${s}</span>`;}).join('')}</div>
      <div class="score-row">
        <span class="score-label">Required</span>
        <div class="score-bar-bg"><div class="score-bar-fill bar-p" style="width:${c.explanation?.breakdown?.required_skills||0}%"></div></div>
        <span class="score-val">${c.explanation?.breakdown?.required_skills||0}</span>
      </div>
      <div class="score-row">
        <span class="score-label">Preferred</span>
        <div class="score-bar-bg"><div class="score-bar-fill bar-g" style="width:${(c.explanation?.breakdown?.preferred_skills||0)*5}%"></div></div>
        <span class="score-val">${c.explanation?.breakdown?.preferred_skills||0}</span>
      </div>
      <div class="score-row">
        <span class="score-label">Experience</span>
        <div class="score-bar-bg"><div class="score-bar-fill bar-o" style="width:${(c.explanation?.breakdown?.experience||0)*5}%"></div></div>
        <span class="score-val">${c.explanation?.breakdown?.experience||0}</span>
      </div>
      ${c.explanation?.required_missing?.length?`<div class="missing-note">&#9888; Missing: ${c.explanation.required_missing.join(', ')}</div>`:''}
      <div class="card-actions">
        <button class="btn-chat" onclick="openChat('${c.id}','${c.name.replace(/'/g,"\\'")}')">&#128172; Chat Now</button>
        <span class="interest-chip" id="ichip-${c.id}">Interest: &mdash;</span>
      </div>
    </div>`;}).join('');
}

// ── AUTO-ENGAGE (WORKS FOR BOTH MODES) ───────────────────────────────────────
async function engageAll(){
  showLoad('Engaging all candidates in parallel...');
  const btn=document.getElementById('engageAllBtn');btn.disabled=true;
  try{
    const r=await fetch('/api/engage-all',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({session_id:S.sessionId})});
    const d=await r.json();if(d.error)throw new Error(d.error);
    S.shortlist=d.shortlist;
    d.shortlist.forEach(c=>{
      const chip=document.getElementById('ichip-'+c.id);
      if(chip)chip.textContent='Interest: '+c.interest_score+'%';
      const sc=S.candidates.find(x=>x.id===c.id);
      if(sc){sc.conversation=c.conversation;sc.interest_score=c.interest_score;}
    });
    renderEngagement(d.shortlist);
    renderShortlist(d.shortlist);
    document.getElementById('panel-engage').classList.remove('hidden');
    document.getElementById('panel-shortlist').classList.remove('hidden');
    setStep(4);
    document.getElementById('panel-engage').scrollIntoView({behavior:'smooth'});
  }catch(e){alert('Error: '+e.message);}finally{hideLoad();btn.disabled=false;}
}

function renderEngagement(sl){
  document.getElementById('engagementArea').innerHTML='<div class="engagement-grid">'+sl.map(c=>{
    const last=[...(c.conversation||[])].filter(m=>m.role==='candidate').pop();
    const up=c.source==='uploaded_cv';
    return `<div class="eng-card">
      <div class="eng-header">
        <div class="eng-name">${c.name}${up?'<span class="source-badge">Your CV</span>':''} &mdash; ${c.title}</div>
        <div class="score-badges">
          <span class="badge bm">Match ${c.match_score}%</span>
          <span class="badge bi">Interest ${c.interest_score}%</span>
          <span class="badge bc">Combined ${c.combined_score}%</span>
        </div>
      </div>
      <div class="conv-preview">"${last?last.content.substring(0,130)+'&hellip;':'No reply yet'}"</div>
      <button class="btn-view" onclick='viewConv(${JSON.stringify(c.name)},${JSON.stringify(c.conversation)})'>
        &#128172; View Full Conversation (${c.conversation?.length||0} messages)</button>
    </div>`;}).join('')+'</div>';
}

function renderShortlist(sl){
  const rc=i=>(['r1','r2','r3'][i]||'rx');
  document.getElementById('shortlistTable').innerHTML=`
    <table class="sl-table">
      <thead><tr><th>Rank</th><th>Candidate</th><th>Role</th><th>Match</th><th>Interest</th><th>Combined</th><th>Conversation</th></tr></thead>
      <tbody>${sl.map((c,i)=>`<tr>
        <td><span class="rank-badge ${rc(i)}">${i+1}</span></td>
        <td><strong>${c.name}</strong>${c.source==='uploaded_cv'?'<span class="source-badge">Your CV</span>':''}<br><small style="color:var(--muted)">${c.location}</small></td>
        <td>${c.title}<br><small style="color:var(--muted)">${c.experience_years}y exp</small></td>
        <td><span class="pill pm">${c.match_score}%</span></td>
        <td><span class="pill pi">${c.interest_score}%</span></td>
        <td><span class="pill pc">${c.combined_score}%</span></td>
        <td><button class="btn-view" onclick='viewConv(${JSON.stringify(c.name)},${JSON.stringify(c.conversation)})'>&#128172; View</button></td>
      </tr>`).join('')}</tbody>
    </table>
    <div class="score-formula">&#128202; Combined = Match &times; 60% + Interest &times; 40%</div>`;
}

// ── CONVERSATION VIEWER ───────────────────────────────────────────────────────
function viewConv(name,conv){
  const ex=document.getElementById('viewModal');if(ex)ex.remove();
  const modal=document.createElement('div');modal.id='viewModal';modal.className='modal';
  const rc=conv.filter(m=>m.role==='recruiter').length;
  const cc=conv.filter(m=>m.role==='candidate').length;
  modal.innerHTML=`
    <div class="modal-backdrop" onclick="this.parentElement.remove()"></div>
    <div class="modal-box conv-viewer-box">
      <div class="modal-header">
        <div>
          <h3>&#128172; ${name} &mdash; Full Conversation</h3>
          <div style="font-size:12px;color:var(--muted);margin-top:2px">${rc} recruiter &middot; ${cc} candidate replies</div>
        </div>
        <button class="modal-close" onclick="document.getElementById('viewModal').remove()">&#10005;</button>
      </div>
      <div class="conv-explain-bar">
        <div class="conv-explain-item">&#128140; Outreach sent</div>
        <div class="conv-explain-arrow">&rarr;</div>
        <div class="conv-explain-item">&#128172; ${cc} replies captured</div>
        <div class="conv-explain-arrow">&rarr;</div>
        <div class="conv-explain-item">&#128200; Interest scored from sentiment</div>
      </div>
      <div class="conv-scroll-area">
        ${conv.map((m,i)=>`
          <div class="chat-msg ${m.role==='recruiter'?'cmr':'cml'}">
            <div class="chat-role">${m.role==='recruiter'?'&#129333; Recruiter':'&#128100; '+name}</div>
            <div class="chat-bubble ${m.role==='recruiter'?'br':'bc2'}">${m.content}</div>
            ${m.role==='candidate'?`<div class="msg-index">Reply ${conv.slice(0,i+1).filter(x=>x.role==='candidate').length}</div>`:''}
          </div>`).join('')}
      </div>
    </div>`;
  document.body.appendChild(modal);
  setTimeout(()=>{const b=modal.querySelector('.conv-scroll-area');if(b)b.scrollTop=b.scrollHeight;},60);
}

// ── LIVE CHAT ─────────────────────────────────────────────────────────────────
function openChat(cid,cname){
  activeCid=cid;activeCname=cname;
  const c=S.candidates.find(x=>x.id===cid);
  document.getElementById('chatModalTitle').textContent='Chat with '+cname;
  const se=document.getElementById('chatInterestScore');
  se.textContent=c?.interest_score!=null?c.interest_score:'—';
  se.style.color='';
  renderChatMsgs(c?.conversation||[]);
  document.getElementById('chatSuggestions').innerHTML='';
  document.getElementById('chatModal').classList.remove('hidden');
  document.getElementById('chatInput').focus();
  loadSuggestions(cid);
}
function closeChatModal(){document.getElementById('chatModal').classList.add('hidden');activeCid=null;}

function renderChatMsgs(conv){
  document.getElementById('chatMessages').innerHTML=conv.map(m=>`
    <div class="chat-msg ${m.role==='recruiter'?'cmr':'cml'}">
      <div class="chat-role">${m.role==='recruiter'?'&#129333; You':'&#128100; '+activeCname}</div>
      <div class="chat-bubble ${m.role==='recruiter'?'br':'bc2'}">${m.content}</div>
    </div>`).join('');
  scrollChat();
}
function scrollChat(){setTimeout(()=>{const b=document.getElementById('chatMessages');if(b)b.scrollTop=b.scrollHeight;},60);}

async function sendMsg(custom){
  const input=document.getElementById('chatInput');
  const msg=typeof custom==='string'?custom:input.value.trim();
  if(!msg||!activeCid)return;
  input.value='';
  const c=S.candidates.find(x=>x.id===activeCid);
  if(!c.conversation)c.conversation=[];
  c.conversation.push({role:'recruiter',content:msg});
  renderChatMsgs(c.conversation);
  showTyping(true);clearSugg();
  try{
    const r=await fetch('/api/chat-turn',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({session_id:S.sessionId,candidate_id:activeCid,recruiter_message:msg})});
    const d=await r.json();if(d.error)throw new Error(d.error);
    c.conversation=d.conversation;c.interest_score=d.interest_score;
    showTyping(false);renderChatMsgs(d.conversation);
    const se=document.getElementById('chatInterestScore');
    se.textContent=d.interest_score;
    se.style.color=d.interest_score>=70?'var(--success)':d.interest_score>=45?'var(--warn)':'var(--accent3)';
    se.classList.add('flash');setTimeout(()=>se.classList.remove('flash'),600);
    const chip=document.getElementById('ichip-'+activeCid);
    if(chip)chip.textContent='Interest: '+d.interest_score+'%';
    await loadSuggestions(activeCid);
  }catch(e){showTyping(false);alert('Error: '+e.message);}
}

function showTyping(show){
  const el=document.getElementById('typingIndicator');
  if(show){
    el.classList.remove('hidden');
    el.innerHTML=`<div class="chat-role">&#128100; ${activeCname} is typing...</div><div class="typing-bubble"><span></span><span></span><span></span></div>`;
    scrollChat();
  }else{el.classList.add('hidden');el.innerHTML='';}
}

async function loadSuggestions(cid){
  try{
    const r=await fetch('/api/suggest-reply',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({session_id:S.sessionId,candidate_id:cid})});
    const d=await r.json();renderSugg(d.suggestions||[]);
  }catch{renderSugg([]);}
}

function renderSugg(list){
  const el=document.getElementById('chatSuggestions');
  if(!list||!list.length){el.innerHTML='';return;}
  el.innerHTML='<div class="sug-label">&#128161; Click to send:</div><div class="sug-list">'+
    list.map(s=>`<button class="sug-btn" type="button" onclick="sendMsg(this.dataset.msg)" data-msg="${s.replace(/"/g,'&quot;').replace(/'/g,'&#39;')}">${s}</button>`).join('')+'</div>';
}
function clearSugg(){document.getElementById('chatSuggestions').innerHTML='';}
function handleChatKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg();}}

// ── CSV EXPORT ────────────────────────────────────────────────────────────────
function exportCSV(){
  if(!S.shortlist.length){alert('No shortlist yet. Please run Auto-Engage first.');return;}
  const h=['Rank','Name','Title','Location','Exp (yrs)','Match %','Interest %','Combined %','Skills','Source'];
  const rows=S.shortlist.map((c,i)=>[i+1,c.name,c.title,c.location,c.experience_years,
    c.match_score,c.interest_score,c.combined_score,c.skills.join('; '),c.source]);
  const csv=[h,...rows].map(r=>r.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(',')).join('\n');
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='talentscout_shortlist.csv';a.click();
}
