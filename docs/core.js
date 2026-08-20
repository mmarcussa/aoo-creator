export const CREATOR_VERSION = "0.2.0";
export const SCHEMA_VERSION = 1;
export const FRAMEWORK_VERSION = "1.0.0";
export const AOO_MIN_VERSION = "0.3.0-dev.17";
export const LIMITS = Object.freeze({ author:24, title:120, chapterTitle:120, tag:80, summary:140, tags:100, minDays:3 });

const nowDate = () => new Date().toISOString().slice(0,10);
export const newId = (prefix="id") => `${prefix}_${crypto.randomUUID().replaceAll("-","")}`;
const shortId = id => String(id || "missing").replace(/[^a-zA-Z0-9]/g,"").slice(-14).toLowerCase();
const cleanNamespace = value => String(value || "AOOCollection").replace(/[^A-Za-z0-9_]/g,"_").replace(/^[^A-Za-z]+/,"") || "AOOCollection";
const cnameSlug = value => String(value || "tag").toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g,"_").replace(/^_+|_+$/g,"").slice(0,44) || "tag";
const redsString = value => `"${String(value ?? "").replaceAll("\\","\\\\").replaceAll("\"","\\\"").replaceAll("\r","").replaceAll("\n","\\n")}"`;
const n = value => `n"${String(value).replace(/[^A-Za-z0-9_.]/g,"_")}"`;
const arr = values => `[${values.join(", ")}]`;
const int = value => Math.max(0, Number.parseInt(value,10) || 0);

export function makeAuthor(pseud="newauthor", active=false){
  return {id:newId("author"),pseud,status:active?"Active":"Inactive"};
}
export function makeChapter(title="Chapter 1"){
  return {id:newId("chapter"),title,body:"",notesBefore:"",notesAfter:"",price:300};
}
export function makeComment(){
  return {id:newId("comment"),user:"reader2077",date:nowDate(),body:"",chapterIndex:0};
}
export function makeWork(author){
  const pseud=author?.pseud || "newauthor";
  return {id:newId("work"),authorId:author?.id||"",title:"Untitled work",pseud,summary:"",rating:"Teen",warning:"None",category:"Gen",fandoms:[],relationships:[],characters:[],tags:[],wordCount:0,complete:true,active:false,releaseIntervalDays:3,stats:{props:0,reads:0,stashes:0,comments:0},notesBefore:"",chapters:[makeChapter()],comments:[]};
}
export function makeProject(){
  const author=makeAuthor("packetloss",false);
  return {schemaVersion:SCHEMA_VERSION,creatorVersion:CREATOR_VERSION,frameworkVersion:FRAMEWORK_VERSION,id:newId("project"),createdAt:new Date().toISOString(),updatedAt:new Date().toISOString(),pack:{name:"My AOO Collection",namespace:"MyAOOCollection",version:"1.0.0",creator:"",description:"A fanwork collection for Archive of Our Overwrites.",nexus:"",credits:"",license:"All rights reserved"},authors:[author],works:[makeWork(author)]};
}

function baseExample(name,namespace){
  const p=makeProject(); p.pack.name=name; p.pack.namespace=namespace; p.pack.creator="Example Modder"; return p;
}
export function getExample(kind){
  if(kind==="oneshot"){
    const p=baseExample("Afterlife One-Shots","AfterlifeOneShots"),a=p.authors[0],w=p.works[0];
    a.pseud="deadfrequency"; w.pseud=a.pseud; w.title="Last Call at the Afterlife"; w.summary="A merc, a rumor, and one drink that nobody remembers ordering."; w.fandoms=["Legends of Night City"]; w.tags=["Unreliable Narrator"]; w.wordCount=420; w.stats={props:12,reads:86,stashes:4,comments:1}; w.chapters[0].title="Last Call"; w.chapters[0].body="The Afterlife was closing, which everybody knows it never does. A merc sat alone with a drink nobody remembered ordering. Then the dead channel answered."; w.comments=[{...makeComment(),user:"deadfrequency",date:"2077-05-19",body:"the ending got me, choom"}]; return p;
  }
  if(kind==="complete"){
    const p=baseExample("Concrete Signals","ConcreteSignals"),a=p.authors[0],w=p.works[0];
    a.pseud="ghostpocket"; w.pseud=a.pseud; w.title="A Signal Through Concrete"; w.summary="Two fragments of the same transmission: one brokered, one left where the signal died."; w.rating="Mature"; w.category="M/M"; w.fandoms=["SAMURAI"]; w.relationships=["Kerry Eurodyne/Johnny Silverhand"]; w.characters=["Kerry Eurodyne","Johnny Silverhand"]; w.tags=["Angst","Slow Burn"]; w.wordCount=2110; w.stats.comments=1; w.chapters=[makeChapter("Static in the Walls"),makeChapter("Antenna")]; w.chapters[0].body="Concrete held the signal until midnight. Then the walls started singing back."; w.chapters[1].body="Kerry found the transmitter beneath a floor nobody remembered pouring."; w.comments=[{...makeComment(),user:"chrome_heart",body:"chapter two hurt in exactly the right way",chapterIndex:1}]; return p;
  }
  if(kind==="active"){
    const p=baseExample("Live Wire Serial","LiveWireSerial"),a=p.authors[0],w=p.works[0];
    a.pseud="pocketloss"; a.status="Active"; w.pseud=a.pseud; w.title="Dead Channel, Live Wire"; w.summary="A dead frequency, one impossible reply, and a netrunner who should really know better."; w.complete=false; w.active=true; w.releaseIntervalDays=3; w.fandoms=["Legends of Night City"]; w.tags=["Work In Progress","Mystery"]; w.chapters=[makeChapter("Carrier Wave"),makeChapter("Unknown Sender"),makeChapter("Handshake")]; w.chapters.forEach((c,i)=>{c.body=`Timed chapter ${i+1}. Replace this example body before release.`;c.price=250+i*50}); return p;
  }
  const p=baseExample("Night City Archive Sampler","NightCitySampler"); p.authors=[]; p.works=[];
  [["chromeheart","Chrome Hearts & Scrambled Eggs","SAMURAI"],["bluemoonstan","The Story They Made Up About Us","Us Cracks"],["ghostpocket","Build a Worse One","Legends of Night City"]].forEach(([pseud,title,fandom],i)=>{const a=makeAuthor(pseud,i===2);const w=makeWork(a);w.title=title;w.pseud=pseud;w.summary=["Breakfast, feelings, and a stove with terrible timing.","The label invented a romance for publicity; one of them stopped pretending.","Two runners, one NET that did not exist yesterday, and the night before it all went wrong."][i];w.fandoms=[fandom];w.chapters[0].body="Example chapter body. Replace this text with the collection's fanwork.";w.active=i===2;w.complete=i!==2;w.releaseIntervalDays=3;p.authors.push(a);p.works.push(w)}); return p;
}

export function normalizeProject(raw){
  if(!raw || typeof raw!=="object") throw new Error("The selected file is not an AOO project.");
  if(Number(raw.schemaVersion)!==SCHEMA_VERSION) throw new Error(`Unsupported schema ${raw.schemaVersion}; this creator expects schema ${SCHEMA_VERSION}.`);
  const p=structuredClone(raw); p.creatorVersion=CREATOR_VERSION; p.frameworkVersion=FRAMEWORK_VERSION; p.updatedAt=new Date().toISOString();
  p.authors=Array.isArray(p.authors)?p.authors:[]; p.works=Array.isArray(p.works)?p.works:[];
  p.authors.forEach(a=>{a.id ||= newId("author");a.status=a.status==="Active"?"Active":"Inactive";a.pseud=String(a.pseud||"")});
  p.works.forEach(w=>{w.id ||= newId("work");w.fandoms ||= [];w.relationships ||= [];w.characters ||= [];w.tags ||= [];w.chapters ||= [];w.comments ||= [];w.stats ||= {props:0,reads:0,stashes:0,comments:0};w.releaseIntervalDays=int(w.releaseIntervalDays)||3;w.chapters.forEach(c=>{c.id ||=newId("chapter");c.price=int(c.price)||300});w.comments.forEach(c=>c.id||=newId("comment"))});
  return p;
}

export function validateProject(project){
  const issues=[]; const error=(path,message)=>issues.push({kind:"error",path,message}); const warning=(path,message)=>issues.push({kind:"warning",path,message});
  if(!project || project.schemaVersion!==SCHEMA_VERSION) error("project","Creator schema must be 1.");
  const pack=project?.pack||{};
  if(!String(pack.name||"").trim()) error("collection.name","Collection name is required.");
  if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(pack.namespace||"")) error("collection.namespace","Namespace must begin with a letter and use only letters, numbers, or underscore.");
  if(!/^\d+\.\d+\.\d+(?:[-.][0-9A-Za-z.-]+)?$/.test(pack.version||"")) error("collection.version","Use a semantic version such as 1.0.0.");
  if(!project.authors?.length) error("authors","Add at least one author.");
  if(!project.works?.length) error("works","Add at least one work.");
  const authorIds=new Set(); project.authors?.forEach((a,i)=>{const path=`author ${i+1}`;if(!a.id||authorIds.has(a.id))error(path,"Stable author ID is missing or duplicated.");authorIds.add(a.id);if(!a.pseud?.trim())error(path,"Pseud is required.");if(a.pseud?.length>LIMITS.author)error(path,`Pseud exceeds ${LIMITS.author} characters.`)});
  const workIds=new Set(); project.works?.forEach((w,i)=>{const path=`work ${i+1}: ${w.title||"untitled"}`,author=project.authors.find(a=>a.id===w.authorId);if(!w.id||workIds.has(w.id))error(path,"Stable work ID is missing or duplicated.");workIds.add(w.id);if(!author)error(path,"Select a registered author.");if(!w.title?.trim())error(path,"Title is required.");if(w.title?.length>LIMITS.title)error(path,`Title exceeds ${LIMITS.title} characters.`);if(!w.pseud?.trim()||w.pseud.length>LIMITS.author)error(path,`Work pseud must be 1–${LIMITS.author} characters.`);if(author&&w.pseud!==author.pseud)error(path,"Work pseud must match its registered author pseud.");if((w.summary||"").length>LIMITS.summary)error(path,`Summary exceeds ${LIMITS.summary} characters.`);const tags=[...(w.fandoms||[]),...(w.relationships||[]),...(w.characters||[]),...(w.tags||[])];if(tags.length>LIMITS.tags)error(path,`Work has ${tags.length} open tags; maximum is ${LIMITS.tags}.`);tags.forEach(t=>{if(!String(t).trim())warning(path,"An empty tag will be ignored.");if(String(t).length>LIMITS.tag)error(path,`Tag exceeds ${LIMITS.tag} characters: ${t}`)});if(!w.complete&&!w.active)error(path,"An incomplete work must use the timed release model.");if(w.active&&author?.status!=="Active")error(path,"Timed releases require the selected author to be Active.");if(w.active&&int(w.releaseIntervalDays)<LIMITS.minDays)error(path,`Active works require at least ${LIMITS.minDays} days between chapters.`);if(w.active&&w.complete)warning(path,"A complete work ignores timed release settings and is immediately available.");if(w.comments?.length&&(!w.complete||author?.status!=="Inactive"))error(path,"Archived comments are limited to complete works by inactive authors.");if(int(w.stats?.comments)<(w.comments?.length||0))error(path,"Comments stat cannot be lower than the number of archived comments.");if(!w.chapters?.length)error(path,"Add at least one chapter.");w.chapters?.forEach((c,ci)=>{if(!c.title?.trim())error(`${path}, chapter ${ci+1}`,"Chapter title is required.");if(c.title?.length>LIMITS.chapterTitle)error(`${path}, chapter ${ci+1}`,`Chapter title exceeds ${LIMITS.chapterTitle} characters.`);if(!c.body?.trim())error(`${path}, chapter ${ci+1}`,"Chapter body is required.");if(int(c.price)<=0)warning(`${path}, chapter ${ci+1}`,"Price is zero; creator will export it as 300.")});Object.entries(w.stats||{}).forEach(([key,value])=>{if(Number(value)<0)error(path,`${key} cannot be negative.`)});w.comments?.forEach((c,ci)=>{if(!c.user?.trim()||!c.body?.trim())error(`${path}, comment ${ci+1}`,"Comment user and body are required.");if(int(c.chapterIndex)>=w.chapters.length)error(`${path}, comment ${ci+1}`,"Comment points to a chapter that does not exist.")})});
  return issues;
}

const warningIds={None:"aoo.warning.none",ChooseNotToWarn:"aoo.warning.choose_not",GraphicViolence:"aoo.warning.graphic_violence",MajorDeath:"aoo.warning.major_death",Underage:"aoo.warning.underage",NonCon:"aoo.warning.noncon"};
const categoryIds={Gen:"aoo.category.gen","F/F":"aoo.category.ff","F/M":"aoo.category.fm","M/M":"aoo.category.mm",Multi:"aoo.category.multi",Other:"aoo.category.other"};
function tagTypeEntries(work){return [["fandom",work.fandoms||[]],["relationship",work.relationships||[]],["character",work.characters||[]],["freeform",work.tags||[]]]}
function tagId(ns,type,label,index){return `aoo.${cnameSlug(ns)}.${type}.${cnameSlug(label)}_${index}`}
function workCName(ns,work){return `aoo.${cnameSlug(ns)}.work.${shortId(work.id)}`}
function authorCName(ns,author){return `aoo.author.${cnameSlug(ns)}.${shortId(author.id)}`}
function locKey(ns,work,kind,index=""){return `aoo_${cnameSlug(ns)}_${shortId(work.id)}_${kind}${index===""?"":`_${index+1}`}`}

export function generatePackFiles(project){
  const issues=validateProject(project); if(issues.some(x=>x.kind==="error")) throw new Error(`Build blocked by ${issues.filter(x=>x.kind==="error").length} validation error(s).`);
  const ns=cleanNamespace(project.pack.namespace), moduleBase=`${ns}.Content`, lines=[`module ${moduleBase}`,"","import ArchiveOfOurOverwrites.Core.*","import ArchiveOfOurOverwrites.Systems.*","",`@addMethod(gameuiInGameMenuGameController)`,`protected cb func Register${ns}(event: ref<AOOFicRegistration>) -> Bool {`];
  project.authors.forEach(a=>lines.push(`  event.AddAuthor(${n(authorCName(ns,a))}, ${redsString(a.pseud)}, AOOAuthorStatus.${a.status});`));
  const registered=new Map(); project.works.forEach(w=>tagTypeEntries(w).forEach(([type,values])=>values.forEach((label,index)=>{const key=`${type}\0${label}`;if(!registered.has(key)){const id=tagId(ns,type,label,registered.size);registered.set(key,id);lines.push(`  event.AddTag(${n(id)}, ${redsString(label)}, ${n(type)});`)}})));
  project.works.forEach((w,wi)=>{
    const varName=`fic${wi+1}`; const author=project.authors.find(a=>a.id===w.authorId);lines.push("",`  let ${varName}: ref<AOOFic> = new AOOFic();`,`  ${varName}.id = ${n(workCName(ns,w))};`,`  ${varName}.authorID = ${n(authorCName(ns,author))};`,`  ${varName}.title = ${redsString(w.title)};`,`  ${varName}.pseud = ${redsString(w.pseud)};`,`  ${varName}.summary = ${redsString(w.summary)};`,`  ${varName}.rating = AOORating.${w.rating};`,`  ${varName}.warnings = ${arr([n(warningIds[w.warning]||warningIds.None)])};`,`  ${varName}.categories = ${arr([n(categoryIds[w.category]||categoryIds.Gen)])};`);
    tagTypeEntries(w).forEach(([type,values])=>{const prop=type==="character"?"characters":type==="relationship"?"relationships":type==="fandom"?"fandoms":"freeform";lines.push(`  ${varName}.${prop} = ${arr(values.map(label=>n(registered.get(`${type}\0${label}`))))};`)});
    lines.push(`  ${varName}.wordCount = ${int(w.wordCount)};`,`  ${varName}.complete = ${w.complete?"true":"false"};`,`  ${varName}.releaseIntervalDays = ${!w.complete&&w.active?Math.max(LIMITS.minDays,int(w.releaseIntervalDays)):0};`,`  ${varName}.props = ${int(w.stats?.props)};`,`  ${varName}.reads = ${int(w.stats?.reads)};`,`  ${varName}.stash = ${int(w.stats?.stashes)};`,`  ${varName}.commentsCount = ${int(w.stats?.comments)};`,`  ${varName}.chapterPrices = ${arr(w.chapters.map(c=>Math.max(1,int(c.price)||300)))};`);
    if(w.notesBefore?.trim())lines.push(`  ${varName}.notesBeforeKey = ${n(locKey(ns,w,"note_before"))};`);
    w.chapters.forEach((c,ci)=>{const cv=`chapter${wi+1}_${ci+1}`;lines.push("",`  let ${cv}: ref<AOOChapter> = new AOOChapter();`,`  ${cv}.title = ${redsString(c.title)};`,`  ${cv}.bodyKey = ${n(locKey(ns,w,"chapter",ci))};`);if(c.notesBefore?.trim())lines.push(`  ${cv}.notesBeforeKey = ${n(locKey(ns,w,"chapter_note_before",ci))};`);if(c.notesAfter?.trim())lines.push(`  ${cv}.notesAfterKey = ${n(locKey(ns,w,"chapter_note_after",ci))};`)});
    lines.push(`  ${varName}.chapters = ${arr(w.chapters.map((_,ci)=>`chapter${wi+1}_${ci+1}`))};`);
    w.comments.forEach((c,ci)=>{const cv=`comment${wi+1}_${ci+1}`;lines.push("",`  let ${cv}: ref<AOOComment> = new AOOComment();`,`  ${cv}.user = ${redsString(c.user)};`,`  ${cv}.date = ${redsString(c.date)};`,`  ${cv}.body = ${redsString(c.body)};`,`  ${cv}.chapterIndex = ${Math.max(0,int(c.chapterIndex))};`)}); if(w.comments.length)lines.push(`  ${varName}.comments = ${arr(w.comments.map((_,ci)=>`comment${wi+1}_${ci+1}`))};`);
    lines.push(`  event.AddFic(${varName});`);
  }); lines.push("}","");
  const loc=[`module ${ns}.Localization`,"","import Codeware.Localization.*","",`public class ${ns}LocProvider extends ModLocalizationProvider {`,`  public func GetPackage(language: CName) -> ref<ModLocalizationPackage> {`,`    switch language {`,`      case n"en-us": return new ${ns}English();`,`      default: return null;`,`    }`,`  }`,``,`  public func GetFallback() -> CName { return n"en-us"; }`,`}`,"",`public class ${ns}English extends ModLocalizationPackage {`,`  protected func DefineTexts() -> Void {`];
  const funcs=[]; project.works.forEach((w,wi)=>{if(w.notesBefore?.trim())loc.push(`    this.Text(${redsString(locKey(ns,w,"note_before"))}, ${redsString(w.notesBefore)});`);w.chapters.forEach((c,ci)=>{const fn=`${ns}Work${wi+1}Chapter${ci+1}`;loc.push(`    this.Text(${redsString(locKey(ns,w,"chapter",ci))}, ${fn}());`);funcs.push("",`public func ${fn}() -> String {`,`  return ${redsString(c.body)};`,`}`);if(c.notesBefore?.trim())loc.push(`    this.Text(${redsString(locKey(ns,w,"chapter_note_before",ci))}, ${redsString(c.notesBefore)});`);if(c.notesAfter?.trim())loc.push(`    this.Text(${redsString(locKey(ns,w,"chapter_note_after",ci))}, ${redsString(c.notesAfter)});`)})});loc.push("  }","}",...funcs,"");
  const manifest={format:"aoopack",schemaVersion:SCHEMA_VERSION,creatorVersion:CREATOR_VERSION,frameworkVersion:FRAMEWORK_VERSION,aooMinimumVersion:AOO_MIN_VERSION,projectId:project.id,namespace:ns,name:project.pack.name,version:project.pack.version,creator:project.pack.creator,workCount:project.works.length,authorCount:project.authors.length,builtAt:new Date().toISOString()};
  const readme=`${project.pack.name}\n${"=".repeat(project.pack.name.length)}\n\nVersion: ${project.pack.version}\nCreator: ${project.pack.creator||"Not specified"}\nRequires: Archive of Our Overwrites ${AOO_MIN_VERSION} or newer\n\n${project.pack.description||""}\n\nInstall the ZIP with a mod manager. Do not remove AOO while this collection is installed.\n${project.pack.nexus?`\nNexus: ${project.pack.nexus}\n`:""}${project.pack.credits?`\nCredits: ${project.pack.credits}\n`:""}\nLicense: ${project.pack.license||"Not specified"}\n`;
  return {[`r6/scripts/${ns}/${ns}.Content.reds`]:lines.join("\n"),[`r6/scripts/${ns}/${ns}.Localization.reds`]:loc.join("\n"),[`r6/scripts/${ns}/pack.aoopack.json`]:JSON.stringify({...manifest,project},null,2),[`r6/scripts/${ns}/manifest.json`]:JSON.stringify(manifest,null,2),[`r6/scripts/${ns}/README.txt`]:readme,[`r6/scripts/${ns}/VERSION`]:String(project.pack.version)};
}

const crcTable=(()=>{const t=new Uint32Array(256);for(let i=0;i<256;i++){let c=i;for(let k=0;k<8;k++)c=(c&1)?0xedb88320^(c>>>1):c>>>1;t[i]=c>>>0}return t})();
const crc32=bytes=>{let c=0xffffffff;for(const b of bytes)c=crcTable[(c^b)&255]^(c>>>8);return(c^0xffffffff)>>>0};
const u16=n=>new Uint8Array([n&255,(n>>>8)&255]); const u32=n=>new Uint8Array([n&255,(n>>>8)&255,(n>>>16)&255,(n>>>24)&255]);
const join=arrays=>{const out=new Uint8Array(arrays.reduce((n,a)=>n+a.length,0));let p=0;for(const a of arrays){out.set(a,p);p+=a.length}return out};
export function createZip(files){
  const encoder=new TextEncoder(),locals=[],central=[];let offset=0;const date=new Date(),dosTime=(date.getHours()<<11)|(date.getMinutes()<<5)|(date.getSeconds()>>1),dosDate=((date.getFullYear()-1980)<<9)|((date.getMonth()+1)<<5)|date.getDate();
  for(const [path,value] of Object.entries(files)){const name=encoder.encode(path.replaceAll("\\","/")),data=encoder.encode(String(value)),crc=crc32(data),local=join([u32(0x04034b50),u16(20),u16(0x0800),u16(0),u16(dosTime),u16(dosDate),u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0),name,data]);locals.push(local);central.push(join([u32(0x02014b50),u16(20),u16(20),u16(0x0800),u16(0),u16(dosTime),u16(dosDate),u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(offset),name]));offset+=local.length}
  const directory=join(central),end=join([u32(0x06054b50),u16(0),u16(0),u16(central.length),u16(central.length),u32(directory.length),u32(offset),u16(0)]);return new Blob([...locals,directory,end],{type:"application/zip"});
}
