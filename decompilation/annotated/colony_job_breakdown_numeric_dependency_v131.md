# Original v1.31 research breakdown buffer feeds numeric job production

## Provenance and scope

Canonical locally supplied official MicroProse v1.31 `ORION2.EXE` SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Four complete named original bodies are authenticated, along with their exact cross-call instruction anchors:

| Original source function | CODE offset | Complete bytes |
|---|---|---:|
| `Colony_Job_Production_` | `0xCE280` | 996 |
| `Colony_Pop_Base_Prod_Produced_` | `0xCE22C` | 84 |
| `Colony_Empire_Base_Research_Produced_` | `0xCFE77` | 253 |
| `Colony_Research_Per_Scientist_` | `0xCFDC6` | 177 |

All four full-body SHA digests are verified by `tools/audit_colony_job_breakdown_dependency_v131.py`, with source-level machine-code anchors, explicit offset arithmetic, eleven source-derived synthetic checks, and a JSON report at `decompilation/reports/colony_job_breakdown_dependency_v131_2026-10-16.json`. This is an **analyst inference from complete original machine-code instruction paths**, not recovered original C and not a DOS differential measurement.

## Direct cross-function data flow

1. **Initialize temporary breakdown:** `Colony_Job_Production_` sets length EBX to `0x256`, zero in EDX, and the local pointer to `[EBP-0x4D4]` before calling `memset_` at CODE `0xCE3DD`. Thus at this point, the local structure begins with zeros.
2. **Conditionally pass it:** CODE `0xCE3E2–0xCE3F2` tests the original external breakdown pointer at local DWORD `[EBP-0x24]`. If non-null, ECX is assigned the temporary local breakdown pointer; otherwise ECX is cleared. CODE `0xCE3FA` calls the original `Colony_Pop_Base_Prod_Produced_` with ECX intact.
3. **Resolve research helper:** the dispatcher makes a source-original indirect CALL through DATA table `_colony_empire_base_functions` at `0xB55C`; research job selector 2 selects `Colony_Empire_Base_Research_Produced_` at `0xCFE77`. Its CODE `0xCFE8E–0xCFEA3` makes a non-null ECX force the original nested scientist helper and passes ECX to that helper in EBX. The original fastcall argument registers are significant.
4. **Write the optional research planet field:** `Colony_Research_Per_Scientist_` examines the original owning planet BYTE `+0x0F` at CODE `0xCFE42–0xCFE4E`. For source planet code **10**, it adds **2** to its normal return and, **only if EBX is non-null**, executes `ADD DWORD [EBX+0x226],2` at `0xCFE5A`. For planet code **11**, it adds **5** and conditionally executes `ADD DWORD [EBX+0x226],5` at `0xCFE6C`.
5. **Read that field during numeric production:** the original job caller later reads `DWORD [EBP-0x2AE]` at CODE `0xCE467` into the outer breakdown accumulator, and again adds `DWORD [EBP-0x2AE]` to the worker's numeric contribution at CODE `0xCE609`, regardless of whether the temporary pointer was passed to the nested helper. The exact alias is:

   `(EBP - 0x4D4) + 0x226 = EBP - 0x2AE`.

6. **Aggregate and return:** original `0xCE617–0xCE61B` admits only strictly positive worker totals to the aggregate. The final original signed `IDIV` at `0xCE65D` computes `(aggregate + 10) / 20` for job selector 2, truncating toward zero.

The local DWORD at `-0x2AE` is zero after initialization, and in this traced branch can be populated by the scientist helper **only when the original optional reporting pointer is non-null**. The nested helper also adds the 2 or 5 to its normal scalar result in both cases, so this is a separate **second source contribution** through the breakdown buffer, not an assumption that the helper's entire return becomes zero when output is null.

## Controlled synthetic counterexample

The deterministic test intentionally chooses a **hypothetical**, not live-observed, one-population valid-address path: job 2 research, entry job flag true, tag 0 with a different owner, source gravity factor 2, original signed government group 0, no morale/officer/other packed flag bonuses, player BYTE `+0x28 !=100`, setting table index 6 (source signed CODE value +8), source planet gravity code yielding factor 2, and research planet BYTE `+0x0F=10`. Source `Colony_Research_Per_Scientist_` yields base 5 in this fixture.

| Same synthetic inputs | Without output pointer | With output pointer |
|---|---:|---:|
| Research per-pop base | 5 | 5 |
| Temporary breakdown DWORD +0x226 | 0 | 2 |
| Source worker raw numeric contribution | 8 | 10 |
| Signed job final `IDIV((aggregate+10),20)` | **0** | **1** |

For research planet code 11, an analogous synthetic case gives base 8, extra breakdown +5 and final 0 versus 1. For a non-10/11 planet, the same synthetic setup has no difference. The audit includes eleven controlled checks; these **do not constitute actual DOS execution** and cannot establish that all constructed state combinations occur in valid game saves. The result identifies a possible reporting-dependent numeric difference **as implied by the source instruction path**.

## Consequences and correctness rule

Do not silently remove, normalize or duplicate this original-dataflow behavior in the future native reconstruction. The project's rule is to preserve verified original v1.31 gameplay unless a separate defect decision is documented and explicitly authorized. A DOS runtime differential/savegame test and a valid game-state reachability demonstration must precede any conclusion that the observed source dependency is a user-visible bug.

Do not confuse the source DATA table `_colony_empire_base_functions` at `0xB55C` with CODE addresses, or treat optional output as a guaranteed no-op on numeric results. This audit records a **specific source-level proof obligation**; it does not claim that the native remaster, broader executable decompilation, or gameplay behavior is completed.
