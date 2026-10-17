# Original v1.31 mixed-mode runtime: 16-bit instruction reconstruction

## Canonical source

Original ORION2.EXE SHA-256: 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f.
Original Watcom LE CODE SHA-256: f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837.
The original DOS CODE object is 1,410,709 bytes. Proprietary original binaries and assets remain local, not committed.

Source-verifying audit: tools/audit_mixed_mode_runtime_v131.py.
Structured report: decompilation/reports/mixed_mode_runtime_v131_2026-10-16.json.

The original source contains 16-bit real-mode routines inside an object otherwise mostly decoded as 32-bit Watcom x86. We use GNU objdump in i8086 instruction mode only for the exactly authenticated 16-bit function extents. Both function bodies are independently authenticated by full source SHA-256, exactly decoded instruction boundaries, and exact correspondence with original CODE bytes. This preserves rather than contaminates the existing 32-bit global CFG.

## Original Greenleaf real-mode interrupt handler

Name: __GreenleafFastRealIsr. CODE: 0x15845A..0x1584C1 inclusive, 104 bytes.
Full body SHA-256: 719f4b010de4b496843c030c66fbf1ec1408a44fda55a46d2a4eff3722e13609.
Contiguous original 16-bit instructions: 45. Last instruction RETF (0xCB) at 0x1584C1.

The source saves BP, DS, SI, constructs a BP/SP frame and loads a far input pointer with LDS SI,DWORD PTR [BP+6] at 0x15845F.

Original machine CODE operations:
- 0x158462 loads DX=WORD [SI+0x0E], an I/O port offset.
- 0x158465–0x15846D computes WORD[SI+0x12] - WORD[SI+0x16] into CX and, when negative, adds 0x400.
- 0x158471–0x158475 reads hardware status through IN AL,DX at port DX+5, then calls original helper at 0x158459. That helper's exact original byte is RET (0xC3). The same helper is called four times.
- 0x15847B ORs the status into BYTE[SI+0x1E]. The source AND AL,1 followed by JE distinguishes an input-ready branch from a flow-control branch.
- 0x158482 reads a data byte from the underlying DX port. The source compares CX with 0x03FF; if not full, source 0x15848F stores AL to [SI+BX+0x3A], using BX=WORD[SI+0x12]. Source 0x158492 increments that WORD and 0x158495 masks it with 0x03FF. This proves a 10-bit circular index, without proving accessible ring capacity in all original runtime states.
- Original 0x15849D..0x1584B2 checks count against 0x0300 and conditionally reads a second I/O port at DX+4, applies bit masking from WORD[SI+0x22] and writes with OUT DX,AL.
- Source 0x1584B5 loads the next far pointer via LDS SI,DWORD PTR [SI+0x06], checks whether segment:offset is zero and otherwise continues through the linked records. It restores saved state and finishes with RETF.

Authenticated direct branch sites and targets: 0x15846B->0x158471, 0x158480->0x15849D, 0x15848A->0x158471, 0x15849B->0x158471, 0x1584A1->0x1584B5, 0x1584BC->0x158462. Near direct helper calls: 0x158475, 0x158483, 0x1584A7 and 0x1584B2, all with source-encoded target 0x158459.

Bounded reconstructed algorithm (not an original-DOS runnable replacement):

    state = input far pointer
    for each original far-linked state record:
        port = state.word[0x0E]
        count = state.word[0x12] - state.word[0x16]
        if count < 0: count += 1024
        repeat:
            status = IN(port+5); invoke original delay helper
            state.byte[0x1E] |= status
            if status & 1:
                byte = IN(port); invoke delay helper
                if count >= 1023: continue
                idx = state.word[0x12]
                state.byte[0x3A+idx] = byte
                state.word[0x12] = (idx+1) & 0x3FF
                count += 1
                continue
            if count > 768:
                ctrl = IN(port+4); invoke delay helper
                OUT(port+4, ctrl & ~(state.word[0x22] & 0xFF))
                invoke delay helper
            break
        state = original far-linked next record
        if null: exit
    restore BP/DS/SI and RETF

Hardware IRQ timing, device I/O, packet validity, relocation and dynamic parity remain untested.

## Original real-mode interrupt dispatcher

Name: __RealDispatcherRR16. CODE 0x1584FE..0x15853A inclusive, 61 bytes.
Full body SHA-256: 8dc35022433ecbaff7b4bc23e2e9ff1dcaa909420bbdf3d3f53c85cb84adf61d.
Contiguous original 16-bit instructions: 36. Terminator IRET (0xCF) at 0x15853A.

The original dispatcher saves BX,CX,DX,SI,DI,BP,ES,DS and loads DS from CS. It computes a DS-relative pointer based on AX, increments WORD[SI+0x3A] and pushes two original WORDs [SI+0x1C] and [SI+0x1A]. The source CALL DWORD PTR [SI+0x10] at 0x158517 is an indirect FAR callback with unknown dynamic target; no address has been invented.

After the callback, the source restores the 4-byte parameter stack space, loads AL=0x20 and conditionally issues OUT DX,AL to two original I/O ports specified by [SI+0x2E] and [SI+0x2A]. It restores registers and uses IRET, not RET. Authentic short branch sites and destinations are 0x158525->0x158528 and 0x15852E->0x158531.

## Distinguishing CODE-object data from executable code

Original CODE symbol _Alphabet at CODE 0x134942 is exactly 37 bytes, the NUL-terminated radix lookup string:

    0123456789abcdefghijklmnopqrstuvwxyz\0

The source instruction at 0x13498F has original machine bytes 2E 8A 92 42 49 13 00, reading byte CS:[EDX+0x134942] into DL. This is direct source proof that the 37-byte CODE-object symbol is a lookup table, not a real code routine. Treating its ASCII letters as 32-bit x86 instructions creates four fake conditional jumps in the global 32-bit CFG.

## Boundaries and limitations

81 complete authenticated 16-bit original instructions, eight direct source branch addresses, four direct helper CALL targets, and 20 exact named opcodes are checked against original x86 bytes. The mode-specific 16-bit routines and lookup data were not injected into, or used to inflate, the previous 32-bit CFG inventory. Baseline remains 396,138 CFG instruction memberships and 21 apparent unresolved edges under its **32-bit-only** decoder.

Among the 21, four 32-bit unresolved edges arise in the true 16-bit routines and four in the _Alphabet data table. These are identified sources of the residual discrepancy, but this audit does not claim that all other 13 unresolved edges are executable branches. Additional mode- and data-aware reconciliation of startup markers, runtime IRQ buffers and source data is still required.

The recovered interrupt behavior is not validated against live DOS runtime, and it is not a native browser port or completed gameplay implementation. Previous informal 87/88% semantic estimates remain unverified.
