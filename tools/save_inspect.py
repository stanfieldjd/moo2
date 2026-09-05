#!/usr/bin/env python3
"""Development-only inspector for classic MOO2 save state.

Reads a deliberately small, bounds-checked subset of the v1.31 save layout.
It does not modify saves and is not part of the remaster runtime.
"""
from __future__ import annotations
import argparse, json, struct
from pathlib import Path

COLONY_COUNT = 0x25B
COLONY_DATA = 0x25D
COLONY_SIZE = 361
PLANET_COUNT = 0x162E7
PLANET_DATA = 0x162E9
PLANET_SIZE = 0x11

class SaveFormatError(ValueError): pass

def need(data: bytes, off: int, size: int, what: str) -> None:
    if off < 0 or size < 0 or off + size > len(data):
        raise SaveFormatError(f"{what}: need bytes 0x{off:X}..0x{off+size-1:X}, file size is 0x{len(data):X}")

def u8(d,o): need(d,o,1,"u8"); return d[o]
def u16(d,o): need(d,o,2,"u16"); return struct.unpack_from('<H',d,o)[0]

def parse(path: Path) -> dict:
    d = path.read_bytes()
    need(d, COLONY_COUNT, 2, "colony count")
    need(d, PLANET_COUNT, 2, "planet count")
    nc, np = u16(d,COLONY_COUNT), u16(d,PLANET_COUNT)
    # Structural sanity limits prevent corrupt counts from driving arbitrary reads.
    if nc > 250: raise SaveFormatError(f"implausible colony count: {nc}")
    if np > 500: raise SaveFormatError(f"implausible planet count: {np}")
    need(d, COLONY_DATA, nc*COLONY_SIZE, "colony records")
    need(d, PLANET_DATA, np*PLANET_SIZE, "planet records")
    planets=[]
    for i in range(np):
        b=PLANET_DATA+i*PLANET_SIZE
        planets.append({
            "index":i,"colony_id":u16(d,b),"star_id":u8(d,b+2),"position":u8(d,b+3),
            "type":u8(d,b+4),"size":u8(d,b+5),"gravity":u8(d,b+6),"group":u8(d,b+7),
            "terrain":u8(d,b+8),"picture":u8(d,b+9),"minerals":u8(d,b+10),
            "foodbase":u8(d,b+11),"terraformations":u8(d,b+12),"max_farms":u8(d,b+13),
            "max_population":u8(d,b+14),"special":u8(d,b+15),"flags":u8(d,b+16)})
    colonies=[]
    for i in range(nc):
        b=COLONY_DATA+i*COLONY_SIZE
        colonies.append({
            "index":i,"owner_id":u8(d,b),"allocated_to":u8(d,b+1),"planet_id":u8(d,b+2),
            "officer_id":u16(d,b+4),"is_outpost":u8(d,b+6),"morale":u8(d,b+7),
            "pollution":u16(d,b+8),"population":u8(d,b+10),"assignment":u8(d,b+11),
            "pop_raised":[u16(d,b+0xB4+2*j) for j in range(10)],
            "pop_grow":[u16(d,b+0xC8+2*j) for j in range(10)],
            "num_turns_existed":u8(d,b+0xDC),"food2_per_farmer":u8(d,b+0xDD),
            "industry_per_worker":u8(d,b+0xDE),"research_per_scientist":u8(d,b+0xDF),
            "max_farms":u8(d,b+0xE0),"max_population":u8(d,b+0xE1),"climate":u8(d,b+0xE2),
            "ground_strength":u16(d,b+0xE3),"space_strength":u16(d,b+0xE5),
            "food":u16(d,b+0xE7),"industry":u16(d,b+0xE9),"research":u16(d,b+0xEB)})
    return {"file":str(path),"size":len(d),"colony_count":nc,"planet_count":np,"colonies":colonies,"planets":planets}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('save',type=Path); ap.add_argument('--compact',action='store_true'); a=ap.parse_args()
    try: obj=parse(a.save)
    except (OSError,SaveFormatError) as e: ap.error(str(e))
    print(json.dumps(obj, indent=None if a.compact else 2, sort_keys=True))
if __name__=='__main__': main()
