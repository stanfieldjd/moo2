import test from "node:test";
import assert from "node:assert/strict";
import {censusColonyWorkforce,decodePopulationEntry} from "../colony-workforce.mjs";
function colony(n=0){const c=new Uint8Array(0x169);c[0x0a]=n;return c;}
function pack(c,idx,category,job,active=true,other=false,high=0) {
 const v = (category&15)|((job&3)<<7)|(active?0x200:0)|(other?0x400:0)|high;
 const at=0x0c+idx*4;
 c[at]=v&255;c[at+1]=(v>>>8)&255;c[at+2]=(v>>>16)&255;c[at+3]=(v>>>24)&255;
}
test("no population returns a complete empty census",()=>{
 assert.deepEqual(censusColonyWorkforce(colony()),{
  populationCount:0,participating:0,skipped:0,
  jobTotals:[0,0,0,0],
  categoriesAll:Array(16).fill(0),
  categoriesByJob:Array.from({length:4},()=>Array(16).fill(0))
 });
});
test("bit 9 gates the production scan and bits 7-8 choose slot",()=>{
 const c=colony(5);pack(c,0,1,0,true);pack(c,1,2,1,true);
 pack(c,2,3,2,true);pack(c,3,4,3,true);pack(c,4,5,2,false);
 const before=new Uint8Array(c);
 const result=censusColonyWorkforce(c);
 assert.equal(result.participating,4);assert.equal(result.skipped,1);
 assert.deepEqual(result.jobTotals,[1,1,1,1]);
 assert.equal(result.categoriesByJob[2][3],1);
 assert.equal(result.categoriesByJob[2][5],0);
 assert.equal(result.categoriesAll[5],1);
 assert.deepEqual(c,before);
});
test("high bits and alternate-group bit do not change job or category",()=>{
 const c=colony(1);pack(c,0,15,2,true,true,0xfa000000);
 assert.deepEqual(decodePopulationEntry(c,0),{
  category:15,jobSlot:2,includedInProductionScan:true,alternateGroupBit:true
 });
 const r=censusColonyWorkforce(c);
 assert.equal(r.categoriesByJob[2][15],1);
});
test("job slot 3 remains explicit and cannot be confused with slot 2",()=>{
 const c=colony(2);pack(c,0,0,3,true);pack(c,1,0,2,true);
 assert.deepEqual(censusColonyWorkforce(c).jobTotals,[0,0,1,1]);
});
test("all low-nibble categories survive; inactive population still counted",()=>{
 const c=colony(16);for(let i=0;i<16;i++)pack(c,i,i,i%4,i%2===0);
 const r=censusColonyWorkforce(c);
 assert.deepEqual(r.categoriesAll,Array(16).fill(1));
 assert.equal(r.participating,8);
 assert.deepEqual(r.jobTotals,[4,0,4,0]);
});
test("record count is bounded before known non-pop fields",()=>{
 const c=colony(55);for(let i=0;i<55;i++)pack(c,i,0,1,true);
 assert.equal(censusColonyWorkforce(c).participating,55);
 c[0x0a]=56;assert.throws(()=>censusColonyWorkforce(c),RangeError);
});
test("invalid index and record format fail closed",()=>{
 const c=colony(1);
 assert.throws(()=>decodePopulationEntry(c,-1),RangeError);
 assert.throws(()=>decodePopulationEntry(c,1),RangeError);
 assert.throws(()=>decodePopulationEntry(c,0.3),RangeError);
 assert.throws(()=>decodePopulationEntry(new Uint8Array(10),0),RangeError);
 assert.throws(()=>censusColonyWorkforce(new Uint8Array(30)),RangeError);
});
