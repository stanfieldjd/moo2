import test from "node:test";
import assert from "node:assert/strict";
import {makeColonyFixture,assignFixtureJob,inspectFixtureColony,JOB_LABELS} from "../games/space-strategy/engine-lab/colony-lab.mjs";

test("synthetic colony uses valid byte records for verified workforce and upkeep inspectors",()=>{
  const fixture=makeColonyFixture(0);
  const before=new Uint8Array(fixture.colonyRecord);
  const snapshot=inspectFixtureColony(fixture,0);
  assert.equal(snapshot.status,"inspection-only");
  assert.equal(snapshot.populationCount,4);
  assert.equal(snapshot.participating,4);
  assert.deepEqual(snapshot.jobTotals,[2,1,1,0]);
  assert.equal(snapshot.foodUpkeep,4);
  assert.equal(snapshot.industryUpkeep,0);
  assert.deepEqual(snapshot.perUnitRates,{
    foodDoublePerFarmer:4,industryPerWorker:2,researchPerScientist:3
  });
  assert.deepEqual(fixture.colonyRecord,before,"inspection must be read-only");
});
test("synthetic job edits change verified job bits without altering caller records",()=>{
  const original=makeColonyFixture(1);
  const originalBytes=new Uint8Array(original.colonyRecord);
  const revised=assignFixtureJob(original,0,2);
  assert.equal(inspectFixtureColony(original,0).personInfo.jobSlot,0);
  assert.equal(inspectFixtureColony(revised,0).personInfo.jobSlot,2);
  assert.deepEqual(inspectFixtureColony(revised,0).jobTotals,[1,1,2,1]);
  assert.deepEqual(original.colonyRecord,originalBytes);
  const first=0x0c;
  for(let i=0;i<4;i++){
    assert.equal(revised.colonyRecord[first+i] & (i===0?0x7f:i===1?0xfe:0xff), originalBytes[first+i] & (i===0?0x7f:i===1?0xfe:0xff));
  }
  assert.equal(revised.colonyRecord[0x0d] & 0x02,0x02,"production-scan inclusion must be preserved");
});
test("explicit synthetic bonus must be supplied in cloned colony record",()=>{
  const fixture=makeColonyFixture(2);
  const before=inspectFixtureColony(fixture,0);
  const c=new Uint8Array(fixture.colonyRecord);c[0x13a]=1;
  const after=inspectFixtureColony({...fixture,colonyRecord:c},0);
  assert.equal(after.perUnitRates.foodDoublePerFarmer,before.perUnitRates.foodDoublePerFarmer+2);
  assert.equal(after.perUnitRates.industryPerWorker,before.perUnitRates.industryPerWorker+1);
  assert.equal(after.perUnitRates.researchPerScientist,before.perUnitRates.researchPerScientist+1);
  assert.equal(fixture.colonyRecord[0x13a],0);
});
test("colony fixture and job editors reject invalid choices",()=>{
  assert.deepEqual(JOB_LABELS,["Food","Industry","Research","Unclassified"]);
  assert.throws(()=>makeColonyFixture(-1),RangeError);
  assert.throws(()=>makeColonyFixture(5),RangeError);
  const fixture=makeColonyFixture(0);
  assert.throws(()=>assignFixtureJob(fixture,-1,1),RangeError);
  assert.throws(()=>assignFixtureJob(fixture,4,1),RangeError);
  assert.throws(()=>assignFixtureJob(fixture,0,3),RangeError);
  assert.throws(()=>inspectFixtureColony(fixture,4),RangeError);
});
