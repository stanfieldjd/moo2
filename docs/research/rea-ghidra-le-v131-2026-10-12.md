# REA/Ghidra investigation: MOO2 v1.31 LE game image

## Question, target, and authority

Can REA 6.4.0 use Ghidra 12.1.4 to analyze original Master of Orion II v1.31 gameplay code without executing DOS/4GW?

**Verified answer:** Yes, for bounded analysis windows representing relocated 32-bit LE code. The source is the locally supplied, hash-matching v1.31 ORION2.EXE (2,612,010 bytes, SHA-256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f). The canonical identity and reference analysis originate in the repository's original_v131_probe.json. No original game executable, assets, machine-code images, or decompiled code are committed here.

## Tools and direct evidence

REA MCP server 6.4.0; Ghidra 12.1.4; Eclipse Temurin JDK 21; Linux x64; GNU assembler and linker. The findings are direct observations from REA tools and hash-verified local analysis images. The separate Ghidra analysis snapshot was retained locally, not uploaded.

The relevant reproducible repository tools are:

- tools/original_probe.py
- tools/export_le_objects.py
- tools/relocate_le_v131.py
- tools/build_rea_window.py
- tools/run_tool_tests.sh

For LE record semantics, see [Open Watcom's exeflat.h](https://github.com/open-watcom/open-watcom-v2/blob/master/bld/watcom/h/exeflat.h) and the [LX format specification](https://komh.github.io/os2books/os2tk45/lxref.htm).

## Original image layout and verified hashes

The LE header begins at file offset 168,676. Its page size is 4,096 bytes and its object map has 365 pages. The original entry is object 1, offset 0xfff18, giving preferred address 0x10ff18.

| LE object | Virtual base | Virtual bytes | File-mapped bytes | Raw object SHA-256 |
|---|---:|---:|---:|---|
| 1: code | 0x10000 | 1,410,709 | 1,410,709 | f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837 |
| 2: data/BSS | 0x170000 | 384,208 | 81,920 | c1f592ecdef3538a34bc42957b4c790152de288d4fa2cd85cc47b3668e448856 |

Unmapped data tail: 302,288 zero-filled bytes. Raw object hashes agree with the repository's existing decompilation/le_objects/le_objects.json.

## Relocation evidence

The entire LE fixup table parsed with no unsupported record variants or out-of-bounds source/target offsets.

| Observation | Count |
|---|---:|
| Source type 0x07, internal references | 51,363 |
| Target flag 0x10 | 40,197 |
| Target flag 0x00 | 11,166 |
| Unique source sites | 51,318 |
| Equal cross-page duplicate records | 45 |
| Conflicting targets/overlapping bytes | 0 |

Observed source/target pairs: object 1 to object 2 = 47,351; object 1 to object 1 = 2,950; object 2 to object 2 = 756; object 2 to object 1 = 306.

Relocated object SHA-256:
- Code: d85e5536e7181c3bfd332d43284522448af22fca2133101869e034d8de29be85
- Data: 13158fa46216feb6a3f93ff119c98be99f8ad487191fe4e2bbaffcea79ecb0e0

For example, source code offset 0xd0a1c holds the unrelocated 32-bit value 0x5806; its recorded target is data object 2 plus offset 0x5806, yielding preferred address 0x175806.

## Bounded Ghidra observations

The successful synthetic ELF32 analysis container maps code-object bytes 0xd0000..0xd4000 to virtual 0xe0000..0xe4000, with relocated initialized data at 0x170000. The generated ELF SHA-256 is 36942cf5838cdb36e0fc50cd153f3d190bacf55181782fe15cb4a3fbed970237; the reproducible builder independently generated this exact digest. It contains 55 Watcom function-symbol labels. Its *analysis seed* at 0xe1839 is not the real game's LE entry point.

Direct REA/Ghidra results:

| Symbol | Entry | Body | Observation |
|---|---|---|---|
| Size_And_Climate_Max_Population_ | 0xe0a18 | 49 bytes | Complete assembly and pseudocode; the relocated 0x175806 reference is visible |
| Colony_Pop_Grows_ | 0xe1839 | 1,204 bytes | Complete analyzed function body; direct call resolved to Colony_Race_Pop_Limit_ at 0xe0c1d |

The recovered body extents agree with the earlier Watcom symbol-bounded records. Decompiled pseudocode is not original source, and reconstructed high-level gameplay semantics are not yet independently verified.

A REA snapshot containing two analysis entries (2,526,386 bytes; SHA-256 1b0b6c533b01745fcba7024225bbd05042e72a1dd5ec196ceddb075213ee597f) was saved locally. After closing and reopening the target using the snapshot, the verified relocated function observation was returned without starting a new Ghidra JVM.

## Reproduction and verification

Use a locally held official v1.31 source. Never upload its binaries or generated code images.

    python3 tools/relocate_le_v131.py --self-test
    python3 tools/relocate_le_v131.py "$MOO2_V131_EXE" /tmp/moo2-le-reloc-new
    python3 tools/build_rea_window.py "$MOO2_V131_EXE" /tmp/moo2-le-reloc-new /tmp/moo2-pop-window-new --first-page 208 --page-count 4 --entry-symbol Colony_Pop_Grows_
    MOO2_V131_EXE="$MOO2_V131_EXE" bash tools/run_tool_tests.sh

Both destination folders must be initially absent. The parser fails closed on unexpected fixup kinds, mismatched hashes, conflicting duplicate targets, and invalid source offsets. The builder verifies the exact ELF32 memory-segment addresses, sizes, and content bytes before reporting success. The real-game integration validation and current regression suite passed.

## Alternatives, confidence, and remaining work

The original MZ loader was independently authenticated, but a direct DOS MZ import loads only roughly 62 KB of startup code, not the appended gameplay LE image. Full-object synthetic ELF auto-analysis was resource intensive and was stopped without a completed function result. Bounded analysis with relocations did produce valid function-body results.

An external LX/LE loader is available, but the inspected release targeted a different Ghidra version. It was not installed.

**High confidence:** input identity, object page mapping, extracted bytes, fixup-table coverage, relocation byte patching, synthetic ELF memory mapping, and the two directly observed Ghidra function extents.

**Not yet established:** all game-code coverage, exact Watcom register calling conventions, complete cross-window call resolution, DOS/4GW runtime behavior, or deterministic equivalence of reconstructed gameplay. Subsequent analysis must keep raw observations, inferences, and implementation separate, and add regression evidence before promoting behavior to native code.

No Qwen integration or game-file modification was performed.
