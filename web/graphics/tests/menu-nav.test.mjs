import test from "node:test";
import assert from "node:assert/strict";
import { MENU_ITEMS,makeMenuState,nextEnabledIndex,updateMenuController,validateAnimationManifest,nextAnimationFrame,makePanelState,updatePanelController } from "../menu-nav.mjs";
const pad=()=>({mapping:"standard",axes:[0,0],buttons:Array.from({length:16},()=>({pressed:false}))});
const manifest=(count,lead)=>({format:"moo2-browser-frames-v1",width:640,height:480,frame_count:count,lead_in:lead,frames:Array.from({length:count},(_,i)=>({frame:i,file:"frame-"+String(i).padStart(3,"0")+".png"}))});
test("disabled game actions cannot receive navigation focus",()=>{
 assert.equal(nextEnabledIndex(MENU_ITEMS,2,1),3);
 assert.equal(nextEnabledIndex(MENU_ITEMS,3,1),2);
 assert.equal(nextEnabledIndex(MENU_ITEMS,2,-1),3);
});
test("D-pad moves once per press; held state prevents repeated actions",()=>{
 const p=pad(),s=makeMenuState();
 p.buttons[13].pressed=true;
 assert.equal(updateMenuController(p,s).selectionChanged,true);assert.equal(s.selected,3);
 assert.equal(updateMenuController(p,s).selectionChanged,false);assert.equal(s.selected,3);
 p.buttons[13].pressed=false;updateMenuController(p,s);
 p.buttons[13].pressed=true;updateMenuController(p,s);assert.equal(s.selected,2);
});
test("A activate and B back fire only on new edge",()=>{
 const p=pad(),s=makeMenuState();
 p.buttons[0].pressed=true;assert.equal(updateMenuController(p,s).activate,"graphics");
 assert.equal(updateMenuController(p,s).activate,null);
 p.buttons[0].pressed=false;p.buttons[1].pressed=true;
 assert.equal(updateMenuController(p,s).back,true);
 assert.equal(updateMenuController(p,s).back,false);
});
test("Analog down select and no controller reset",()=>{
 const p=pad(),s=makeMenuState();p.axes[1]=0.8;updateMenuController(p,s);assert.equal(s.selected,3);
 updateMenuController(null,s);p.axes[1]=-0.8;updateMenuController(p,s);assert.equal(s.selected,2);
});
test("Manifest validates contiguous private frames",()=>{
 const a=manifest(50,49);assert.equal(validateAnimationManifest(a),a);
 assert.equal(nextAnimationFrame(0,a),1);assert.equal(nextAnimationFrame(49,a),49);
 const b=manifest(3,0);assert.equal(nextAnimationFrame(2,b),0);
});
test("Manifest rejects path traversal and broken frame order",()=>{
 const a=manifest(3,0);a.frames[1].file="../../other.png";
 assert.throws(()=>validateAnimationManifest(a));
 const b=manifest(3,0);b.lead_in=3;
 assert.throws(()=>validateAnimationManifest(b));
});
test("Xbox graphics panel cycles and activates focused controls",()=>{
 const p=pad(),s=makePanelState();
 p.buttons[13].pressed=true;assert.equal(updatePanelController(p,s,3).selectionChanged,true);
 assert.equal(s.selected,1);assert.equal(updatePanelController(p,s,3).selectionChanged,false);
 p.buttons[13].pressed=false;updatePanelController(p,s,3);
 p.buttons[0].pressed=true;assert.equal(updatePanelController(p,s,3).activate,true);
 assert.equal(updatePanelController(p,s,3).activate,false);
 p.buttons[0].pressed=false;p.buttons[1].pressed=true;
 assert.equal(updatePanelController(p,s,3).back,true);
});
