/** Xbox/keyboard menu focus model independent of browser DOM or game rules. */
export const MENU_ITEMS = Object.freeze([
  {id:"start",label:"New Game",enabled:false},
  {id:"load",label:"Load Game",enabled:false},
  {id:"graphics",label:"Graphics",enabled:true},
  {id:"input",label:"Controller Test",enabled:true},
]);
export function makeMenuState() {
  return {selected:2,heldUp:false,heldDown:false,heldA:false,heldB:false};
}
export function nextEnabledIndex(items,current,direction) {
  if(!Number.isInteger(current)||current<0||current>=items.length)return -1;
  const step=direction<0?-1:1;
  for(let i=1;i<=items.length;i++){
    const index=(current+step*i+items.length*2)%items.length;
    if(items[index]?.enabled)return index;
  }
  return current;
}
const pressed=(pad,index)=>Boolean(pad.buttons?.[index]?.pressed);
export function updateMenuController(gamepad,state,items=MENU_ITEMS){
  if(!gamepad||gamepad.mapping!=="standard"){
    for(const k of ["heldUp","heldDown","heldA","heldB"])state[k]=false;
    return {selectionChanged:false,activate:null,back:false};
  }
  const axis=gamepad.axes?.[1]??0;
  const up=pressed(gamepad,12)||axis < -0.65;
  const down=pressed(gamepad,13)||axis > 0.65;
  const a=pressed(gamepad,0),b=pressed(gamepad,1);
  let selectionChanged=false;
  if(up&&!state.heldUp&&!down){
    const next=nextEnabledIndex(items,state.selected,-1);
    selectionChanged=next!==state.selected;state.selected=next;
  }
  if(down&&!state.heldDown&&!up){
    const next=nextEnabledIndex(items,state.selected,1);
    selectionChanged=next!==state.selected;state.selected=next;
  }
  const activate=a&&!state.heldA&&items[state.selected]?.enabled?items[state.selected].id:null;
  const back=b&&!state.heldB;
  Object.assign(state,{heldUp:up,heldDown:down,heldA:a,heldB:b});
  return {selectionChanged,activate,back};
}
export function validateAnimationManifest(obj){
  if(!obj||obj.format!=="moo2-browser-frames-v1"||!Number.isInteger(obj.frame_count)
      ||obj.frame_count<1||obj.frame_count>255
      ||!Number.isInteger(obj.width)||obj.width<1||obj.width>2048
      ||!Number.isInteger(obj.height)||obj.height<1||obj.height>2048
      ||!Array.isArray(obj.frames)||obj.frames.length!==obj.frame_count
      ||!Number.isInteger(obj.lead_in)||obj.lead_in<0||obj.lead_in>=obj.frame_count)
      throw new Error("Invalid private animation manifest");
  for(let i=0;i<obj.frame_count;i++){
    if(obj.frames[i]?.frame!==i || obj.frames[i].file!=="frame-"+String(i).padStart(3,"0")+".png")
      throw new Error("Invalid frame sequence");
  }
  return obj;
}
export function nextAnimationFrame(frame,manifest){
  if(!Number.isInteger(frame)||frame<0||frame>=manifest.frame_count)throw new RangeError("frame out of bounds");
  return frame+1<manifest.frame_count?frame+1:manifest.lead_in;
}

/** Focus navigation inside a graphics/controller panel. */
export function makePanelState(){
  return {selected:0,heldUp:false,heldDown:false,heldA:false,heldB:false};
}
export function updatePanelController(gamepad,state,controlCount){
  if(!Number.isInteger(controlCount)||controlCount<1||controlCount>8)
    throw new RangeError("Invalid panel control count");
  if(!gamepad||gamepad.mapping!=="standard"){
    for(const k of ["heldUp","heldDown","heldA","heldB"])state[k]=false;
    return {selectionChanged:false,activate:false,back:false};
  }
  const axis=gamepad.axes?.[1]??0;
  const up=pressed(gamepad,12)||axis < -0.65;
  const down=pressed(gamepad,13)||axis > 0.65;
  const a=pressed(gamepad,0),b=pressed(gamepad,1);
  let selectionChanged=false;
  if(up&&!state.heldUp&&!down){state.selected=(state.selected+controlCount-1)%controlCount;selectionChanged=true;}
  if(down&&!state.heldDown&&!up){state.selected=(state.selected+1)%controlCount;selectionChanged=true;}
  const activate=a&&!state.heldA;
  const back=b&&!state.heldB;
  Object.assign(state,{heldUp:up,heldDown:down,heldA:a,heldB:b});
  return {selectionChanged,activate,back};
}
