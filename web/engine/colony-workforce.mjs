/**
 * MOO2 v1.31 packed workforce census, extracted from the original
 * Colony_Job_Production_ x86 record scan at 0xDE376..0xDE3B9.
 *
 * Original instructions:
 *  - four-byte records begin at colony+0x0c; colony+0x0a is count
 *  - TEST BYTE PTR [record+1],0x02 at 0xDE393 skips records without bit 9
 *  - SHL EDX,0x17; SHR EDX,0x1e at 0xDE39F/0xDE3A6 gets bits 7..8
 *  - AND EAX,0x0f at 0xDE3B3 gets the low-nibble category
 *
 * "Participates in this production scan" is what bit 9 proves; do not
 * infer employment, citizenship or a playable turn from these records.
 * Job slot 3 is retained as a distinct unclassified slot, not silently
 * assigned to farmers, workers, or scientists.
 */
export const WORKFORCE_COLONY_MIN_BYTES = 0x169;
export const WORKFORCE_SLOT_BYTES = 4;
export const WORKFORCE_RECORD_OFFSET = 0x0c;
export const WORKFORCE_KNOWN_NONPOP_START = 0xe9;
export const WORKFORCE_JOB_SLOTS = 4;

function validate(colony) {
  if (!(colony instanceof Uint8Array) || colony.length < WORKFORCE_COLONY_MIN_BYTES) {
    throw new RangeError("colonyRecord must be a complete Uint8Array record");
  }
  const count = colony[0x0a];
  // The known non-pop field +0xe9 bounds our validated layout. This is
  // a conservative defensive limit, not an established in-game pop cap.
  if (WORKFORCE_RECORD_OFFSET + count * WORKFORCE_SLOT_BYTES >
      WORKFORCE_KNOWN_NONPOP_START) {
    throw new RangeError("packed population exceeds verified record area");
  }
  return count;
}

export function decodePopulationEntry(colonyRecord, index) {
  const count = validate(colonyRecord);
  if (!Number.isInteger(index) || index < 0 || index >= count) {
    throw new RangeError("population index out of bounds");
  }
  const at = WORKFORCE_RECORD_OFFSET + index * WORKFORCE_SLOT_BYTES;
  const packed = (colonyRecord[at] | colonyRecord[at+1] << 8 |
                  colonyRecord[at+2] << 16 | colonyRecord[at+3] << 24) >>> 0;
  return {
    category: packed & 0x0f,
    jobSlot: (packed >>> 7) & 3,
    includedInProductionScan: (packed & 0x200) !== 0,
    alternateGroupBit: (packed & 0x400) !== 0,
  };
}

/** Pure census, no source mutation and no total production calculation. */
export function censusColonyWorkforce(colonyRecord) {
  const count = validate(colonyRecord);
  const jobTotals = [0, 0, 0, 0];
  const categoriesByJob = Array.from({length: WORKFORCE_JOB_SLOTS}, () =>
    Array(16).fill(0));
  const categoriesAll = Array(16).fill(0);
  let participating = 0;
  for (let index=0; index<count; index++) {
    const at = WORKFORCE_RECORD_OFFSET + index * WORKFORCE_SLOT_BYTES;
    const packed = (colonyRecord[at] | colonyRecord[at+1] << 8 |
                    colonyRecord[at+2] << 16 | colonyRecord[at+3] << 24) >>> 0;
    const category = packed & 0x0f;
    categoriesAll[category]++;
    if ((packed & 0x200) === 0) continue;
    const job = (packed >>> 7) & 3;
    participating++;
    jobTotals[job]++;
    categoriesByJob[job][category]++;
  }
  return {
    populationCount: count,
    participating,
    skipped: count - participating,
    jobTotals,
    categoriesAll,
    categoriesByJob,
  };
}
