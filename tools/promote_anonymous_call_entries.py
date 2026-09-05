#!/usr/bin/env python3
"""Promote high-confidence unnamed direct CALL targets to synthetic function entries.

A direct near CALL target that decodes inside object 1 is an executable entry even
when no Watcom PUBDEF/LPUBDEF survived. Branch-only targets are intentionally not
promoted because they are commonly basic blocks inside named functions.
"""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'decompilation/anonymous_code_entry_candidates.csv'
OUT=ROOT/'decompilation/synthetic_function_entries.csv'
MAN=ROOT/'decompilation/synthetic_function_entries.json'
rows=[]; seen=set()
for r in csv.DictReader(SRC.open()):
    calls=int(r['call_references'])
    if calls < 1: continue
    off=int(r['offset']); seen.add(off)
    rows.append({
        'name':f'anon_call_{off:08X}', 'offset':off, 'offset_hex':f'0x{off:X}',
        'evidence':'direct_call_target', 'call_references':calls,
        'total_references':int(r['references']), 'watcom_symbol':'no'
    })
# Runtime initialization tables are another compiler-proven source of function
# entries even when the target has no surviving PUBDEF/LPUBDEF symbol.
rt=ROOT/'decompilation/runtime_init_targets.csv'
if rt.exists():
    for r in csv.DictReader(rt.open()):
        off=int(r['target_offset'])
        if not off or r.get('named_target')=='1' or off in seen: continue
        seen.add(off)
        rows.append({'name':f'anon_runtime_{off:08X}','offset':off,'offset_hex':f'0x{off:X}',
                     'evidence':'runtime_init_table_target','call_references':0,
                     'total_references':1,'watcom_symbol':'no'})
rows.sort(key=lambda r:r['offset'])
with OUT.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
MAN.write_text(json.dumps({
    'synthetic_function_entries':len(rows),
    'criterion':'decoded object-1 address proven by direct CALL or Watcom runtime init/fini callback table and absent from Watcom CODE globals',
    'excluded':'branch-only targets; these remain CFG/basic-block candidates'
},indent=2)+'\n')
print(MAN.read_text(),end='')
