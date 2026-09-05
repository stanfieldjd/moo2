#!/usr/bin/env python3
"""Find Watcom-style tail merging: functions jumping into another known function body/epilogue."""
import csv,re,json,argparse
from pathlib import Path
JMP=re.compile(r'^\s*([0-9a-fA-F]+):.*\bjmp\s+0x([0-9a-fA-F]+)\b')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--disasm',type=Path,default=Path('decompilation/code_object_1.disasm')); ap.add_argument('--functions',type=Path,default=Path('decompilation/functions.csv')); ap.add_argument('--csv',type=Path,default=Path('decompilation/shared_function_tails.csv')); ap.add_argument('--json',type=Path,default=Path('decompilation/shared_function_tails.json')); a=ap.parse_args()
 fs=sorted([(int(r['offset']),r['name'],r.get('module','')) for r in csv.DictReader(a.functions.open())])
 starts={x[0] for x in fs}; ranges=[]
 for i,(s,n,m) in enumerate(fs): ranges.append((s,fs[i+1][0] if i+1<len(fs) else 1<<31,n,m))
 def owner(x):
  lo,hi=0,len(ranges)
  while lo<hi:
   mid=(lo+hi)//2
   if ranges[mid][0]<=x: lo=mid+1
   else: hi=mid
  if lo==0:return None
  r=ranges[lo-1]; return r if x<r[1] else None
 edges=[]
 for line in a.disasm.read_text(errors='replace').splitlines():
  m=JMP.match(line)
  if not m: continue
  src=int(m.group(1),16); dst=int(m.group(2),16); so=owner(src); do=owner(dst)
  if not so or not do or so[2]==do[2] or dst in starts: continue
  # Only jumps into the interior of another symbol extent: classic tail merge candidate.
  edges.append({'caller':so[2],'caller_offset':so[0],'jump_site':src,'target_owner':do[2],'target_owner_offset':do[0],'target':dst,'target_delta':dst-do[0]})
 a.csv.parent.mkdir(parents=True,exist_ok=True)
 with a.csv.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(edges[0]) if edges else ['caller']);w.writeheader();w.writerows(edges)
 bytarget={}
 for e in edges: bytarget.setdefault((e['target_owner'],e['target']),0);bytarget[(e['target_owner'],e['target'])]+=1
 manifest={'interior_cross_function_jumps':len(edges),'unique_shared_targets':len(bytarget),'top_shared_targets':[{'target_owner':k[0],'target':k[1],'incoming':v} for k,v in sorted(bytarget.items(),key=lambda kv:-kv[1])[:50]]}
 a.json.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
