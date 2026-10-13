/**
 * Read-only v1.31 record adapter for the verified uncached empire-production
 * arithmetic and Colony_Pop_Base_Prod_Produced_ minimum-output wrapper.
 *
 * Inputs include an EXPLICIT computed per-worker base amount and climate
 * globals. The original code's cache and race/player selection remain
 * unimplemented. Do not use as a complete colony turn or save transformer.
 */
import {empireFoodBonuses,empireIndustryBonus,empireResearchBonuses,
  combineUncachedEmpireBase} from "./empire-base-bonuses.mjs";
import {applyBaseProductionMinimum} from "./colony-base-production.mjs";

const STRIDE = 0xea9;
const MIN_COLONY = 0xe3;
function sourceBytes(bytes, minimum, name) {
  if (!(bytes instanceof Uint8Array) || bytes.length < minimum) {
    throw new RangeError(name + " requires a Uint8Array with at least " + minimum + " bytes");
  }
  return bytes;
}
function signed8(v) { return (v << 24) >> 24; }

/**
 * Calculate the original arithmetic on the uncached path, plus the minimum
 * returned by Colony_Pop_Base_Prod_Produced_. Never mutates the input.
 *
 * - jobSlot: original 0=food, 1=industry, 2=research
 * - category: original low nibble of the packed population record
 * - computedBaseProduced: signed 16-bit result supplied from the verified
 *   separately reconstructed per-worker primitive or owner fast-path.
 * - raceRecords: original 0xea9-byte records for categories 0..7
 * - climateGlobals: when a matching food climate case actually needs it,
 *   explicit Uint8Array 'table' (indices 0..8) and capA/capB values.
 */
export function inspectUncachedEmpireBase({
  colonyRecord, raceRecords, jobSlot, category, computedBaseProduced,
  climateGlobals,
} = {}) {
  const colony = sourceBytes(colonyRecord, MIN_COLONY, "colonyRecord");
  // Race records must be selected by a future state module; this supplied
  // array is the explicit original 0xea9-stride race table only.
  const races = sourceBytes(raceRecords, STRIDE * 8, "raceRecords");
  if (!Number.isInteger(category) || category < 0 || category > 15) {
    throw new RangeError("population category must fit low nibble");
  }
  if (!Number.isInteger(jobSlot) || jobSlot < 0 || jobSlot > 2) {
    throw new RangeError("only original production jobs 0..2 are valid");
  }
  if (!Number.isInteger(computedBaseProduced) ||
      computedBaseProduced < -32768 || computedBaseProduced > 32767) {
    throw new RangeError("computedBaseProduced must fit signed word");
  }

  let raceBonus=0, specialBonus=0;
  if (jobSlot === 0) {
    if (computedBaseProduced > 0) {
      // The original food function immediately returns before its race
      // bonus computation if the base is nonpositive.
      let globalValues = {};
      if (category < 8 && races[category*STRIDE + 0x8ab] !== 0 &&
          [4,5,6,8].includes(colony[0xe2])) {
        if (!climateGlobals || !(climateGlobals.table instanceof Uint8Array) ||
            climateGlobals.table.length <= colony[0xe2]) {
          throw new RangeError("verified climate table required for this original path");
        }
        globalValues = {
          climateTableByte: climateGlobals.table[colony[0xe2]],
          climateCapA: climateGlobals.capA,
          climateCapB: climateGlobals.capB,
        };
      }
      const options = category < 8 ? {
        raceBonusByte8a1:signed8(races[category*STRIDE + 0x8a1]),
        raceClimateFlag8ab:races[category*STRIDE + 0x8ab] !== 0,
        colonyClimateByteE2:colony[0xe2],
        ...globalValues,
      } : {};
      const result=empireFoodBonuses({category,...options});
      raceBonus=result.raceBonus;specialBonus=result.climateBonus;
    }
  } else if (jobSlot === 1) {
    raceBonus=empireIndustryBonus({
      category,
      ...(category < 8 ? {raceBonusByte8a2:signed8(races[category*STRIDE + 0x8a2])} : {}),
    });
  } else {
    const result=empireResearchBonuses({
      category,
      ...(category < 8 ? {
        raceBonusByte8a3:signed8(races[category*STRIDE + 0x8a3]),
        colonyOwnerCategory:signed8(colony[0]),
        raceByte016b:races[category*STRIDE + 0x16b],
      } : {}),
    });
    raceBonus=result.raceBonus;specialBonus=result.ownerBonus;
  }
  const uncachedProduced=combineUncachedEmpireBase({
    jobSlot,baseProduced:computedBaseProduced,raceBonus,specialBonus,
  });
  const afterMinimum=applyBaseProductionMinimum({
    jobSlot,baseProduced:uncachedProduced,colonyByte00dd:colony[0xdd],
  });
  return {
    jobSlot,category,computedBaseProduced,
    raceBonus,specialBonus,uncachedProduced,
    afterMinimum,
    sourcePath:"uncached-verified-arithmetic-only",
  };
}
