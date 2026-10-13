/**
 * Read-only colony accounting snapshot from verified v1.31 primitives.
 *
 * This is a bridge between isolated native routines. It cannot calculate
 * colony total production or advance a turn: the Watcom production loop's
 * per-colonist race/worker and gravity modifiers remain unresolved.
 *
 * Inputs must identify the relevant production race separately; the engine
 * does not invent an owner-to-race mapping or anomaly/event outcome.
 */
import {censusColonyWorkforce} from "./colony-workforce.mjs";
import {colonyProductionRates} from "./colony-records.mjs";
import {applyColonyMaintenance} from "./colony-maintenance.mjs";

export function inspectColonyEconomy({
  colonyRecord, planetRecords, productionRaceRecord, raceRecords, anomaly,
} = {}) {
  const workforce = censusColonyWorkforce(colonyRecord);
  const perUnitRates = colonyProductionRates({
    colonyRecord, planetRecords, productionRaceRecord,
  });
  const afterMaintenance = applyColonyMaintenance({
    colonyRecord, raceRecords, anomaly,
  });
  return {
    populationCount: workforce.populationCount,
    workforce,
    perUnitRates,
    maintenance: {
      food: afterMaintenance[0xef],
      industry: afterMaintenance[0xf0],
      // Output is a new snapshot buffer, not the caller's live game state.
      colonyRecord: afterMaintenance,
    },
    status: "inspection-only",
  };
}
