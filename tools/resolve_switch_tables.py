#!/usr/bin/env python3
"""Resolve compiler switch jump tables using local bounds-check patterns.

Recognizes the Watcom idiom `cmp index,N; ja default; ...; jmp cs:[index*4+TABLE]`.
Only emits a table when every dword entry is a decoded code address.  This keeps
recovery evidence-based and also identifies embedded data that must not be decoded
as instructions.
"""
import csv,json,re,bisect
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIS=(ROOT/'decompilation/code_object_1_resynced.disasm') if (ROOT/'decompilation/code_object_1_resynced.disasm').exists() else ROOT/'decompilation/code_object_1.disasm'; BIN=ROOT/'decompilation/code_object_1.bin'
IND=ROOT/'decompilation/indirect_transfers.csv'; OUT=ROOT/'decompilation/switch_tables.csv'; TARGETS=ROOT/'decompilation/switch_targets.csv'; MAN=ROOT/'decompilation/switch_tables.json'
rx=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)
jtab=re.compile(r'(?:cs:)?\[([a-z][a-z0-9]*)\*4\+(?:0x)?([0-9a-f]+)\]',re.I)
jtab_prescaled=re.compile(r'(?:cs:)?\[([a-z][a-z0-9]*)\+(?:0x)?([0-9a-f]+)\]',re.I)
shl4=re.compile(r'^([a-z][a-z0-9]*),0x?2$',re.I)
cmpi=re.compile(r'^([a-z][a-z0-9]*),0x([0-9a-f]+)$',re.I)
movx=re.compile(r'^(?:movzx|movsx)\s+([a-z][a-z0-9]*),([a-z][a-z0-9]*)$',re.I)
reg_family={'eax':'eax','ax':'eax','al':'eax','ah':'eax','ebx':'ebx','bx':'ebx','bl':'ebx','bh':'ebx','ecx':'ecx','cx':'ecx','cl':'ecx','ch':'ecx','edx':'edx','dx':'edx','dl':'edx','dh':'edx','esi':'esi','si':'esi','edi':'edi','di':'edi','ebp':'ebp','bp':'ebp','esp':'esp','sp':'esp'}
def norm_operand(x):
 x=re.sub(r'^(?:BYTE|WORD|DWORD|FWORD|QWORD) PTR ','',x.strip(),flags=re.I)
 return x.replace(' ','').lower()
def dep_key(x):
 x=norm_operand(x)
 return reg_family.get(x,x)
def split2(x):
 p=x.split(',',1); return (norm_operand(p[0]),norm_operand(p[1])) if len(p)==2 else (None,None)
ins=[]; byaddr={}
for line in DIS.open(errors='replace'):
 m=rx.match(line)
 if m:
  rec=(int(m.group(1),16),len(m.group(2).split()),m.group(3).lower(),m.group(4).strip())
  byaddr[rec[0]]=rec; ins.append(rec)
addrs=[x[0] for x in ins]; blob=BIN.read_bytes(); rows=[]; trows=[]; rejected=0
candidates=None
if IND.exists():
 ind_rows=list(csv.DictReader(IND.open()))
 candidates={int(r['site_offset']) for r in ind_rows if r.get('kind')=='jump'}
for idx,(a,sz,op,ops) in enumerate(ins):
 if not op.startswith('jmp'): continue
 if candidates is not None and a not in candidates: continue
 jm=jtab.search(ops); prescaled=False
 if not jm:
  jm=jtab_prescaled.search(ops)
  if jm:
   # Unscaled CS:[reg+table] is a switch only when this exact register was
   # multiplied by four in the local dispatch sequence.
   reg0=jm.group(1).lower()
   for q in range(idx-1,max(-1,idx-10),-1):
    if ins[q][2]=='shl':
     sm=shl4.match(ins[q][3].replace(' ',''))
     if sm and sm.group(1).lower()==reg0:
      prescaled=True; break
   if not prescaled: jm=None
 if not jm: continue
 reg=jm.group(1).lower(); table=int(jm.group(2),16)
 # Recover the value feeding the dispatch register by slicing MOV/MOVZX/MOVSX
 # chains backward, including simple stack spills. This handles Watcom idioms
 # where an index is widened, copied, or spilled before being scaled by four.
 tracked={dep_key(reg)}
 bound=None; cmp_addr=None; guard=None
 for p in range(idx-1,max(-1,idx-35),-1):
  pa,psz,pop,pops=ins[p]
  if pop in {'mov','movzx','movsx'}:
   dst,src=split2(pops)
   if dst and dep_key(dst) in tracked:
    tracked.add(dep_key(src))
  if pop=='cmp':
   lhs,rhs=split2(pops)
   if lhs and rhs and dep_key(lhs) in tracked and re.fullmatch(r'0x[0-9a-f]+|[0-9]+',rhs,re.I):
    # Require an unsigned upper-bound guard shortly after this comparison.
    for q in range(p+1,min(idx,p+7)):
     if ins[q][2] in {'ja','jnbe'}:
      guard=ins[q][2]; break
    if guard:
     bound=int(rhs,0); cmp_addr=pa; break
 # Watcom also emits sparse switches as a linear key scan followed by a
 # dispatch indexed by the remaining ECX count:
 #   mov ecx,N; mov edi,keys; repnz scas[b/w/d]; jmp [ecx*4+table]
 # In this form the jump table has exactly N entries and no cmp/ja guard.
 scan_count=None; scan_addr=None
 if bound is None:
  for p in range(idx-1,max(-1,idx-12),-1):
   if ins[p][2].startswith('repnz') or ins[p][2].startswith('repne'):
    # objdump may render `repnz scas` as mnemonic+operand or a combined mnemonic.
    for q in range(p-1,max(-1,p-6),-1):
     qa,qsz,qop,qops=ins[q]
     dst,src=split2(qops)
     if qop=='mov' and dst and dep_key(dst)=='ecx' and src and re.fullmatch(r'0x[0-9a-f]+|[0-9]+',src,re.I):
      scan_count=int(src,0); scan_addr=qa; break
    if scan_count is not None: break
 if bound is None and scan_count is None:
  rejected+=1; continue
 if bound is not None and (not guard or bound>4095):
  rejected+=1; continue
 count=(bound+1) if bound is not None else scan_count
 if not count or count>4096:
  rejected+=1; continue
 if table<0 or table+count*4>len(blob): rejected+=1; continue
 targets=[int.from_bytes(blob[table+i*4:table+i*4+4],'little') for i in range(count)]
 if not all(t in byaddr for t in targets): rejected+=1; continue
 rows.append({'site_offset':a,'site_hex':hex(a),'index_register':reg,
              'bound_source_hex':hex(cmp_addr if cmp_addr is not None else scan_addr),
              'dispatch_evidence':'cmp/ja' if bound is not None else 'repnz-scan',
              'max_index':bound if bound is not None else count-1,'entry_count':count,'table_offset':table,'table_hex':hex(table),
              'table_end_hex':hex(table+count*4),'unique_targets':len(set(targets))})
 for i,t in enumerate(targets): trows.append({'site_hex':hex(a),'case_index':i,'target_offset':t,'target_hex':hex(t)})
with OUT.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys() if rows else ['site_offset']); w.writeheader(); w.writerows(rows)
with TARGETS.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=trows[0].keys() if trows else ['site_hex']); w.writeheader(); w.writerows(trows)
MAN.write_text(json.dumps({'resolved_switch_tables':len(rows),'resolved_case_entries':len(trows),
 'unique_case_targets':len({r['target_offset'] for r in trows}),'unresolved_indexed_jumps':rejected,
 'reachable_indirect_jump_candidates':len(candidates) if candidates is not None else None,
 'method':'CFG-reachable indirect JMP + bounded Watcom cmp/ja + either indexed CS:[reg*4+table] or locally proven prescaled CS:[reg+table]; all table entries required to land on decoded instruction starts'},indent=2)+'\n')
print(MAN.read_text(),end='')
