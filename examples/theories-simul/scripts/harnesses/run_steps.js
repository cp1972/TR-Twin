// Schritt-Trajektorie mit festen Reglern aus einem Profil (Endjahr-Werte, konstant).
const fs = require('fs');
const { JSDOM } = require('jsdom');
const APP = process.argv[2] || '/home/claude/TR-Twin-extract/tr-twin.html';
const PROFILE = process.argv[3] || '';
const NSTEPS = +(process.argv[4] || 1819);
const OUT = process.argv[5] || '/home/claude/tr-headless/out/trajektorie.json';
const html = fs.readFileSync(APP,'utf8');
const profileCsv = PROFILE ? fs.readFileSync(PROFILE,'utf8') : '';
const ctxStub = new Proxy({},{get:()=>(()=>ctxStub),set:()=>true});
const dom = new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext=()=>ctxStub; w.requestAnimationFrame=()=>0; w.cancelAnimationFrame=()=>{};
  if(!w.matchMedia)w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
}});
function runInPage(c){const s=dom.window.document.createElement('script');s.textContent=c;dom.window.document.body.appendChild(s);s.remove();}
runInPage(`window.__t=(function(){try{
  const dt=1/60*0.68;
  if(${JSON.stringify(!!profileCsv)}){
    const r=parseCursorCSV(${JSON.stringify(profileCsv)});
    if(r){ const yE=Math.max(...r.years.filter(y=>!isNaN(y)));
      for(const cid in r.keys){const p=r.keys[cid];const v=p[p.length-1].val;const el=document.getElementById(cid);if(el){el.value=v;el.dispatchEvent(new Event('input'));}}
      if(r.chains&&Object.keys(r.chains).length){loadedChains=r.chains;for(const sx in r.chains)setChain(+sx,r.chains[sx]);}
    }
  }
  reset();
  const Shist=[],G=[],R=[],SAT=[];
  for(let i=0;i<${NSTEPS};i++){step(dt);Shist.push(S.map(v=>+v.toFixed(5)));G.push(+gini().toFixed(5));R.push(+reciprocity().toFixed(5));SAT.push(satS.map(v=>+v.toFixed(4)));}
  return {ok:true,nsteps:${NSTEPS},S:Shist,gini:G,recip:R,sat:SAT};
}catch(e){return{ok:false,err:String((e&&e.stack)||e)};}})();`);
const r=dom.window.__t;
if(!r||!r.ok){console.error('FEHLER:',r&&r.err);process.exit(1);}
fs.mkdirSync(require('path').dirname(OUT),{recursive:true});
fs.writeFileSync(OUT,JSON.stringify(r));
const last=r.S[r.S.length-1];
console.log(`${r.nsteps} Schritte · Endgrößen = ${last.map(v=>(v*100).toFixed(1)+'%').join(' / ')} (Kultur/Politik/Wirtschaft/Medien)`);
console.log('→',OUT);
