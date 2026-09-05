#!/usr/bin/env python3
"""Inventory indirect CALL/JMP sites and classify likely switch tables/vtables.

This is deliberately structural: it does not invent targets.  It associates each
site with the recovered function/module owner and records addressing forms so
later decompilers can resolve them systematically.
"""
import csv, json, re, bisect
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIS=(ROOT/'decompilation/code_object_1_resynced.disasm') if (ROOT/'decompilation/code_object_1_resynced.disasm').exists() else ROOT/'decompilation/code_object_1.disasm'
FUN=ROOT/'decompilation/functions.csv'
SYM=ROOT/'decompilation/symbols.csv'
ASM_DIR=ROOT/'decompilation/functions_asm'
OUT=ROOT/'decompilation/indirect_transfers.csv'
MAN=ROOT/'decompilation/indirect_transfers.json'
rx=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)
direct=re.compile(r'^(?:0x)?[0-9a-f]+(?:\s|$)',re.I)
mem_abs=re.compile(r'(?:\[(?:[a-z]{2}:)?(?:0x)?([0-9a-f]+)\]|(?:[DFQ]WORD PTR )?(?:[a-z]{2}:)?0x([0-9a-f]+)$)',re.I)
scale=re.compile(r'\[([^\]]*\*[1248][^\]]*)\]',re.I)
funcs=list(csv.DictReader(FUN.open())); starts=sorted(((int(r['offset']),r) for r in funcs), key=lambda x:x[0]); keys=[x[0] for x in starts]
def owner(a):
 i=bisect.bisect_right(keys,a)-1
 return starts[i][1] if i>=0 else None
# Linker-address -> symbol lookup is useful for absolute pointer slots.
syms=list(csv.DictReader(SYM.open()))
# Restrict the inventory to instructions proven reachable by the per-function CFG
# corpus.  The resynchronized interval disassembly still contains embedded data
# between real instructions; interpreting those bytes as CALL/JMP opcodes creates
# false indirect-transfer sites.
reachable=set()
if ASM_DIR.exists():
 for ap in ASM_DIR.glob('*.asm'):
  for line in ap.open(errors='replace'):
   mm=rx.match(line)
   if mm: reachable.add(int(mm.group(1),16))
rows=[]; forms=Counter(); kinds=Counter(); excluded_unreachable=0
for line in DIS.open(errors='replace'):
 m=rx.match(line)
 if not m: continue
 a=int(m.group(1),16); op=m.group(3).lower(); ops=m.group(4).strip()
 if reachable and a not in reachable:
  if op.startswith('call') or op.startswith('jmp'): excluded_unreachable += 1
  continue
 if not (op.startswith('call') or op.startswith('jmp')) or direct.match(ops): continue
 f=owner(a) or {}
 if scale.search(ops): form='indexed_memory'
 elif mem_abs.search(ops) or '[' in ops: form='memory'
 else: form='register'
 kind='call' if op.startswith('call') else 'jump'
 # Indexed indirect JMP is the strongest switch-table signature on this target.
 likely_switch=(kind=='jump' and form=='indexed_memory')
 rows.append({'site_offset':a,'site_hex':hex(a),'kind':kind,'operand':ops,
              'form':form,'likely_switch':int(likely_switch),
              'function':f.get('name',''),'function_offset':f.get('offset',''),
              'segment':f.get('segment','')})
 forms[form]+=1; kinds[kind]+=1
rows.sort(key=lambda r:r['site_offset'])
with OUT.open('w',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
MAN.write_text(json.dumps({'indirect_transfers':len(rows),'by_kind':dict(kinds),'by_form':dict(forms),
 'likely_switch_sites':sum(r['likely_switch'] for r in rows),'reachable_instruction_addresses':len(reachable),
 'excluded_unreachable_call_jump_decodes':excluded_unreachable,
 'method':'restrict to CFG-reachable per-function corpus, then classify non-immediate CALL/JMP operands; indexed-memory JMPs marked as switch candidates, never assigned speculative targets'},indent=2)+'\n')
print(MAN.read_text(),end='')
