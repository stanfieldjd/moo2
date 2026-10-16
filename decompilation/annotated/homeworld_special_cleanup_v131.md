# Original v1.31 later home-world star-special cleanup, with code-10 exception

## Source authenticity and scope

Official locally supplied original MicroProse v1.31 ORION2.EXE SHA-256: 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f. Extracted original Watcom LE CODE SHA-256: f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837. Original EXE and proprietary game assets are not committed.

tools/audit_homeworld_special_cleanup_v131.py verifies five entire named original function body SHA digests (Init_New_Game_ 801 bytes; Generate_Home_Worlds_ 745; Modify_Home_Worlds_ 576; Twiddle_Initial_Homeworlds_ 693; Twiddle_Initial_Homeworld_ 530). The exact source stage CALLs, original CODE/DATA addresses, 706 contiguous instructions across four complete procedures and two limited new-game CALL spans, 32 selected exact machine-opcode anchors, 769 bounded special-code branch assertions, and the original shared x86 return tail are verified. Machine report: decompilation/reports/homeworld_special_cleanup_v131_2026-10-16.json.

Init_New_Game_ has unsupported generic linear-disassembly regions outside the selected CALL-site spans: its entire source body is SHA-256 checked, but only the two relevant CALL instructions are counted for original instruction coverage.

## New-game stage order and linked special-code writes

Original Init_New_Game_ CODE **0x252A** CALLs Generate_Home_Worlds_ **0x6B8CD**, and **later** at CODE **0x2700** CALLs Twiddle_Initial_Homeworlds_ **0xD5832**. The direct call displacements and linker callgraph agree.

Generate_Home_Worlds_ CODE **0x6BB46** CALLs Modify_Home_Worlds_. When source player BYTE **+0x8AF** is nonzero, this modification procedure writes original **planet BYTE +0x0F = 10** at CODE **0x6C635**, and **star BYTE +0x28 = 10** at CODE **0x6C645**. Original DATA global _planet is at 0x1B0D4 (planet record 17 bytes) and _star at 0x1B06C (star record 113 bytes). The previous homeworld-colony audit established that this path then constructs a colony linked to the same selected planet ID.

Twiddle_Initial_Homeworlds_ loops over existing initialized colony records (original stride 0x169) and directly CALLs Twiddle_Initial_Homeworld_ at CODE **0xD586A**. In the latter procedure, CODE **0xD55F3–0xD5605** resolves its colony planet ID, planet record parent star ID and star record pointer; CODE **0xD570D** loads the selected **star BYTE +0x28** for branch dispatch.

## Original precise star-special cleanup branch partition

The source branch sequence at CODE **0xD5710–0xD572E** splits original unsigned star BYTE +0x28:

- Codes **6 and 7** enter CODE **0xD574E**, clear star BYTE +0x28 and then loop over the star's planet indices, writing **planet BYTE +0x0F = 0** at CODE **0xD5776** for valid linked planets. These are the source planet-special clearing cases.
- Code **10** instead passes original CMP BL,0xA at **0xD5725** and takes original JBE to **0xD57C7** at **0xD5728**. The target writes **star BYTE +0x70 = 1** and jumps to the shared original return tail at CODE **0xD1F98**. It does **not** execute the planet-special clearing loop.
- Codes **2/3** clear the star-special BYTE but do not use the linked-planet clearing loop. Code **8** enters a separate star-special handling path; **9** returns through the shared tail, and codes **11+** likewise take an immediate return. No unsupported semantics are invented for those separate cases.
- Source shared epilogue CODE **0xD1F98–0xD1F9D** has original bytes 5F 5E 5A 59 5B C3 (pop the saved registers and RET), independently checked by this audit.

The generator and later cleanup thus use **the same special-code 10 value**, and the explicit later cleanup switch does **not erase** the special in its code-10 branch. This is a concrete original-machine-code exception, not a generic claim that every helper, corruption path or save edit can never modify that field.

## Limits and remaining evidence

Twiddle_Initial_Homeworld_ also performs substantial **worker-job reallocation and colony recomputation before the special-code switch**; original source initialization of a research worker is not a guarantee that those exact job bits are unchanged after twiddling. The original routine CALLs additional game functions, and their comprehensive side effects were not exhaustively audited in this checkpoint. This does not by itself prove a legal saved-game state simultaneously satisfying all player flags, government, research output and optional reporting conditions of the prior synthetic research discrepancy.

The original executable has not been run under DOS for a differential comparison. No original rule is changed and no whole-executable completion percentage is recomputed.
