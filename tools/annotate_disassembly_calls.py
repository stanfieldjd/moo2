#!/usr/bin/env python3
"""Annotate direct x86 CALL targets in a raw function disassembly with recovered symbols."""
import argparse,csv,re,bisect
from pathlib import Path
CALL_RE=re.compile(r'^(\s*[0-9a-fA-F]+:.*\bcall\s+0x)([0-9a-fA-F]+)(.*)$')

def load_symbols(path):
    rows=list(csv.DictReader(open(path,newline='',encoding='utf-8')))
    arr=sorted((int(r['offset']),r['name']) for r in rows)
    return arr,[a for a,_ in arr]

def annotate(lines,start,arr,addrs):
    out=[]
    for line in lines:
        m=CALL_RE.match(line.rstrip('\n'))
        if not m:
            out.append(line.rstrip('\n')); continue
        raw=int(m.group(2),16)
        if raw >= 0x80000000: raw -= 0x100000000
        actual=start+raw
        i=bisect.bisect_right(addrs,actual)-1
        if i>=0 and arr[i][0]==actual:
            line=line.rstrip('\n')+f'  # {arr[i][1]} @ 0001:{actual:08X}'
        out.append(line.rstrip('\n'))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('disassembly',type=Path)
    ap.add_argument('--start',required=True,type=lambda s:int(s,0),help='linker offset of sliced function')
    ap.add_argument('--symbols',type=Path,default=Path('decompilation/functions.csv'))
    ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args()
    arr,addrs=load_symbols(a.symbols)
    text='\n'.join(annotate(a.disassembly.read_text().splitlines(),a.start,arr,addrs))+'\n'
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text)
    else: print(text,end='')
if __name__=='__main__': main()
