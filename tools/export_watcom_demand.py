#!/usr/bin/env python3
"""Export/validate Watcom demand-loaded LOCALS/TYPES/LINES blocks from official MOO2 v1.31."""
from __future__ import annotations
import argparse,csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import original_probe as op
from export_watcom_modules import modules

CLASSES=(('locals','locals_offset','locals_entries'),('types','types_offset','types_entries'),('lines','lines_offset','lines_entries'))

def demand_blocks(data,layout,row,offkey,nkey):
    s=layout['section_start']; off=int(row[offkey]); n=int(row[nkey]); out=[]
    for i in range(n):
        link=s+off+4*i
        if link+8>s+layout['section_size']: raise op.ProbeError('demand link outside section')
        start=op.u32(data,link); end=op.u32(data,link+4)
        if not (18 <= start < end <= layout['section_size']): raise op.ProbeError(f'invalid demand block {start:x}..{end:x}')
        out.append((start,end,data[s+start:s+end]))
    return out

def records(block):
    """Watcom LOCALS/TYPES are streams of one-byte-length-prefixed records."""
    p=0; out=[]
    while p<len(block):
        ln=block[p]
        if ln<2 or p+ln>len(block): raise op.ProbeError(f'invalid record length {ln} at {p:x}')
        raw=block[p:p+ln]; out.append({'offset':p,'length':ln,'kind':raw[1],'raw':raw.hex()}); p+=ln
        # TYPE_NAME EOF (0x14) terminates the type-record stream; auxiliary cue data may follow.
        if raw[1] == 0x14: break
    return out

def printable_suffix(raw):
    # Diagnostic only: names in Watcom records occupy the tail. Do not claim semantic parsing here.
    i=len(raw)
    while i>2 and 32<=raw[i-1]<127: i-=1
    return raw[i:].decode('ascii','replace') if i<len(raw) else ''

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('exe',type=Path); ap.add_argument('--outdir',type=Path,required=True); a=ap.parse_args()
    data=a.exe.read_bytes()
    if hashlib.sha256(data).hexdigest()!=op.OFFICIAL_SHA256: raise SystemExit('refusing non-official v1.31 executable')
    layout=op.watcom_layout(data); rows=modules(data,layout); a.outdir.mkdir(parents=True,exist_ok=True)
    manifest={'modules':len(rows),'classes':{},'object_debug_version':layout['object_debug_version']}
    for cname,ok,nk in CLASSES:
        blocks=[]; hist=Counter(); rec_total=0
        for r in rows:
            for bi,(start,end,b) in enumerate(demand_blocks(data,layout,r,ok,nk)):
                ent={'module_index':r['index'],'module':r['name'],'block_index':bi,'section_offset':start,'size':end-start}
                if cname in ('locals','types'):
                    rr=records(b); ent['record_count']=len(rr); rec_total+=len(rr)
                    for x in rr:
                        hist[f"0x{x['kind']:02x}"]+=1
                        raw=bytes.fromhex(x['raw']); x['printable_suffix']=printable_suffix(raw)
                    ent['records']=rr
                else:
                    ent['sha256']=hashlib.sha256(b).hexdigest()
                blocks.append(ent)
        (a.outdir/f'{cname}.json').write_text(json.dumps(blocks,indent=2),encoding='utf-8')
        manifest['classes'][cname]={'blocks':len(blocks),'records':rec_total,'kind_histogram':dict(sorted(hist.items()))}
    (a.outdir/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
