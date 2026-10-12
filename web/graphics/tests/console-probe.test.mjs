import test from "node:test";
import assert from "node:assert/strict";
import { probeGamepads } from "../console-probe.mjs";

test("Gamepad feature unsupported",()=>{
  assert.deepEqual(probeGamepads({}),{status:"unsupported",gamepads:[]});
});
test("No connected pads yet on Xbox Edge",()=>{
  assert.deepEqual(probeGamepads({getGamepads(){return [null,null];}}),
                   {status:"waiting-for-input",gamepads:[]});
});
test("Connected controller is reported without requiring a standard mapping",()=>{
  const pad={id:"test-controller",connected:true,mapping:""};
  assert.deepEqual(probeGamepads({getGamepads(){return [null,pad];}}),
                   {status:"detected",gamepads:[pad]});
});
test("Permission-policy errors do not crash rendering",()=>{
  const result=probeGamepads({getGamepads(){const e=new Error("blocked");e.name="SecurityError";throw e;}});
  assert.deepEqual(result,{status:"blocked",gamepads:[],reason:"SecurityError"});
});
test("Invalid responses are distinguished from absent controller",()=>{
  assert.deepEqual(probeGamepads({getGamepads(){return null;}}),
                   {status:"invalid-response",gamepads:[]});
});
