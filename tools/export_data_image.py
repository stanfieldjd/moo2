#!/usr/bin/env python3
"""Reconstruct the initialized/BSS image of LE data object 2 from official v1.31."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
import original_probe as probe
exe=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
data=exe.read_bytes(); r=probe.inspect(exe)
if not r['official_v131_reference']: raise SystemExit('refusing non-official executable')
le=r['le_image']; obj=le['objects'][1]; image=bytearray(obj['size']); initialized=0
for off in range(0,obj['size'],le['page_size']):
 n=min(le['page_size'],obj['size']-off)
 try: fo=probe.le_object_file_offset(data,le,2,off)
 except probe.ProbeError: continue
 image[off:off+n]=data[fo:fo+n]; initialized=max(initialized,off+n)
(out/'data_object_2.bin').write_bytes(image)
manifest={'exe_sha256':r['sha256'],'object':2,'virtual_size':obj['size'],'mapped_pages':obj['map_count'],'initialized_span':initialized,'zero_fill_span':obj['size']-initialized}
(out/'data_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
