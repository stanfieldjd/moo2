/**
 * Verified post-dispatch minimum for v1.31 Colony_Pop_Base_Prod_Produced_.
 *
 * Official x86 function at 0xDE22C (84-byte symbol interval).
 * Dispatch table at preferred 0x17B55C:
 *   job 0 -> Colony_Empire_Base_Food2_Produced_
 *   job 1 -> Colony_Empire_Base_Industry_Produced_
 *   job 2 -> Colony_Empire_Base_Research_Produced_
 *   job 3 -> null (not a dispatchable production job).
 *
 * This function deliberately accepts an already computed signed 16-bit
 * base rate. It does NOT model the three called empire-production routines.
 * Its result describes the low signed 16-bit word (AX), not an invented
 * full 32-bit Watcom return ABI.
 */
export const VERIFIED_PRODUCTION_JOB_NAMES = Object.freeze([
  "food", "industry", "research",
]);

export function applyBaseProductionMinimum({
  jobSlot, baseProduced, colonyByte00dd,
} = {}) {
  if (!Number.isInteger(jobSlot) || jobSlot < 0 || jobSlot > 2) {
    throw new RangeError("jobSlot must select the original non-null dispatch entries 0..2");
  }
  if (!Number.isInteger(baseProduced) || baseProduced < -32768 ||
      baseProduced > 32767) {
    throw new RangeError("baseProduced must fit signed 16-bit AX");
  }
  if (!Number.isInteger(colonyByte00dd) || colonyByte00dd < 0 ||
      colonyByte00dd > 255) {
    throw new RangeError("colonyByte00dd must be an unsigned byte");
  }
  if (baseProduced > 0) return baseProduced;
  const floor = jobSlot !== 0 || colonyByte00dd !== 0 ? 1 : 0;
  return baseProduced < floor ? floor : baseProduced;
}
