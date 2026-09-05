# Apply_Colony_Pop_Growth_ — v1.31 reconstruction notes

Source: verified official v1.31 `ORION2.EXE`; function `0001:000D2DCA`, physical file offset `0x16841E`.
Function boundary remains provisional (next recovered CODE symbol).

## Verified mechanics

The routine consumes each population category's signed `pop_grow[10]` value and accumulates it into the corresponding signed `pop_raised[10]` value.

### Population loss

For a category whose `pop_grow` is negative, the routine adds that negative value to `pop_raised`. While the accumulator remains below zero it removes one matching colonist record and adds **1000** back to the accumulator. Thus one colonist is represented by 1000 accumulator units for this transition logic.

When selecting a colonist record to remove, the routine distinguishes record flags (`0x0180`) and uses the original `Random_` routine when multiple eligible records exist. It also decrements the category count maintained on the stack. The routine can emit an `Add_Msg_` notification after losses alter colony output.

### Population gain

For a category whose `pop_grow` is positive, the routine adds it to `pop_raised`. While `pop_raised >= 1000`, it asks `Colony_Race_Pop_Limit_` for that category's carrying limit.

If the colony is below that race/category limit, a new four-byte colonist record is appended, the colony colonist count is incremented, and **1000** is subtracted from `pop_raised` for that category. The new record encodes the population category/race, colony owner bits, and a selected worker assignment.

If the colony cannot accept another colonist at the applicable race limit, the accumulator is clamped to **999**, preserving sub-colonist progress without allowing an over-limit birth.

### New-colonist assignment

The assignment decision is not a fixed default. The routine examines colony food/industry state and player/race status fields. If no forced assignment is selected, it counts existing assignment classes and calls `Get_Weighted_Choice_Int_`; it also calls `Event_Check_Colony_Researching_` in one branch. The final assignment is encoded in bits 7–8 of the new colonist record.

The exact semantic names of every status byte used by the assignment heuristic remain unresolved and are intentionally not guessed here.

## Direct calls resolved from this routine

- `Event_Check_Space_Anomaly_`
- `Random_`
- `memset_`
- `Add_Msg_`
- `Shuffle_Sint_`
- `Colony_Race_Pop_Limit_`
- `Event_Check_Colony_Researching_`
- `Get_Weighted_Choice_Int_`

See `apply_colony_pop_growth.annotated.disasm` for instruction-level call annotations.
