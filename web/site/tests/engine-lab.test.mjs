import test from "node:test";
import assert from "node:assert/strict";
import {LAB_SYSTEMS,inspectFixture,stepSystem} from "../games/space-strategy/engine-lab/model.mjs";

test("synthetic fixtures are valid, bounded native-yield inputs",()=>{
  assert.equal(LAB_SYSTEMS.length,5);
  for (let i=0;i<LAB_SYSTEMS.length;i++){
    const result=inspectFixture(i);
    assert.ok(Number.isInteger(result.foodDouble));
    assert.ok(Number.isInteger(result.industry));
    assert.ok(Number.isInteger(result.research));
    assert.equal(result.source,LAB_SYSTEMS[i]);
    assert.ok(result.foodDouble>=0);
  }
});
test("test deck uses original doubled-food units without inventing turns",()=>{
  assert.deepEqual([inspectFixture(0).foodDouble,inspectFixture(0).industry,inspectFixture(0).research],[4,2,3]);
  assert.deepEqual([inspectFixture(3).foodDouble,inspectFixture(3).industry,inspectFixture(3).research],[8,1,8]);
});
test("explicit byte flag adjusts all three verified per-worker yields",()=>{
  const before=inspectFixture(1,false),after=inspectFixture(1,true);
  assert.equal(after.foodDouble,before.foodDouble+2);
  assert.equal(after.industry,before.industry+1);
  assert.equal(after.research,before.research+1);
});
test("controller index navigation wraps and rejects invalid indices",()=>{
  assert.equal(stepSystem(0,-1),4);
  assert.equal(stepSystem(4,1),0);
  assert.equal(stepSystem(2,1),3);
  assert.throws(()=>stepSystem(-1,1),RangeError);
  assert.throws(()=>stepSystem(2,0),RangeError);
  assert.throws(()=>inspectFixture(5),RangeError);
});
