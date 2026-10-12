import test from "node:test";
import assert from "node:assert/strict";
import {calculateIndustryTax,signedWord} from "../colony-tax.mjs";

test("v1.31 verified tax arithmetic fixtures",()=>{
  const cases=[
    [[100,20,25],[20,80]],
    [[50,50,25],[0,50]],
    [[5,10,100],[0,5]],
    [[100,1,33],[32,68]],
    [[100,0,50],[50,50]],
    [[32767,0,100],[32767,0]],
    [[-32768,0,255],[0,-32768]],
    [[100,0,255],[255,-155]],
    [[32767,0,255],[18019,14748]],
  ];
  for(const [[industry,reserved,taxRate],[tax,next]] of cases) {
    const actual=calculateIndustryTax({industry,reserved,taxRate});
    assert.deepEqual(actual,{tax,industry:next});
  }
});
test("16-bit stores wrap exactly as original x86 word operations",()=>{
  assert.equal(signedWord(65535),-1);
  assert.equal(signedWord(65536),0);
  assert.equal(signedWord(32768),-32768);
  assert.equal(signedWord(-32769),32767);
});
test("rejects unsupported input widths instead of guessing",()=>{
  assert.throws(()=>calculateIndustryTax({industry:32768,reserved:0,taxRate:10}),RangeError);
  assert.throws(()=>calculateIndustryTax({industry:-32769,reserved:0,taxRate:10}),RangeError);
  assert.throws(()=>calculateIndustryTax({industry:100,reserved:256,taxRate:10}),RangeError);
  assert.throws(()=>calculateIndustryTax({industry:100,reserved:0,taxRate:300}),RangeError);
  assert.throws(()=>calculateIndustryTax({industry:100.1,reserved:0,taxRate:100}),RangeError);
  assert.throws(()=>calculateIndustryTax(),RangeError);
});
