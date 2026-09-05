#!/usr/bin/env python3
"""Separate executable routine entries from linker/runtime code-address markers."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; CFG=ROOT/'decompilation/function_cfg_extents.csv'; OUT=ROOT/'decompilation/code_symbol_classification.csv'; MAN=ROOT/'decompilation/code_symbol_classification.json'
marker_names={'___GETDSEnd_','__SegmentStartRR16','__IrqDataArrayRR16','__VideoBasePD16','__SegmentStartPC32','__SegmentEndPC32'}
rows=[]; counts={'routine_entry':0,'runtime_marker':0}
for r in csv.DictReader(CFG.open()):
 cls='runtime_marker' if r['name'] in marker_names and r['status']=='no_entry_decode' else 'routine_entry'
 counts[cls]+=1; rows.append({'name':r['name'],'offset':r['offset'],'classification':cls,'cfg_status':r['status']})
with OUT.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
MAN.write_text(json.dumps({'counts':counts,'unclassified_decode_failures':sum(x['cfg_status']=='no_entry_decode' and x['classification']!='runtime_marker' for x in rows),
 'rule':'Only the six surviving non-decoding Watcom CODE globals are classified as linker/runtime address markers; no decoding symbol is demoted.'},indent=2)+'\n')
print(MAN.read_text(),end='')
