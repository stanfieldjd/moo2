import test from "node:test";
import assert from "node:assert/strict";
import {createControllerState,readController,controllerEvents,nextFocusIndex} from "../site-nav.mjs";
const pad = ({buttons=[],axes=[0,0],connected=true}={}) => ({
  connected,buttons:Array.from({length:16},(_,i)=>({pressed:buttons.includes(i)})),axes,
});
test("initial controller and absent gamepad are neutral",()=>{
 assert.deepEqual(readController(null),createControllerState());
 assert.deepEqual(readController(pad({connected:false})),createControllerState());
});
test("D-pad moves focus with both axes",()=>{
 assert.equal(readController(pad({buttons:[12]})).direction,-1);
 assert.equal(readController(pad({buttons:[13]})).direction,1);
 assert.equal(readController(pad({buttons:[14]})).direction,-1);
 assert.equal(readController(pad({buttons:[15]})).direction,1);
});
test("analog threshold prevents drift and ignores invalid axes",()=>{
 assert.equal(readController(pad({axes:[0,0.5]})).direction,0);
 assert.equal(readController(pad({axes:[0.65,0]})).direction,1);
 assert.equal(readController(pad({axes:[-0.65,0]})).direction,-1);
 assert.equal(readController(pad({axes:[NaN,undefined]})).direction,0);
});
test("opposed inputs cancel instead of moving unpredictably",()=>{
 assert.equal(readController(pad({buttons:[12,13]})).direction,0);
 assert.equal(readController(pad({buttons:[14,15]})).direction,0);
});
test("A confirm and B back fire on initial press, never continuously",()=>{
 const before=createControllerState();
 const pressed=readController(pad({buttons:[0,1]}));
 assert.deepEqual(controllerEvents(before,pressed),{move:0,activate:true,back:true});
 assert.deepEqual(controllerEvents(pressed,pressed),{move:0,activate:false,back:false});
 assert.deepEqual(controllerEvents(pressed,before),{move:0,activate:false,back:false});
});
test("held D-pad direction triggers one movement per press",()=>{
 const neutral=createControllerState(),down=readController(pad({buttons:[13]}));
 assert.equal(controllerEvents(neutral,down).move,1);
 assert.equal(controllerEvents(down,down).move,0);
 assert.equal(controllerEvents(down,neutral).move,0);
 assert.equal(controllerEvents(neutral,down).move,1);
});
test("focus positions are bounded and wrap for navigation",()=>{
 assert.equal(nextFocusIndex(-1,3,1),0);
 assert.equal(nextFocusIndex(0,3,-1),2);
 assert.equal(nextFocusIndex(2,3,1),0);
 assert.equal(nextFocusIndex(1,3,1),2);
 assert.equal(nextFocusIndex(0,0,1),-1);
 assert.equal(nextFocusIndex(0,2,0),0);
});
test("source-only navigation does not require game-specific data",()=>{
 const r=readController({buttons:[],axes:[]});
 assert.deepEqual(r,createControllerState());
});
