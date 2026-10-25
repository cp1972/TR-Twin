// Thresholds and stimulus probe: they do not change the runs of the run file; a sweep at the theory's own value is the
// theory's run; every threshold is found to one slider step; a probe run is the same as the stimulus written in a run file.
//   node tests/test_thresholds.js
const fs=require('fs'),path=require('path'),{JSDOM}=require('jsdom');
const REPO=path.resolve(__dirname,'..');
const ctx=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return()=>({addColorStop(){}});if(p==='measureText')return()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const w=new JSDOM(fs.readFileSync(path.join(REPO,'tr-twin.html'),'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){w.HTMLCanvasElement.prototype.getContext=()=>ctx;w.requestAnimationFrame=()=>0;w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});}}).window;
const run=code=>{const s=w.document.createElement('script');s.textContent='window.__o=(function(){'+code+'})();';w.document.body.appendChild(s);s.remove();return w.__o;};
let bad=0;const check=(ok,what)=>{if(!ok){bad++;console.log('✗',what);}else console.log('✓',what);};
w.__p=fs.readFileSync(path.join(REPO,'simulation-mode/profiles/profil_Meier.csv'),'utf8');
const o=run(`const f={'p.csv':window.__p};
  const a=r68Run(parseRunFile('mode,simulation\\nprofile,p.csv\\nseeds,1-2').spec,f);
  const b=r68Run(parseRunFile('mode,simulation\\nprofile,p.csv\\nseeds,1-2\\nthresholds,no\\nprobe,no').spec,f);
  const end=r=>JSON.stringify(r.rows[r.rows.length-1].S);
  const same=JSON.stringify(a.runs.map(r=>r.rows.map(q=>q.S)))===JSON.stringify(b.runs.map(r=>r.rows.map(q=>q.S)));
  // a sweep at the own value with seed 1 = the main run with seed 1 (end state)
  const own=a.sweeps.filter(r=>r.theory==='p'&&r.seed===1&&r.over.id==='alpha'&&r.over.v===r.own)[0];
  const main=a.runs.find(r=>r.theory==='p'&&r.seed===1);
  const T=r68SweepTable(a.sweeps);let steps=true,flips=0;
  for(const n in T)for(const id in T[n]){const st=+r68SliderEl(id).step;for(const f of [T[n][id].up,T[n][id].down])if(f){flips++;if(Math.abs(f.v-f.last)>st*1.01)steps=false;}}
  // the probe run for C weakened, seed 1 = the stimulus written in a run file
  const pr=a.probes.find(r=>r.theory==='p'&&r.seed===1&&r.probeX===2);
  const c=r68Run(parseRunFile('mode,simulation\\nprofile,p.csv\\nseeds,1\\nstimulus,C,weaken,300,2.6,1819\\nthresholds,no\\nprobe,no').spec,f);
  const cr=c.runs.find(r=>r.theory==='p'&&!r.control);
  const sm=r68Summary(a);
  return {same,ownEq:end(own)===end(main),flips,steps,probeEq:JSON.stringify(pr.stimulus.end)===JSON.stringify(cr.stimulus.end),
    tables:sm.tables.map(t=>t.id),findings:sm.tables.find(t=>t.id==='findings').rows.length};`);
check(o.same,'thresholds and probe leave the runs of the run file unchanged');
check(o.ownEq,'a sweep at the theory’s own value is the theory’s run');
check(o.flips>0&&o.steps,'every threshold found to one slider step ('+o.flips+' thresholds)');
check(o.probeEq,'probe run = the same stimulus written in a run file');
check(['thresholds','thresholds_nearest','probe','findings'].every(id=>o.tables.includes(id))&&o.findings>0,'tables: thresholds, nearest threshold, probe, findings');
console.log(bad?`${bad} failed`:'all passed');process.exit(bad?1:0);
