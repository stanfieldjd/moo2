#!/usr/bin/env python3
import csv,re,json
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
DIS=ROOT/'decompilation/code_object_1.disasm'; FUN=ROOT/'decompilation/functions.csv'
OUT=ROOT/'decompilation/anonymous_code_entry_candidates.csv'; MAN=ROOT/'decompilation/anonymous_code_entry_candidates.json'
rx=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)
tr=re.compile(r'^(?:0x)?([0-9a-f]+)(?:\s|$)',re.I)
ins={}
for line in DIS.open(errors='replace'):
 m=rx.match(line)
 if m: ins[int(m.group(1),16)]=(len(m.group(2).split()),m.group(3).lower(),m.group(4).strip())
rows=list(csv.DictReader(FUN.open())); entries={int(r['offset']):r['name'] for r in rows}
# Direct branch/call destinations not represented by known CODE symbols.
refs=defaultdict(list)
for a,(sz,op,ops) in ins.items():
 if not (op.startswith('call') or op.startswith('j') or op.startswith('loop')): continue
 m=tr.match(ops)
 if not m: continue
 t=int(m.group(1),16)
 if t in ins and t not in entries:
  refs[t].append((a,op))
# Strong candidates: referenced by a call, or by >=2 distinct branch sites.
cands=[]
for t,rs in refs.items():
 calls=sum(op.startswith('call') for _,op in rs); branches=len(rs)-calls
 if calls or len({a for a,_ in rs})>=2:
  cands.append({'offset':t,'offset_hex':hex(t),'references':len(rs),'call_references':calls,'branch_references':branches,'first_ref_hex':hex(min(a for a,_ in rs))})
cands.sort(key=lambda r:(-r['call_references'],-r['references'],r['offset']))
with OUT.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cands[0].keys()); w.writeheader(); w.writerows(cands)
MAN.write_text(json.dumps({'candidate_entries':len(cands),'called_unnamed_entries':sum(c['call_references']>0 for c in cands),'method':'direct call targets or multiply-referenced direct branch targets that decode as instructions but have no Watcom CODE global'},indent=2)+'\n')
print(MAN.read_text(),end='')
