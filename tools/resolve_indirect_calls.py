#!/usr/bin/env python3
"""Resolve statically initialized indirect CALL targets through LE data object 2.

Conservative: only absolute DS dword slots whose on-disk initialized value is an
exact recovered CODE entry are promoted. Zero/BSS/runtime callback slots remain
unresolved rather than guessed.
"""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[1]
IND=ROOT/'decompilation/indirect_transfers.csv'; DATA=ROOT/'decompilation/data_object_2.bin'; FUN=ROOT/'decompilation/functions.csv'
OUT=ROOT/'decompilation/indirect_call_resolutions.csv'; MAN=ROOT/'decompilation/indirect_call_resolutions.json'
mem=re.compile(r'^(?:(DWORD|FWORD) PTR )?ds:0x([0-9a-f]+)$',re.I)
indexed=re.compile(r'^DWORD PTR \[[a-z]{2,3}\*4\+0x([0-9a-f]+)\]$',re.I)
rows=list(csv.DictReader(IND.open())); data=DATA.read_bytes(); code=(ROOT/'decompilation/code_object_1.bin').read_bytes(); funcs=list(csv.DictReader(FUN.open()))
byoff={int(r['offset']):r['name'] for r in funcs}
resolved=[]; symbolic_slots=[]; table_resolved=[]; candidates=0; zero=0; noncode=0; oob=0
syms=list(csv.DictReader((ROOT/'decompilation/symbols.csv').open()))
data_symbol_names={}
for s in syms:
 if int(s['segment'])==2:
  data_symbol_names.setdefault(int(s['offset']),[]).append(s['name'])
for r in rows:
 if r['kind']!='call': continue
 m=mem.match(r['operand'].strip())
 if not m: continue
 candidates+=1; width=m.group(1) or 'DWORD'; slot=int(m.group(2),16)
 names=data_symbol_names.get(slot,[])
 if names:
  symbolic_slots.append({'site_offset':r['site_offset'],'site_hex':r['site_hex'],'function':r['function'],'slot_offset':slot,'slot_hex':hex(slot),'width':width,'slot_symbols':';'.join(names),'classification':'named runtime/static callback slot'})
 if width.upper()!='DWORD':
  continue
 if slot+4>len(data): oob+=1; continue
 val=int.from_bytes(data[slot:slot+4],'little')
 if val==0: zero+=1; continue
 name=byoff.get(val)
 if not name: noncode+=1; continue
 resolved.append({'site_offset':r['site_offset'],'site_hex':r['site_hex'],'function':r['function'],'slot_offset':slot,'slot_hex':hex(slot),'target_offset':val,'target_hex':hex(val),'target':name})
# Export named indirect callback slots separately: knowing the slot identity is
# decompilation progress even when the runtime target is intentionally dynamic.
slot_out=ROOT/'decompilation/indirect_call_slots.csv'
with slot_out.open('w',newline='') as f:
 fields=['site_offset','site_hex','function','slot_offset','slot_hex','width','slot_symbols','classification']
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(symbolic_slots)

# Resolve indexed function-pointer tables only when table shape is independently
# bounded by symbol evidence: a named data symbol's next symbol, or compiler helper
# names whose numeric suffix exactly matches their table index.
data_offsets=sorted(set(int(s['offset']) for s in syms if int(s['segment'])==2))
import bisect
for r in rows:
 if r['kind']!='call': continue
 m=indexed.match(r['operand'].strip())
 if not m: continue
 base=int(m.group(1),16); targets=[]; bound=None; evidence=''
 if base < len(data):
  i=bisect.bisect_right(data_offsets,base); end=data_offsets[i] if i<len(data_offsets) else len(data)
  if end>base and (end-base)%4==0 and end-base<=1024:
   bound=(end-base)//4; blob=data; evidence='next Watcom DATA symbol boundary'
 elif base < len(code):
  # Infer compiler dispatch-table length from exact _PREFIX_N target names.
  blob=code; vals=[]
  for i in range(256):
   v=int.from_bytes(blob[base+4*i:base+4*i+4],'little') if base+4*i+4<=len(blob) else 0
   vals.append(v)
  named=[]
  for i,v in enumerate(vals):
   n=byoff.get(v,''); mm=re.match(r'^(_[A-Za-z]+_)(\d+)$',n)
   if mm and int(mm.group(2))==i: named.append((i,mm.group(1)))
  if named:
   prefix=max(set(x[1] for x in named),key=lambda z:sum(y[1]==z for y in named))
   idx=[i for i,p in named if p==prefix]; mx=max(idx)
   # Watcom helper tables here are power-of-two sized; require several indexed names.
   if len(idx)>=2:
    bound=mx+1; evidence=f'indexed Watcom helper names {prefix}N through {mx}'
 if bound:
  for i in range(bound):
   v=int.from_bytes(blob[base+4*i:base+4*i+4],'little')
   if v in byoff: targets.append((i,v,byoff[v]))
  table_resolved.append({'site_offset':r['site_offset'],'site_hex':r['site_hex'],'function':r['function'],'table_base':base,'table_hex':hex(base),'entries':bound,'nonzero_code_targets':len(targets),'targets':';'.join(f'{i}:{hex(v)}:{n}' for i,v,n in targets),'evidence':evidence})
(ROOT/'decompilation/indirect_call_tables.csv').write_text('site_offset,site_hex,function,table_base,table_hex,entries,nonzero_code_targets,targets,evidence\n'+''.join(','.join('"'+str(x).replace('"','""')+'"' for x in rr.values())+'\n' for rr in table_resolved))

with OUT.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=resolved[0].keys() if resolved else ['site_offset']); w.writeheader(); w.writerows(resolved)
manifest={'indirect_calls':sum(r['kind']=='call' for r in rows),'absolute_ds_slot_candidates':candidates,'named_callback_slot_sites':len(symbolic_slots),'resolved_static_calls':len(resolved),'zero_or_bss_slots':zero,'initialized_noncode_values':noncode,'out_of_bounds_slots':oob,'resolved_indexed_call_sites':len(table_resolved),'true_register_call_sites':sum(r['kind']=='call' and r['form']=='register' for r in rows),'unclassified_indirect_calls':sum(r['kind']=='call' for r in rows)-len(symbolic_slots)-len(table_resolved)-sum(r['kind']=='call' and r['form']=='register' for r in rows),'method':'classify absolute DS callback slots by exact Watcom DATA symbol; resolve initialized DWORD slots only when value exactly matches a recovered CODE entry; classify indexed tables conservatively; never invent runtime callback targets'}
MAN.write_text(json.dumps(manifest,indent=2)+'\n'); print(json.dumps(manifest,indent=2))
