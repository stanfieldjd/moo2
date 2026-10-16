# Original v1.31 colony empire-base dispatch — resolved function-pointer table

## Verified original source coordinates

The original `Colony_Pop_Base_Prod_Produced_` machine function (CODE `0xCE22C`, 84 bytes, original full-body SHA-256 `964117fde615677bbecb22bd682edf239015961f1ef758b03b67aaec5c0e0661`) performs an **indirect `CALL DWORD PTR [EDI*4+0xB55C]` at CODE `0xCE24E`**. EDI is sign-extended from source BX, which holds the job selector. This is *not* a call into CODE offset `0xB55C`; it is a function-pointer lookup in the **DATA** object.

The named original DATA symbol `_colony_empire_base_functions` starts at DATA `0xB55C`, corroborated by `decompilation/symbols.csv`. Its exact original initialized 12-byte table is `c6e00c0047ed0c0077fe0c00`, SHA-256 `75647e47f704410f38e1a68dfcfee8d47d9af95c90669291aa441d597244b1b9`, read from the authenticated original LE DATA segment. Three little-endian DWORD entries resolve to the following original CODE functions:

| Original selector | DATA table offset | Original CODE target | Original named function | Complete original bytes |
|---|---|---|---|---:|
| **0** | `0xB55C` | `0xCE0C6` | `Colony_Empire_Base_Food2_Produced_` | 358 |
| **1** | `0xB560` | `0xCED47` | `Colony_Empire_Base_Industry_Produced_` | 212 |
| **2** | `0xB564` | `0xCFE77` | `Colony_Empire_Base_Research_Produced_` | 253 |

Every target is exactly a named function start in the original Watcom LE function map and is verified by its complete-body SHA-256 from the authenticated original CODE object. The three target bodies themselves have contiguous static x86 instruction coverage and validated complete direct branch/call targets. The initialized DATA is authenticated as SHA-256 `082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b`; its relocated variant adds the expected module base `0x10000` to the 3 CODE pointers, so these are source-object-relative addresses and not accidental code-looking values.

The source verifier `tools/audit_colony_job_dispatch_v131.py` also verifies two levels of named child callees (the original `Colony_Food2_Per_Farmer_`, `Colony_Industry_Per_Worker_`, `Colony_Research_Per_Scientist_`, and `memset_` full original bodies). The entire evidence and exact direct transfer inventory are in `decompilation/reports/colony_job_dispatch_v131_2026-10-16.json`. No original executable or extracted game binary data files are published.

## Source-observed fallback and shared tail

The indirect target returns a result in AX. `Colony_Pop_Base_Prod_Produced_` then checks signed AX against zero, and may install a local minimum of one if the selector is nonzero or the colony's BYTE `+0xDD` is positive. It compares signed AX to that minimum; when AX falls below the minimum, it jumps to original CODE `0xCEE14` to load the local fallback, otherwise to `0xCEE17` to retain the call result. For valid small signed-domain fixtures, the normal returned low WORD is the greater of the two.

The source common tail at CODE `0xCEE10..0xCEE1A` is shared across named function boundaries; its exact original bytes are `668945fc8b45fcc95f5ec3`. It includes an original `WORD [EBP-4] = AX` entry at `0xCEE10`, a `MOV EAX,[EBP-4]` at `0xCEE14` and the register-restoring return beginning `0xCEE17`. **These are real separate branch targets**, not erroneous single-function-only fallthrough. Their byte identity is verified separately.

## Gravity_Player_Production_Factor_ observed small input domain

The complete source BODY is CODE `0xCDF2C` (167 bytes), SHA-256 `a0660fd4edfd3b57bb91c406ca614e6c445ff509fb191eb5b757bdc254142200`, statically decoded as 52 instructions with 10 direct branches. It reads colony BYTE `+0x14F`, signed population tag DX, owning planet BYTE `+0x06`, and player flag BYTEs `+0x8A9` / `+0x8AA`.

Within the observed **bounded** source gravity index domain 0/1/2 and population tag 0..7:

- If colony BYTE `+0x14F` is nonzero, or tag is at least 8, return **4**.
- For gravity index 0, return **4** if player BYTE `+0x8A9` is set, otherwise **3**.
- For gravity index 1, return **3** if player BYTE `+0x8A9` is set, otherwise **4**.
- For gravity index 2, return **4** if player BYTE `+0x8AA` is set, otherwise **2**.

These outcomes follow exact source branch guards; no gameplay interpretation is inferred for out-of-domain gravity index values or corrupt negative player tags.

## Remaining limitations

This is a **static original-machine-code dispatch resolution** with five fully decoded procedure bodies, named/helper SHA checks, separate CODE/DATA verification, and eight bounded source-derived fixtures. It does not prove the semantics of every food, industry or research empire-base modifier within the three callee functions, and it has not executed the original DOS runtime or established native remaster behavioral equivalence.

Next work: inspect the three specific empire-base routines' operands and nested per-worker/farmer/scientist helper calculations, then close their source state lifecycles and test the original behavior where possible.
