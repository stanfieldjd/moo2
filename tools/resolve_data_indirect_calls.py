#!/usr/bin/env python3
"""Resolve direct DS absolute indirect calls whose initialized pointer is in LE object 2."""
import csv,json,re,bisect
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
IND=ROOT/'decompilation/indirect_transfers.csv'; DATA=ROOT/'decompilation/le_objects/object_2.bin'; FUN=ROOT/'decompilation/functions.csv'
out=ROOT/'decompilation/resolved_data_indirect_calls.csv'; man=ROOT/'decompilation/resolved_data_indirect_calls.json'
mem=re.compile(r'^(?:DWORD|FWORD) PTR ds:0x([0-9a-f]+)$',re.I)
data=DATA.read_bytes(); funcs=list(csv.DictReader(FUN.open())); byoff={int(r['offset']):r['name'] for r in funcs}; starts=sorted(byoff)
def sym(v):
    # Stored callback values use the same object-relative CODE address space
    # as the recovered Watcom segment-1 symbols and disassembly VMAs.
    off=v
    return off,byoff.get(off,'')
rows=[]; candidates=0; initialized=0
for r in csv.DictReader(IND.open()):
    if r['kind']!='call': continue
    m=mem.match(r['operand'])
    if not m: continue
    candidates+=1; slot=int(m.group(1),16)
    if slot+4>len(data): continue
    v=int.from_bytes(data[slot:slot+4],'little')
    if not v: continue
    initialized+=1; off,name=sym(v)
    rows.append({'site_hex':r['site_hex'],'function':r['function'],'slot_hex':hex(slot),'initial_value_hex':hex(v),'target_offset_hex':hex(off) if off>=0 else '','target_symbol':name,'exact_symbol':int(bool(name))})
if rows:
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
exact=sum(int(r['exact_symbol']) for r in rows)
man.write_text(json.dumps({'absolute_ds_call_sites':candidates,'initialized_slots':initialized,'resolved_exact_code_symbols':exact,'rows':len(rows),'method':'read initialized DWORD from reconstructed LE object 2; interpret initialized callback value in recovered segment-1 code address space; require exact recovered CODE symbol'},indent=2)+'\n')
print(man.read_text(),end='')
