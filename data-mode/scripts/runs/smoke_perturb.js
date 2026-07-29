const fs=require("fs");
const {JSDOM,VirtualConsole}=require("jsdom");
const ctxProxy=new Proxy({},{get:(o,p)=>{
  if(p==='createRadialGradient'||p==='createLinearGradient')return ()=>({addColorStop(){}});
  if(p==='measureText')return ()=>({width:10});
  return typeof p==='string'?(()=>{}):undefined;}});
const errors=[];
const vc=new VirtualConsole();
vc.on("jsdomError",e=>errors.push(e&&e.message?e.message:String(e)));
const html=fs.readFileSync("tr-twin.html","utf8");
const dom=new JSDOM(html,{runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,
  beforeParse(window){
    window.HTMLCanvasElement.prototype.getContext=()=>ctxProxy;
    window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});
    window.requestAnimationFrame=()=>0;window.cancelAnimationFrame=()=>{};
    if(!window.performance)window.performance={now:()=>0};
  }});
const w=dom.window;
setTimeout(()=>{
  let ok=true;
  if(errors.length){ok=false;console.log("✗ erreurs de chargement :");errors.forEach(e=>console.log("   ",String(e).split("\n")[0]));}
  else console.log("✓ page chargée et exécutée jusqu'au bout sans erreur");
  const need=["parseContractCSV","buildCohortByActor","step","probeWeightAt","setLang","instLane","renderPrismRead","drawProbes"];
  const missing=need.filter(f=>typeof w[f]!=="function");
  console.log(missing.length?("✗ fonctions manquantes : "+missing.join(",")):"✓ fonctions prisme/poids définies");
  try{ w.setLang('en'); w.setLang('fr'); w.renderProbeList&&w.renderProbeList(); w.renderPrismRead();
       console.log("✓ render/setLang s'exécutent sans throw");
  }catch(e){ok=false;console.log("✗ exécution panneau :",e.message);}
  const pb=w.document.getElementById('perturbBox');
  console.log("✓ panneau de perturbation manuelle retiré ?", pb?'NON (présent)':'oui');
  // pipeline POIDS
  try{const rec=w.parseContractCSV(fs.readFileSync('data-mode/data/instances/instances_probe_demo.csv','utf8'));
    const withW=rec.filter(r=>r.w!=null).length;
    const by=w.buildCohortByActor(rec);
    const wi=w.probeWeightAt(by['reuters'],1920), wo=w.probeWeightAt(by['reuters'],1830);
    console.log('✓ poids lus:',withW+'/'+rec.length,'· probeWeightAt reuters@1920 (att.~0.775):',wi.toFixed(3),'· @1830 hors-durée:',wo);
  }catch(e){ok=false;console.log('✗ pipeline poids:',e.message);}
  console.log(ok&&!missing.length?"\nSMOKE TEST OK ✓":"\n✗ ÉCHEC");
},120);
