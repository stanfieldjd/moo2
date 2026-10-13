/**
 * Master of Orion II v1.31: uncached per-category empire production bonuses.
 *
 * Evidence: original executable instructions of
 *   Colony_Empire_Base_Food2_Produced_       0xDE0C6..0xDE22B
 *   Colony_Empire_Base_Industry_Produced_    0xDED47..0xDEE1A
 *   Colony_Empire_Base_Research_Produced_    0xDFE77..0xDFF73
 *
 * These functions model ONLY the uncached arithmetic branch reached after
 * original per-worker base computation. Cached signed-byte results,
 * cache invalidation, calling-convention outputs and full colony
 * production are not represented.
 */
export const EMPIRE_BASE_BONUS_JOB_NAMES = Object.freeze(["food", "industry", "research"]);

function categoryIndex(value) {
  if (!Number.isInteger(value) || value < 0 || value > 15) {
    throw new RangeError("population category must be 0..15");
  }
  return value;
}
function signedByte(value, field) {
  if (!Number.isInteger(value) || value < -128 || value > 127) {
    throw new RangeError(field + " must be a signed byte");
  }
  return value;
}
function unsignedByte(value, field) {
  if (!Number.isInteger(value) || value < 0 || value > 255) {
    throw new RangeError(field + " must be an unsigned byte");
  }
  return value;
}

/**
 * Category bonuses to doubled-food output. For categories 0..7, the
 * original checks race byte +0x8a1 and flag +0x8ab, with colony +0xe2
 * selecting which externally configured climate cap to use. The caller
 * supplies those source bytes explicitly; no unverified lookup is done.
 */
export function empireFoodBonuses({
  category,
  raceBonusByte8a1, raceClimateFlag8ab,
  colonyClimateByteE2, climateTableByte, climateCapA, climateCapB,
} = {}) {
  const index = categoryIndex(category);
  if (index === 8) return { raceBonus: 6, climateBonus: 0 };
  if (index === 9) return { raceBonus: 4, climateBonus: 0 };
  if (index > 9) return { raceBonus: 0, climateBonus: 0 };

  const raceBonus = signedByte(raceBonusByte8a1, "raceBonusByte8a1");
  if (typeof raceClimateFlag8ab !== "boolean") {
    throw new TypeError("raceClimateFlag8ab must be an explicit boolean");
  }
  const climate = unsignedByte(colonyClimateByteE2, "colonyClimateByteE2");
  let climateBonus = 0;
  if (raceClimateFlag8ab && (climate === 4 || climate === 5 ||
                               climate === 6 || climate === 8)) {
    const table = unsignedByte(climateTableByte, "climateTableByte");
    const cap = (climate === 4 || climate === 6)
      ? unsignedByte(climateCapA, "climateCapA")
      : unsignedByte(climateCapB, "climateCapB");
    climateBonus = (cap - table) * 2;
  }
  return { raceBonus, climateBonus };
}

/** Category bonus to industry, raw race byte at original +0x8a2. */
export function empireIndustryBonus({category, raceBonusByte8a2} = {}) {
  const index = categoryIndex(category);
  if (index === 8) return 3;
  if (index > 8) return 0;
  return signedByte(raceBonusByte8a2, "raceBonusByte8a2");
}

/**
 * Category bonus to research, raw race byte at +0x8a3.
 * The +1 condition additionally requires current category to equal
 * the signed colony-owner byte and race byte +0x16b to equal 3.
 */
export function empireResearchBonuses({
  category, raceBonusByte8a3, colonyOwnerCategory, raceByte016b,
} = {}) {
  const index = categoryIndex(category);
  if (index === 8) return { raceBonus: 3, ownerBonus: 0 };
  if (index > 8) return { raceBonus: 0, ownerBonus: 0 };
  const raceBonus = signedByte(raceBonusByte8a3, "raceBonusByte8a3");
  const owner = signedByte(colonyOwnerCategory, "colonyOwnerCategory");
  const raceStatus = unsignedByte(raceByte016b, "raceByte016b");
  return {
    raceBonus,
    ownerBonus: (index === owner && raceStatus === 3) ? 1 : 0,
  };
}

/**
 * Original base-output arithmetic before the byte-sized global cache.
 * Food returns directly without bonus when its computed base <= 0.
 * x86 ADD word wraps to a signed 16-bit value.
 */
export function combineUncachedEmpireBase({
  jobSlot, baseProduced, raceBonus, specialBonus = 0,
} = {}) {
  if (!Number.isInteger(jobSlot) || jobSlot < 0 || jobSlot > 2) {
    throw new RangeError("only original job slots 0..2 are dispatchable");
  }
  if (!Number.isInteger(baseProduced) || baseProduced < -32768 || baseProduced > 32767) {
    throw new RangeError("baseProduced must be a signed 16-bit integer");
  }
  if (!Number.isInteger(raceBonus) || raceBonus < -128 || raceBonus > 127) {
    throw new RangeError("raceBonus must be a signed race or special-category bonus");
  }
  if (!Number.isInteger(specialBonus) || specialBonus < -510 || specialBonus > 510) {
    throw new RangeError("specialBonus outside verified climate bonus bound");
  }
  if (jobSlot === 0 && baseProduced <= 0) return baseProduced;
  const total = (baseProduced + raceBonus + specialBonus) & 0xffff;
  return (total ^ 0x8000) - 0x8000;
}
