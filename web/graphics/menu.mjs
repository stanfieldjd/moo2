import {scale2x} from "./scaler.mjs";
import {probeGamepads} from "./console-probe.mjs";
import {MENU_ITEMS,makeMenuState,nextEnabledIndex,updateMenuController,validateAnimationManifest,nextAnimationFrame,makePanelState,updatePanelController} from "./menu-nav.mjs";

const get=id=>document.getElementById(id);
const canvas=get("art");
const ctx=canvas.getContext("2d",{alpha:false});
const state=makeMenuState();
const panelState=makePanelState();
const buttons=MENU_ITEMS.map(x=>get(x.id));
let manifest=null,frameNumber=0,playing=false,frameTick=0,pending=false;
let picture=null,edgeCache=null,lastPad="",view="menu",lastKey="";
const frameRoot="./private-assets/mainmenu/";
const status=message=>{get("feedback").textContent=message;};
function fallbackArt(){
  ctx.fillStyle="#081628";ctx.fillRect(0,0,640,480);
  ctx.fillStyle="#abd879";ctx.textAlign="center";ctx.font="bold 23px monospace";
  ctx.fillText("MASTER OF ORION II",320,140);
  ctx.font="16px monospace";ctx.fillText("Private artwork unavailable",320,180);
  ctx.fillText("Export MAINMENU.LBX locally first",320,212);
}
fallbackArt();
function render(){
  if(!picture){fallbackArt();return;}
  ctx.imageSmoothingEnabled=false;
  ctx.clearRect(0,0,640,480);
  if(get("mode").value==="edge"){
    if(!edgeCache){
      const off=document.createElement("canvas");off.width=640;off.height=480;
      const offctx=off.getContext("2d",{willReadFrequently:true});
      offctx.drawImage(picture,0,0,640,480);
      const out=scale2x(offctx.getImageData(0,0,640,480));
      edgeCache=document.createElement("canvas");edgeCache.width=1280;edgeCache.height=960;
      edgeCache.getContext("2d").putImageData(new ImageData(out.data,1280,960),0,0);
    }
    ctx.drawImage(edgeCache,0,0,640,480);
  }else ctx.drawImage(picture,0,0,640,480);
}
function focusSelected(){
  const b=buttons[state.selected];if(b&&!b.disabled)b.focus({preventScroll:true});
}
function setSelection(i){
  if(!MENU_ITEMS[i]?.enabled)return;
  state.selected=i;focusSelected();
}
function showPanel(name){
  view=name;
  panelState.selected=0;panelState.heldUp=false;panelState.heldDown=false;panelState.heldB=false;
  get("graphicsPanel").hidden=name!=="graphics";
  get("inputPanel").hidden=name!=="input";
  if(name==="graphics")get("mode").focus();
  else if(name==="input")get("inputPanel").querySelector(".back").focus();
  else focusSelected();
}
function openSelected(id,fromController=false){
  if(id==="graphics"||id==="input"){
    showPanel(id);panelState.heldA=fromController;
    status(id==="graphics"?"Select scaling or animation.":"Input diagnostics active; press controller buttons.");
  }
}
function back(){
  showPanel("menu");status("Main menu preview; game start and load are not implemented.");
}
for(let i=0;i<buttons.length;i++)buttons[i].addEventListener("click",()=>{setSelection(i);openSelected(MENU_ITEMS[i].id);});
for(const b of document.querySelectorAll(".back"))b.addEventListener("click",back);
get("mode").addEventListener("change",()=>{edgeCache=null;render();});
get("animate").addEventListener("click",()=>{
  if(!manifest){status("No local animation sequence; run the offline exporter.");return;}
  playing=!playing;get("animate").textContent=playing?"Pause animation preview":"Play animation preview (unverified speed)";
  status(playing?"Preview animation at arbitrary 8 frames/sec; NOT verified original timing.":"Animation preview paused.");
});
async function fetchFrame(index){
  if(!manifest||pending)return;
  pending=true;
  try{
    const filename=manifest.frames[index].file;
    const img=new Image();
    img.decoding="async";
    img.src=frameRoot+filename;
    await img.decode();
    picture=img;frameNumber=index;edgeCache=null;render();
  }catch(error){playing=false;status("Private animation frame unavailable: "+String(error.message||error));}
  finally{pending=false;}
}
async function loadPrivateArt(){
  try{
    const response=await fetch(frameRoot+"manifest.json",{cache:"no-store"});
    if(!response.ok)throw new Error("private manifest not found");
    manifest=validateAnimationManifest(await response.json());
    if(manifest.width!==640||manifest.height!==480)throw new Error("unexpected 4:3 source resolution");
    await fetchFrame(0);
    status("Authentic locally converted main-menu artwork loaded. 50-frame animation is available for preview; gameplay is not implemented.");
  }catch(error){
    manifest=null;fallbackArt();status("Art preview unavailable: "+String(error.message||error)+". Controller menus remain testable.");
  }
}
document.addEventListener("keydown",event=>{
  lastKey=event.key;if(view==="input")get("inputStatus").textContent="Last browser keyboard event: "+event.key;
  const active=document.activeElement?.tagName;
  if(view==="menu"&&(event.key==="ArrowUp"||event.key==="ArrowDown")){
    event.preventDefault();setSelection(nextEnabledIndex(MENU_ITEMS,state.selected,event.key==="ArrowUp"?-1:1));
  }else if(view==="menu"&&event.key==="Enter"&&!["BUTTON","SELECT"].includes(active)){
    event.preventDefault();openSelected(MENU_ITEMS[state.selected].id);
  }else if(event.key==="Escape"&&view!=="menu"){
    event.preventDefault();back();
  }
});
document.addEventListener("pointerdown",event=>{
  if(view==="input")get("inputStatus").textContent="Pointer event detected at "+Math.round(event.clientX)+", "+Math.round(event.clientY);
});
let lastNow=performance.now(),checkNext=0;
function tick(now){
  const elapsed=Math.min(0.12,(now-lastNow)/1000);lastNow=now;
  const current=probeGamepads(navigator);
  const gamepad=current.gamepads.find(p=>p.mapping==="standard");
  if(view==="menu"){
    const input=updateMenuController(gamepad,state);
    if(input.selectionChanged)focusSelected();
    if(input.activate)openSelected(input.activate,true);
  }else{
    // Panel focus is separate; Xbox A activates the selected panel item,
    // never an unrelated main-menu action.
    const controls=view==="graphics"
      ? [get("mode"),get("animate"),get("graphicsPanel").querySelector(".back")]
      : [get("inputPanel").querySelector(".back")];
    const input=updatePanelController(gamepad,panelState,controls.length);
    if(input.selectionChanged)controls[panelState.selected].focus({preventScroll:true});
    if(input.activate){
      if(view==="graphics"&&panelState.selected===0){
        get("mode").value=get("mode").value==="sharp"?"edge":"sharp";
        get("mode").dispatchEvent(new Event("change"));
      }else if(view==="graphics"&&panelState.selected===1)get("animate").click();
      else back();
    }
    if(input.back)back();
  }
  if(now>checkNext){
    checkNext=now+500;
    const message=gamepad?"Xbox-compatible standard controller detected: "+gamepad.id:
      "Controller status: "+current.status+(current.reason?" ("+current.reason+")":"")+
      ". Xbox One Edge hardware has not been verified.";
    if(message!==lastPad){get("controllerStatus").textContent=message;lastPad=message;}
    if(view==="input"&&gamepad)
      get("inputStatus").textContent="Gamepad axes: "+Array.from(gamepad.axes||[]).map(n=>Number(n).toFixed(2)).join(", ")+
        "; buttons held: "+Array.from(gamepad.buttons||[]).map((b,i)=>b.pressed?i:null).filter(x=>x!==null).join(", ")+
        (lastKey?"; keyboard event: "+lastKey:"");
  }
  if(playing&&manifest){
    frameTick+=elapsed;
    if(frameTick>=0.125&&!pending){frameTick=0;const next=nextAnimationFrame(frameNumber,manifest);
      if(next!==frameNumber)void fetchFrame(next);else playing=false;
    }
  }
  requestAnimationFrame(tick);
}
void loadPrivateArt();
requestAnimationFrame(tick);
