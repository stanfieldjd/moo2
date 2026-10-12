/**
 * Isolated v1.31 Master of Orion II colony production calculations.
 *
 * Source: canonical, SHA-256 verified MicroProse ORION2.EXE:
 *   Colony_Food2_Per_Farmer_      0xDE03E .. 0xDE0C5
 *   Colony_Industry_Per_Worker_   0xDEC95 .. 0xDED46
 *   Colony_Research_Per_Scientist_ 0xDFDC6 .. 0xDFE76
 *
 * Inputs describe original record bytes/flags by offset; they are not
 * guessed building/race names. The optional Watcom EBX breakdown output and
 * surrounding turn/economy state are not implemented here.
 *
 * Validation limits represent our known safe source-data domain; the
 * original executable may read out-of-bounds memory for invalid indices.
 */

export const MINERALS_PER_MINE = Object.freeze([1, 2, 3, 5, 8]);

function byte(value, field) {
  if (!Number.isInteger(value) || value < 0 || value > 255) {
    throw new RangeError(field + " must be an unsigned byte (0..255)");
  }
  return value;
}

function present(value, field) {
  if (typeof value !== "boolean") {
    throw new TypeError(field + " must be a boolean value for an original nonzero flag byte");
  }
  return value;
}

/**
 * Food uses DOUBLE units. A returned 6 therefore represents 3 food,
 * not 6; fractional handling belongs to the future colony-economy state.
 */
export function foodPerFarmer({
  planetFoodByte, raceByte0134,
  flag0164, flag013a,
} = {}) {
  let yieldDouble = byte(planetFoodByte, "planetFoodByte") * 2;
  const raceByte = byte(raceByte0134, "raceByte0134");
  const bonus4 = present(flag0164, "flag0164");
  const bonus2 = present(flag013a, "flag013a");

  // Special race state applies ONLY when base doubled food is zero.
  if (yieldDouble === 0 && raceByte === 3) yieldDouble = 2;
  // Original instruction TEST DX,DX / JLE skips bonuses when nonpositive.
  if (yieldDouble > 0) {
    if (bonus4) yieldDouble += 4;
    if (bonus2) yieldDouble += 2;
  }
  return yieldDouble;
}

/** Industry per worker in whole industry units, using original mineral table. */
export function industryPerWorker({
  mineralClass, raceByte0183,
  flag013a, flag013d, flag015a, flag0142,
} = {}) {
  if (!Number.isInteger(mineralClass) ||
      mineralClass < 0 || mineralClass >= MINERALS_PER_MINE.length) {
    throw new RangeError("mineralClass must be a verified mineral table index 0..4");
  }
  const raceByte = byte(raceByte0183, "raceByte0183");
  const additions = [
    present(flag013a, "flag013a") ? 1 : 0,
    present(flag013d, "flag013d") ? 1 : 0,
    present(flag015a, "flag015a") ? 2 : 0,
    present(flag0142, "flag0142") ? 3 : 0,
  ];
  return MINERALS_PER_MINE[mineralClass] +
    additions.reduce((a, b) => a + b, 0) + (raceByte === 3 ? 1 : 0);
}

/** Research per scientist with the byte at planet record offset +0x0f. */
export function researchPerScientist({
  planetModifierByte,
  flag013a, flag0154, flag0149, flag0159,
} = {}) {
  const special = byte(planetModifierByte, "planetModifierByte");
  const base = 3 +
    (present(flag013a, "flag013a") ? 1 : 0) +
    (present(flag0154, "flag0154") ? 2 : 0) +
    (present(flag0149, "flag0149") ? 3 : 0) +
    (present(flag0159, "flag0159") ? 1 : 0);
  return base + (special === 10 ? 2 : special === 11 ? 5 : 0);
}
