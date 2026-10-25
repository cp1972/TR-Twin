// Run files: the same run written in English, German and French gives the same specification; seeds, stimulus,
// categories and errors are read as documented.   node tests/test_runfile.js
const fs=require('fs'),path=require('path'),{JSDOM}=require('jsdom');
const REPO=path.resolve(__dirname,'..');
const ctx=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return()=>({addColorStop(){}});if(p==='measureText')return()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const w=new JSDOM(fs.readFileSync(path.join(REPO,'tr-twin.html'),'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,beforeParse(w){w.HTMLCanvasElement.prototype.getContext=()=>ctx;w.requestAnimationFrame=()=>0;w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});}}).window;
const parse=text=>{w.__t=text;const s=w.document.createElement('script');s.textContent='window.__p=parseRunFile(window.__t);';w.document.body.appendChild(s);s.remove();return JSON.parse(JSON.stringify(w.__p));};
let bad=0;const check=(ok,what)=>{if(!ok){bad++;console.log('✗',what);}else console.log('✓',what);};
const sim={en:'mode,simulation\nprofile,p.csv\nsteps,500\nseeds,1-3,7\nstimulus,politics,weaken,200,2,400',
  de:'Modus;Simulation\nProfil;p.csv\nSchritte;500\nStartwerte;1-3,7\nReiz;Politik;schwächen;200;2;400',
  fr:'mode,simulation\nprofil,p.csv\npas,500\ngraines,"1-3,7"\nstimulus,B,affaiblir,200,2,400'};
const ps=Object.fromEntries(Object.entries(sim).map(([k,v])=>[k,parse(v)]));
check(JSON.stringify(ps.en.spec)===JSON.stringify(ps.de.spec)&&JSON.stringify(ps.en.spec)===JSON.stringify(ps.fr.spec),'simulation: en = de = fr');
check(JSON.stringify(ps.en.spec.seeds)==='[1,2,3,7]','seeds 1-3,7');
check(ps.en.spec.stimulus&&ps.en.spec.stimulus.x===1&&ps.en.spec.stimulus.dir===-1&&ps.en.spec.stimulus.dauer===200&&ps.en.spec.stimulus.beginn===400,'stimulus read');
const data={en:'mode,data\ncontracts,c.csv\ninstances,i.csv\ncategories,composition\nstepped,no\ntrend window,20\nseeds,2',
  de:'modus,Daten\nvertragstabelle,c.csv\ninstanzen,i.csv\nkategorien,Gesamtzusammensetzung\nstufen,nein\ntrendfenster,20\nstartwerte,2',
  fr:'mode,données\ncontrats,c.csv\ninstances,i.csv\ncatégories,composition\npaliers,non\nfenêtre,20\ngraines,2'};
const pd=Object.fromEntries(Object.entries(data).map(([k,v])=>[k,parse(v)]));
check(JSON.stringify(pd.en.spec)===JSON.stringify(pd.de.spec)&&JSON.stringify(pd.en.spec)===JSON.stringify(pd.fr.spec),'data: en = de = fr');
check(pd.en.spec.categories==='pool'&&pd.en.spec.stepped===false&&pd.en.spec.trend===20,'categories, stepped, trend window');
check(parse('modus,Daten\nstartwerte,1').errors.length===1,'data mode without contract table is an error');
check(parse('mode,simulation\nseeds,x').errors.length===1,'bad seeds are an error');
check(parse('mode,data\ncontracts,c.csv\ntrend window,200').errors.length===1,'trend window over 100 is an error');
check(parse('mode,simulation\nfoo,1').warnings.length===1,'unknown key is a warning');
check(parse('# comment only\nmode,simulation').spec.steps===1819,'simulation without time: 1819 steps');
check(parse('mode,simulation\nstimulus,B,-1,300,2.6,1819').spec.stimulus.dir===-1,'stimulus direction -1 = weaken');
check(parse('Modus;Simulation\nReiz;B;schwächen;300;2,6;1819').spec.stimulus.k===2.6,'decimal comma with semicolons');
check(parse('mode,simulation\nstimulus,B,weaken\nstart,1900\nend,2000').errors.length===1,'stimulus with years is an error');
check(parse('mode,simulation\nstart,1900').errors.length===1,'start without end is an error');
check(JSON.stringify(parse('mode,simulation').spec.seeds)==='[1,2,3,4,5,6,7,8]','default seeds 1–8');
// thresholds, stimulus probe and interpretation file
check(parse('mode,simulation').spec.thresholds===true&&parse('mode,simulation').spec.probe===true,'thresholds and stimulus probe on by default (simulation)');
check(parse('modus,Simulation\nschwellen,nein\nreizprobe,nein').spec.thresholds===false&&parse('mode,simulation\nseuils,non\nsonde,non').spec.probe===false,'thresholds and probe off (de, fr)');
check(parse('mode,data\ncontracts,c.csv').spec.thresholds===false&&parse('mode,data\ncontracts,c.csv').spec.probe===false,'no thresholds or probe in data mode');
{w.__s=parse('modus,Simulation\nprofil,p.csv\ndeutung,d.org').spec;const s=w.document.createElement('script');s.textContent='window.__n=runFileNames(window.__s);';w.document.body.appendChild(s);s.remove();
 check(JSON.stringify(w.__n)==='["p.csv","d.org"]','the interpretation file is one of the files a run file names');}
// every example in runs/ parses without errors
for(const f of fs.readdirSync(path.join(REPO,'runs')).filter(f=>f.endsWith('.csv'))){const p=parse(fs.readFileSync(path.join(REPO,'runs',f),'utf8'));check(!p.errors.length&&!p.warnings.length,'runs/'+f+' parses');}
console.log(bad?`${bad} failed`:'all passed');process.exit(bad?1:0);
