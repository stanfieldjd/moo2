# Original Master of Orion II v1.31: 16-bit PD16 video support code

## Source image and segment map

Original official DOS EXE SHA256: 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f. Original extracted Watcom LE CODE image SHA256: f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837.

The original Watcom symbol __VideoBasePD16 at CODE 0x15839D is a mixed 188-byte source span. Its exact SHA256 is 4fc3b2a5781a5ecac7bb49222db60a6217605e951969cacf3ef526ea4ed889d3. The first eight bytes, CODE 0x15839D..0x1583A4, are zero-filled storage. Actual original 16-bit executable code starts at CODE 0x1583A5. The source contains four compact independently terminating RET procedures through CODE 0x158458; CODE 0x158459 is one additional one-byte RET delay helper, immediately preceding the separately audited Greenleaf ISR at CODE 0x15845A.

All **181 original source executable bytes** across those five procedures are re-decoded with i8086 instruction mode, checked contiguously against authenticated original CODE with no gaps or overlaps, and verified against complete SHA256 per routine. There are **104 original 16-bit instructions**. Original direct branches (5), original near helper CALLs (3), and original named opcode/operand anchors (23) are independently asserted in tools/audit_video_pd16_v131.py. Structured result: decompilation/reports/video_pd16_v131_2026-10-16.json.

## 1. Position and video cursor setup, CODE 0x1583A5..0x1583D4

This 48-byte source procedure has 29 original decoded 16-bit instructions and ends in RET. Full body SHA256: 5e4fd6eda38910b842bbdea2774e0d244a1326562119ea9767db2fb73a8d0c39.

The original BP-based frame saves DS/ES and AX/BX/CX/DX, then uses PUSH CS; POP DS to select the routine's source data segment. CODE 0x1583B0 uses LES BX,DWORD PTR DS:0x26D to load an original segment:offset far pointer. CODE 0x1583B4 reads WORD [BP+0x4] into AX, sets CL=0xA0, then MUL CL. CODE 0x1583BD reads a second WORD from [BP+0x6], shifts AX left by one and adds it to BX. This proves arithmetic of first argument times 160 plus second argument times 2, **not** the actual display mode, buffer width or layout of the game screens.

CODE 0x1583C4..0x1583C9 stores ES into original WORD DS:0x273 and BX into WORD DS:0x271. The adjacent WORDs thus hold the far cursor pointer. Original registers are restored, ending RET at 0x1583D4.

## 2. Single-byte video write, CODE 0x1583D5..0x1583FB

This 39-byte source procedure has 22 original 16-bit instructions and ends in RET. Full SHA256 c648095e9df03e070e13a56f8285b87b39cedfb72af0c0a1993856440c25d3d2.

It loads the saved far ES:BX pointer through LES BX,DWORD PTR DS:0x271 at CODE 0x1583DE. CODE 0x1583E4 compares ES with zero. If ES is nonzero, the source reads the caller's WORD argument at [BP+0x4], stores AL through **MOV BYTE PTR ES:[BX],AL** at CODE 0x1583EC, increments BX by **2** at 0x1583EF, and saves the updated cursor WORD through DS:0x271 at 0x1583F2. If ES is zero, the source branches from 0x1583E7 directly to 0x1583F6 to restore registers. The pointer stride suggests an interleaved storage convention, but does **not** prove a specific hardware screen mode.

## 3. NUL-terminated character sequence, CODE 0x1583FC..0x15841F

This 36-byte source routine contains 24 original 16-bit instructions, ending RET at CODE 0x15841F. SHA256 a3125eb2a69f505a63a6225de72e8101d63a54b564c35c8801abde5dd8485096.

The routine saves its BP/segment/register context, reads the caller's pointer from WORD [BP+0x4] into BX, sets DS=CS, then reads **MOV AL,BYTE PTR [BX]** at CODE 0x158408. It terminates on zero AL via original source branch **0x15840C -> 0x15841A**, otherwise pushes the character, executes original relative **CALL 0x1583D5** from CODE 0x158411, balances two stack bytes, advances BX, and jumps **0x158418 -> 0x158408**. This is directly source-confirmed string iteration and character-output dispatch, without making assumptions about Unicode, font or the modern web client.

## 4. Two hexadecimal output characters, CODE 0x158420..0x158458

This 57-byte procedure contains 28 original real-mode instructions, ends RET at CODE 0x158458, and hashes to 1804b85a0e0dc3e4581c929fc3a93ae6c765e5f519d323abd632a48e43e6ea6d.

From the caller's WORD at [BP+0x4], the source shifts AL right four times, masks AX with 0x000F, adds ASCII '0' and, when above '9', adds seven more to form the original hex letter. It passes the result to the original byte writer via CODE **0x15843B CALL 0x1583D5**. Next it masks the original input WORD's lower four bits and repeats the same ASCII transformation, outputting via **0x158450 CALL 0x1583D5**. Original conditional branch pairs are **0x158436->0x15843A** and **0x15844B->0x15844F**. The actual source uses AL/AX arithmetic, not any presumed high-level printf formatting library.

## 5. One-byte delay/return helper, CODE 0x158459

Source byte C3 (RET). Full one-byte SHA256 ae3f4619b0413d70d3004b9131c3752153074e45725be13b9a148978895e359e. The original separate Greenleaf ISR source used this helper as the target of four near CALLs; this audit checks its original byte directly and records it as the fifth tiny contiguous source unit. No hardware timing is claimed from its RET instruction.

## Implications and limitations

Before this work the legacy global analyzer attempted to decode original CODE symbol __VideoBasePD16 as a 32-bit function, encountering an initial zero-filled header and inappropriate 32-bit decoding of its 16-bit routines. That was a tool model problem, not proof of missing underlying native MOO2 game logic. The new **104 original 16-bit instructions** are separately verified, **not added** to the global 32-bit CFG's 396,305 membership records. Combining them would conflate two instruction domains and produce a misleading completion statistic.

These source routines are internal real-mode video support and may be used by the runtime; source names and bytes alone do not establish all callers, display hardware assumptions, original DOS execution frequency, or browser game behavior. The native final Game Lab implementation must use its own compatible graphics pipeline and cannot rely on DOS interrupts or protected proprietary game assets at runtime. Original DOS parity, complete gameplay reconstruction, and modern browser/controller delivery remain outstanding.
