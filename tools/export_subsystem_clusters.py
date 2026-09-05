#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'decompilation'
rows=list(csv.DictReader(open(D/'game_module_symbols.csv',newline='')))
# Classify on lexical tokens, not raw substrings. This prevents e.g. POPUP from
# being mistaken for population and MAINTAIN from being mistaken for AI.
rules={
 'population':{'POP','POPS','POPULATION','GROW','GROWS','GROWTH','SUBTERRANEAN'},
 'food':{'FOOD','FARM','FARMS','FARMER'},
 'industry':{'INDUSTRY','INDUSTRIAL','WORKER','WORKERS','MINE','MINES','MINERAL','MINERALS','POLLUTION','REPLICATOR'},
 'research':{'RESEARCH','SCIENTIST','SCIENTISTS','TECH','TECHNOLOGY'},
 'economy':{'BC','MONEY','TAX','INCOME','MAINTENANCE','BUY','COST','TRADE'},
 'colony':{'COLONY','COLONIES','COLONIZE','COLONIZATION','COLCALC','COLBLDG','COLMOVE','COLLAND','COLXPORT','COLREFIT','COLSUM'},
 'combat':{'CMBT','COMBAT','BOMB','BOMBING','WEAPON','WEAPONS','MISSILE','MISSILES','ARMOR','TACTICAL'},
 'diplomacy':{'DIPLOMACY','DIPLOMAC','DIP','COUNCIL','TREATY','TREATIES','SPY','SPIES','ESPIONAGE'},
 'ai':{'AI','NPC'},
 'fleet':{'FLEET','FLEETS','SHIP','SHIPS','STARBASE','COMMAND','POINT'},
 'ui':{'DRAW','SCREEN','SCRN','BUTTON','BUTTONS','WINDOW','MENU','POPUP','POPUPS','HOTPOP'},
}
# Module basenames carry strong subsystem information even when concatenated
# (COLCALC.C, AIBUILD.C, CMBTDRW1.C). Keep these explicit and auditable.
module_prefix={
 'colony':('COL',), 'combat':('CMBT','COMB'), 'diplomacy':('DIP','COUNCIL','SPY'),
 'ai':('AI','NPC'), 'fleet':('FLEET',), 'ui':('HOTPOP',),
}
def tokens(text):
 return set(re.findall(r'[A-Z0-9]+', text.upper()))

def module_base(path):
 return re.split(r'[\\/]',path)[-1].split('.')[0].upper()

out=[]; counts={k:0 for k in rules}
for r in rows:
 if r['symbol_type']!='code': continue
 toks=tokens(r['name']) | tokens(module_base(r['module']))
 mb=module_base(r['module'])
 labs=[]
 for k,terms in rules.items():
  hit=bool(toks & terms) or any(mb.startswith(p) for p in module_prefix.get(k,()))
  if hit: labs.append(k); counts[k]+=1
 if labs: out.append({**r,'subsystems':';'.join(labs)})
out.sort(key=lambda r:(r['subsystems'],r['module'],int(r['offset'])))
with open(D/'subsystem_functions.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
json.dump({'classified_code_symbols':len(out),'subsystem_memberships':counts,'method':'tokenized multi-label classification from recovered original module/symbol names; explicit module-prefix rules'},open(D/'subsystem_manifest.json','w'),indent=2)
print(json.dumps({'classified_code_symbols':len(out),'subsystem_memberships':counts},indent=2))
