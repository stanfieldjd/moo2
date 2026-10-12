/**
 * Isolated original MOO2 v1.31 colony food and industry maintenance scans.
 *
 * Evidence: independent REA/Ghidra assembly of the verified 32-bit LE image:
 * Colony_Food_Maintenance_     0xDEB4B .. 0xDEC94
 * Colony_Industry_Maintenance_ 0xDF546 .. 0xDF66E
 *
 * Records are original 0x169-byte colony records and race records with
 * stride 0xEA9. Their source pointer resolution and anomaly detection are
 * not reconstructed: the caller must supply the bytes and guard result.
 *
 * No job assignment, turn advancement, colony production or save/load is
 * performed. Returned records are copies; original buffers are not mutated.
 */
export const COLONY_RECORD_SIZE = 0x169;
export const RACE_RECORD_STRIDE = 0xea9;
const POP_START = 0x0c;
const POP_BYTES = 4;
// Prevent population records from overlapping the earliest known downstream
// production field at +0xE9. This is a conservative memory-safety bound,
// NOT an assertion that 55 is the original game's population cap.
const KNOWN_FIRST_NONPOP_FIELD = 0xe9;
const CATEGORY_MASK = 0x0f;
const GROUP_MASK = 1 << 10;

function requireBytes(data, minSize, field) {
  if (!(data instanceof Uint8Array) || data.length < minSize) {
    throw new RangeError(field + " must be a Uint8Array of at least " + minSize + " bytes");
  }
  return data;
}

function validate(colonyRecord, raceRecords, anomaly) {
  const colony = requireBytes(colonyRecord, COLONY_RECORD_SIZE, 'colonyRecord');
  const race = requireBytes(raceRecords, RACE_RECORD_STRIDE * 8, 'raceRecords');
  if (typeof anomaly !== 'boolean') throw new TypeError('anomaly must be a known boolean');
  const count = colony[0x0a];
  if (POP_START + count * POP_BYTES > KNOWN_FIRST_NONPOP_FIELD) {
    throw new RangeError('packed population count exceeds original colony record bounds');
  }
  return { colony, race, count };
}

function addByte(record, offset, amount) {
  record[offset] = (record[offset] + amount) & 0xff;
}

function apply(record, raceRecords, anomaly, kind, count) {
  const food = kind === 'food';
  const output = food ? 0xef : 0xf0;
  const categories = food ? 0x104 : 0x10c;
  const aggregates = food ? [0xfc, 0xfd, 0xfe, 0xff] : [0x100, 0x102, 0x103, 0x101];
  if (anomaly) {
    // Original early-exit branch only clears its final maintenance byte.
    record[output] = 0;
    return;
  }
  record.fill(0, categories, categories + 8);
  for (const at of aggregates) record[at] = 0;
  const signedOwner = record[0] < 128 ? record[0] : record[0] - 256;
  for (let index = 0; index < count; index++) {
    const at = POP_START + index * POP_BYTES;
    // The original uses an unsigned 32-bit packed record, then isolates
    // the low 4 bits and bit 10. No unverified field names are assigned.
    const packed = (record[at] | record[at+1] << 8 |
                    record[at+2] << 16 | record[at+3] << 24) >>> 0;
    const category = packed & CATEGORY_MASK;
    const alternateGroup = (packed & GROUP_MASK) !== 0;
    if (category < 8) {
      const raceAt = category * RACE_RECORD_STRIDE;
      const flagB0 = raceRecords[raceAt + 0x8b0] !== 0;
      const flagB1 = raceRecords[raceAt + 0x8b1] !== 0;
      const weight = food ? (flagB0 ? 1 : flagB1 ? 0 : 2) : (flagB0 ? 1 : 0);
      const aggregate = category === signedOwner ? aggregates[0] :
                        alternateGroup ? aggregates[2] : aggregates[1];
      addByte(record, aggregate, weight);
      addByte(record, categories + category, weight);
    } else if (category === (food ? 9 : 8)) {
      // The two original functions differ: food checks 9, industry checks 8.
      addByte(record, aggregates[3], 2);
    }
  }
  const sum = aggregates.reduce((value, at) => value + record[at], 0);
  // The original adds one then uses signed arithmetic shift, storing AL.
  // With bounded original colony records, sum is nonnegative and <= 110.
  record[output] = (sum + 1) >> 1;
}

/** Return a cloned colony record with original food upkeep counters updated. */
export function applyFoodMaintenance({ colonyRecord, raceRecords, anomaly } = {}) {
  const { colony, race, count } = validate(colonyRecord, raceRecords, anomaly);
  const result = new Uint8Array(colony);
  apply(result, race, anomaly, 'food', count);
  return result;
}

/** Return a cloned colony record with original industry upkeep counters updated. */
export function applyIndustryMaintenance({ colonyRecord, raceRecords, anomaly } = {}) {
  const { colony, race, count } = validate(colonyRecord, raceRecords, anomaly);
  const result = new Uint8Array(colony);
  apply(result, race, anomaly, 'industry', count);
  return result;
}

/** Apply both independently verified scans, without advancing a game turn. */
export function applyColonyMaintenance({ colonyRecord, raceRecords, anomaly } = {}) {
  const food = applyFoodMaintenance({ colonyRecord, raceRecords, anomaly });
  return applyIndustryMaintenance({ colonyRecord: food, raceRecords, anomaly });
}
