#!/usr/bin/env python3
"""Export caller/callee neighborhoods for recovered MOX functions."""
import argparse,csv,json
from collections import defaultdict
from pathlib import Path

def load_edges(path):
    with open(path,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--edges',default='decompilation/game_call_edges.csv'); ap.add_argument('--subsystems',default='decompilation/subsystem_functions.csv'); ap.add_argument('--out',default='decompilation/function_neighborhoods.json'); a=ap.parse_args()
    edges=load_edges(a.edges); callers=defaultdict(list); callees=defaultdict(list)
    for e in edges:
        n=int(e['call_sites']);
        callees[e['caller']].append({'function':e['callee'],'module':e['callee_module'],'call_sites':n})
        callers[e['callee']].append({'function':e['caller'],'module':e['caller_module'],'call_sites':n})
    subs={}
    p=Path(a.subsystems)
    if p.exists():
      with p.open(newline='',encoding='utf-8') as f:
       for r in csv.DictReader(f): subs[r['name']]=[x for x in r.get('subsystems','').split(';') if x]
    names=sorted(set(callers)|set(callees))
    out={}
    for name in names:
      out[name]={'subsystems':subs.get(name,[]), 'callers':sorted(callers[name],key=lambda x:(-x['call_sites'],x['function'])), 'callees':sorted(callees[name],key=lambda x:(-x['call_sites'],x['function']))}
    Path(a.out).write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(f'function neighborhoods: {len(out)} functions -> {a.out}')
if __name__=='__main__': main()
