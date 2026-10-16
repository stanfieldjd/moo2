# MOO2 v1.31 original code-10 home-world colony and worker initialization

## Source and verification

Original MicroProse ORION2.EXE v1.31 SHA-256: 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f. Original Watcom LE CODE SHA-256: f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837. The original executable and proprietary game assets remain outside Git.

Original complete indexed body hashes and function extents were verified for seven named functions: Init_New_Game_ (CODE 0x2479, 801 bytes), Generate_Home_Worlds_ (0x6B8CD, 745), Modify_Home_Worlds_ (0x6C4AF, 576), Init_Homeworld_Colony_ (0x3FA7, 16), Init_Homeworld_Colony2_ (0x3A3D, 1386), Init_Colony_ (0x2D75, 147), and Colony_Job_Production_ (0xCE280, 996).

Reproducible audit: tools/audit_special_homeworld_colony_v131.py. Structured source evidence: decompilation/reports/special_homeworld_colony_v131_2026-10-16.json.

The auditor checks 61 exact original machine instruction anchors and 1,030 source-byte-contiguous decoded instructions across explicitly named scopes, plus five direct original CALL destinations, DATA pointer identities, and 420 bounded controlled assertions. Init_New_Game_ and Init_Colony_ contain sections that the generic linear objdump decoder cannot classify reliably: both have full-function SHA-256 verification, but **only the relevant original CALL-site and colony field-initialization blocks respectively are instruction-decoded in this audit**. This distinction is deliberate, and no complete disassembly coverage is claimed for those two functions.

## Original new-game call route

The original new-game chain is source-authenticated at the machine-code level, against the original direct CALL displacements and the named-function edge index:

1. Init_New_Game_ CODE 0x252A directly calls Generate_Home_Worlds_ CODE 0x6B8CD.
2. Generate_Home_Worlds_ CODE 0x6BB46 directly calls Modify_Home_Worlds_ CODE 0x6C4AF.
3. Modify_Home_Worlds_ CODE 0x6C61F checks player BYTE +0x8AF. When nonzero, CODE 0x6C629 loads the selected planet ID from local WORD [EBP-0x4], and CODE 0x6C635 writes **planet BYTE +0x0F = 10** using DATA global _planet at 0x1B0D4, planet stride 17.
4. Later in the same original procedure, CODE 0x6C697 **reloads that same planet ID from WORD [EBP-0x4]** into EAX, CODE 0x6C69B obtains the home-world owner/player identifier in EDX from a star-record BYTE +0x14, and CODE 0x6C6A3 calls Init_Homeworld_Colony_ CODE 0x3FA7.
5. Init_Homeworld_Colony_ sets EBX=1 at CODE 0x3FA8 and directly calls Init_Homeworld_Colony2_ CODE 0x3A3D at 0x3FB1.
6. Init_Homeworld_Colony2_ obtains an available colony slot, then at CODE 0x3AAC–0x3ABA passes colony slot in EAX, owner/player in EBX, and **the passed planet ID in EDX** to Init_Colony_ CODE 0x2D75.
7. Init_Colony_ first zeroes the new record at original DATA _colony (0x1AB18) using record stride 0x169. At CODE 0x2DB1 it writes the new colony slot into original planet WORD +0x00; CODE 0x2DBA writes planet ID to colony WORD +0x02, and CODE 0x2DBE writes owner BYTE to colony +0x00. It does **not overwrite** planet special +0x0F in these audited operations.

This ties the same selected original planet record carrying code 10 to an actually constructed home-world colony record in the same source control path. It is stronger evidence than only authenticating a planet-code writer.

## Original home-world population and research worker assignment

Original Init_Homeworld_Colony2_ CODE 0x3B0F tests source settings DATA BYTE 0x21CB5 against decimal 2. On the branch for values **other than 2**, original CODE 0x3B9B–0x3BA0 initializes the new colony population count BYTE +0x0A to **8**. On the alternative path, original calculation determines the initial count, but CODE 0x3B71–0x3B77 ensures it is at least **1**; this audit does not assume a fixed count on that alternative branch.

Its population-entry loop begins at CODE 0x3BB5 and loops while the entry index EDI is less than colony BYTE +0x0A (CODE 0x3C6D–0x3C73). The initial colony record was cleared. Each packed entry at colony DWORD +0x0C + 4*i is given:

- Owner/lineage tag **owner player index & 0x0F** in bits 0–3 (CODE 0x3C42–0x3C4C).
- Job selector **bits 7–8**, using one of two original guarded formulas:
  - If planet BYTE +0x0B is nonzero and player BYTE +0x8B1 is zero, CODE 0x3BEB–0x3C02 writes **i mod 3** (food 0, industry 1, research 2).
  - Otherwise CODE 0x3C15–0x3C2F writes **(i mod 2 + 1) & 3** (industry 1, research 2 alternating).
- Participation flag **bit 9**, written by CODE 0x3C62 OR BYTE [entry+1],0x02, after clearing the corresponding old fields.

Those precise packed bits are the ones consumed by original Colony_Job_Production_ CODE 0xCE393 (require bit 9) and CODE 0xCE39F–0xCE3AB (compare bits 7–8 against job selector).

Consequently, **when population count is at least 3**, at least one source-initialized entry is assigned to research job 2 **under either original assignment branch**. In the source branch that sets population count to 8, this condition is necessarily satisfied. It also holds for the alternating branch at count 2 or greater, but **not necessarily** for the i-mod-3 branch at count 1 or 2. The controlled source-fixture tests explicitly limit the cross-branch research guarantee to population count >=3.

## Bounded confidence and remaining obligations

Source-established conditional chain: player option BYTE +0x8AF nonzero -> chosen homeworld planet gets source code 10 -> the same selected planet receives an initialized owned colony -> in the original settings branch initializing eight population entries, this colony contains at least one packed research worker eligible under the production-stage bit filters.

The actual legal game UI setting combinations, colony research player flags, government, signed settings byte, officer/morale state and original DOS numeric outputs have not been established as **a complete single validated save-state witness**. The previous 0-versus-1 difference remains a controlled synthetic demonstration of source dataflow, not a verified original gameplay defect. No gameplay change is made, and no whole-executable completion percentage is recalculated.
