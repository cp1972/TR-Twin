// A run does not depend on what was computed before it in the same page: the same run file twice gives the same
// series, and a seed computed alone gives what it gives inside a series of seeds (data mode with instances,
// where the smoothed friction of migration is not zero).   node tests/test_repeat.js
const fs=require('fs'),path=require('path'),{JSDOM}=require('jsdom');
const REPO=path.resolve(__dirname,'..');
const ctx=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return()=>({addColorStop(){}});if(p==='measureText')return()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const w=new JSDOM(fs.readFileSync(path.join(REPO,'tr-twin.html'),'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){w.HTMLCanvasElement.prototype.getContext=()=>ctx;w.requestAnimationFrame=()=>0;w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});}}).window;
w.__f={'c.csv':fs.readFileSync(path.join(REPO,'data-mode/data/actors/cohorte_contrat.csv'),'utf8'),'i.csv':fs.readFileSync(path.join(REPO,'data-mode/data/instances/instances_full_empirical.csv'),'utf8')};
const run=c=>{const s=w.document.createElement('script');s.textContent='window.__o=(function(){'+c+'})();';w.document.body.appendChild(s);s.remove();return w.__o;};
const out=run(`const sp=t=>parseRunFile(t).spec;const ser=r=>JSON.stringify(r.runs.map(q=>q.rows.map(x=>[x.S,x.recip])));
  const a=r68Run(sp('mode,data\\ncontracts,c.csv\\ninstances,i.csv\\nseeds,1-4'),window.__f);
  const b=r68Run(sp('mode,data\\ncontracts,c.csv\\ninstances,i.csv\\nseeds,1-4'),window.__f);
  const c=r68Run(sp('mode,data\\ncontracts,c.csv\\ninstances,i.csv\\nseeds,3'),window.__f);
  return {twice:ser(a)===ser(b),alone:JSON.stringify(c.runs[0].rows.map(x=>[x.S,x.recip]))===JSON.stringify(a.runs[2].rows.map(x=>[x.S,x.recip]))};`);
console.log((out.twice?'✓':'✗')+' the same run file twice gives the same series');
console.log((out.alone?'✓':'✗')+' seed 3 alone = seed 3 inside seeds 1–4');
process.exit(out.twice&&out.alone?0:1);
