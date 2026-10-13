/**
 * Temporary synthetic colony laboratory, NOT a reconstructed colony turn.
 * Record offsets and inspectors come from the verified v1.31 native modules.
 * No original game data, images, save files or game assets are included.
 */
import {inspectColonyEconomy} from "../../../../engine/colony-economy-inspect.mjs";
import {decodePopulationEntry} from "../../../../engine/colony-workforce.mjs";
import {LAB_SYSTEMS} from "./model.mjs";

const COLONY_BYTES = 0x169;
const RACE_STRIDE = 0xea9;
const PLANET_BYTES = 17;
const JOB_SHIFT = 7;
const JOB_MASK = 3 << JOB_SHIFT;
export const JOB_LABELS = Object.freeze(["Food", "Industry", "Research", "Unclassified"]);

function indexOfFixture(index) {
  if (!Number.isInteger(index) || index < 0 || index >= LAB_SYSTEMS.length)
    throw new RangeError("Fixture index out of range");
  return index;
}

export function makeColonyFixture(index) {
  const system = LAB_SYSTEMS[indexOfFixture(index)];
  const colonyRecord = new Uint8Array(COLONY_BYTES);
  const planetRecords = new Uint8Array(PLANET_BYTES);
  const productionRaceRecord = new Uint8Array(0x184);
  const raceRecords = new Uint8Array(8 * RACE_STRIDE);
  const populationCount = 4 + (index % 3);
  colonyRecord[0] = 0; // Explicit synthetic owner category
  colonyRecord[0x02] = 0; colonyRecord[0x03] = 0; // Synthetic planet index 0
  colonyRecord[0x0a] = populationCount;
  planetRecords[0x0a] = system.mineralClass;
  planetRecords[0x0b] = system.foodByte;
  planetRecords[0x0f] = system.researchModifier;
  for (let i = 0; i < populationCount; i++) {
    const slot = i % 3;
    const packed = (0x200 | (slot << JOB_SHIFT)) >>> 0;
    const at = 0x0c + 4*i;
    for (let byte = 0; byte < 4; byte++)
      colonyRecord[at + byte] = (packed >>> (byte*8)) & 0xff;
  }
  return {colonyRecord,planetRecords,productionRaceRecord,raceRecords,anomaly:false};
}

/** Assign a synthetic packed job slot on a CLONE. Not the game's employment algorithm. */
export function assignFixtureJob(fixture, person, jobSlot) {
  if (!fixture || !(fixture.colonyRecord instanceof Uint8Array))
    throw new TypeError("Fixture colony record required");
  const count = fixture.colonyRecord[0x0a];
  if (!Number.isInteger(person) || person < 0 || person >= count)
    throw new RangeError("Population index out of bounds");
  if (!Number.isInteger(jobSlot) || jobSlot < 0 || jobSlot > 2)
    throw new RangeError("Only verified production job slots 0, 1 and 2 may be assigned");
  // Read and validate through the original workforce decoder first.
  decodePopulationEntry(fixture.colonyRecord, person);
  const colonyRecord = new Uint8Array(fixture.colonyRecord);
  const at = 0x0c + 4*person;
  const word = (colonyRecord[at] | colonyRecord[at+1]<<8 |
    colonyRecord[at+2]<<16 | colonyRecord[at+3]<<24) >>> 0;
  const revised = ((word & ~JOB_MASK) | (jobSlot << JOB_SHIFT)) >>> 0;
  for (let byte=0;byte<4;byte++)
    colonyRecord[at+byte] = (revised >>> (byte*8)) & 0xff;
  return {...fixture,colonyRecord};
}

export function inspectFixtureColony(fixture, person) {
  if (!fixture || !(fixture.colonyRecord instanceof Uint8Array))
    throw new TypeError("Fixture required");
  const personInfo = decodePopulationEntry(fixture.colonyRecord, person);
  const view = inspectColonyEconomy(fixture);
  return {
    populationCount: view.populationCount,
    participating: view.workforce.participating,
    skipped: view.workforce.skipped,
    jobTotals: [...view.workforce.jobTotals],
    foodUpkeep: view.maintenance.food,
    industryUpkeep: view.maintenance.industry,
    personInfo,
    perUnitRates: view.perUnitRates,
    status: view.status,
  };
}
