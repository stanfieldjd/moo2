#!/usr/bin/env python3
"""Recover named routines, lexical blocks and local names from Watcom $$SYMBOLS.

This intentionally decodes only fields whose layout is unambiguous in Watcom 1.3.
Original machine code remains authoritative.
"""
from __future__ import annotations
import argparse,csv,json,struct
from pathlib import Path

ROUTINES={0x21:(2,2),0x22:(2,2),0x24:(4,4),0x25:(4,4)}
BLOCKS={0x20:(2,2),0x23:(4,4)}

def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def tail_name(raw:bytes)->str:
    i=len(raw)
    while i>2 and 32 <= raw[i-1] < 127: i-=1
    return raw[i:].decode('ascii','replace') if i<len(raw) else ''

def parse(inp:Path):
    blocks=json.loads(inp.read_text())
    routines=[]; lexical=[]; variables=[]
    for db in blocks:
        base_seg=None; base_off=0; current_routine=None
        for rec in db['records']:
            raw=bytes.fromhex(rec['raw']); k=rec['kind']
            if k==0x32 and len(raw)>=8: # SET_BASE386: 32-bit offset + 16-bit segment
                base_off=u32(raw,2); base_seg=u16(raw,6); current_routine=None
            elif k==0x31 and len(raw)>=6: # SET_BASE: 16:16 pointer
                base_off=u16(raw,2); base_seg=u16(raw,4); current_routine=None
            elif k==0x30 and len(raw)>=4 and base_seg is not None:
                base_seg=(base_seg+u16(raw,2))&0xffff; base_off=0; current_routine=None
            elif k in ROUTINES:
                ow,sw=ROUTINES[k]; p=2
                start=u32(raw,p) if ow==4 else u16(raw,p); p+=ow
                size=u32(raw,p) if sw==4 else u16(raw,p)
                name=tail_name(raw)
                ent={'module_index':db['module_index'],'module':db['module'],'kind':f'0x{k:02x}',
                     'base_segment':base_seg,'base_offset':base_off,'start_offset':start,'size':size,
                     'segment':base_seg,'linker_offset':(base_off+start) if base_seg is not None else None,
                     'name':name,'locals':[]}
                routines.append(ent); current_routine=ent
            elif k in BLOCKS:
                ow,sw=BLOCKS[k]; p=2
                start=u32(raw,p) if ow==4 else u16(raw,p); p+=ow
                size=u32(raw,p) if sw==4 else u16(raw,p)
                lexical.append({'module_index':db['module_index'],'module':db['module'],'kind':f'0x{k:02x}',
                                'segment':base_seg,'linker_offset':(base_off+start) if base_seg is not None else None,
                                'size':size})
            elif 0x10 <= k <= 0x13:
                name=tail_name(raw)
                v={'module_index':db['module_index'],'module':db['module'],'kind':f'0x{k:02x}','name':name,
                   'routine':current_routine['name'] if current_routine else ''}
                variables.append(v)
                if current_routine is not None and name: current_routine['locals'].append(name)
    return routines,lexical,variables

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('locals_json',type=Path); ap.add_argument('--outdir',type=Path,required=True); a=ap.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True); routines,blocks,vars=parse(a.locals_json)
    # CSV keeps local names readable while JSON preserves complete structure.
    fields=['module_index','module','kind','segment','linker_offset','size','name','local_count','locals']
    with (a.outdir/'watcom_routines.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in routines:
            w.writerow({'module_index':r['module_index'],'module':r['module'],'kind':r['kind'],'segment':r['segment'],
                        'linker_offset':r['linker_offset'],'size':r['size'],'name':r['name'],
                        'local_count':len(r['locals']),'locals':';'.join(r['locals'])})
    (a.outdir/'watcom_routines.json').write_text(json.dumps(routines,indent=2),encoding='utf-8')
    manifest={'routines':len(routines),'named_routines':sum(bool(r['name']) for r in routines),
              'lexical_blocks':len(blocks),'variables':len(vars),'named_variables':sum(bool(v['name']) for v in vars),
              'routines_with_base':sum(r['segment'] is not None for r in routines)}
    (a.outdir/'watcom_routines_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
