import test from "node:test";
import assert from "node:assert/strict";
import {applyBaseProductionMinimum,VERIFIED_PRODUCTION_JOB_NAMES} from "../colony-base-production.mjs";

const run=(jobSlot,baseProduced,colonyByte00dd=0)=>
  applyBaseProductionMinimum({jobSlot,baseProduced,colonyByte00dd});

test("original indirect dispatch has three named production slots only",()=>{
 assert.deepEqual(VERIFIED_PRODUCTION_JOB_NAMES,["food","industry","research"]);
 assert.equal(Object.isFrozen(VERIFIED_PRODUCTION_JOB_NAMES),true);
});
test("food with no +0xdd colony modifier clamps negatives to zero",()=>{
 for(const x of [-32768,-50,-1,0])assert.equal(run(0,x),0);
 for(const x of [1,2,32767])assert.equal(run(0,x),x);
});
test("food with nonzero original colony +0xdd requires minimum one",()=>{
 for(const n of [1,7,255]){
  for(const x of [-100,-1,0])assert.equal(run(0,x,n),1);
  assert.equal(run(0,4,n),4);
 }
});
test("industry and research always clamp zero and negative to one",()=>{
 for(const job of [1,2]){
  for(const x of [-32768,-10,0])assert.equal(run(job,x),1);
  for(const x of [1,2,32767])assert.equal(run(job,x),x);
 }
});
test("job three is null in original dispatch, so reject it",()=>{
 assert.throws(()=>run(3,0),RangeError);
 assert.throws(()=>run(-1,2),RangeError);
 assert.throws(()=>run(1.3,5),RangeError);
});
test("unsupported signed-word inputs and missing modifier fail closed",()=>{
 assert.throws(()=>run(1,-32769),RangeError);
 assert.throws(()=>run(2,32768),RangeError);
 assert.throws(()=>run(1,2,-1),RangeError);
 assert.throws(()=>run(0,1,256),RangeError);
 assert.throws(()=>applyBaseProductionMinimum({jobSlot:0,baseProduced:0}),RangeError);
});
