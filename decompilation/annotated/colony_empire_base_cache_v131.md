# Original v1.31 empire-base producer result-cache contract

## Evidence and trust boundaries

Original game SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original extracted Watcom LE CODE SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. The official DOS executable and proprietary assets are **not committed**.

This is a source-byte-verified **static reconstruction** of the cache handling surrounding the already authenticated original per-job base-production helpers. Source verification and 23 synthetic bounded fixtures: `tools/audit_colony_empire_base_cache_v131.py`. Machine-readable originals and complete direct transfer inventories: `decompilation/reports/colony_empire_base_cache_v131_2026-10-16.json`.

| Original Watcom producer | Original CODE | Original body | Source SHA-256 |
|---|---|---:|---|
| `Colony_Empire_Base_Food2_Produced_` | `0xCE0C6` | 358 bytes | `705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2` |
| `Colony_Empire_Base_Industry_Produced_` | `0xCED47` | 212 bytes | `35aa50fa88250f254ba329b69bc8ed99ba7b9d647fe29f1fcffa1e7ecb4c24d8` |
| `Colony_Empire_Base_Research_Produced_` | `0xCFE77` | 253 bytes | `1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9` |

All three complete named bodies are checked by SHA-256, contiguously decoded into 223 original x86 instructions with 56 validated direct control transfers, and checked against 86 exact instruction anchors, including source-cache paths. Nine disassembler continuation rows are incorporated back into their actual instruction starts.

## The three cache records

The three procedures have **independent caches**, each keyed by last colony pointer and one population selector BYTE, and each holding ten data BYTES. Source addresses below refer to the original **Watcom LE DATA** object, *not CODE*. Do not conflate the DATA `0xB568` fields with the original CODE function-pointer table at DATA `0xB55C` — the table ends just before those cache-key fields.

| Source procedure | Previous colony pointer DATA | Previous tag BYTE DATA | Ten-slot cached bytes DATA | Colony's owner base BYTE |
|---|---|---|---|---|
| Food | `0xB568` | `0xB56C` | `0x32358` | `+0xDD` |
| Industry | `0xB56D` | `0xB571` | `0x32362` | `+0xDE` |
| Research | `0xB572` | `0xB576` | `0x3236C` | `+0xDF` |

For valid tag indices **0–9 only**, the original initialization uses `memset_(cache, 99, 10)` to mark all ten slots as not computed. The original checks the **previous colony pointer**, then the **previous selector BYTE**, then the optional component-breakdown pointer:

1. If colony pointer or selector differs from the saved key, the full 10-byte array is reset to 99 and the two keys are updated.
2. If the caller supplies a **non-null breakdown output pointer**, the cache is also reset and the original nested helper is called, even if colony and selector keys match. Component-by-component output cannot be served from a cached scalar alone.
3. Otherwise, if the relevant ten-byte array slot is **not 99**, a cache hit returns the **signed 8-bit** stored result via original `MOVSX AX, BYTE`. This is not a full integer cache.
4. On a miss, source computes nested base production plus original tag-dependent contributions; then stores the **low byte** to the tag slot. The full freshly calculated low WORD remains available on the immediate return path.

**Important limitation:** The source `MOV EAX,[EBP-4]` or `MOV EAX,[EBP-8]` reads a DWORD local whose upper 16 bits are not written in every path by the immediately preceding source instructions. The audit makes only **low-WORD** return assertions for these paths; it does not invent a guaranteed EAX high-half.

A synthetic result of 140 is stored as BYTE `0x8C`, and a later cache hit sign-extends that to AX `0xFF8C` (signed -116). This is a consequence of the original instruction width and **not proof** that such a case occurs during ordinary valid gameplay.

Another edge case is a freshly calculated low BYTE of **99**: its cache slot is indistinguishable from the source sentinel, so the next request recomputes. Again, this is a documented source property, not an observed gameplay defect.

## Distinguishing the three producers

**Food** has a unique early return at CODE `0xCE0FC–0xCE0FF` when the initial signed AX base is nonpositive. It returns before cache-key comparison, cache-array reset, and cache writes. For positive base, tag values 0–7 contribute the original tag-owner player's signed BYTE `+0x8A1`, tag 8 contributes 6, tag 9 contributes 4, and a separate planet/flag-dependent path may add a climate correction. Complete climatic modifier branch semantics are left for separate source analysis. The original base itself is previously traced in `Colony_Food2_Per_Farmer_`.

**Industry** uses tag-indexed player's signed BYTE `+0x8A2` for selectors 0–7, exactly +3 for tag 8, and 0 for tag 9. The original owner-shortcut base is colony BYTE `+0xDE`; otherwise `Colony_Industry_Per_Worker_` is called. It writes tag-specific optional WORD source contributions to the breakdown structure and its scalar low byte to the cache.

**Research** uses tag-indexed player's signed BYTE `+0x8A3` for selectors 0–7, exactly +3 for tag 8, and 0 for tag 9. It has a further +1 original state condition when the population tag matches signed colony owner and that player's BYTE `+0x16B` equals 3. The original owner-shortcut base is colony BYTE `+0xDF`; otherwise `Colony_Research_Per_Scientist_` is called. On a non-null breakdown output it writes a tag-indexed WORD at `+0x04+2*tag` and a DWORD at `+0x22A` to describe the additional +1 condition.

The original shared return tail at CODE `0xCEE10..0xCEE1A` spans the named-function boundary; it is verified in the earlier function-pointer dispatch audit. The industry producer owns its ordinary epilogue while food and research also jump into different points in that tail. The audit permits these verified external branch targets; it does not falsely classify them as missing instructions.

## Evidence classification

The complete code identities, direct branch destinations, invalidation guards, sentinel BYTE, tag cases and conditional write **locations** are source-verified from original machine code. The test model's memory IDs, fixture input values and cache histories are synthetic. No DOS dynamic differential checks, complete game-state lifespan, invalid tag 10+, or native engine parity are claimed. Source-specific planet-climate subbranches in the food producer are not fully reconstructed here. The previous 87% whole-executable estimate remains unrecalculated.
