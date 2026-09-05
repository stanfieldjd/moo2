#!/usr/bin/env python3
import sys
from pathlib import Path
from original_probe import inspect, OFFICIAL_SHA256, TARGET_SYMBOLS

if len(sys.argv) != 2:
    raise SystemExit("usage: test_original_probe.py /path/to/ORION2.EXE")

p=Path(sys.argv[1])
r=inspect(p)
assert r['sha256']==OFFICIAL_SHA256 and r['official_v131_reference']
assert r['bound_payload']=={'file_offset':62580,'signature':'BW'}, r['bound_payload']
expected={
'_planet_size_table':(2,0x57f7), '_planet_max_farms':(2,0x57fc), '_planet_max_mines':(2,0x5801),
'_planet_max_population':(2,0x5806), '_climate_modifier_table':(2,0x5817), '_food_per_farmer_table':(2,0x581c)}
for n in TARGET_SYMBOLS:
 s=r['target_symbols'][n]; assert (s['segment'],s['offset'])==expected[n], (n,s)
print('original_probe self-test: PASS')
assert r['le_image']['module_base']==0x26654
assert r['le_image']['le_start']==0x292e4
assert r['le_image']['data_pages_start']==0x95654
expected_tables={
'_planet_size_table':[1,3,7,9,10],
'_planet_max_farms':[2,4,5,7,10],
'_planet_max_mines':[2,4,6,9,12],
'_planet_max_population':[5,10,15,20,25],
'_climate_modifier_table':[0,0,0,246,236],
'_food_per_farmer_table':[0,0,0,1,1,2,2,1,2,3],
}
for n,b in expected_tables.items(): assert r['target_tables'][n]['bytes']==b,(n,r['target_tables'][n])
assert r['target_tables']['_planet_max_population']['length']==5
assert r['target_tables']['_climate_modifier_table']['signed_bytes']==[0,0,0,-10,-20]
print('original_probe LE/table extraction: PASS')

assert r['gameplay_functions']['isqrt_']['segment']==1
assert r['gameplay_functions']['isqrt_']['offset']==0x124c92
assert r['gameplay_functions']['isqrt_']['file_offset']==0x1ba2e6
print('original_probe isqrt resolution: PASS')
