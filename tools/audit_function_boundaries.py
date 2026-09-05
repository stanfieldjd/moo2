#!/usr/bin/env python3
"""Audit provisional next-symbol function boundaries using direct control-flow targets."""
import csv,re,subprocess,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CODE=ROOT/'decompilation/code_object_1.bin'
FUN=ROOT/'decompilation/functions.csv'
OUT=ROOT/'decompilation/function_boundary_audit.csv'
MAN=ROOT/'decompilation/function_boundary_audit.json'
rows=list(csv.DictReader(FUN.open()))
code=CODE.read_bytes()
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
                    issues.append({'name':r['name'],'start':start,'provisional_end':end,'size':size,'instruction':insn,'opcode':op,'target':target,'direction':'before' if target<start else 'after','delta':target-end if target>=end else start-target})
                    break
with OUT.open('w',newline='') as f:
    fields=['name','start','provisional_end','size','instruction','opcode','target','direction','delta']; w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(issues)
MAN.write_text(json.dumps({'audited_functions':audited,'functions_with_outgoing_direct_jump':len(issues),'warning':'Outgoing direct jumps identify suspect next-symbol boundaries; some may be legitimate tail calls.'},indent=2)+'\n')
print(f'audited={audited} suspect={len(issues)}')
print(OUT)
