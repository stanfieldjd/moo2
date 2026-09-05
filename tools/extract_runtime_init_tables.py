#!/usr/bin/env python3
"""Recover Watcom runtime init/fini callback tables from __InitRtns/__FiniRtns.

These routines iterate fixed-size 6-byte records in LE data object 2 and invoke
record+2 as a function pointer. The table bounds are embedded as immediate DS
addresses in the runtime routines, so targets can be recovered without guessing.
"""
from pathlib import Path
import csv, json, re
ROOT=Path(__file__).resolve().parents[1]
DEC=ROOT/'decompilation'
FUN=DEC/'functions.csv'; DIS=DEC/'code_object_1_resynced.disasm'; DATA=DEC/'data_object_2.bin'
OUT=DEC/'runtime_init_tables.csv'; TOUT=DEC/'runtime_init_targets.csv'; MAN=DEC/'runtime_init_tables.json'
rx=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)
imm_mov=re.compile(r'^([a-z]{2,3}),0x([0-9a-f]+)$',re.I)
funcs=list(csv.DictReader(FUN.open()))
byname={r['name']:r for r in funcs}; byoff={int(r['offset']):r['name'] for r in funcs}
ins=[]
for line in DIS.open(errors='replace'):
 m=rx.match(line)
 if m:
  op=m.group(3).lower(); ops=m.group(4).strip()
  if op in {'ds','cs','es','ss'} and ' ' in ops:
   op,ops=ops.split(None,1); op=op.lower()
  ins.append((int(m.group(1),16),op,ops))
data=DATA.read_bytes(); tables=[]; targets=[]
for fname in ('__InitRtns','__FiniRtns'):
 r=byname.get(fname)
 if not r: continue
 start=int(r['offset']); end=int(r['inferred_end'])
 body=[x for x in ins if start<=x[0]<end]
 starts=[]; ends=[]; has_step=False; has_indirect=False
 for a,op,ops in body:
  if op=='mov':
   mm=imm_mov.match(ops.replace(' ',''))
   if mm and mm.group(1).lower()=='esi': starts.append((a,int(mm.group(2),16)))
   if mm and mm.group(1).lower()=='edi': ends.append((a,int(mm.group(2),16)))
  if op=='add' and ops.replace(' ','').lower()=='esi,0x6': has_step=True
  if op.startswith('call') and ops.strip().lower()=='eax': has_indirect=True
 if not (starts and ends and has_step and has_indirect):
  continue
 # The loop re-loads ESI/EDI each iteration; use the recurring table bounds.
 table_start=starts[0][1]; table_end=ends[0][1]
 if table_end<=table_start or (table_end-table_start)%6 or table_end>len(data): continue
 count=(table_end-table_start)//6
 tables.append({'function':fname,'function_offset':start,'table_start':table_start,'table_start_hex':hex(table_start),'table_end':table_end,'table_end_hex':hex(table_end),'record_size':6,'records':count,'evidence':'immediate ESI/EDI bounds + add esi,6 + call eax'})
 for i,off in enumerate(range(table_start,table_end,6)):
  state=data[off]; priority=data[off+1]; target=int.from_bytes(data[off+2:off+6],'little')
  targets.append({'function':fname,'record_index':i,'record_offset':off,'record_hex':hex(off),'state':state,'priority':priority,'target_offset':target,'target_hex':hex(target),'target_symbol':byoff.get(target,''),'named_target':int(target in byoff)})
with OUT.open('w',newline='') as f:
 fields=list(tables[0]) if tables else ['function']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(tables)
with TOUT.open('w',newline='') as f:
 fields=list(targets[0]) if targets else ['function']; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(targets)
MAN.write_text(json.dumps({'tables':len(tables),'records':len(targets),'named_targets':sum(x['named_target'] for x in targets),'unnamed_targets':sum(not x['named_target'] for x in targets),'method':'recover fixed 6-byte Watcom init/fini records from immediate runtime loop bounds'},indent=2)+'\n')
print(MAN.read_text(),end='')
