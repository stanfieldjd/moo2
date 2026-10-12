/**
 * Byte-level bridge between known v1.31 colony/planet/race record fields and
 * the verified native per-worker arithmetic primitives.
 *
 * Caller-selected race records must be supplied explicitly. Their selection
 * rules and original Watcom calling conventions are not established here.
 * This is NOT a complete game turn or a save-file loader.
 */
import {foodPerFarmer, industryPerWorker, researchPerScientist} from "./colony-yields.mjs";
import {calculateIndustryTax} from "./colony-tax.mjs";

const PLANET_RECORD_BYTES = 17;
const COLONY_MIN_BYTES = 0x165;
const PRODUCTION_RACE_MIN_BYTES = 0x184;
const TAX_RECORD_MIN_BYTES = 0x32;

function bytes(data, minimum, name) {
  if (!(data instanceof Uint8Array) || data.length < minimum) {
    throw new RangeError(name + " must be a byte array of at least " + minimum + " bytes");
  }
  return data;
}

function readI16(data, offset) {
  const value = data[offset] | data[offset + 1] << 8;
  return value >= 0x8000 ? value - 0x10000 : value;
}
function writeI16(data, offset, value) {
  const word = value & 0xffff;
  data[offset] = word & 0xff;
  data[offset + 1] = word >>> 8;
}

/** Original offset +2 is a signed colony planet-id word, not a byte. */
export function selectPlanet(colonyRecord, planetRecords) {
  bytes(colonyRecord, COLONY_MIN_BYTES, "colonyRecord");
  bytes(planetRecords, PLANET_RECORD_BYTES, "planetRecords");
  const planetId = readI16(colonyRecord, 0x02);
  if (planetId < 0 || !Number.isSafeInteger(planetId * PLANET_RECORD_BYTES)) {
    throw new RangeError("Colony planet id cannot index a verified planet record");
  }
  const start = planetId * PLANET_RECORD_BYTES;
  if (start + PLANET_RECORD_BYTES > planetRecords.length) {
    throw new RangeError("Colony planet id exceeds available planet record data");
  }
  return planetRecords.subarray(start, start + PLANET_RECORD_BYTES);
}

/**
 * Return the three rates with no modification to any caller-supplied record.
 * Values are per-unit primitives, not final food/industry/research totals.
 */
export function colonyProductionRates({colonyRecord,planetRecords,productionRaceRecord}={}) {
  const colony = bytes(colonyRecord,COLONY_MIN_BYTES,"colonyRecord");
  const race = bytes(productionRaceRecord,PRODUCTION_RACE_MIN_BYTES,"productionRaceRecord");
  const planet = selectPlanet(colony,planetRecords);

  const flag013a = colony[0x13a] !== 0;
  return {
    foodDoublePerFarmer:foodPerFarmer({
      planetFoodByte:planet[0x0b],raceByte0134:race[0x134],
      flag013a, flag0164:colony[0x164] !== 0,
    }),
    industryPerWorker:industryPerWorker({
      mineralClass:planet[0x0a],raceByte0183:race[0x183],
      flag013a, flag013d:colony[0x13d] !== 0,
      flag015a:colony[0x15a] !== 0,flag0142:colony[0x142] !== 0,
    }),
    researchPerScientist:researchPerScientist({
      planetModifierByte:planet[0x0f],
      flag013a,flag0154:colony[0x154] !== 0,
      flag0149:colony[0x149] !== 0,flag0159:colony[0x159] !== 0,
    }),
  };
}

/**
 * Reproduce the isolated v1.31 industry-to-tax store and subtraction on a
 * CLONE of the colony record. Returns no turn advancement or player treasury
 * update. The owner tax record is caller-selected.
 */
export function applyIsolatedIndustryTax({colonyRecord,taxOwnerRecord}={}) {
  const colony=bytes(colonyRecord,COLONY_MIN_BYTES,"colonyRecord");
  const owner=bytes(taxOwnerRecord,TAX_RECORD_MIN_BYTES,"taxOwnerRecord");
  const before = readI16(colony,0xe9);
  const result=calculateIndustryTax({
    industry:before, reserved:colony[0xf0],taxRate:owner[0x31],
  });
  const updated=new Uint8Array(colony);
  writeI16(updated,0x127,result.tax);
  writeI16(updated,0xe9,result.industry);
  return {colonyRecord:updated, tax:result.tax, industry:result.industry};
}
