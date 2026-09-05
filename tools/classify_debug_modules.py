#!/usr/bin/env python3
import argparse,csv,json,re
from pathlib import Path

def family(name):
    u=name.upper().replace('/','\\')
    if '\\MOX\\' in u: return 'game_mox'
    if '\\WLIBS\\' in u: return 'simtex_wlibs'
    if '\\AIL\\' in u or u.endswith('AILA.ASM') or u.endswith('AILSSA.ASM'): return 'miles_audio'
    return 'other'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('modules_csv',type=Path); ap.add_argument('output',type=Path)
    a=ap.parse_args(); rows=list(csv.DictReader(a.modules_csv.open()))
    out=[]
    for r in rows:
        x=dict(r); x['family']=family(r['name'])
        for k in ('locals_entries','types_entries','lines_entries'): x[k]=int(r[k])
        out.append(x)
    fam={}
    for r in out:
        d=fam.setdefault(r['family'],{'modules':0,'with_locals':0,'with_types':0,'with_lines':0})
        d['modules']+=1; d['with_locals']+=bool(r['locals_entries']); d['with_types']+=bool(r['types_entries']); d['with_lines']+=bool(r['lines_entries'])
    payload={'summary':{'module_count':len(out),'families':fam},'modules':out}
    a.output.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload['summary'],indent=2))
if __name__=='__main__': main()
