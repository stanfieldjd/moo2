import test from "node:test";
import assert from "node:assert/strict";
import {MINERALS_PER_MINE, foodPerFarmer, industryPerWorker, researchPerScientist} from "../colony-yields.mjs";

// These fixture fields are raw original record-offset flags, not unverified names.
const noneFood=Object.freeze({planetFoodByte:0,raceByte0134:0,flag0164:false,flag013a:false});
const noneIndustry=Object.freeze({mineralClass:0,raceByte0183:0,flag013a:false,flag013d:false,flag015a:false,flag0142:false});
const noneResearch=Object.freeze({planetModifierByte:0,flag013a:false,flag0154:false,flag0149:false,flag0159:false});

test("official v1.31 mineral table is five indexed values",()=>{
  assert.deepEqual(MINERALS_PER_MINE,[1,2,3,5,8]);
  assert.equal(Object.isFrozen(MINERALS_PER_MINE),true);
});
test("farmer base uses doubled food and race special case only for zero",()=>{
  for(let value=0;value<=255;value++){
    const standard=foodPerFarmer({...noneFood,planetFoodByte:value});
    assert.equal(standard,2*value);
    const special=foodPerFarmer({...noneFood,planetFoodByte:value,raceByte0134:3});
    assert.equal(special,value===0?2:2*value);
  }
});
test("farmer flags only add when doubled base is positive",()=>{
  assert.equal(foodPerFarmer({...noneFood,flag0164:true,flag013a:true}),0);
  assert.equal(foodPerFarmer({...noneFood,raceByte0134:3,flag0164:true,flag013a:true}),8);
  assert.equal(foodPerFarmer({...noneFood,planetFoodByte:2,flag0164:true,flag013a:true}),10);
  assert.equal(foodPerFarmer({...noneFood,planetFoodByte:255,flag0164:true,flag013a:true}),516);
});
test("worker industry uses only the five valid mineral classes",()=>{
  for(let i=0;i<5;i++) {
    assert.equal(industryPerWorker({...noneIndustry,mineralClass:i}),MINERALS_PER_MINE[i]);
  }
  assert.equal(industryPerWorker({...noneIndustry,mineralClass:4,raceByte0183:3,
    flag013a:true,flag013d:true,flag015a:true,flag0142:true}),16);
});
test("worker industry flag contributions are independent",()=>{
  const checks={flag013a:1,flag013d:1,flag015a:2,flag0142:3};
  for(const [key,value] of Object.entries(checks)){
    assert.equal(industryPerWorker({...noneIndustry,[key]:true}),1+value);
  }
  assert.equal(industryPerWorker({...noneIndustry,raceByte0183:3}),2);
  assert.equal(industryPerWorker({...noneIndustry,raceByte0183:4}),1);
});
test("research starts at three, adds flag effects and selected planet modifier",()=>{
  assert.equal(researchPerScientist(noneResearch),3);
  const checks={flag013a:1,flag0154:2,flag0149:3,flag0159:1};
  for(const [key,value] of Object.entries(checks)){
    assert.equal(researchPerScientist({...noneResearch,[key]:true}),3+value);
  }
  for(let i=0;i<=255;i++){
    const expected=3+(i===10?2:i===11?5:0);
    assert.equal(researchPerScientist({...noneResearch,planetModifierByte:i}),expected);
  }
  assert.equal(researchPerScientist({...noneResearch,planetModifierByte:11,
    flag013a:true,flag0154:true,flag0149:true,flag0159:true}),15);
});
test("invalid indices, missing flags and unsupported widths fail closed",()=>{
  assert.throws(()=>industryPerWorker({...noneIndustry,mineralClass:5}),RangeError);
  assert.throws(()=>industryPerWorker({...noneIndustry,mineralClass:-1}),RangeError);
  assert.throws(()=>industryPerWorker({...noneIndustry,mineralClass:1.5}),RangeError);
  assert.throws(()=>researchPerScientist({...noneResearch,planetModifierByte:256}),RangeError);
  assert.throws(()=>foodPerFarmer({...noneFood,planetFoodByte:-1}),RangeError);
  assert.throws(()=>foodPerFarmer({...noneFood,flag013a:1}),TypeError);
  assert.throws(()=>industryPerWorker({...noneIndustry,flag015a:undefined}),TypeError);
  assert.throws(()=>researchPerScientist(),RangeError);
});
