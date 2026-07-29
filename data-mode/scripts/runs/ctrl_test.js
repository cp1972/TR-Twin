const fs=require("fs");const {JSDOM,VirtualConsole}=require("jsdom");
const ctxProxy=new Proxy({},{get:(o,p)=>{if(p==='createRadialGradient'||p==='createLinearGradient')return ()=>({addColorStop(){}});if(p==='measureText')return ()=>({width:10});return typeof p==='string'?(()=>{}):undefined;}});
const vc=new VirtualConsole();const errors=[];vc.on("jsdomError",e=>errors.push(e&&e.message?e.message:String(e)));
const dom=new JSDOM(fs.readFileSync("tr-twin.html","utf8"),{runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,
  beforeParse(window){window.HTMLCanvasElement.prototype.getContext=()=>ctxProxy;window.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){},addListener(){},removeListener(){}});window.requestAnimationFrame=()=>0;window.cancelAnimationFrame=()=>{};if(!window.performance)window.performance={now:()=>0};}});
const w=dom.window;
function load(id,text,name){return new Promise(res=>{const input=w.document.getElementById(id);const file=new w.File([text],name,{type:'text/csv'});Object.defineProperty(input,'files',{value:[file],configurable:true});input.dispatchEvent(new w.Event('change'));setTimeout(res,90);});}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  await sleep(150);
  await load('instcohortfile',fs.readFileSync(process.argv[2]||'data-mode/data/instances/control_parc_demo.csv','utf8'),'parc.csv');
  const YR=+(process.argv[3]||1900);const cc=w.controlCapacity(YR); const NM=['A','B','C','D'];
  console.log('Année '+YR+' · Plancher par structure (Ictrl) :',cc.floor.map(v=>v.toFixed(3)).join(' '));
  const grad=cc.floor[0]<cc.floor[1]&&cc.floor[1]<cc.floor[2]&&cc.floor[2]<cc.floor[3];
  console.log(grad?'✓ gradation structure A<B<C<D':'✗ gradation');
  console.log('Profil par séquence (capacité par cellule capCell[x][q]) :');
  console.log('        seqA   seqB   seqC   seqD');
  for(let x=0;x<4;x++)console.log('  '+NM[x]+'   '+cc.cell[x].map(v=>v.toFixed(3)).join('  '));
  // sauvegarder pour la figure
  fs.writeFileSync('/tmp/capcell.json',JSON.stringify(cc));
})();
