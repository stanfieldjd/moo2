import test from "node:test";
import assert from "node:assert/strict";
import {EMPIRE_BASE_BONUS_JOB_NAMES,empireFoodBonuses,empireIndustryBonus,
  empireResearchBonuses,combineUncachedEmpireBase} from "../empire-base-bonuses.mjs";

const food = (category,extra={})=>empireFoodBonuses({
  category,raceBonusByte8a1:2,raceClimateFlag8ab:false,
  colonyClimateByteE2:0,...extra,
});
const research = (category,extra={})=>empireResearchBonuses({
  category,raceBonusByte8a3:2,colonyOwnerCategory:1,raceByte016b:3,...extra,
});

test("the original three dispatch slots retain exact names",()=>{
 assert.deepEqual(EMPIRE_BASE_BONUS_JOB_NAMES,["food","industry","research"]);
 assert.equal(Object.isFrozen(EMPIRE_BASE_BONUS_JOB_NAMES),true);
});
test("food categories 8/9 are special; all other >=10 add nothing",()=>{
 assert.deepEqual(food(8),{raceBonus:6,climateBonus:0});
 assert.deepEqual(food(9),{raceBonus:4,climateBonus:0});
 for(let category=10;category<=15;category++)
  assert.deepEqual(food(category),{raceBonus:0,climateBonus:0});
});
test("food normal categories read signed +0x8a1, climate flag +0x8ab",()=>{
 for(let i=0;i<8;i++)assert.deepEqual(food(i),{raceBonus:2,climateBonus:0});
 assert.deepEqual(food(3,{raceBonusByte8a1:-8}),{raceBonus:-8,climateBonus:0});
});
test("food climate types 4/6 use cap A; 5/8 use cap B",()=>{
 for(const [climate,expected] of [[4,10],[5,20],[6,10],[8,20],[7,0],[9,0]]) {
  assert.deepEqual(food(2,{
   raceClimateFlag8ab:true,colonyClimateByteE2:climate,
   climateTableByte:2,climateCapA:7,climateCapB:12,
  }),{raceBonus:2,climateBonus:expected});
 }
 assert.deepEqual(food(1,{
  raceClimateFlag8ab:false,colonyClimateByteE2:4,
 }),{raceBonus:2,climateBonus:0});
});
test("food climate cap below table can reduce output (no inferred clamp)",()=>{
 assert.equal(food(2,{
  raceClimateFlag8ab:true,colonyClimateByteE2:4,
  climateTableByte:8,climateCapA:3,
 }).climateBonus,-10);
});
test("industry uses signed race +0x8a2 for normal, +3 special category 8",()=>{
 for(let i=0;i<8;i++)
  assert.equal(empireIndustryBonus({category:i,raceBonusByte8a2:-3}),-3);
 assert.equal(empireIndustryBonus({category:8}),3);
 for(let i=9;i<16;i++)assert.equal(empireIndustryBonus({category:i}),0);
});
test("research +1 condition requires owner match and +0x16b equals 3",()=>{
 assert.deepEqual(research(1),{raceBonus:2,ownerBonus:1});
 assert.deepEqual(research(1,{raceByte016b:2}),{raceBonus:2,ownerBonus:0});
 assert.deepEqual(research(2),{raceBonus:2,ownerBonus:0});
 assert.deepEqual(research(3,{raceBonusByte8a3:-4}),{raceBonus:-4,ownerBonus:0});
 assert.deepEqual(research(8),{raceBonus:3,ownerBonus:0});
 assert.deepEqual(research(9),{raceBonus:0,ownerBonus:0});
});
test("combine respects food early exit and signed 16-bit word stores",()=>{
 assert.equal(combineUncachedEmpireBase({jobSlot:0,baseProduced:0,raceBonus:6}),0);
 assert.equal(combineUncachedEmpireBase({jobSlot:0,baseProduced:-2,raceBonus:6}),-2);
 assert.equal(combineUncachedEmpireBase({jobSlot:0,baseProduced:2,raceBonus:6,specialBonus:4}),12);
 assert.equal(combineUncachedEmpireBase({jobSlot:1,baseProduced:0,raceBonus:-4}),-4);
 assert.equal(combineUncachedEmpireBase({jobSlot:2,baseProduced:32767,raceBonus:3}),-32766);
});
test("incomplete original bytes and invalid original job slot fail closed",()=>{
 assert.throws(()=>empireFoodBonuses({category:1,raceBonusByte8a1:2}),TypeError);
 assert.throws(()=>empireFoodBonuses({category:1,raceBonusByte8a1:255,raceClimateFlag8ab:false,colonyClimateByteE2:0}),RangeError);
 assert.throws(()=>empireIndustryBonus({category:1}),RangeError);
 assert.throws(()=>research(1,{raceByte016b:256}),RangeError);
 assert.throws(()=>empireResearchBonuses({category:4,raceBonusByte8a3:2,raceByte016b:3}),RangeError);
 assert.throws(()=>combineUncachedEmpireBase({jobSlot:3,baseProduced:1,raceBonus:0}),RangeError);
 assert.throws(()=>combineUncachedEmpireBase({jobSlot:1,baseProduced:32768,raceBonus:0}),RangeError);
});
