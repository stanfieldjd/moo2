/**
 * Master of Orion II v1.31: colony industry-to-tax arithmetic primitive.
 *
 * Evidence: original, SHA-256-verified ORION2.EXE function
 * Colony_Industry_To_Tax_ at 0xe08f6, 89 bytes.
 * See docs/research/rea-v131-colony-yields.md and
 * tools/test_rea_colony_tax.py.
 *
 * This primitive is a verified arithmetic interpretation of one isolated
 * function, NOT a complete native game turn, ABI or economy implementation.
 */

function integerBetween(value, low, high, field) {
  if (!Number.isInteger(value) || value < low || value > high) {
    throw new RangeError(field + " must be an integer between " + low + " and " + high);
  }
}
export function signedWord(n) {
  if (!Number.isSafeInteger(n)) throw new TypeError("signedWord requires an integer");
  return ((n & 0xffff) ^ 0x8000) - 0x8000;
}

/**
 * @param {object} args
 * @param {number} args.industry signed 16-bit colony industry (+0xe9)
 * @param {number} args.reserved unsigned 8-bit reserved output (+0xf0)
 * @param {number} args.taxRate unsigned 8-bit selected record rate (+0x31)
 * @returns {{tax:number,industry:number}} signed 16-bit stored words
 */
export function calculateIndustryTax({ industry, reserved, taxRate } = {}) {
  integerBetween(industry, -32768, 32767, "industry");
  integerBetween(reserved, 0, 255, "reserved");
  integerBetween(taxRate, 0, 255, "taxRate");
  const surplus = industry - reserved;
  if (surplus <= 0) return { tax: 0, industry };
  // Source instruction sequence: signed IMUL, CDQ, signed IDIV 100.
  // The numerator is positive and fits signed 32-bit for the validated
  // input widths. IDIV truncates toward zero, not bankers' rounding.
  const quotient = Math.trunc((surplus * taxRate) / 100);
  const tax = signedWord(quotient); // 16-bit store at colony +0x127
  return {
    tax,
    industry: signedWord(industry - tax), // 16-bit SUB at colony +0xe9
  };
}
