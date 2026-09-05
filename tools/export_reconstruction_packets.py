#!/usr/bin/env python3
import csv,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'decompilation'
sub=list(csv.DictReader(open(D/'subsystem_functions.csv',encoding='utf-8')))
neigh=json.load(open(D/'function_neighborhoods.json',encoding='utf-8'))
funcs=list(csv.DictReader(open(D/'functions.csv',encoding='utf-8')))
# Build provisional next-symbol sizes from functions.csv
byseg={}
for r in funcs:
    try: seg=int(r.get('segment') or 1); off=int(r.get('offset') or 0)
    except: continue
    byseg.setdefault(seg,[]).append((off,r.get('name','')))
sizes={}
for seg,items in byseg.items():
    items.sort()
    for i,(off,name) in enumerate(items):
        sizes[name]=(items[i+1][0]-off) if i+1<len(items) else None

focus=[]
for r in sub:
    ss=(r.get('subsystems') or '').split(';')
    if 'population' not in ss or 'colony' not in ss: continue
    # mechanics, not rendering/input helpers
    if any(t in r['name'] for t in ('Draw_','String_','Anim_','Fields_','Scanned_','Selected_','Info_')): continue
    n=neigh.get(r['name'],{})
    focus.append({
      'name':r['name'],'module':r['module'],'segment':int(r['segment']),
      'offset':int(r['offset']),'file_offset':int(r['file_offset']),
      'provisional_size':sizes.get(r['name']),
      'callers':n.get('callers',[]),'callees':n.get('callees',[]),
      'subsystems':ss
    })
focus.sort(key=lambda x:x['offset'])
out={'packet':'population_colony_mechanics','boundary_warning':'sizes use next recovered symbol and remain provisional','functions':focus}
(D/'population_reconstruction_packet.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
with open(D/'population_reconstruction_packet.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['name','module','segment','offset','file_offset','provisional_size','caller_count','callee_count'])
    for x in focus:w.writerow([x['name'],x['module'],x['segment'],x['offset'],x['file_offset'],x['provisional_size'],len(x['callers']),len(x['callees'])])
print(f'population reconstruction packet: {len(focus)} mechanics functions')
