import test from 'node:test';
import assert from 'node:assert/strict';
import {
  COLONY_RECORD_SIZE, RACE_RECORD_STRIDE, applyFoodMaintenance,
  applyIndustryMaintenance, applyColonyMaintenance,
} from '../colony-maintenance.mjs';

const colony = () => new Uint8Array(COLONY_RECORD_SIZE);
const races = () => new Uint8Array(8 * RACE_RECORD_STRIDE);
function pack(record, index, category, alternate = false) {
  const at = 0x0c + 4 * index;
  const value = category | (alternate ? 1 << 10 : 0);
  record[at] = value & 0xff;
  record[at+1] = (value >>> 8) & 0xff;
  record[at+2] = (value >>> 16) & 0xff;
  record[at+3] = (value >>> 24) & 0xff;
}
function flag(race, category, at, enabled = true) {
  race[category * RACE_RECORD_STRIDE + at] = enabled ? 1 : 0;
}

test('original population records are four bytes; bit 10 splits non-owner aggregates', () => {
  const c = colony(), r = races();
  c[0] = 1; c[0x0a] = 4;
  pack(c,0,1);pack(c,1,2,false);pack(c,2,3,true);pack(c,3,0,false);
  flag(r,1,0x8b0); // 1 food, 1 industry
  flag(r,2,0x8b1); // 0 food, 0 industry
  // race 3 default 2 food, 0 industry; race 0 default 2 food.
  const f = applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.deepEqual([...f.slice(0xfc,0x100)],[1,2,2,0]);
  assert.deepEqual([...f.slice(0x104,0x108)],[2,1,0,2]);
  assert.equal(f[0xef],3); // ceil((1+0+2+2)/2)
  const i = applyIndustryMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.deepEqual([...i.slice(0x100,0x104)],[1,0,0,0]);
  assert.deepEqual([...i.slice(0x10c,0x110)],[0,1,0,0]);
  assert.equal(i[0xf0],1);
});

test('food has special category 9; industry has special category 8 (not vice versa)', () => {
  const c = colony(), r = races(); c[0x0a]=2;
  pack(c,0,8);pack(c,1,9);
  const f = applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  const i = applyIndustryMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.equal(f[0xff],2);assert.equal(f[0xef],1);
  assert.equal(i[0x101],2);assert.equal(i[0xf0],1);
  assert.deepEqual([...f.slice(0x104,0x10c)],Array(8).fill(0));
  assert.deepEqual([...i.slice(0x10c,0x114)],Array(8).fill(0));
});

test('race byte b0 wins over b1 in food, and b1 alone makes zero-food weight', () => {
  const c=colony(),r=races();c[0x0a]=3;pack(c,0,1);pack(c,1,2);pack(c,2,3);
  flag(r,1,0x8b0);flag(r,1,0x8b1);flag(r,2,0x8b1);
  const out=applyColonyMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.equal(out[0x105],1);assert.equal(out[0x106],0);assert.equal(out[0x107],2);
  assert.equal(out[0xef],2);
  assert.equal(out[0xf0],1);
});

test('anomaly guard clears only the maintenance output bytes, not old counters', () => {
  const c=colony(),r=races();c[0x0a]=1;pack(c,0,1);
  c.fill(217,0xfc,0x104);c.fill(37,0x104,0x114);c[0xef]=23;c[0xf0]=29;
  const out=applyColonyMaintenance({colonyRecord:c,raceRecords:r,anomaly:true});
  assert.equal(out[0xef],0);assert.equal(out[0xf0],0);
  assert.deepEqual([...out.slice(0xfc,0x114)],[...c.slice(0xfc,0x114)]);
  assert.deepEqual([...c.slice(0xef,0xf1)],[23,29]);
});

test('native aggregate counters are recomputed on copies, original remains unchanged', () => {
  const c=colony(),r=races();c[0x0a]=1;c[0]=0;pack(c,0,0);
  c[0xfc]=9;c[0x100]=21;c[0x104]=99;c[0xef]=88;
  const before=new Uint8Array(c);
  const out=applyColonyMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.notStrictEqual(out,c);assert.deepEqual(c,before);
  assert.equal(out[0xef],1);assert.equal(out[0xf0],0);
  assert.equal(out[0xfc],2);assert.equal(out[0x104],2);
  assert.equal(out[0x100],0);assert.equal(out[0x10c],0);
});

test('all 16 categories are accounted for and only documented specials contribute', () => {
  const c=colony(),r=races();c[0x0a]=16;
  for(let i=0;i<16;i++)pack(c,i,i);
  const f=applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  const j=applyIndustryMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.equal(f[0xef],9); // 8 * 2 plus category 9 * 2
  assert.equal(j[0xf0],1); // only category 8 * 2
  assert.equal(f[0xff],2);assert.equal(j[0x101],2);
});

test('packed count and byte arrays fail closed before out-of-bounds access', () => {
  const c=colony(),r=races();
  c[0x0a]=56;
  assert.throws(()=>applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false}),RangeError);
  assert.throws(()=>applyIndustryMaintenance({colonyRecord:c,raceRecords:r,anomaly:true}),RangeError);
  c[0x0a]=0;
  assert.throws(()=>applyColonyMaintenance({colonyRecord:c,raceRecords:new Uint8Array(4),anomaly:false}),RangeError);
  assert.throws(()=>applyColonyMaintenance({colonyRecord:new Uint8Array(14),raceRecords:r,anomaly:false}),RangeError);
  assert.throws(()=>applyColonyMaintenance({colonyRecord:c,raceRecords:r}),TypeError);
});

test('conservative known-field boundary permits 55 but rejects 56 overlapping records', () => {
  const c=colony(),r=races();
  c[0x0a]=55;
  for(let i=0;i<55;i++)pack(c,i,0);
  const food=applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.equal(food[0xef],55);
  c[0x0a]=56;
  assert.throws(()=>applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false}),RangeError);
});

test('signed owner byte and unrelated packed high bits are handled explicitly', () => {
  const c=colony(),r=races();c[0]=0xff;c[0x0a]=1;pack(c,0,0,false);
  c[0x0c+3]=0xf0; // add unrelated upper packed bits
  const f=applyFoodMaintenance({colonyRecord:c,raceRecords:r,anomaly:false});
  assert.equal(f[0xfc],0);assert.equal(f[0xfd],2);
  assert.equal(f[0x104],2);assert.equal(f[0xef],1);
});
