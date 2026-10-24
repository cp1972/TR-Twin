// The stimulus verdict of a run file equals the stimulus probe of v67 (reizProbe), per theory and seed,
// with the free run of the run file (the same for all theories: 30 000 steps, since the TR has M5).
//   node tests/test_stimulus.js <v67.html>
const fs=require('fs'),path=require('path'),{JSDOM}=require('jsdom');
const REPO=path.resolve(__dirname,'..');
const ctx=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return()=>({addColorStop(){}});if(p==='measureText')return()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const open=f=>{const d=new JSDOM(fs.readFileSync(f,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){w.HTMLCanvasElement.prototype.getContext=()=>ctx;w.requestAnimationFrame=()=>0;w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});}});
  const w=d.window;w.__run=c=>{const s=w.document.createElement('script');s.textContent='window.__o=(function(){'+c+'})();';w.document.body.appendChild(s);s.remove();return w.__o;};return w;};
const prof=fs.readFileSync(path.join(REPO,'simulation-mode/profiles/profil_Luhmann.csv'),'utf8');
const w8=open(path.join(REPO,'tr-twin.html'));
const got=w8.__run(`const sp=parseRunFile('mode,simulation\\nprofile,p.csv\\nstimulus,B,weaken,300,2.6,1819\\nseeds,1-2').spec;const res=r68Run(sp,{'p.csv':${JSON.stringify(prof)}});
  const out={};for(const r of res.runs){if(r.control)continue;const c=res.runs.find(q=>q.control&&q.theory===r.theory&&q.seed===r.seed);
    const abw=Math.max(...r.stimulus.end.map((s,i)=>Math.abs(s-c.stimulus.end[i])));const bew=Math.max(r.stimulus.drift,c.stimulus.drift)>=0.005;
    out[r.theory+' '+r.seed]={urteil:bew?'bewegung':(abw>=0.03?'fest':'zurueck'),abw,S:r.stimulus.end};}return out;`);
let bad=0;
for(const [name,csv] of [['TR',null],['Luhmann',prof]])for(const sd of [1,2]){
  const w7=open(process.argv[2]);
  const ref=w7.__run(`seed=${sd};applyDefaults();loadedChains=null;resetChains();const csv=${JSON.stringify(csv)};
    if(csv){const r=parseCursorCSV(csv);for(const cid in r.keys){const p=r.keys[cid];const el=document.getElementById(cid);if(el){el.value=p[p.length-1].val;el.dispatchEvent(new Event('input'));}}
      if(r.chains&&Object.keys(r.chains).length){loadedChains=r.chains;for(const sx in r.chains)setChain(+sx,r.chains[sx]);}profilMech(r);}
    satS=[0,0,0,0];rulerHold=[0,0,0,0];
    const p=reizProbe({x:1,dir:-1,dauer:300,k:2.6,beginn:1819,nachlauf:30000});/* v68: every theory runs as long as the longest (the TR has M5) */return {urteil:p.urteil,abw:p.abw,S:p.mit.ende.S};`);
  const g=got[(name==='TR'?'TR':'p')+' '+sd];const ok=JSON.stringify(ref)===JSON.stringify(g);if(!ok)bad++;
  console.log(name,sd,ok?'identical':'DIFF',ref.urteil,g.urteil,ref.abw.toFixed(5),g.abw.toFixed(5));}
process.exit(bad?1:0);
