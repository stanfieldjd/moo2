#!/usr/bin/env python3
"""Self-test for the development-only classic MOO2 save inspector."""
from pathlib import Path
import importlib.util, tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("save_inspect", HERE / "save_inspect.py")
si = importlib.util.module_from_spec(spec); spec.loader.exec_module(si)

# Build only enough synthetic bytes to exercise the documented records.
size = si.PLANET_DATA + 2 * si.PLANET_SIZE
buf = bytearray(size)
buf[si.COLONY_COUNT:si.COLONY_COUNT+2] = (1).to_bytes(2, 'little')
buf[si.PLANET_COUNT:si.PLANET_COUNT+2] = (2).to_bytes(2, 'little')
cb = si.COLONY_DATA
buf[cb] = 3; buf[cb+2] = 1; buf[cb+10] = 8
for j,v in enumerate(range(10,20)): buf[cb+0xB4+2*j:cb+0xB6+2*j] = v.to_bytes(2,'little')
for j,v in enumerate(range(20,30)): buf[cb+0xC8+2*j:cb+0xCA+2*j] = v.to_bytes(2,'little')
buf[cb+0xDD:cb+0xE3] = bytes([2,3,4,5,15,8])
pb = si.PLANET_DATA + si.PLANET_SIZE
buf[pb:pb+17] = bytes([0x34,0x12,7,2,1,2,0,4,8,9,3,2,1,5,15,6,4])

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'fixture.gam'; p.write_bytes(buf)
    x=si.parse(p)
    assert x['colony_count']==1 and x['planet_count']==2
    c=x['colonies'][0]; q=x['planets'][1]
    assert c['owner_id']==3 and c['planet_id']==1 and c['population']==8
    assert c['pop_raised']==list(range(10,20))
    assert c['pop_grow']==list(range(20,30))
    assert (c['food2_per_farmer'],c['industry_per_worker'],c['research_per_scientist'])==(2,3,4)
    assert (c['max_farms'],c['max_population'],c['climate'])==(5,15,8)
    assert q['colony_id']==0x1234 and q['star_id']==7 and q['size']==2
    assert q['max_farms']==5 and q['max_population']==15
    bad=Path(td)/'bad.gam'; bad.write_bytes(b'bad')
    try: si.parse(bad)
    except si.SaveFormatError: pass
    else: raise AssertionError('short input was not rejected')
print('save_inspect self-test: PASS')
