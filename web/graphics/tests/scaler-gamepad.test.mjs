import test from "node:test";
import assert from "node:assert/strict";
import {scale2x,nearest2x,fitContain} from "../scaler.mjs";
import {controllerStep,newControllerState} from "../gamepad.mjs";
const image=(width,height,colors)=>({width,height,data:new Uint8ClampedArray(colors.flat())});
const W=[255,255,255,255], B=[0,0,0,255], T=[0,0,0,0];
function pixels(img) {const a=[];for(let j=0;j<img.data.length;j+=4)a.push([...img.data.slice(j,j+4)]);return a}
test("pixel-perfect 2x duplicates every pixel (preserving alpha)",()=>{
  const result=nearest2x(image(2,1,[W,T]));
  assert.deepEqual([result.width,result.height],[4,2]);
  assert.deepEqual(pixels(result),[W,W,T,T,W,W,T,T]);
});
test("Scale2x retains flat colors and alpha",()=>{
 const result=scale2x(image(2,2,[T,T,T,T]));
 assert.equal(result.width,4);assert.equal(result.height,4);
 assert.deepEqual(pixels(result),Array(16).fill(T));
});
test("Scale2x smooths only exact-color orthogonal corners",()=>{
 const input=image(3,3,[B,W,W,W,B,B,W,B,B]);
 const result=scale2x(input);
 assert.deepEqual(pixels(result)[(2*6)+2],W);
 assert.deepEqual(pixels(result)[(2*6)+3],B);
});
test("Scale2x refuses malformed/big input",()=>{
 assert.throws(()=>scale2x({width:0,height:1,data:new Uint8ClampedArray(0)}),RangeError);
 assert.throws(()=>nearest2x({width:2,height:2,data:new Uint8ClampedArray(3)}),RangeError);
});
test("fitContain preserves 4:3 and centers display",()=>{
 assert.deepEqual(fitContain(640,480,1280,720),{x:160,y:0,width:960,height:720});
 assert.deepEqual(fitContain(640,480,1280,960),{x:0,y:0,width:1280,height:960});
});
test("Xbox A and B fire on edge, not every frame",()=>{
 const state=newControllerState();let a=0,b=0;
 const pad={mapping:"standard",axes:[0,0],buttons:Array.from({length:16},()=>({pressed:false}))};
 const h={activate:()=>a++,back:()=>b++};
 pad.buttons[0].pressed=true;controllerStep(pad,state,1/60,h);controllerStep(pad,state,1/60,h);
 assert.equal(a,1);
 pad.buttons[0].pressed=false;pad.buttons[1].pressed=true;controllerStep(pad,state,1/60,h);
 assert.equal(b,1);
 controllerStep(pad,state,1/60,h);assert.equal(b,1);
 pad.buttons[1].pressed=false;controllerStep(pad,state,1/60,h);
 pad.buttons[0].pressed=true;controllerStep(pad,state,1/60,h);assert.equal(a,2);
});
test("Xbox D-pad and stick obey speed and bounds",()=>{
 const state=newControllerState();
 const pad={mapping:"standard",axes:[0.5,0],buttons:Array.from({length:16},()=>({pressed:false}))};
 controllerStep(pad,state,0.1);
 assert.equal(state.x,336);
 pad.axes[0]=0;pad.buttons[14].pressed=true;
 for(let i=0;i<400;i++)controllerStep(pad,state,0.1);
 assert.equal(state.x,0);
});
