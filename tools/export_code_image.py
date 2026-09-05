#!/usr/bin/env python3
"""Export the official v1.31 LE code object plus symbol-derived function boundaries."""
from pathlib import Path
import csv, json, subprocess, sys
sys.path.insert(0, str(Path(__file__).parent))
import original_probe as probe

exe=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
data=exe.read_bytes(); r=probe.inspect(exe)
if not r['official_v131_reference']: raise SystemExit('refusing non-official executable')
le=r['le_image']; syms=probe.global_symbols(data,r['watcom']); obj=le['objects'][0]
# Reconstruct virtual object bytes through the verified LE page map, not by assuming file contiguity.
image=bytearray(obj['size'])
for off in range(0,obj['size'],le['page_size']):
    n=min(le['page_size'],obj['size']-off)
    try: fo=probe.le_object_file_offset(data,le,1,off)
    except probe.ProbeError: continue
    image[off:off+n]=data[fo:fo+n]
(out/'code_object_1.bin').write_bytes(image)
code=[]
for name,s in syms.items():
    if s['segment']==1 and (s['kind'] & 4): code.append((s['offset'],name,s['module_index'],s['kind']))
code.sort()
unique=sorted(set(x[0] for x in code)); nextoff={o:(unique[i+1] if i+1<len(unique) else obj['size']) for i,o in enumerate(unique)}
with (out/'functions.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['name','offset','inferred_end','inferred_size','module_index','kind'])
    for off,name,mi,k in code: w.writerow([name,off,nextoff[off],nextoff[off]-off,mi,k])
# One complete instruction listing; symbol boundaries stay separately machine-readable.
with (out/'code_object_1.disasm').open('w') as f:
    subprocess.run(['objdump','-D','-b','binary','-m','i386','-M','intel','--adjust-vma=0',str(out/'code_object_1.bin')],stdout=f,check=True)
manifest={'exe_sha256':r['sha256'],'code_object_size':obj['size'],'code_symbols':len(code),'unique_code_addresses':len(unique),'boundary_method':'next Watcom CODE global; provisional until CFG recovery'}
(out/'code_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
