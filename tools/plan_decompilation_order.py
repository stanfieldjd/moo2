#!/usr/bin/env python3
"""Compute SCC-aware reconstruction order for original MOX modules.

Strongly-connected module groups are kept together because their dependencies are
cyclic.  The condensation graph is then ordered dependency-first: groups with no
outgoing dependencies appear before groups that depend on them.
"""
import csv, json, pathlib, collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'decompilation'
rows=list(csv.DictReader((D/'game_module_edges.csv').open()))
nodes=set(); graph=collections.defaultdict(set); weights=collections.Counter()
for r in rows:
    a,b=r['caller_module'],r['callee_module']; nodes|={a,b}; graph[a].add(b); weights[(a,b)]+=int(r['call_sites'])
for n in nodes: graph[n]
# Tarjan SCC
idx=0; stack=[]; on=set(); ids={}; low={}; comps=[]
def visit(v):
    global idx
    ids[v]=low[v]=idx; idx+=1; stack.append(v); on.add(v)
    for w in graph[v]:
        if w not in ids: visit(w); low[v]=min(low[v],low[w])
        elif w in on: low[v]=min(low[v],ids[w])
    if low[v]==ids[v]:
        c=[]
        while True:
            w=stack.pop(); on.remove(w); c.append(w)
            if w==v: break
        comps.append(sorted(c))
for n in sorted(nodes):
    if n not in ids: visit(n)
ci={n:i for i,c in enumerate(comps) for n in c}
out=collections.defaultdict(set); incoming=collections.defaultdict(set); cw=collections.Counter()
for (a,b),w in weights.items():
    x,y=ci[a],ci[b]
    if x!=y: out[x].add(y); incoming[y].add(x); cw[(x,y)]+=w
# dependency-first topo: a caller depends on callee, so process sinks first.
remaining=set(range(len(comps))); order=[]
while remaining:
    ready=sorted([x for x in remaining if not (out[x]&remaining)], key=lambda x:(len(comps[x]), comps[x]))
    if not ready: raise RuntimeError('condensation graph unexpectedly cyclic')
    for x in ready: order.append(x); remaining.remove(x)
rank=[]
for pos,x in enumerate(order,1):
    internal=sum(weights[(a,b)] for a in comps[x] for b in comps[x] if a!=b)
    rank.append({'order':pos,'scc':x,'module_count':len(comps[x]),'internal_cross_calls':internal,
                 'modules':' | '.join(comps[x])})
with (D/'reconstruction_order.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rank[0].keys()); w.writeheader(); w.writerows(rank)
manifest={'modules':len(nodes),'scc_count':len(comps),'cyclic_scc_count':sum(len(c)>1 for c in comps),
          'largest_scc':max(map(len,comps)),
          'first_dependency_groups':[{'order':r['order'],'module_count':r['module_count'],'modules':r['modules']} for r in rank[:20]]}
(D/'reconstruction_order.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
