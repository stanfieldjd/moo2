#!/usr/bin/env python3
import csv,json,collections,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'decompilation'
rows=list(csv.DictReader((D/'game_call_edges.csv').open()))
# Collapse function edges to module dependencies while retaining both distinct
# function relationships and direct call-site weight. Peer-module counts must be
# sets: counting function relationships here overstates graph degree.
edges=collections.defaultdict(lambda:{'relationships':0,'call_sites':0})
in_peers=collections.defaultdict(set); out_peers=collections.defaultdict(set)
rel_in=collections.Counter(); rel_out=collections.Counter()
weighted_in=collections.Counter(); weighted_out=collections.Counter()
modules=set()
for r in rows:
    a=r['caller_module']; b=r['callee_module']; w=int(r['call_sites'])
    modules.update((a,b))
    if a == b:
        continue
    e=edges[(a,b)]; e['relationships']+=1; e['call_sites']+=w
    out_peers[a].add(b); in_peers[b].add(a)
    rel_out[a]+=1; rel_in[b]+=1
    weighted_out[a]+=w; weighted_in[b]+=w
out=[{'caller_module':a,'callee_module':b,**v}
     for (a,b),v in sorted(edges.items(), key=lambda kv:(-kv[1]['call_sites'],-kv[1]['relationships'],kv[0]))]
with (D/'game_module_edges.csv').open('w',newline='') as f:
    fields=['caller_module','callee_module','relationships','call_sites']
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
rank=[]
for m in sorted(modules):
    rank.append({'module':m,
                 'incoming_modules':len(in_peers[m]),'outgoing_modules':len(out_peers[m]),
                 'incoming_relationships':rel_in[m],'outgoing_relationships':rel_out[m],
                 'incoming_call_sites':weighted_in[m],'outgoing_call_sites':weighted_out[m],
                 'total_call_sites':weighted_in[m]+weighted_out[m]})
rank.sort(key=lambda r:(-r['total_call_sites'],r['module']))
with (D/'game_module_centrality.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rank[0].keys()); w.writeheader(); w.writerows(rank)
manifest={'module_dependency_edges':len(out),'modules_ranked':len(rank),
          'cross_module_function_relationships':sum(x['relationships'] for x in out),
          'cross_module_call_sites':sum(x['call_sites'] for x in out),
          'max_in_degree':max((len(v) for v in in_peers.values()),default=0),
          'max_out_degree':max((len(v) for v in out_peers.values()),default=0),
          'top_modules':rank[:20]}
assert manifest['max_in_degree'] <= max(0,len(rank)-1)
assert manifest['max_out_degree'] <= max(0,len(rank)-1)
(D/'game_callgraph_analysis.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
