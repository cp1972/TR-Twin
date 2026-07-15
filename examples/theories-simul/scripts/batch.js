// Alle Theorie-Profile headless durchrechnen (Schritt-Modus, 1819 Schritte).
const fs=require('fs'), path=require('path');
const {JSDOM}=require('jsdom');
const DIR='/home/claude/TR-Twin-extract/examples/theories-simul';
const OUT='/home/claude/tr-headless/out/profiles';
fs.mkdirSync(OUT,{recursive:true});
const html=fs.readFileSync('/home/claude/TR-Twin-extract/tr-twin.html','utf8');
const ctxStub=new Proxy({},{get:()=>(()=>ctxStub),set:()=>true});
const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){
  w.HTMLCanvasElement.prototype.getContext=()=>ctxStub; w.requestAnimationFrame=()=>0; w.cancelAnimationFrame=()=>{};
  if(!w.matchMedia)w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});}});
function rip(c){const s=dom.window.document.createElement('script');s.textContent=c;dom.window.document.body.appendChild(s);s.remove();}

// Lauf aus Profil-CSV: Regler auf Endjahr-Werte (konstant), Ketten, reset, N Schritte, volle Trajektorie
rip(`window.__fromCsv=function(csv,n){
  const dt=1/60*0.68;
  const r=parseCursorCSV(csv);
  if(!r) return {ok:false,err:'Profil nicht lesbar'};
  applyDefaults();   // WICHTIG: alle Regler auf TR-Vorgaben, sonst schleppt der vorige Lauf Werte mit
  const cursors={};
  for(const cid in r.keys){const p=r.keys[cid];cursors[cid]=p[p.length-1].val;
    const el=document.getElementById(cid); if(el){el.value=cursors[cid]; el.dispatchEvent(new Event('input'));}}
  if(r.chains&&Object.keys(r.chains).length){loadedChains=r.chains;for(const sx in r.chains)setChain(+sx,r.chains[sx]);}
  else {loadedChains=null;resetChains();}
  reset();
  const Sh=[],G=[],R=[],SAT=[],RUL=[];
  for(let i=0;i<n;i++){step(dt);
    Sh.push(S.map(v=>+v.toFixed(5))); G.push(+gini().toFixed(5)); R.push(+reciprocity().toFixed(5));
    SAT.push(satS.map(v=>+v.toFixed(3))); RUL.push(ruler.slice());}
  return {ok:true,cursors,chains:r.chains||null,S:Sh,gini:G,recip:R,sat:SAT,ruler:RUL};
};`);

const files=fs.readdirSync(DIR).filter(f=>/^profil_.*\.csv$/.test(f)).sort();
const NAMES=['K','P','W','M'];
console.log(`${files.length} Profile · 1819 Schritte je Lauf\n`);
console.log('Theorie                       K     P     W     M    | GINI   R     Regent  satS(max)');
console.log('-'.repeat(88));
for(const f of files){
  const csv=fs.readFileSync(path.join(DIR,f),'utf8');
  const r=dom.window.__fromCsv(csv,1819);
  const name=f.replace(/^profil_/,'').replace(/\.csv$/,'');
  if(!r.ok){ console.log(`${name.padEnd(28)} FEHLER: ${r.err}`); continue; }
  fs.writeFileSync(path.join(OUT,name+'.json'), JSON.stringify(r));
  const S=r.S[r.S.length-1], G=r.gini[r.gini.length-1], R=r.recip[r.recip.length-1];
  const sat=r.sat[r.sat.length-1], rul=r.ruler[r.ruler.length-1];
  const dom_i=S.indexOf(Math.max(...S));
  const regent = rul.every(v=>v===rul[0]) ? NAMES[rul[0]] : (rul.map(v=>NAMES[v]).join(''));
  console.log(`${name.padEnd(28)} ${S.map(v=>(v*100).toFixed(1).padStart(5)).join(' ')} | ${G.toFixed(3)} ${R.toFixed(3)}  ${regent.padEnd(6)}  ${Math.max(...sat).toFixed(2)}`);
}
console.log('\nJSON-Trajektorien:', OUT);
