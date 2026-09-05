#!/usr/bin/env python3
import argparse,csv,json,re
from pathlib import Path

CALL_RE=re.compile(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+call\s+(?:0x)?([0-9a-f]+)\b',re.I)

def i(x): return int(x,0) if isinstance(x,str) else int(x)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('symbols_csv',type=Path)
    ap.add_argument('disasm',type=Path)
    ap.add_argument('edges_csv',type=Path)
    ap.add_argument('manifest',type=Path)
    a=ap.parse_args()
    rows=list(csv.DictReader(a.symbols_csv.open()))
    funcs=[]
    for r in rows:
        if r['symbol_type']!='code': continue
        funcs.append({**r,'offset_i':i(r['offset'])})
    funcs.sort(key=lambda r:(i(r['segment']),r['offset_i']))
    # Bulk image is LE object 1 / linker segment 1, starting at offset zero.
    seg1=[r for r in funcs if i(r['segment'])==1]
    by_addr={r['offset_i']:r for r in seg1}
    starts=sorted(by_addr)
    edges={}
    calls=0; resolved=0
    for line in a.disasm.open(errors='replace'):
        m=CALL_RE.match(line)
        if not m: continue
        src=int(m.group(1),16); dst=int(m.group(2),16); calls+=1
        # find owning source symbol using rightmost start <= src
        import bisect
        p=bisect.bisect_right(starts,src)-1
        if p<0: continue
        s=by_addr[starts[p]]; d=by_addr.get(dst)
        if not d: continue
        resolved+=1
        key=(s['module_index'],s['name'],d['module_index'],d['name'])
        edges[key]=edges.get(key,0)+1
    with a.edges_csv.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['caller_module_index','caller_module','caller','callee_module_index','callee_module','callee','call_sites'])
        for (smi,sn,dmi,dn),n in sorted(edges.items(),key=lambda x:(int(x[0][0]),x[0][1],int(x[0][2]),x[0][3])):
            sm=next(r['module'] for r in seg1 if r['module_index']==smi and r['name']==sn)
            dm=next(r['module'] for r in seg1 if r['module_index']==dmi and r['name']==dn)
            w.writerow([smi,sm,sn,dmi,dm,dn,n])
    cross=sum(1 for k in edges if k[0]!=k[2])
    man={'direct_call_instructions':calls,'resolved_game_symbol_calls':resolved,'unique_symbol_edges':len(edges),'cross_module_edges':cross,'segment_1_game_code_symbols':len(seg1)}
    a.manifest.write_text(json.dumps(man,indent=2)+'\n')
    print(json.dumps(man,indent=2))
if __name__=='__main__': main()
