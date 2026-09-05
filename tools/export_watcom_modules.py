#!/usr/bin/env python3
"""Export Watcom module metadata from the verified MOO2 v1.31 executable."""
from __future__ import annotations
import argparse,csv,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import original_probe as op

def demand(d,o):
    # Watcom demand_info: offset (u32), entries (u16). Verified against wddoc structure.
    return op.u32(d,o), op.u16(d,o+4)

def modules(data, layout):
    p,end=layout['module_info_start'],layout['global_symbols_start']; out=[]; idx=0
    while p < end:
        if p+21>end: raise op.ProbeError('truncated module info')
        lang=op.u16(data,p); lo,ln=demand(data,p+2); to,tn=demand(data,p+8); li,lin=demand(data,p+14)
        n=data[p+20]; q=p+21+n
        if q>end: raise op.ProbeError('truncated module name')
        name=data[p+21:q].decode('latin1')
        out.append(dict(index=idx,language_offset=lang,name=name,locals_offset=lo,locals_entries=ln,
                        types_offset=to,types_entries=tn,lines_offset=li,lines_entries=lin))
        p=q; idx+=1
    if p!=end: raise op.ProbeError('module class length mismatch')
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('exe',type=Path); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    data=a.exe.read_bytes(); digest=hashlib.sha256(data).hexdigest()
    if digest!=op.OFFICIAL_SHA256: raise SystemExit('refusing non-official v1.31 executable')
    lay=op.watcom_layout(data); rows=modules(data,lay); a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    have_l=sum(bool(r['locals_entries']) for r in rows); have_t=sum(bool(r['types_entries']) for r in rows); have_n=sum(bool(r['lines_entries']) for r in rows)
    print(f'modules={len(rows)} locals={have_l} types={have_t} lines={have_n}')
    for r in rows[:8]: print(r['index'],r['name'],r['locals_entries'],r['types_entries'],r['lines_entries'])
if __name__=='__main__': main()
