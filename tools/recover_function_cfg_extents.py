#!/usr/bin/env python3
"""Recover conservative function extents from direct x86 control flow.

Starts only at known Watcom CODE symbols. Calls are not followed. Direct branches
are followed unless they land on another known function entry. This deliberately
produces conservative extents: indirect jumps and undecodable instructions end a
path rather than guessing.
"""
import csv, json, re
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIS=(ROOT/'decompilation/code_object_1_resynced.disasm') if (ROOT/'decompilation/code_object_1_resynced.disasm').exists() else ROOT/'decompilation/code_object_1.disasm'
FUN=ROOT/'decompilation/functions.csv'
OUT=ROOT/'decompilation/function_cfg_extents.csv'
MAN=ROOT/'decompilation/function_cfg_extents.json'
MEM=ROOT/'decompilation/function_cfg_membership.csv'

# addr: bytes mnemonic operands
rx=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)
target_rx=re.compile(r'^(?:0x)?([0-9a-f]+)(?:\s|$)',re.I)
ins={}
for line in DIS.open(errors='replace'):
    m=rx.match(line)
    if not m: continue
    addr=int(m.group(1),16); nbytes=len(m.group(2).split())
    ins[addr]=(nbytes,m.group(3).lower(),m.group(4).strip())

rows=list(csv.DictReader(FUN.open()))
# Merge compiler-proven synthetic entries (direct CALL targets and runtime
# init/fini callback targets) so they participate in CFG recovery instead of
# remaining outside the decompilation corpus.
synth=ROOT/'decompilation/synthetic_function_entries.csv'
if synth.exists():
    existing={int(r['offset']) for r in rows}
    for sr in csv.DictReader(synth.open()):
        off=int(sr['offset'])
        if off in existing: continue
        rows.append({'name':sr['name'],'offset':str(off),'inferred_end':'0','inferred_size':'0',
                     'module_index':'-1','kind':'4'})
        existing.add(off)
# Recompute provisional next-entry boundaries over the combined entry set.
combined=sorted({int(r['offset']) for r in rows})
next_entry={o:(combined[i+1] if i+1<len(combined) else (ROOT/'decompilation/code_object_1.bin').stat().st_size)
            for i,o in enumerate(combined)}
for r in rows:
    off=int(r['offset']); r['inferred_end']=str(next_entry[off]); r['inferred_size']=str(next_entry[off]-off)
rows.sort(key=lambda r:(int(r['offset']),r['name']))
entries={int(r['offset']):r['name'] for r in rows}
sorted_entries=sorted(entries)
import bisect
def provisional_owner(addr):
    i=bisect.bisect_right(sorted_entries,addr)-1
    return sorted_entries[i] if i>=0 else None
code_size=(ROOT/'decompilation/code_object_1.bin').stat().st_size
switch_targets={}
st=ROOT/'decompilation/switch_targets.csv'
if st.exists():
    for rr in csv.DictReader(st.open()): switch_targets.setdefault(int(rr['site_hex'],16),[]).append(int(rr['target_offset']))

def direct_target(ops):
    m=target_rx.match(ops)
    return int(m.group(1),16) if m else None

def successors(addr, rec, own_entry):
    size,op,ops=rec; fall=addr+size
    if addr in switch_targets: return switch_targets[addr]
    if op.startswith('ret') or op in {'iret','iretd','hlt','ud2'}:
        return []
    if op.startswith('call'):
        return [fall]
    if op=='jmp' or op.startswith('jmp'):
        t=direct_target(ops)
        return [t] if t is not None else []
    if (op.startswith('j') and op not in {'jmp'}) or op.startswith('loop'):
        t=direct_target(ops)
        return ([fall] if t is None else [fall,t])
    return [fall]

results=[]; memberships=[]; exact=extended=truncated=ambiguous=0
for r in rows:
    start=int(r['offset']); provisional=int(r['inferred_end'])
    if start not in ins:
        results.append({**r,'cfg_min':start,'cfg_end':start,'reachable_instructions':0,'status':'no_entry_decode','foreign_entry_edges':0,'shared_tail_edges':0,'unresolved_edges':1})
        ambiguous+=1; continue
    q=deque([start]); seen=set(); foreign=0; unresolved=0; shared_tail=0; max_end=start
    # Hard guard against corrupted control flow swallowing the image.
    while q and len(seen)<200000:
        a=q.popleft()
        if a in seen: continue
        if a != start and a in entries:
            foreign+=1; continue
        rec=ins.get(a)
        if rec is None:
            unresolved+=1; continue
        seen.add(a); max_end=max(max_end,a+rec[0])
        for s in successors(a,rec,start):
            # Watcom performs tail merging: an unconditional JMP may reuse the
            # epilogue inside another routine.  Do not let that shared tail
            # inflate this function's extent.
            if rec[1].startswith('jmp') and s is not None:
                owner=provisional_owner(s)
                if owner is not None and owner != start and s not in entries:
                    shared_tail += 1
                    continue
            if s is None or s<0 or s>=code_size:
                unresolved+=1; continue
            if s != start and s in entries:
                foreign+=1; continue
            q.append(s)
    if len(seen)>=200000:
        unresolved+=1
    for aa in sorted(seen): memberships.append({'function_offset':start,'instruction_offset':aa})
    if max_end>provisional: status='extends'; extended+=1
    elif max_end<provisional: status='shorter'; truncated+=1
    else: status='matches'; exact+=1
    if unresolved: status += '+unresolved'
    results.append({**r,'cfg_min':min(seen) if seen else start,'cfg_end':max_end,'reachable_instructions':len(seen),'status':status,'foreign_entry_edges':foreign,'shared_tail_edges':shared_tail,'unresolved_edges':unresolved})

with MEM.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['function_offset','instruction_offset']); w.writeheader(); w.writerows(memberships)
fields=list(results[0].keys())
with OUT.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(results)
MAN.write_text(json.dumps({
    'functions':len(results),'watcom_code_symbols':sum(int(r.get('module_index','-1'))>=0 for r in rows),'synthetic_entries':sum(int(r.get('module_index','-1'))<0 for r in rows),'instruction_records':len(ins),
    'matches_provisional_end':exact,'extends_beyond_provisional_end':extended,
    'ends_before_provisional_end':truncated,'entry_decode_failures':ambiguous,
    'cfg_membership_records':len(memberships),
    'method':'recursive direct-CFG traversal; calls not followed; other known CODE entries are hard boundaries; unconditional jumps into another provisional function body are classified as Watcom shared tails; indirect transfers terminate path'
},indent=2)+'\n')
print(json.dumps(json.loads(MAN.read_text()),indent=2))
