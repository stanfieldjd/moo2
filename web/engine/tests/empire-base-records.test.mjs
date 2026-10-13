import test from "node:test";
import assert from "node:assert/strict";
import {inspectUncachedEmpireBase} from "../empire-base-records.mjs";
function setup(){
 const colonyRecord=new Uint8Array(0x169);
 const raceRecords=new Uint8Array(8*0xea9);
 colonyRecord[0]=1;
 return {colonyRecord,raceRecords};
}
const inspect=(rec,jobSlot,category,computedBaseProduced,climateGlobals)=>inspectUncachedEmpireBase({
 ...rec,jobSlot,category,computedBaseProduced,climateGlobals,
});
test("industry reads signed +0x8a2 with original 0xea9 category stride",()=>{
 const rec=setup();
 rec.raceRecords[1*0xea9+0x8a2]=0xfd; // -3
 rec.raceRecords[2*0xea9+0x8a2]=4;
 assert.equal(inspect(rec,1,1,8).afterMinimum,5);
 assert.equal(inspect(rec,1,2,8).afterMinimum,12);
 assert.equal(inspect(rec,1,8,8).afterMinimum,11);
 assert.equal(inspect(rec,1,9,8).afterMinimum,8);
});
test("research combines signed +0x8a3 and +0x16b owner trait only on match",()=>{
 const rec=setup();
 rec.raceRecords[1*0xea9+0x8a3]=0xfe; // -2
 rec.raceRecords[1*0xea9+0x16b]=3;
 rec.raceRecords[2*0xea9+0x8a3]=0xfe;
 rec.raceRecords[2*0xea9+0x16b]=3;
 assert.equal(inspect(rec,2,1,3).afterMinimum,2);
 assert.equal(inspect(rec,2,2,3).afterMinimum,1);
 assert.equal(inspect(rec,2,8,3).afterMinimum,6);
});
test("food returns nonpositive base before bonus/climate calculations",()=>{
 const rec=setup();rec.colonyRecord[0xe2]=4;
 rec.raceRecords[1*0xea9+0x8a1]=2;rec.raceRecords[1*0xea9+0x8ab]=1;
 assert.equal(inspect(rec,0,1,0).uncachedProduced,0);
 assert.equal(inspect(rec,0,1,0).afterMinimum,0);
 rec.colonyRecord[0xdd]=1;
 assert.equal(inspect(rec,0,1,-2).afterMinimum,1);
});
test("food uses explicit global climate table, cap A/B, owner offset",()=>{
 const rec=setup();rec.colonyRecord[0xe2]=6;
 rec.raceRecords[1*0xea9+0x8a1]=3;
 rec.raceRecords[1*0xea9+0x8ab]=1;
 const climateGlobals={table:new Uint8Array(9),capA:7,capB:20};
 climateGlobals.table[6]=2;
 const value=inspect(rec,0,1,4,climateGlobals);
 assert.deepEqual([value.raceBonus,value.specialBonus,value.uncachedProduced,value.afterMinimum],
                  [3,10,17,17]);
 rec.colonyRecord[0xe2]=8;climateGlobals.table[8]=2;
 assert.equal(inspect(rec,0,1,4,climateGlobals).afterMinimum,43);
});
test("special food and non-race categories do not need climate tables",()=>{
 const rec=setup();rec.colonyRecord[0xe2]=8;
 assert.equal(inspect(rec,0,8,2).afterMinimum,8);
 assert.equal(inspect(rec,0,9,2).afterMinimum,6);
 assert.equal(inspect(rec,0,10,2).afterMinimum,2);
});
test("industry/research negatives use verified wrapper minimum",()=>{
 const rec=setup();rec.raceRecords[0x8a2]=0xf6; // -10
 assert.equal(inspect(rec,1,0,0).uncachedProduced,-10);
 assert.equal(inspect(rec,1,0,0).afterMinimum,1);
 assert.equal(inspect(rec,2,8,-3).uncachedProduced,0);
 assert.equal(inspect(rec,2,8,-3).afterMinimum,1);
});
test("missing required climate data or byte-record widths fail closed",()=>{
 const rec=setup();rec.colonyRecord[0xe2]=4;
 rec.raceRecords[0x8ab]=1;
 assert.throws(()=>inspect(rec,0,0,4),RangeError);
 assert.throws(()=>inspect(rec,0,0,4,{table:new Uint8Array(3),capA:1,capB:2}),RangeError);
 assert.throws(()=>inspect(rec,0,0,4,{table:new Uint8Array(9),capA:256,capB:2}),RangeError);
 assert.throws(()=>inspect({...rec,raceRecords:new Uint8Array(10)},1,0,4),RangeError);
 assert.throws(()=>inspect({...rec,colonyRecord:new Uint8Array(2)},1,0,4),RangeError);
 assert.throws(()=>inspect(rec,3,0,4),RangeError);
});
test("adapter does not modify source colony, races or climate table",()=>{
 const rec=setup();rec.colonyRecord[0xe2]=5;rec.raceRecords[0x8ab]=1;
 const c=new Uint8Array(rec.colonyRecord),r=new Uint8Array(rec.raceRecords);
 const globals={table:new Uint8Array(9),capA:8,capB:9};const before=new Uint8Array(globals.table);
 inspect(rec,0,0,4,globals);
 assert.deepEqual(rec.colonyRecord,c);assert.deepEqual(rec.raceRecords,r);
 assert.deepEqual(globals.table,before);
});
