#!/usr/bin/env python3
"""Decode Watcom $$TYPES records into indexed, machine-readable type definitions."""
from __future__ import annotations
import argparse,json
from pathlib import Path

# Intel variable-length type index used by Watcom.
def idx(b: bytes, p: int):
    if p >= len(b): raise ValueError('missing type index')
    x=b[p]
    if x & 0x80:
        if p+1 >= len(b): raise ValueError('truncated type index')
        return ((x & 0x7f)<<8)|b[p+1],p+2
    return x,p+1

def tail(b,p): return b[p:].decode('latin1','replace')

def decode(rawhex: str):
    r=bytes.fromhex(rawhex); k=r[1]; b=r[2:]; d={'kind':f'0x{k:02x}'}
    try:
      if k==0x10: d.update(class_='scalar',scalar=b[0],name=tail(b,1))
      elif k==0x11: d.update(class_='scope',name=tail(b,0))
      elif k==0x12:
        s,p=idx(b,0); t,p=idx(b,p); d.update(class_='name',scope=s,type=t,name=tail(b,p))
      elif k==0x13: d.update(class_='cue_table',table_offset=int.from_bytes(b[:4],'little'))
      elif k==0x14: d.update(class_='eof')
      elif k in (0x20,0x21,0x22,0x23,0x24):
        base,p=idx(b,0); d.update(class_='array',base_type=base,subclass=k&15,payload=b[p:].hex())
      elif k in (0x40,0x41,0x42,0x43,0x44,0x45,0x46):
        base,p=idx(b,0); d.update(class_='pointer',base_type=base,subclass=k&15,payload=b[p:].hex())
      elif k==0x60:
        d.update(class_='struct',field_count=int.from_bytes(b[:2],'little'))
        if len(b)>=6: d['size']=int.from_bytes(b[2:6],'little')
      elif k in (0x61,0x62,0x63):
        n={0x61:1,0x62:2,0x63:4}[k]; off=int.from_bytes(b[:n],'little'); t,p=idx(b,n)
        d.update(class_='field',offset=off,type=t,name=tail(b,p))
      elif k in (0x70,0x71,0x72,0x73):
        ret,p=idx(b,0); n=b[p]; p+=1; pars=[]
        while p<len(b) and len(pars)<n:
          t,p=idx(b,p); pars.append(t)
        d.update(class_='procedure',subclass=k&15,return_type=ret,param_count=n,params=pars)
      elif k==0x74:
        pars=[]; p=0
        while p<len(b): t,p=idx(b,p); pars.append(t)
        d.update(class_='ext_params',params=pars)
      else: d.update(class_='other',payload=b.hex())
    except (ValueError,IndexError) as e: d.update(parse_error=str(e),payload=b.hex())
    return d

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('types_json',type=Path); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
 src=json.loads(a.types_json.read_text()); out=[]; totals={'modules':len(src),'indexed_types':0,'structures':0,'fields':0,'procedures':0,'named_types':0,'parse_errors':0}
 for block in src:
   mod={'module_index':block['module_index'],'module':block['module'],'types':[],'fields':[]}; ti=0; current_struct=None
   for rr in block['records']:
     d=decode(rr['raw']); d['record_offset']=rr['offset']
     # FIELD/BIT/INHERIT and EXT_PARMS do not receive type indices.
     indexed = d.get('class_') not in ('field','ext_params') and not (0x64 <= int(d['kind'],16) <= 0x69)
     if indexed: ti+=1; d['type_index']=ti; totals['indexed_types']+=1
     if d.get('class_')=='struct': current_struct=ti; totals['structures']+=1
     elif d.get('class_')=='field': d['struct_type_index']=current_struct; mod['fields'].append(d); totals['fields']+=1
     if d.get('class_')=='procedure': totals['procedures']+=1
     if d.get('class_')=='name': totals['named_types']+=1
     if 'parse_error' in d: totals['parse_errors']+=1
     mod['types'].append(d)
   out.append(mod)
 a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps({'summary':totals,'modules':out},indent=2))
 print(json.dumps(totals,indent=2))
if __name__=='__main__': main()
