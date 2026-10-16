# Original v1.31 maintenance inputs for worker balancing

The original Pre_Import_Computing_ resets four bytes at colony offsets +0xEF through +0xF2 using the named Watcom memset_ function, then computes maintenance and production. Colony_Industry_Maintenance_ writes BYTE+0xF0. Colony_Food_Maintenance_ writes BYTE+0xEF. Colony_BC_Maintenance_ writes BYTE+0xF2.

On non-anomaly branches, food maintenance calculates the low byte of ceil((counter_FC + counter_FD + counter_FE + counter_FF)/2) and industry maintenance calculates the low byte of ceil((counter_100 + counter_101 + counter_102 + counter_103)/2). The original counters are BYTE-sized, and the original source stores AL, so high synthetic totals can truncate modulo 256. On source anomaly branches the fields are zeroed.

Twiddle_Initial_Homeworld_ reads these food/industry BYTE outputs for comparisons against the corresponding signed food/industry WORD totals; Pass_Out_Imports_ also reads food BYTE+0xEF. This completes direct source writer-to-reader provenance, not a guaranteed final worker distribution.

Auditor: tools/audit_maintenance_rebalance_inputs_v131.py; report: decompilation/reports/maintenance_rebalance_inputs_v131_2026-10-16.json; source annotation: decompilation/annotated/maintenance_rebalance_inputs_v131.md. Canonical original ORION2.EXE SHA-256: 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f. Seven authenticated named bodies, 780 decoded original machine instructions, 61 opcode anchors, eight direct original CALL destinations and 8,200 controlled assertions.

The original DOS game was not executed for comparison. No verified full valid save state, native browser game completion, gameplay changes or revised 87% overall estimate is claimed.
