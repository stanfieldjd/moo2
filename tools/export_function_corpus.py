#!/usr/bin/env python3
"""Export one corrected-CFG assembly file per recovered Watcom CODE entry.
Development-only: contains no original executable bytes, only textual disassembly.
"""
from pathlib import Path
import csv, re, shutil, bisect
ROOT=Path(__file__).resolve().parents[1]
DEC=ROOT/'decompilation'; OUT=DEC/'functions_asm'
EXT=DEC/'function_cfg_extents.csv'; MEM=DEC/'function_cfg_membership.csv'; DIS=DEC/'code_object_1_resynced.disasm'
INS=re.compile(r'^\s*([0-9a-fA-F]+):\s+((?:[0-9a-fA-F]{2}\s+)+)\s*(.*)$')
SAFE=re.compile(r'[^A-Za-z0-9_.@+-]+')

def main():
    rows=list(csv.DictReader(EXT.open()))
    members={}
    for rr in csv.DictReader(MEM.open()): members.setdefault(int(rr['function_offset']),[]).append(int(rr['instruction_offset']))
    # Decode objdump once; retain textual instructions by address.
    inst={}
    for line in DIS.open(errors='replace'):
        m=INS.match(line)
        if m: inst[int(m.group(1),16)] = (m.group(2).strip(),m.group(3).rstrip())
    addrs=sorted(inst)
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    manifest=[]; empty=0; total=0
    seen={}
    for i,r in enumerate(rows):
        start=int(r['cfg_min']); end=int(r['cfg_end'])
        name=r['name'] or f'sub_{start:08x}'
        base=SAFE.sub('_',name).strip('_') or f'sub_{start:08x}'
        key=(base,start)
        n=seen.get(key,0); seen[key]=n+1
        fn=f'{start:08x}_{base}{"_"+str(n) if n else ""}.asm'
        selected=[(a,*inst[a]) for a in members.get(int(r['offset']),[]) if a in inst]
        # Avoid O(Nfunctions*Ninstructions) in future revisions; current corpus is modest.
        text=[f'; {name}',f'; cfg range 0x{start:08X}..0x{end:08X}',f'; module {r["module_index"]}; status {r["status"]}','']
        for a,b,op in selected: text.append(f'{a:08x}:  {b:<24} {op}')
        (OUT/fn).write_text('\n'.join(text)+'\n')
        count=len(selected); total+=count; empty += (count==0)
        manifest.append({**r,'file':f'functions_asm/{fn}','instruction_count':count})
    fields=list(manifest[0])+[]
    with (DEC/'function_corpus.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(manifest)
    (DEC/'function_corpus_manifest.txt').write_text(
        f'functions={len(manifest)}\nnonempty={len(manifest)-empty}\nempty={empty}\n'
        f'instruction_instances={total}\nunique_disassembly_instructions={len(inst)}\n'
        'boundary_source=exact conservative CFG membership with shared-tail handling\n')
    print((DEC/'function_corpus_manifest.txt').read_text(),end='')
if __name__=='__main__': main()
