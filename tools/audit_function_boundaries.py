#!/usr/bin/env python3
"""Audit provisional next-symbol function boundaries using direct control-flow targets."""
import bisect,csv,re,subprocess,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/'decompilation/code_object_1.bin'
FUN=ROOT/'decompilation/functions.csv'
OUT=ROOT/'decompilation/function_boundary_audit.csv'
MAN=ROOT/'decompilation/function_boundary_audit.json'
rows=list(csv.DictReader(FUN.open()))
code=CODE.read_bytes()
starts=sorted(int(r['offset']) for r in rows)
owner_by_start={int(r['offset']):r['name'] for r in rows}

def target_owner(target):
    """Return the symbol interval containing target, if it lies in CODE."""
    i=bisect.bisect_right(starts,target)-1
    if i < 0: return None,None
    start=starts[i]
    return owner_by_start[start],start

def classify(op,start,end,target,owner,owner_start):
    exact=owner_start==target
    if target < start and start-target <= 16:
        return 'near_predecessor_epilogue'
    if target >= end and target-end <= 16:
        return 'near_successor_boundary'
    if op=='jmp' and owner and owner != owner_by_start.get(start):
        return 'tail_call' if exact else 'shared_epilogue_or_tail'
    if owner and owner != owner_by_start.get(start):
        return 'cross_function_conditional'
    return 'outside_code_image' if owner is None else 'unclassified'
# Audit functions >= 16 bytes. Decode each independently so targets are address-correct.
branch_re=re.compile(r'^\s*([0-9a-f]+):.*\b(j[a-z]+|loop[a-z]*|call)\s+0x([0-9a-f]+)\b',re.I)
issues=[]; audited=0
with tempfile.NamedTemporaryFile() as tf:
    for r in rows:
        start=int(r['offset']); end=int(r['inferred_end']); size=end-start
        if size<16 or start<0 or end>len(code): continue
        audited+=1
        tf.seek(0); tf.truncate(); tf.write(code[start:end]); tf.flush()
        p=subprocess.run(['objdump','-D','-b','binary','-m','i386','-M','intel',f'--adjust-vma={start}',tf.name],text=True,capture_output=True)
        for line in p.stdout.splitlines():
            m=branch_re.match(line)
            if not m: continue
            insn=int(m.group(1),16); op=m.group(2).lower(); target=int(m.group(3),16)
            # Calls normally leave a function; jumps should not, except tail calls. Record all outgoing jumps.
            if op.startswith('j') or op.startswith('loop'):
                if target < start or target >= end:
                    owner,owner_start=target_owner(target)
                    issues.append({'name':r['name'],'start':start,'provisional_end':end,'size':size,'instruction':insn,'opcode':op,'target':target,'direction':'before' if target<start else 'after','delta':target-end if target>=end else start-target,'target_owner':owner or '', 'target_owner_start':owner_start if owner_start is not None else '', 'target_relation':'entry' if owner_start==target else ('interior' if owner else 'outside'), 'classification':classify(op,start,end,target,owner,owner_start)})
                    break
with OUT.open('w',newline='') as f:
    fields=['name','start','provisional_end','size','instruction','opcode','target','direction','delta','target_owner','target_owner_start','target_relation','classification']; w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(issues)
counts={}
for issue in issues: counts[issue['classification']]=counts.get(issue['classification'],0)+1
MAN.write_text(json.dumps({'audited_functions':audited,'functions_with_outgoing_direct_jump':len(issues),'classifications':counts,'method':'Decode each symbol-bounded function independently; map the first outgoing direct jump to its exact target symbol interval; distinguish tail calls and shared epilogues from conditional cross-boundary control flow. Cross-function conditionals remain boundary-review candidates.'},indent=2,sort_keys=True)+'\n')
print(f'audited={audited} suspect={len(issues)}')
print(OUT)
