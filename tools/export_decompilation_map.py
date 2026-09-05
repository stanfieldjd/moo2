#!/usr/bin/env python3
"""Export verified official v1.31 Watcom symbols as a decompilation map."""
from pathlib import Path
import csv, json, sys
import original_probe as probe

exe=Path(sys.argv[1])
out=Path(sys.argv[2])
r=probe.inspect(exe)
if not r['official_v131_reference']:
    raise SystemExit('refusing non-official executable')
data=exe.read_bytes(); syms=probe.global_symbols(data,r['watcom']); le=r['le_image']
rows=[]
for name,s in syms.items():
    try: fo=probe.le_object_file_offset(data,le,s['segment'],s['offset'])
    except probe.ProbeError: fo=None
    rows.append({'name':name,'segment':s['segment'],'offset':s['offset'],'kind':s['kind'],'module_index':s['module_index'],'file_offset':fo})
rows.sort(key=lambda x:(x['segment'],x['offset'],x['name']))
out.mkdir(parents=True,exist_ok=True)
with (out/'symbols.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
(out/'manifest.json').write_text(json.dumps({'exe_sha256':r['sha256'],'symbol_count':len(rows),'mapped_count':sum(x['file_offset'] is not None for x in rows)},indent=2))
print(json.dumps({'symbol_count':len(rows),'mapped_count':sum(x['file_offset'] is not None for x in rows)},indent=2))
