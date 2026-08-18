import assert from "node:assert/strict";
import {getExample,validateProject,generatePackFiles,createZip,LIMITS} from "../core.js";

for (const kind of ["oneshot","complete","active","collection"]) {
  const project=getExample(kind);
  const errors=validateProject(project).filter(issue=>issue.kind==="error");
  assert.deepEqual(errors,[],`${kind} example should satisfy schema v1`);
  const files=generatePackFiles(project);
  assert.ok(Object.keys(files).some(path=>path.endsWith(".Content.reds")));
  assert.ok(Object.keys(files).some(path=>path.endsWith(".Localization.reds")));
  assert.match(files["manifest.json"],/"schemaVersion": 1/);
  const bytes=new Uint8Array(await createZip(files).arrayBuffer());
  assert.deepEqual([...bytes.slice(0,4)],[0x50,0x4b,0x03,0x04],"ZIP must have a local-file signature");
}

const invalid=getExample("oneshot");
invalid.works[0].title="X".repeat(LIMITS.title+1);
invalid.works[0].tags=Array.from({length:LIMITS.tags+1},(_,i)=>`Tag ${i}`);
invalid.works[0].active=true;
invalid.works[0].releaseIntervalDays=1;
const messages=validateProject(invalid).map(x=>x.message).join("\n");
assert.match(messages,/Title exceeds/);
assert.match(messages,/maximum is 100/);
assert.match(messages,/at least 3 days/);

const active=getExample("active");
const activeFiles=generatePackFiles(active);
const content=Object.entries(activeFiles).find(([path])=>path.endsWith(".Content.reds"))[1];
assert.match(content,/AOOAuthorStatus.Active/);
assert.match(content,/releaseIntervalDays = 3/);
assert.match(content,/chapterPrices = \[250, 300, 350\]/);

console.log("AOO Creator tests passed.");
