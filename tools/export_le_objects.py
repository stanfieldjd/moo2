#!/usr/bin/env python3
"""Export every mapped LE object from the verified official v1.31 executable.

Development-only output.  This makes code/data cross-reference recovery possible
without treating object-relative DS addresses as offsets into the code object.
"""
from pathlib import Path
import hashlib, json, sys
sys.path.insert(0,str(Path(__file__).parent))
import original_probe as probe

exe=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
data=exe.read_bytes(); r=probe.inspect(exe)
if not r['official_v131_reference']:
    raise SystemExit('refusing non-official executable')
le=r['le_image']; manifest=[]
for obj in le['objects']:
    image=bytearray(obj['size'])
    mapped=0
    for off in range(0,obj['size'],le['page_size']):
        n=min(le['page_size'],obj['size']-off)
        try: fo=probe.le_object_file_offset(data,le,obj['number'],off)
        except probe.ProbeError: continue
        image[off:off+n]=data[fo:fo+n]; mapped += n
    p=out/f"object_{obj['number']}.bin"; p.write_bytes(image)
    manifest.append({**obj,'mapped_bytes':mapped,'sha256':hashlib.sha256(image).hexdigest(),'path':p.name})
(out/'le_objects.json').write_text(json.dumps({'exe_sha256':r['sha256'],'objects':manifest},indent=2)+'\n')
print((out/'le_objects.json').read_text(),end='')
