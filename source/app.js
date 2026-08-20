import {CREATOR_VERSION,LIMITS,makeProject,makeAuthor,makeWork,makeChapter,makeComment,getExample,normalizeProject,validateProject,generatePackFiles,generateNexusPage,workWordCount,createZip} from "./core.js";

const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const STORAGE="aoo-creator-project-v1", LIBRARY="aoo-creator-library-v1", THEME="aoo-creator-theme";
let library=loadLibrary(),project=library.projects[library.currentId],selectedWorkId=project.works[0]?.id||null,selectedChapterId=project.works[0]?.chapters[0]?.id||null,activeTab="write",undoStack=[],redoStack=[],saveTimer=null,pristine=!localStorage.getItem(LIBRARY)&&!localStorage.getItem(STORAGE);

function loadLibrary(){
  try{
    const raw=localStorage.getItem(LIBRARY);
    if(raw){const lib=normalizeLibrary(JSON.parse(raw));if(Object.keys(lib.projects).length)return lib}
    const legacy=localStorage.getItem(STORAGE);
    if(legacy){const p=withId(normalizeProject(JSON.parse(legacy)));return{currentId:p.id,projects:{[p.id]:p},saved:{}}}
  }catch(error){console.warn(error)}
  const p=makeProject();return{currentId:p.id,projects:{[p.id]:p},saved:{}};
}
function normalizeLibrary(lib){const projects={};
  Object.values(lib?.projects||{}).forEach(raw=>{try{const p=withId(normalizeProject(raw));projects[p.id]=p}catch(error){console.warn(error)}});
  const ids=Object.keys(projects);return{currentId:projects[lib?.currentId]?lib.currentId:ids[0],projects,saved:lib?.saved||{}};
}
function withId(p){if(!p.id)p.id=`project_${crypto.randomUUID().replaceAll("-","")}`;return p}
function collections(){return Object.values(library.projects).sort((a,b)=>String(a.pack.name||"").localeCompare(String(b.pack.name||"")))}
function adoptCollection(next,message){library.projects[next.id]=next;library.currentId=next.id;project=next;selectedWorkId=project.works[0]?.id||null;selectedChapterId=project.works[0]?.chapters[0]?.id||null;activeTab="write";pristine=false;save(message);render()}
function snapshot(){pristine=false;undoStack.push(JSON.stringify(project));if(undoStack.length>40)undoStack.shift();redoStack=[]}
let pendingFileSave=false;
function save(message="Autosaved in this browser."){clearTimeout(saveTimer);saveTimer=setTimeout(()=>{
  project.updatedAt=new Date().toISOString();library.projects[project.id]=project;library.currentId=project.id;
  if(pendingFileSave){library.saved=library.saved||{};library.saved[project.id]=project.updatedAt;pendingFileSave=false}
  try{localStorage.setItem(LIBRARY,JSON.stringify(library));status(message)}
  catch(error){status("Browser storage is full, so this change was not autosaved. Use Save project to write a file.","error")}
  renderBackupState();
},180)}
function status(message,kind=""){const el=$("#statusBar");el.textContent=message;el.className=`status-text ${kind}`;void el.offsetWidth;el.classList.add("flash")}
const tourSteps=[
 {tab:"write",sel:"#collectionSelect",title:"Your collections",text:"Every collection you build lives here. Switching keeps each one\u2019s works, authors and settings separate. New starts another; nothing is lost when you do."},
 {tab:"write",sel:"#projectSettingsBtn",title:"Name it carefully",text:"Settings holds the collection name and its namespace. The namespace is permanent once you publish \u2014 changing it later turns an update into a separate, competing mod."},
 {tab:"write",sel:"#authorSummary",title:"Your authors",text:"Pseuds are in-world handles, up to 24 characters. Each gets a hidden permanent ID, so renaming an author never breaks anything."},
 {tab:"write",sel:"#workList",title:"Works and their state",text:"Each work shows its author and chapter count, plus a dot: green ready, amber warnings, red errors. The heading counts anything still needing a fix."},
 {tab:"write",sel:"#chapterStrip",title:"Write here",text:"Add chapters with the plus, then write in the panel beside this list. Word counts keep themselves up to date as you type."},
 {tab:"details",sel:"#workForm",title:"Metadata readers see",text:"Rating, archive warnings, tags and summary. Release timing only appears on a work in progress, and the word count is counted for you."},
 {tab:"preview",sel:"#aooPreview",title:"How it looks in game",text:"The work card as Archive of Our Overwrites will render it, including long titles and large tag walls."},
 {tab:"validate",sel:"#validationList",title:"Errors block the build",text:"Every problem names the work and what to fix. Errors stop the export on purpose; warnings are only advice."},
 {tab:"write",sel:"#backupState",title:"This is the one that matters",text:"Autosave lives only in this browser. Save project writes a .aoopack.json \u2014 keep it. Re-importing that file is the only way to publish an update your readers keep their library through."},
 {tab:"write",sel:"#buildBtn",title:"Build the mod, and get your Nexus page",text:"When validation passes, this exports a Nexus-ready ZIP. Upload it and list Archive of Our Overwrites as a required mod."}
];
let tourOn=false,tourAt=0;
function startTour(){tourOn=true;tourAt=0;renderTourStep()}
function endTour(){tourOn=false;tourAt=0;$("#tutorialRoot").innerHTML="";localStorage.setItem("aoo-creator-tutorial-seen","1");status("Tour finished. Reopen it any time from Tutorial.")}
function renderTourStep(){
  if(!tourOn)return;const step=tourSteps[tourAt];if(!step)return endTour();
  if(activeTab!==step.tab){showTab(step.tab);return setTimeout(renderTourStep,60)}
  const target=document.querySelector(step.sel);
  if(!target||!target.getClientRects().length){tourAt+=1;return renderTourStep()}
  const r=target.getBoundingClientRect(),pad=6,cardW=Math.min(360,innerWidth-32),cardH=250;
  const below=r.bottom+cardH<innerHeight;
  const top=below?Math.min(innerHeight-cardH-12,r.bottom+12):Math.max(12,r.top-cardH-12);
  const left=Math.min(innerWidth-cardW-16,Math.max(16,r.left));
  $("#tutorialRoot").innerHTML=`<div class="tour-highlight" style="left:${Math.max(0,r.left-pad)}px;top:${Math.max(0,r.top-pad)}px;width:${r.width+pad*2}px;height:${r.height+pad*2}px"></div><article class="tour-card" role="dialog" aria-modal="true" style="left:${left}px;top:${top}px"><span class="eyebrow">Guided tour</span><h2>${esc(step.title)}</h2><p>${esc(step.text)}</p><footer><span class="tour-count">${tourAt+1} / ${tourSteps.length}</span><button data-tour="skip" class="ghost">Skip</button><button data-tour="back" class="ghost" ${tourAt===0?"disabled":""}>Back</button><button data-tour="next" class="primary">${tourAt===tourSteps.length-1?"Finish":"Next"}</button></footer></article>`;
}
function ask(body,{title="Are you sure?",eyebrow="Confirm",okLabel="Confirm",danger=false}={}){const d=$("#confirmDialog");$("#confirmEyebrow").textContent=eyebrow;$("#confirmTitle").textContent=title;$("#confirmBody").textContent=body;const ok=$("#confirmOk");ok.textContent=okLabel;ok.className=danger?"danger":"primary";d.showModal();return new Promise(resolve=>d.addEventListener("close",()=>resolve(d.returnValue==="ok"),{once:true}))}
function currentWork(){return project.works.find(w=>w.id===selectedWorkId)||null}
const countWords=t=>{const v=String(t||"").trim();return v?v.split(/\s+/).length:0};
function currentChapter(){const w=currentWork();if(!w)return null;return w.chapters.find(c=>c.id===selectedChapterId)||w.chapters[0]||null}
function deriveWork(w){if(!w)return;w.wordCount=w.chapters.reduce((t,c)=>t+countWords(c.body),0);if((Number(w.stats.comments)||0)<w.comments.length)w.stats.comments=w.comments.length}
function updateDerivedFields(){const w=currentWork();if(!w)return;const f=$("#wordCountField");if(f)f.value=String(w.wordCount||0);const cs=document.querySelector('[data-bind-stat="comments"]');if(cs)cs.value=w.stats.comments??0}
function selectedAuthor(){const w=currentWork();return project.authors.find(a=>a.id===w?.authorId)||project.authors[0]||null}
function download(blob,name){const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
const bool=v=>String(v)==="true";
const list=v=>String(v||"").split(",").map(x=>x.trim()).filter(Boolean);
const esc=v=>String(v??"").replace(/[&<>\"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function mutate(fn,{full=false,message}={}){snapshot();fn();deriveWork(currentWork());save(message);if(full)render();else{renderSummary();renderPreview();renderValidationBadges();updateCounters();updateDerivedFields()}}
function render(){renderCollections();renderBackupState();renderSummary();renderAuthors();renderWorks();renderWorkForm();renderChapterStrip();renderChapterEditor();renderComments();renderPreview();renderValidation();showTab(activeTab)}
function perWorkIssues(){const map={},issues=validateProject(project);project.works.forEach((w,i)=>{const mine=issues.filter(x=>String(x.path).startsWith(`work ${i+1}:`));map[w.id]={errors:mine.filter(x=>x.kind==="error").length,warnings:mine.filter(x=>x.kind==="warning").length}});return map}
function renderBackupState(){const el=$("#backupState");if(!el)return;const saved=library.saved?.[project.id],dirty=saved!==project.updatedAt;el.textContent=dirty?"Not saved to a file":"Saved to a file";el.className=`backup-state ${dirty?"dirty":"clean"}`;el.title=dirty?"Autosave lives only in this browser. Use Save project to write a .aoopack.json you keep — it is the only way to publish an update later.":`Written to a file ${new Date(saved).toLocaleString()}. Autosave since then lives only in this browser.`}
function renderCollections(){const m=$("#mastheadName");if(m)m.textContent=project.pack.name||"Untitled collection";
  const sel=$("#collectionSelect");if(!sel)return;const all=collections();
  sel.innerHTML=all.map(p=>`<option value="${p.id}"${p.id===project.id?" selected":""}>${esc(p.pack.name||"Untitled collection")}</option>`).join("");
  const del=$("#deleteCollectionBtn");if(del)del.disabled=all.length<=1}
function renderSummary(){const p=project.pack;$("#projectSummary").innerHTML=`<span>${project.authors.length} ${project.authors.length===1?"author":"authors"} · ${project.works.length} ${project.works.length===1?"work":"works"} · v${esc(p.version)}</span><code class="ns" title="Permanent after your first public release">${esc(p.namespace||"no namespace")}</code>`}
function renderAuthors(){const total=project.authors.length,active=project.authors.filter(a=>a.status==="Active").length;renderBackupState();$("#authorSummary").innerHTML=`<strong>${total} ${total===1?"author":"authors"}</strong><span>${active} active · ${total-active} inactive · manage</span>`}
function renderAuthorsPane(){const host=$("#authorRows");if(!host)return;const q=($("#authorSearch")?.value||"").toLowerCase();const rows=project.authors.filter(a=>!q||(a.pseud||"").toLowerCase().includes(q));host.innerHTML=rows.map(a=>{const uses=project.works.filter(w=>w.authorId===a.id).length;return `<article class="author-row" data-author-row="${a.id}"><label>Pseud <input data-author-field="pseud" maxlength="${LIMITS.author}" value="${esc(a.pseud)}"></label><label>Status <select data-author-field="status"><option value="Inactive"${a.status!=="Active"?" selected":""}>Inactive</option><option value="Active"${a.status==="Active"?" selected":""}>Active</option></select></label><div class="author-meta"><i class="author-dot ${a.status==="Active"?"active":""}"></i><small>${uses} ${uses===1?"work":"works"}</small></div><button class="danger" data-delete-author${uses?" disabled":""}>Delete</button></article>`}).join("")||`<p class="help-callout">No authors match that search.</p>`}
function renderWorks(){const query=$("#workSearch").value.toLowerCase(),host=$("#workList"),issues=pristine?{}:perWorkIssues();
  let attention=0;project.works.forEach(w=>{if(issues[w.id]?.errors)attention++});
  const badge=$("#worksAttention");if(badge){badge.textContent=attention?`${attention} need fixing`:"";badge.hidden=!attention}
  host.innerHTML=project.works.filter(w=>{const a=project.authors.find(x=>x.id===w.authorId);return !query||`${w.title} ${a?.pseud||""}`.toLowerCase().includes(query)}).map(w=>{
    const a=project.authors.find(x=>x.id===w.authorId),st=issues[w.id],state=st?.errors?"error":st?.warnings?"warning":"ok",
      label=st?.errors?`${st.errors} error(s)`:st?.warnings?`${st.warnings} warning(s)`:"Ready";
    return `<button class="nav-item work-item ${w.id===selectedWorkId?"active":""}" data-work="${w.id}" title="${esc(w.title||"Untitled")} — ${label}"><span class="work-line"><span class="work-title">${esc(w.title||"Untitled")}</span><small class="work-by">${esc(a?.pseud||"no author")} · ${w.chapters.length} ch</small></span><i class="work-state ${pristine?"":state}" aria-hidden="true"></i></button>`}).join("")||`<small>No matching works.</small>`}

function renderWorkForm(){const w=currentWork();if(!w)return;deriveWork(w);const t=w.title||"Untitled work";$("#workHeading").textContent=t;$("#detailsHeading").textContent=t;$("#authorSelect").innerHTML=project.authors.map(a=>`<option value="${a.id}">${esc(a.pseud)}</option>`).join("");$$('[data-bind]').forEach(el=>{const key=el.dataset.bind,value=w[key];el.value=typeof value==='boolean'?String(value):(value??'')});$$('[data-bind-list]').forEach(el=>el.value=(w[el.dataset.bindList]||[]).join(', '));renderRatingChips(w);renderTagFields(w);$$('[data-bind-stat]').forEach(el=>el.value=w.stats?.[el.dataset.bindStat]??0);$("#chapterCount").textContent=w.chapters.length;$("#commentCount").textContent=w.comments.length;toggleConditionalFields(w);updateDerivedFields();updateCounters()}
function renderRatingChips(w){const box=$("#ratingChips");if(!box)return;
  $$("#ratingChips [data-rating]").forEach(b=>{const on=b.dataset.rating===w.rating;
    b.classList.toggle("on",on);b.setAttribute("aria-checked",String(on))})}
function renderTagFields(w){$$("[data-tagfield]").forEach(field=>{
  const key=field.dataset.tagfield,values=w[key]||[],host=field.querySelector(".tag-chips");
  host.innerHTML=values.map((t,i)=>`<span class="tag-chip">${esc(t)}<button type="button" data-drop="${i}" aria-label="Remove ${esc(t)}">×</button></span>`).join("")})}
function writeTagField(field,values){const bound=field.querySelector("[data-bind-list]");
  bound.value=values.join(", ");bound.dispatchEvent(new Event("input",{bubbles:true}))}
function toggleConditionalFields(w){const wip=w.complete===false||String(w.complete)==="false";const m=$("#releaseModelField"),i=$("#releaseIntervalField");if(m)m.hidden=!wip;if(i)i.hidden=!wip}
function updateCounters(){const w=currentWork();if(!w)return;$$('[data-counter]').forEach(el=>{const key=el.dataset.counter;el.textContent=`${String(w[key]||"").length} / ${key==="summary"?LIMITS.summary:key==="pseud"?LIMITS.author:LIMITS.title}`});const count=[...w.fandoms,...w.relationships,...w.characters,...w.tags].length;$("#tagTotal").textContent=`${count} / ${LIMITS.tags}`}

function renderChapterStrip(){const w=currentWork(),host=$("#chapterStrip");if(!host)return;if(!w){host.innerHTML="";return}const cur=currentChapter();host.innerHTML=w.chapters.map((c,i)=>`<button class="strip-item ${c.id===cur?.id?"active":""}" data-chapter-select="${c.id}"><span class="strip-num">${i+1}</span><span class="strip-name">${esc(c.title||"Untitled chapter")}</span><small>${countWords(c.body)}w</small></button>`).join("")||`<small>No chapters yet.</small>`}
function renderChapterEditor(){const w=currentWork(),host=$("#chapterEditor");if(!host)return;if(!w){host.innerHTML="";return}const c=currentChapter();if(!c){host.innerHTML=`<p class="help-callout">This work needs at least one chapter. Choose <strong>Add chapter</strong> to begin.</p>`;return}const i=w.chapters.indexOf(c);host.innerHTML=`<div class="editor-bar"><label class="grow">Chapter title<input data-chapter-field="title" maxlength="${LIMITS.chapterTitle}" value="${esc(c.title)}"></label><label class="tight">Price (€$)<input data-chapter-field="price" type="number" min="1" value="${c.price||300}"></label><div class="card-actions"><button data-move-chapter="up" ${i===0?"disabled":""} title="Move up">↑</button><button data-move-chapter="down" ${i===w.chapters.length-1?"disabled":""} title="Move down">↓</button><button class="danger" data-delete-chapter>Delete</button></div></div><textarea class="manuscript" data-chapter-field="body" placeholder="Write the chapter here. Leave a blank line between paragraphs.">${esc(c.body)}</textarea><div class="editor-foot"><span id="chapterWords">${countWords(c.body)} words</span><span>Chapter ${i+1} of ${w.chapters.length}</span></div><details class="notes"><summary>Author&rsquo;s notes (optional)</summary><label>Notes before<textarea data-chapter-field="notesBefore" rows="3">${esc(c.notesBefore)}</textarea></label><label>Notes after<textarea data-chapter-field="notesAfter" rows="3">${esc(c.notesAfter)}</textarea></label></details>`}
function renderComments(){const w=currentWork(),host=$("#commentList");if(!w){host.innerHTML="";return}host.innerHTML=w.comments.map((c,i)=>`<article class="edit-card" data-comment="${c.id}"><div class="edit-card-header"><strong>Comment ${i+1}</strong><button class="danger" data-delete-comment>Delete</button></div><div class="card-fields"><label>User <input data-comment-field="user" value="${esc(c.user)}"></label><label>Date <input data-comment-field="date" value="${esc(c.date)}"></label><label>Attached to <select data-comment-field="chapterIndex"><option value="0">Whole work / chapter 1</option>${w.chapters.map((ch,ci)=>ci?`<option value="${ci}" ${Number(c.chapterIndex)===ci?"selected":""}>Chapter ${ci+1}: ${esc(ch.title)}</option>`:"").join("")}</select></label><label class="body">Comment <textarea data-comment-field="body" rows="3">${esc(c.body)}</textarea></label></div></article>`).join("")||`<p class="help-callout">No comments added. This is valid; comments are optional.</p>`}

function renderPreview(){const w=currentWork(),hosts=$$(".aoo-preview");if(!hosts.length)return;if(!w){hosts.forEach(h=>h.innerHTML="");return}const tags=[...w.fandoms,...w.relationships,...w.characters,...w.tags],shown=tags.slice(0,12),author=project.authors.find(a=>a.id===w.authorId);const html=`<article class="preview-work"><h2>${esc(w.title||"Untitled")}</h2><div class="preview-byline">by ${esc(w.pseud||author?.pseud||"unknown")}</div><div class="preview-meta"><strong>RATING</strong><span>${esc(w.rating)}</span><strong>WARNINGS</strong><span>${esc(w.warning)}</span><strong>CATEGORY</strong><span>${esc(w.category)}</span><strong>FANDOM</strong><span>${esc(w.fandoms.join(", ")||"—")}</span></div><div class="preview-tag-row">${shown.map(t=>`<span class="preview-tag" title="${esc(t)}">${esc(t)}</span>`).join("")}${tags.length>shown.length?`<span class="preview-more">SHOW ALL · +${tags.length-shown.length} TAGS</span>`:""}</div><p class="preview-summary">${esc(w.summary||"No summary provided.")}</p><div class="preview-stats"><span><small>Props</small>${w.stats.props||0}</span><span><small>Reads</small>${w.stats.reads||0}</span><span><small>Comments</small>${w.stats.comments||0}</span><span><small>Stashes</small>${w.stats.stashes||0}</span><span><small>Words</small>${w.wordCount||0}</span><span><small>Chapters</small>${w.chapters.length} / ${w.complete?"Complete":"WIP"}</span></div></article>`;hosts.forEach(h=>h.innerHTML=html)}
let worksTimer=null;
function scheduleWorks(){clearTimeout(worksTimer);worksTimer=setTimeout(renderWorks,250)}
function renderReadyState(){const el=$("#readyState");if(!el)return;
  if(pristine){el.hidden=true;return}
  const errors=validateProject(project).filter(i=>i.kind==="error").length;
  el.hidden=false;el.textContent=errors?`${errors} to fix`:"Ready to build";
  el.className=`ready-state ${errors?"blocked":"ready"}`;
  el.title=errors?"Validation errors block the export. Click to see them.":"Validation passes. This collection can be built."}
function renderValidationBadges(){scheduleWorks();renderReadyState();const badge=$("#issueCount");if(pristine){badge.textContent="–";badge.title="Nothing to check yet";return}const issues=validateProject(project),errors=issues.filter(i=>i.kind==="error").length;badge.textContent=errors||issues.length;badge.title=`${errors} errors, ${issues.filter(i=>i.kind==="warning").length} warnings`}
function renderValidation(){const host=$("#validationList");if(pristine){$("#validationSummary").innerHTML=`<p class="help-callout">Nothing checked yet. Start writing and this report fills in automatically.</p>`;host.innerHTML="";renderValidationBadges();return}const issues=validateProject(project),errors=issues.filter(i=>i.kind==="error").length,warnings=issues.filter(i=>i.kind==="warning").length;$("#validationSummary").innerHTML=`<p class="help-callout"><strong>${errors}</strong> errors · <strong>${warnings}</strong> warnings. Errors block ZIP export; warnings are advisory.</p>`;host.innerHTML=issues.length?issues.map(i=>`<article class="issue ${i.kind}"><span class="issue-kind">${i.kind}</span><div><strong>${esc(i.path)}</strong><br>${esc(i.message)}</div></article>`).join(""):`<article class="issue ok"><span class="issue-kind">ready</span><div><strong>Framework contract passed.</strong><br>The collection is ready to build.</div></article>`;renderValidationBadges()}
function renderProjectForm(){$$('[data-pack]').forEach(el=>el.value=project.pack[el.dataset.pack]??"")}
function showTab(tab){activeTab=tab;$$('.editor-tabs button').forEach(b=>b.classList.toggle('active',b.dataset.tab===tab));$$('.pane').forEach(p=>p.classList.remove('active'));const w=currentWork(),needsWork=tab!=="project"&&tab!=="authors";$("#emptyState").hidden=!(needsWork&&!w);if(needsWork&&!w)return;const pane=document.querySelector(`#${tab}Pane`);if(pane)pane.classList.add("active");if(tab==="authors")renderAuthorsPane();if(tab==="project")renderProjectForm();if(tab==="validate")renderValidation();if(tab==="preview")renderPreview();if(tab==="write"){renderChapterStrip();renderChapterEditor()}}

document.addEventListener("click",event=>{const tab=event.target.closest("[data-tab]");if(tab)return showTab(tab.dataset.tab);const workBtn=event.target.closest("[data-work]");if(workBtn){selectedWorkId=workBtn.dataset.work;selectedChapterId=currentWork()?.chapters[0]?.id||null;activeTab="write";return render()}const delAuthor=event.target.closest("[data-delete-author]");if(delAuthor){const row=delAuthor.closest("[data-author-row]");const a=project.authors.find(x=>x.id===row.dataset.authorRow);if(!a)return;const uses=project.works.filter(w=>w.authorId===a.id).length;if(uses){status(`Reassign ${a.pseud}\u2019s ${uses} work(s) to another author first.`,"error");return}if(project.authors.length<=1){status("A collection needs at least one author.","error");return}ask(`\u201c${a.pseud}\u201d will be removed from this collection.`,{title:"Delete author?",okLabel:"Delete",danger:true}).then(yes=>{if(yes)mutate(()=>{project.authors=project.authors.filter(x=>x.id!==a.id)},{full:true,message:"Author deleted."})});return}
  const pick=event.target.closest("[data-chapter-select]");if(pick){selectedChapterId=pick.dataset.chapterSelect;renderChapterStrip();renderChapterEditor();return}
  const w=currentWork(),chapter=currentChapter();
  if(w&&chapter&&event.target.closest("[data-delete-chapter]")){const i=w.chapters.indexOf(chapter);ask(`\u201c${chapter.title||"Untitled chapter"}\u201d and its text will be removed.`,{title:"Delete chapter?",okLabel:"Delete",danger:true}).then(yes=>{if(yes)mutate(()=>{w.chapters.splice(i,1);selectedChapterId=w.chapters[Math.max(0,i-1)]?.id||null},{full:true,message:"Chapter deleted."})});return}
  const move=event.target.closest("[data-move-chapter]")?.dataset.moveChapter;
  if(w&&chapter&&move){const i=w.chapters.indexOf(chapter),j=move==="up"?i-1:i+1;if(j>=0&&j<w.chapters.length)mutate(()=>{[w.chapters[i],w.chapters[j]]=[w.chapters[j],w.chapters[i]]},{full:true,message:"Chapter reordered."});return}
  const commentCard=event.target.closest("[data-comment]");if(commentCard&&event.target.closest("[data-delete-comment]")){const w=currentWork(),i=w.comments.findIndex(c=>c.id===commentCard.dataset.comment);ask("This archived comment will be removed.",{title:"Delete comment?",okLabel:"Delete",danger:true}).then(yes=>{if(yes)mutate(()=>w.comments.splice(i,1),{full:true,message:"Comment deleted."})});return}
});

$("#workForm").addEventListener("input",event=>{const w=currentWork();if(!w)return;const bind=event.target.dataset.bind,listKey=event.target.dataset.bindList,stat=event.target.dataset.bindStat;snapshot();if(bind){let value=event.target.value;if(["complete","active"].includes(bind))value=bool(value);if(["releaseIntervalDays","wordCount"].includes(bind))value=Number(value)||0;w[bind]=value;if(bind==="authorId"){const a=project.authors.find(x=>x.id===value);if(a){w.pseud=a.pseud;document.querySelector('[data-bind="pseud"]').value=a.pseud}}if(bind==="title"){$("#workHeading").textContent=value||"Untitled work";$("#detailsHeading").textContent=value||"Untitled work"}if(bind==="complete"){if(value===true)w.active=false;toggleConditionalFields(w);const a=document.querySelector('[data-bind="active"]');if(a)a.value=String(w.active)}}else if(listKey)w[listKey]=list(event.target.value);else if(stat)w.stats[stat]=Number(event.target.value)||0;save();renderSummary();renderPreview();renderValidationBadges();updateCounters()});
$("#projectForm").addEventListener("input",event=>{const key=event.target.dataset.pack;if(!key)return;snapshot();project.pack[key]=event.target.value;save();renderSummary();if(key==="name")renderCollections();renderValidationBadges()});
$("#chapterEditor").addEventListener("input",event=>{const field=event.target.dataset.chapterField;if(!field)return;const c=currentChapter();if(!c)return;snapshot();c[field]=field==="price"?Number(event.target.value)||0:event.target.value;if(field==="body"){deriveWork(currentWork());const wc=$("#chapterWords");if(wc)wc.textContent=`${countWords(c.body)} words`;renderChapterStrip();updateDerivedFields();renderPreview()}if(field==="title"){renderChapterStrip();renderPreview()}save();renderValidationBadges()});
$("#commentList").addEventListener("input",event=>{const card=event.target.closest("[data-comment]"),field=event.target.dataset.commentField;if(!card||!field)return;const c=currentWork().comments.find(x=>x.id===card.dataset.comment);snapshot();c[field]=field==="chapterIndex"?Number(event.target.value):event.target.value;save();renderValidationBadges()});

$("#addAuthorBtn").addEventListener("click",()=>{mutate(()=>project.authors.push(makeAuthor("newauthor",false)),{full:true,message:"Author added — give it a pseud."});showTab("authors");const rows=$$("[data-author-row]"),input=rows[rows.length-1]?.querySelector('[data-author-field="pseud"]');if(input){input.focus();input.select()}});
$("#backupState").addEventListener("click",()=>$("#saveProjectBtn").click());
$("#readyState").addEventListener("click",()=>showTab("validate"));
$("#livePreviewBtn").addEventListener("click",()=>{const p=$("#writePreview"),b=$("#livePreviewBtn");
  const on=p.hidden;p.hidden=!on;b.setAttribute("aria-pressed",String(on));
  b.textContent=on?"Hide preview":"Show preview";$("#writePane").classList.toggle("with-preview",on);
  localStorage.setItem("aoo-creator-live-preview",on?"1":"");if(on)renderPreview()});
$("#manageAuthorsBtn").addEventListener("click",()=>showTab("authors"));
$("#authorSummary").addEventListener("click",()=>showTab("authors"));
$("#ratingChips").addEventListener("click",event=>{const b=event.target.closest("[data-rating]");if(!b)return;
  const input=$("#ratingValue");input.value=b.dataset.rating;
  input.dispatchEvent(new Event("input",{bubbles:true}));renderRatingChips(currentWork())});
$("#workForm").addEventListener("keydown",event=>{if(event.key!=="Enter")return;
  const entry=event.target.closest(".tag-entry");if(!entry)return;event.preventDefault();
  const field=entry.closest("[data-tagfield]"),w=currentWork();if(!w)return;
  const value=entry.value.trim();if(!value)return;
  const next=(w[field.dataset.tagfield]||[]).concat(value);entry.value="";
  writeTagField(field,next);renderTagFields(currentWork())});
$("#workForm").addEventListener("click",event=>{const drop=event.target.closest("[data-drop]");if(!drop)return;
  const field=drop.closest("[data-tagfield]"),w=currentWork();if(!w)return;
  const next=(w[field.dataset.tagfield]||[]).filter((_,i)=>i!==Number(drop.dataset.drop));
  writeTagField(field,next);renderTagFields(currentWork())});
$("#authorSearch").addEventListener("input",renderAuthorsPane);
$("#authorRows").addEventListener("input",event=>{const row=event.target.closest("[data-author-row]"),field=event.target.dataset.authorField;if(!row||!field)return;const a=project.authors.find(x=>x.id===row.dataset.authorRow);if(!a)return;snapshot();if(field==="pseud"){a.pseud=event.target.value.slice(0,LIMITS.author);project.works.filter(w=>w.authorId===a.id).forEach(w=>w.pseud=a.pseud)}else{a.status=event.target.value;row.querySelector(".author-dot").classList.toggle("active",a.status==="Active")}save("Author updated.");renderAuthors();renderSummary();renderWorkForm();renderPreview();renderValidationBadges()});
$("#collectionSelect").addEventListener("change",event=>{const next=library.projects[event.target.value];if(!next||next.id===project.id)return;library.projects[project.id]=project;adoptCollection(next,`Switched to ${next.pack.name||"Untitled collection"}.`)});
function freshCollection(){const p=makeProject(),taken=new Set(Object.values(library.projects).map(x=>String(x.pack.name||"")));let name="New collection",i=1;while(taken.has(name)){i++;name=`New collection ${i}`}p.pack.name=name;p.pack.namespace=name.replace(/[^A-Za-z0-9]/g,"")||"NewCollection";return p}
$("#newProjectBtn").addEventListener("click",()=>{library.projects[project.id]=project;adoptCollection(freshCollection(),"New collection created. The previous one is still in the list.")});
$("#deleteCollectionBtn").addEventListener("click",async()=>{const all=collections();if(all.length<=1){status("This is your only collection. Create another before deleting it.","error");return}
  const name=project.pack.name||"Untitled collection";
  const yes=await ask(`\u201c${name}\u201d will be removed from this browser. Any unsaved work in it is lost.`,{title:"Delete collection?",eyebrow:"Remove from library",okLabel:"Delete",danger:true});
  if(!yes)return;const gone=project.id;delete library.projects[gone];const next=collections()[0];library.currentId=next.id;adoptCollection(next,`Deleted ${name}.`)});
$("#addWorkBtn").addEventListener("click",()=>{if(!project.authors.length){status("Add an author before adding a work.","error");return}mutate(()=>{const w=makeWork(project.authors[0]);project.works.push(w);selectedWorkId=w.id;activeTab="write"},{full:true,message:"Work added."})});
$("#addChapterBtn").addEventListener("click",()=>{const w=currentWork();if(!w)return;mutate(()=>{const c=makeChapter(`Chapter ${w.chapters.length+1}`);w.chapters.push(c);selectedChapterId=c.id},{full:true,message:"Chapter added."})});
$("#addCommentBtn").addEventListener("click",()=>mutate(()=>currentWork().comments.push(makeComment()),{full:true,message:"Comment added."}));
$("#duplicateWorkBtn").addEventListener("click",()=>{const source=currentWork();if(!source)return;mutate(()=>{const copy=structuredClone(source);copy.id=`work_${crypto.randomUUID().replaceAll("-","")}`;copy.title=`${copy.title} (Copy)`;copy.chapters.forEach(c=>c.id=`chapter_${crypto.randomUUID().replaceAll("-","")}`);copy.comments.forEach(c=>c.id=`comment_${crypto.randomUUID().replaceAll("-","")}`);project.works.push(copy);selectedWorkId=copy.id},{full:true,message:"Work duplicated with new stable IDs."})});
$("#deleteWorkBtn").addEventListener("click",async()=>{const w=currentWork();if(!w)return;const yes=await ask(`\u201c${w.title||"Untitled work"}\u201d and all of its chapters will be removed.`,{title:"Delete work?",okLabel:"Delete",danger:true});if(!yes)return;mutate(()=>{project.works=project.works.filter(x=>x.id!==w.id);selectedWorkId=project.works[0]?.id||null;selectedChapterId=currentWork()?.chapters[0]?.id||null},{full:true,message:"Work deleted."})});
$("#projectSettingsBtn").addEventListener("click",()=>showTab("project"));$("#workSearch").addEventListener("input",renderWorks);$("#runValidationBtn").addEventListener("click",renderValidation);
function showWelcome(){$("#welcomeScreen").hidden=false;$("#welcomeExamples").hidden=true;$("#welcomeClose").textContent=localStorage.getItem("aoo-creator-welcome-seen")?"Close":"Skip";const s=$("#welcomeSuppress");if(s)s.checked=!!localStorage.getItem("aoo-creator-welcome-off")}
function closeWelcome(){$("#welcomeScreen").hidden=true;localStorage.setItem("aoo-creator-welcome-seen","1");const s=$("#welcomeSuppress");if(s){if(s.checked)localStorage.setItem("aoo-creator-welcome-off","1");else localStorage.removeItem("aoo-creator-welcome-off")}}
$("#tutorialBtn").addEventListener("click",()=>{closeWelcome();startTour()});
$("#welcomeClose").addEventListener("click",closeWelcome);
$("#welcomeBtn").addEventListener("click",showWelcome);
addEventListener("keydown",event=>{if(event.key==="Escape"&&!$("#welcomeScreen").hidden)closeWelcome()});
$("#welcomeScreen").addEventListener("click",event=>{
  const pick=event.target.closest("[data-example]");
  if(pick){closeWelcome();snapshot();library.projects[project.id]=project;adoptCollection(withId(getExample(pick.dataset.example)),"Example opened as a new collection.");return}
  const card=event.target.closest("[data-welcome]")?.dataset.welcome;if(!card)return;
  if(card==="example"){const box=$("#welcomeExamples");box.hidden=!box.hidden;return}
  if(card==="import"){closeWelcome();$("#importFile").click();return}
  closeWelcome();
  if(card==="tour")setTimeout(startTour,140);
});
$("#tutorialRoot").addEventListener("click",event=>{const a=event.target.closest("[data-tour]")?.dataset.tour;if(!a)return;
  if(a==="skip")return endTour();
  if(a==="back"){tourAt=Math.max(0,tourAt-1);return renderTourStep()}
  tourAt+=1;tourAt>=tourSteps.length?endTour():renderTourStep()});
addEventListener("resize",()=>{if(tourOn)renderTourStep()});
addEventListener("keydown",event=>{if(!tourOn)return;if(event.key==="Escape"){event.preventDefault();endTour()}if(event.key==="ArrowRight"){event.preventDefault();tourAt+=1;tourAt>=tourSteps.length?endTour():renderTourStep()}if(event.key==="ArrowLeft"){event.preventDefault();tourAt=Math.max(0,tourAt-1);renderTourStep()}});
$("#themeSelect").addEventListener("change",event=>{const root=document.documentElement;root.dataset.theme=event.target.value;localStorage.setItem(THEME,event.target.value);// force a full style recalculation: switching a theme swaps every custom property at
// once, and some engines keep painting descendants with the previous values
root.style.display="none";void root.offsetHeight;root.style.display=""});
$("#exampleSelect").addEventListener("change",event=>{if(!event.target.value)return;snapshot();library.projects[project.id]=project;adoptCollection(withId(getExample(event.target.value)),"Example added as a new collection.");event.target.value=""});
$("#saveProjectBtn").addEventListener("click",()=>{download(new Blob([JSON.stringify(project,null,2)],{type:"application/json"}),`${project.pack.namespace||"aoo-project"}.aoopack.json`);pendingFileSave=true;save("Project file written. Keep it — you need it to publish updates.")});
$("#importBtn").addEventListener("click",()=>$("#importFile").click());$("#importFile").addEventListener("change",async event=>{const file=event.target.files[0];if(!file)return;try{const next=withId(normalizeProject(JSON.parse(await file.text())));const existing=library.projects[next.id];if(existing){const yes=await ask(`This file is a copy of \u201c${existing.pack.name||"Untitled collection"}\u201d, which is already in this browser. Importing replaces the browser copy with what is in the file. Ctrl+Z undoes it.`,{title:"Replace this collection?",eyebrow:"Same collection",okLabel:"Replace",danger:true});if(!yes){status("Import cancelled.");event.target.value="";return}}snapshot();library.projects[project.id]=project;pendingFileSave=true;adoptCollection(next,`Imported ${file.name}.`);status(existing?`Replaced ${esc(existing.pack.name)} from ${file.name}.`:`Imported ${file.name} as a new collection.`,"success")}catch(error){status(error.message,"error")}event.target.value=""});
function openPublish(){
  const p=project.pack,works=project.works,chapters=works.reduce((t,w)=>t+w.chapters.length,0);
  const words=works.reduce((t,w)=>t+workWordCount(w),0);
  const ns=p.namespace||"UnnamedPack";
  $("#publishTitle").textContent=p.name||"Untitled collection";
  $("#publishFacts").innerHTML=[
    ["Namespace",ns+" · permanent"],["Version",p.version||"1.0.0"],
    ["Authors",project.authors.length],["Works",works.length],
    ["Chapters",chapters],["Words",words.toLocaleString()],
    ["Requires","Archive of Our Overwrites "+AOO_MIN_VERSION+" or newer"]
  ].map(([k,v])=>`<div><dt>${esc(k)}</dt><dd>${esc(String(v))}</dd></div>`).join("");
  $("#publishFileList").innerHTML=Object.keys(generatePackFiles(project))
    .map(f=>`<li>${esc(f)}</li>`).join("");
  const saved=library.saved?.[project.id];
  $("#publishNote").innerHTML=saved===project.updatedAt
    ? "Your <code>.aoopack.json</code> is up to date. Keep it — re-importing it is how you publish a compatible update."
    : "<strong>You have not saved this collection to a file since your last edit.</strong> Do that before you publish: re-importing the <code>.aoopack.json</code> is the only way to ship an update your readers keep their library through.";
  $("#publishNote").className="publish-note "+(saved===project.updatedAt?"ok":"warn");
  renderNexusPage();
  $("#publishScreen").hidden=false;
}
function renderNexusPage(){
    // Regenerated every time the publish screen opens, so it always reflects
    // the collection as it stands rather than a stale copy from an earlier edit.
    let page;
    try{ page=generateNexusPage(project); }
    catch(err){
      $("#nexusText").value="The page could not be generated: "+err.message;
      $("#nexusNotes").hidden=true;
      return;
    }
    $("#nexusText").value=page.text;
    const notes=$("#nexusNotes");
    notes.innerHTML=page.notes.map(t=>`<li>${esc(t)}</li>`).join("");
    notes.hidden=page.notes.length===0;
    $("#nexusCopied").hidden=true;
  }
$("#nexusCopy").addEventListener("click",async()=>{
    const field=$("#nexusText");
    try{
      // navigator.clipboard needs a secure context; file:// is not one, so the
      // selection fallback is the path the standalone actually takes
      await navigator.clipboard.writeText(field.value);
    }catch(err){
      field.focus(); field.select();
      try{ document.execCommand("copy"); }
      catch(e){ status("Press Ctrl+C to copy the selected text.","error"); return; }
    }
    const flag=$("#nexusCopied");
    flag.hidden=false;
    setTimeout(()=>{flag.hidden=true},2200);
  });
function closePublish(){$("#publishScreen").hidden=true}
$("#publishCancel").addEventListener("click",closePublish);
addEventListener("keydown",event=>{if(event.key==="Escape"&&!$("#publishScreen").hidden)closePublish()});
$("#publishGo").addEventListener("click",()=>{
  try{const files=generatePackFiles(project),zip=createZip(files),
    name=`${project.pack.namespace}-v${project.pack.version}.zip`;
    download(zip,name);closePublish();
    status(`Built ${name}. Upload it to Nexus and list AOO as a requirement.`,"success");
  }catch(error){closePublish();status(error.message,"error")}
});
$("#buildBtn").addEventListener("click",()=>{renderValidation();
  const errors=validateProject(project).filter(x=>x.kind==="error");
  if(errors.length){activeTab="validate";showTab("validate");
    status(`Build blocked: ${errors.length} validation error(s).`,"error");return}
  openPublish()});

document.addEventListener("keydown",event=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="z"){event.preventDefault();if(!undoStack.length)return;redoStack.push(JSON.stringify(project));project=normalizeProject(JSON.parse(undoStack.pop()));selectedWorkId=project.works.find(w=>w.id===selectedWorkId)?.id||project.works[0]?.id||null;save("Undo autosaved.");render()}if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="y"){event.preventDefault();if(!redoStack.length)return;undoStack.push(JSON.stringify(project));project=normalizeProject(JSON.parse(redoStack.pop()));selectedWorkId=project.works[0]?.id||null;save("Redo autosaved.");render()}});

if(localStorage.getItem("aoo-creator-live-preview")){$("#writePreview").hidden=false;$("#writePane").classList.add("with-preview");$("#livePreviewBtn").textContent="Hide preview";$("#livePreviewBtn").setAttribute("aria-pressed","true")}
const theme=localStorage.getItem(THEME)||"aoo";document.documentElement.dataset.theme=theme;$("#themeSelect").value=theme;render();function afterBoot(){if(!localStorage.getItem("aoo-creator-welcome-off"))showWelcome()}
function runBoot(){
  const el=$("#boot");
  const skip=matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(!el||skip){afterBoot();return}
  el.hidden=false;
  let done=false;
  const finish=()=>{if(done)return;done=true;
    removeEventListener("keydown",finish,true);removeEventListener("pointerdown",finish,true);
    el.classList.add("out");setTimeout(()=>{el.hidden=true;el.classList.remove("out");afterBoot()},380)};
  addEventListener("keydown",finish,true);addEventListener("pointerdown",finish,true);
  // no timeout: the boot holds until the reader acknowledges it
  setTimeout(()=>el.classList.add("ready"),1850);  // marks the wait, styling is CSS-driven
}
runBoot();status(`AOO Creator v${CREATOR_VERSION} · autosaved in this browser only. Use Save project to keep a file copy.`);


/* ---------------------------------------------------------------------------
   For whoever opened DevTools. The tool claims nothing leaves your machine;
   the console is where a sceptic goes to check, so point them at the proof.
   --------------------------------------------------------------------------- */
(function () {
  try {
    if (!window.console || !console.log) return;
    var NL = String.fromCharCode(10);
    var gold = "color:#f0c94a;font-weight:700;font-size:12px";
    var cyan = "color:#31d5d6";
    var dim  = "color:#88a09e";
    var red  = "color:#ef5867;font-style:italic";

    console.log(
      "%c" +
      "  ______________________________________________" + NL +
      "     _   ___  ___" + NL +
      "    /_\\ / _ \\/ _ \\   ARCHIVE OF OUR OVERWRITES" + NL +
      "   / _ \\ (_) | (_) |  creator" + NL +
      "  /_/ \\_\\___/ \\___/" + NL +
      "  ______________________________________________",
      gold);

    console.log("%cNETDIR://AOO.PUB%c  link established \u00b7 no relay in the path", cyan, dim);
    console.log(
      "%cEverything here runs in this tab. No account, no telemetry, no beacon." + NL +
      "Do not take our word for it - open the Network tab and reload. You should" + NL +
      "see this page and its own assets, and nothing else. Ever.",
      dim);
    console.log("%c\u201cThe archive remembers what the city would rather overwrite.\u201d", red);
    console.log("%cWriting a collection? The guide is PackAuthorGuide.md in the repo.", dim);
  } catch (e) { /* a console that dislikes styling is not worth an error */ }
})();
