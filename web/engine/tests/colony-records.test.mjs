import test from "node:test";
import assert from "node:assert/strict";
import {colonyProductionRates,applyIsolatedIndustryTax,selectPlanet} from "../colony-records.mjs";

function fixture() {
  const colony=new Uint8Array(0x165),planets=new Uint8Array(17*3),
        productionRace=new Uint8Array(0x184),taxOwner=new Uint8Array(0x32);
  // Select planet record 2; leave planet 0/1 poisoned to prove stride+id.
  colony[0x02]=2;planets[0x0a]=255;planets[17+0x0a]=254;
  planets[34+0x0a]=4;planets[34+0x0b]=2;planets[34+0x0f]=11;
  return {colonyRecord:colony,planetRecords:planets,productionRaceRecord:productionRace,taxOwnerRecord:taxOwner};
}
test("record adapter uses signed colony +2 and 17-byte planet-record stride",()=>{
 const f=fixture();
 assert.deepEqual([...selectPlanet(f.colonyRecord,f.planetRecords)].slice(10,12),[4,2]);
 assert.deepEqual(colonyProductionRates(f),{
   foodDoublePerFarmer:4,industryPerWorker:8,researchPerScientist:8,
 });
});
test("all known colony/planet/race fields contribute through exact byte offsets",()=>{
 const f=fixture();
 f.colonyRecord[0x13a]=1;f.colonyRecord[0x13d]=7;
 f.colonyRecord[0x15a]=1;f.colonyRecord[0x142]=1;
 f.colonyRecord[0x154]=1;f.colonyRecord[0x149]=1;f.colonyRecord[0x159]=1;
 f.colonyRecord[0x164]=1;f.productionRaceRecord[0x183]=3;
 assert.deepEqual(colonyProductionRates(f),{
   foodDoublePerFarmer:10,industryPerWorker:16,researchPerScientist:15,
 });
});
test("zero planet food requires race flag for special adjustment",()=>{
 const f=fixture();f.planetRecords[34+0x0b]=0;f.colonyRecord[0x164]=3;
 assert.equal(colonyProductionRates(f).foodDoublePerFarmer,0);
 f.productionRaceRecord[0x134]=3;
 assert.equal(colonyProductionRates(f).foodDoublePerFarmer,6);
});
test("isolated industry tax applies 16-bit writes to cloned colony only",()=>{
 const f=fixture();f.colonyRecord[0xe9]=100;f.colonyRecord[0xf0]=20;f.taxOwnerRecord[0x31]=25;
 const original=new Uint8Array(f.colonyRecord);
 const result=applyIsolatedIndustryTax(f);
 assert.notStrictEqual(result.colonyRecord,f.colonyRecord);
 assert.deepEqual(f.colonyRecord,original);
 assert.deepEqual([result.tax,result.industry],[20,80]);
 assert.equal(result.colonyRecord[0x127],20);
 assert.equal(result.colonyRecord[0xe9],80);
});
test("negative signed industry and insufficient production leave industry unchanged",()=>{
 const f=fixture();f.colonyRecord[0xe9]=0xff;f.colonyRecord[0xea]=0xff;
 f.taxOwnerRecord[0x31]=100;f.colonyRecord[0x127]=200;
 const result=applyIsolatedIndustryTax(f);
 assert.equal(result.industry,-1);assert.equal(result.tax,0);
 assert.equal(result.colonyRecord[0x127],0);assert.equal(f.colonyRecord[0x127],200);
});
test("invalid planet id, class and record sizes are rejected",()=>{
 const f=fixture();f.colonyRecord[0x02]=0xff;f.colonyRecord[0x03]=0xff;
 assert.throws(()=>colonyProductionRates(f),RangeError);
 f.colonyRecord[0x03]=0;f.colonyRecord[0x02]=2;f.planetRecords[34+0x0a]=5;
 assert.throws(()=>colonyProductionRates(f),RangeError);
 f.planetRecords[34+0x0a]=4;f.productionRaceRecord=new Uint8Array(10);
 assert.throws(()=>colonyProductionRates(f),RangeError);
 assert.throws(()=>applyIsolatedIndustryTax({...f,taxOwnerRecord:new Uint8Array(2)}),RangeError);
});
