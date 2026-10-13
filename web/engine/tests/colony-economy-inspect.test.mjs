import test from "node:test";
import assert from "node:assert/strict";
import {inspectColonyEconomy} from "../colony-economy-inspect.mjs";

function fixture(){
 const c=new Uint8Array(0x169);
 const planetRecords=new Uint8Array(17*2);
 const productionRaceRecord=new Uint8Array(0x184);
 const raceRecords=new Uint8Array(8*0xea9);
 c[0x02]=1;
 planetRecords[17+0x0a]=1; // 2 industry per worker
 planetRecords[17+0x0b]=2; // 4 doubled food per farmer
 planetRecords[17+0x0f]=10; // 5 research per scientist
 c[0x0a]=3;c[0]=0;
 for(let i=0;i<3;i++){
  let value=(i+1)|((i%3)<<7)|0x200;
  c[0x0c+i*4]=value&255;c[0x0d+i*4]=(value>>>8)&255;
 }
 return {colonyRecord:c,planetRecords,productionRaceRecord,raceRecords,anomaly:false};
}
test("inspection joins verified per-unit rates, maintenance and workforce census",()=>{
 const input=fixture();const original=new Uint8Array(input.colonyRecord);
 const view=inspectColonyEconomy(input);
 assert.equal(view.status,"inspection-only");
 assert.equal(view.populationCount,3);
 assert.deepEqual(view.workforce.jobTotals,[1,1,1,0]);
 assert.deepEqual(view.perUnitRates,{
  foodDoublePerFarmer:4,industryPerWorker:2,researchPerScientist:5
 });
 assert.equal(view.maintenance.food,3); // three ordinary race classes: 3*2/2
 assert.equal(view.maintenance.industry,0);
 assert.deepEqual(input.colonyRecord,original);
 assert.notStrictEqual(view.maintenance.colonyRecord,input.colonyRecord);
});
test("anomaly outcome is explicit and skips maintenance scan",()=>{
 const input=fixture();input.anomaly=true;
 input.colonyRecord[0xef]=50;input.colonyRecord[0xf0]=25;
 const view=inspectColonyEconomy(input);
 assert.equal(view.maintenance.food,0);
 assert.equal(view.maintenance.industry,0);
 assert.deepEqual(view.workforce.jobTotals,[1,1,1,0]);
});
test("missing unverified race record or anomaly cannot silently default",()=>{
 const input=fixture();delete input.anomaly;
 assert.throws(()=>inspectColonyEconomy(input),TypeError);
 const invalid=fixture();invalid.productionRaceRecord=new Uint8Array(4);
 assert.throws(()=>inspectColonyEconomy(invalid),RangeError);
});
