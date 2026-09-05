# New colonist assignment heuristic — verified v1.31 control flow

Source: official v1.31 `ORION2.EXE`, inside `Apply_Colony_Pop_Growth_`.

This note deliberately retains unknown field names as offsets. It records only control flow visible in the machine code.

## Assignment encoding

The chosen assignment is an integer in the range 0..2 and is written into bits 7-8 of the new four-byte population record (`assignment << 7`). Existing population records are decoded with the reciprocal bit extraction, so the same three assignment classes are used for weighting.

## Decision order

The routine initializes the assignment to `-1` (undecided), then applies the following precedence:

1. If colony byte `+0xDD` is nonzero, evaluate a food-state expression built from bytes `+0xFC..+0xFF` and twice signed word `+0xE7`, plus player/race status fields. Several branches force assignment class **0**. The exact meanings of the status fields are not yet named.
2. If still undecided, compare colony byte `+0xF0` against signed word `+0xE9`. One branch forces assignment class **1**. An equality branch additionally tests a player/race flag and parity of the sum of bytes `+0x100..+0x103`; when satisfied it also chooses class 1.
3. If still undecided, call `Event_Check_Colony_Researching_`. A nonzero result forces assignment class **2**.
4. If still undecided, count the assignment classes of all existing colonists. If there are no existing class-1 or class-2 colonists, choose class **1**. Otherwise zero the class-0 weight and call `Get_Weighted_Choice_Int_` with three weights, choosing between the remaining existing assignment distribution.

The weighted fallback therefore does **not** simply select uniformly among jobs. It derives weights from the colony's current population assignments, excludes class 0 in that fallback, and delegates the final weighted choice to the game's common weighted-choice routine.

## Record creation

After selection the routine clears the new four-byte population record and writes:

- assignment: bits 7-8 from `assignment << 7`;
- population category/race: low nibble from the growth-category index;
- colony owner: encoded from the colony owner byte into the record;
- an additional fixed flag bit in the second record byte.

The record construction is now mechanically separated from the unresolved semantic naming of the preceding policy fields.
