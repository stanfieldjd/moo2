/**
 * Synthetic navigation fixtures for exercising source-verified v1.31
 * per-worker yield primitives. NOT a galaxy generator, save-game parser,
 * complete economy, turn simulation, or claim of in-game values.
 */
import {foodPerFarmer,industryPerWorker,researchPerScientist} from "../../../../engine/colony-yields.mjs";

export const LAB_SYSTEMS = Object.freeze([
  Object.freeze({name:"Beacon", coordinate:[13,25], foodByte:2, mineralClass:1, researchModifier:0}),
  Object.freeze({name:"Lyra", coordinate:[41,11], foodByte:3, mineralClass:2, researchModifier:10}),
  Object.freeze({name:"Vesper", coordinate:[70,38], foodByte:1, mineralClass:4, researchModifier:0}),
  Object.freeze({name:"Aster", coordinate:[24,69], foodByte:4, mineralClass:0, researchModifier:11}),
  Object.freeze({name:"Helion", coordinate:[79,79], foodByte:0, mineralClass:3, researchModifier:0}),
]);
export function stepSystem(index, direction) {
  if (!Number.isInteger(index) || index < 0 || index >= LAB_SYSTEMS.length ||
      (direction !== 1 && direction !== -1)) throw new RangeError("Invalid system navigation");
  return (index + direction + LAB_SYSTEMS.length) % LAB_SYSTEMS.length;
}
export function inspectFixture(index, enhanced=false) {
  if (!Number.isInteger(index) || index < 0 || index >= LAB_SYSTEMS.length ||
      typeof enhanced !== "boolean") throw new RangeError("Invalid inspection");
  const source = LAB_SYSTEMS[index];
  const bonus = enhanced;
  return {
    source,
    foodDouble: foodPerFarmer({
      planetFoodByte:source.foodByte,raceByte0134:0,
      flag0164:false,flag013a:bonus,
    }),
    industry: industryPerWorker({
      mineralClass:source.mineralClass,raceByte0183:0,
      flag013a:bonus,flag013d:false,flag015a:false,flag0142:false,
    }),
    research: researchPerScientist({
      planetModifierByte:source.researchModifier,
      flag013a:bonus,flag0154:false,flag0149:false,flag0159:false,
    }),
  };
}
