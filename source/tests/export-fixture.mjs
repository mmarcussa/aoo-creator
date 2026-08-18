import fs from "node:fs";
import path from "node:path";
import {getExample,generatePackFiles} from "../core.js";

const target=path.resolve(process.argv[2]);
const project=getExample("collection");
const files=generatePackFiles(project);
for(const [relative,content] of Object.entries(files)){
  const destination=path.join(target,relative);
  fs.mkdirSync(path.dirname(destination),{recursive:true});
  fs.writeFileSync(destination,content,"utf8");
}
console.log(`Exported ${Object.keys(files).length} fixture files to ${target}`);
