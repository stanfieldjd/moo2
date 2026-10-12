import {scale2x, fitContain} from "./scaler.mjs";
import {controllerStep, newControllerState, GAME_WIDTH, GAME_HEIGHT} from "./gamepad.mjs";

const find = id => document.getElementById(id);
const canvas=find("screen");
const context=canvas.getContext("2d",{alpha:false});
const source=document.createElement("canvas");
source.width=GAME_WIDTH;source.height=GAME_HEIGHT;
const src=source.getContext("2d",{willReadFrequently:true});
const edge=document.createElement("canvas");
const edgeCtx=edge.getContext("2d");
const controller=newControllerState();
let edgeReady=false, dirty=true, lastTime=performance.now(), oldGamepadName="";

function status(message){find("status").textContent=message;}
function placeholder(){
  src.fillStyle="#071421";src.fillRect(0,0,GAME_WIDTH,GAME_HEIGHT);
  for(let y=0;y<GAME_HEIGHT;y+=32)for(let x=0;x<GAME_WIDTH;x+=32){
    src.fillStyle=(x/32+y/32)%2===0?"#11273e":"#142d44";
    src.fillRect(x,y,32,32);
  }
  src.fillStyle="#f1f4fa";src.textAlign="center";
  src.font="bold 27px monospace";src.fillText("ARTWORK NOT LOADED",320,217);
  src.font="16px monospace";src.fillText("Select a decoded image to preview",320,250);
  src.font="13px monospace";src.fillText("No original game art is included",320,281);
  edgeReady=false;dirty=true;
}
placeholder();
function generateEdge(){
  if(edgeReady)return;
  const image=src.getImageData(0,0,GAME_WIDTH,GAME_HEIGHT);
  const doubled=scale2x(image);
  edge.width=doubled.width;edge.height=doubled.height;
  edgeCtx.putImageData(new ImageData(doubled.data,doubled.width,doubled.height),0,0);
  edgeReady=true;
}
function render(){
  if(!dirty)return;
  const rect=canvas.getBoundingClientRect();
  if(rect.width<1||rect.height<1)return;
  const ratio=Math.min(2,window.devicePixelRatio||1);
  const width=Math.max(1,Math.round(rect.width*ratio));
  const height=Math.max(1,Math.round(rect.height*ratio));
  if(width!==canvas.width||height!==canvas.height){canvas.width=width;canvas.height=height;}
  context.fillStyle="#000";context.fillRect(0,0,width,height);
  const mode=find("mode").value;
  if(mode==="edge")generateEdge();
  context.imageSmoothingEnabled=mode==="smooth";
  const bounds=fitContain(GAME_WIDTH,GAME_HEIGHT,width,height);
  context.drawImage(mode==="edge"?edge:source,bounds.x,bounds.y,bounds.width,bounds.height);
  if(controller.active){
    const px=bounds.x+controller.x*bounds.width/GAME_WIDTH;
    const py=bounds.y+controller.y*bounds.height/GAME_HEIGHT;
    context.save();context.lineWidth=Math.max(2,ratio);context.strokeStyle="#fff";
    context.fillStyle="#142033";context.beginPath();context.arc(px,py,8*ratio,0,Math.PI*2);
    context.fill();context.stroke();
    context.beginPath();context.moveTo(px-16*ratio,py);context.lineTo(px+16*ratio,py);
    context.moveTo(px,py-16*ratio);context.lineTo(px,py+16*ratio);context.stroke();context.restore();
  }
  dirty=false;
}
function activate(x,y){status("Prototype input at "+x+", "+y+". Gameplay controls are not yet wired.");}
function goBack(){status("Back action detected; game menu is not implemented yet.");}
find("mode").addEventListener("change",()=>{dirty=true;render();});
find("full").addEventListener("click",async()=>{
  try{if(document.fullscreenElement)await document.exitFullscreen();
      else await find("stage").requestFullscreen();}
  catch(error){status("Fullscreen unavailable: "+String(error.message||error));}
});
find("file").addEventListener("change",async event=>{
  const file=event.target.files?.[0];
  if(!file)return;
  if(!file.type.startsWith("image/")||file.size>32*1024*1024){
    status("Choose an image under 32 MB.");return;
  }
  try{
    const image=await createImageBitmap(file);
    if(image.width>8192||image.height>8192){image.close?.();throw new Error("Image dimensions too large.");}
    src.imageSmoothingEnabled=false;src.clearRect(0,0,GAME_WIDTH,GAME_HEIGHT);
    src.drawImage(image,0,0,GAME_WIDTH,GAME_HEIGHT);image.close?.();
    dirty=true;edgeReady=false;
    status("Local artwork loaded: "+file.name+"; scaled from 640 × 480 game coordinates.");
  }catch(error){status("Cannot decode image: "+String(error.message||error));}
});
canvas.addEventListener("pointerdown",event=>{
  const b=canvas.getBoundingClientRect();
  const x=Math.max(0,Math.min(639,Math.floor((event.clientX-b.left)*640/b.width)));
  const y=Math.max(0,Math.min(479,Math.floor((event.clientY-b.top)*480/b.height)));
  activate(x,y);
});
document.addEventListener("keydown",event=>{
  const steps={ArrowLeft:[-12,0],ArrowRight:[12,0],ArrowUp:[0,-12],ArrowDown:[0,12]};
  if(steps[event.key]){
    event.preventDefault();controller.active=true;
    controller.x=Math.max(0,Math.min(639,controller.x+steps[event.key][0]));
    controller.y=Math.max(0,Math.min(479,controller.y+steps[event.key][1]));dirty=true;
  }else if(event.key==="Enter"&&!["INPUT","SELECT","BUTTON"].includes(document.activeElement.tagName)){
    activate(Math.round(controller.x),Math.round(controller.y));
  }else if(event.key==="Escape")goBack();
});
window.addEventListener("resize",()=>{dirty=true;});
function frame(now){
  const dt=Math.min(.1,Math.max(0,(now-lastTime)/1000));lastTime=now;
  const pads=typeof navigator.getGamepads==="function"?navigator.getGamepads():[];
  const pad=Array.from(pads||[]).find(g=>g?.connected&&g.mapping==="standard");
  const x=controller.x,y=controller.y,active=controller.active;
  controllerStep(pad,controller,dt,{activate,back:goBack});
  const padName=pad?.id||"";
  if(padName!==oldGamepadName){
    oldGamepadName=padName;
    find("gamepadStatus").textContent=pad?"Controller detected: "+padName:"No standard Xbox-type controller detected.";
  }
  if(controller.x!==x||controller.y!==y||controller.active!==active)dirty=true;
  render();requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
