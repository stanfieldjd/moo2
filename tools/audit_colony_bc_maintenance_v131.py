#!/usr/bin/env python3
"""Source-verified MOO2 v1.31 Colony_BC_Maintenance_ static reconstruction.

Reproduces the named original function's complete byte identity, typed CODE/DATA
references, full building maintenance table, anomaly predicate, branch anchors,
shared epilogue and arithmetic. Does NOT claim DOS runtime equivalence.
"""
import argparse
import csv
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE_SHA = "4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA = "f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
DATA_SHA = "082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b"
MAIN_START, MAIN_SIZE = 0xD094F, 197
MAIN_SHA = "2a9e964cfbd9c9068ba9998f3d4e8c55ddc39bb4546107fc097a915b6133bfe5"
EVENT_START, EVENT_SIZE = 0x1341E, 80
EVENT_SHA = "dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4"
BUILDINGS_START, BUILDINGS_STRIDE, BUILDINGS_COUNT = 0x6B3D, 19, 49
BUILDINGS_SHA = "5d20847fb80f0a7668ead6e3afc36300cbce9edf11bee04b77903711800cf9e2"
CLIMATE_START = 0xCD4BA
CLIMATE_MODIFIERS = (50, 25, 0, 25, 0)

# Anchors deliberately include both branch paths and the shared return tail.
OPS = {
    0xD095A: ("cmp", "byte ptr [eax+0xa],0x0"),
    0xD095E: ("jne", "0xd096c"),
    0xD0960: ("mov", "byte ptr [eax+0xf2],0x0"),
    0xD0967: ("jmp", "0xd09f7"),
    0xD096C: ("sub", "eax,dword ptr ds:0x1ab18"),
    0xD0972: ("mov", "ecx,0x169"),
    0xD0978: ("idiv", "ecx"),
    0xD097B: ("call", "0x1341e"),
    0xD0980: ("test", "ax,ax"),
    0xD0983: ("je", "0xd098e"),
    0xD0985: ("mov", "byte ptr [ebx+0xf2],0x0"),
    0xD098C: ("jmp", "0xd09f7"),
    0xD0994: ("add", "ecx,0x136"),
    0xD09A5: ("add", "edi,ecx"),
    0xD09A7: ("cmp", "byte ptr [edi],0x0"),
    0xD09AA: ("je", "0xd09b8"),
    0xD09AC: ("imul", "ecx,ecx,0x13"),
    0xD09AF: ("movsx", "ecx,word ptr [ecx+0x6b49]"),
    0xD09B8: ("inc", "edx"),
    0xD09B9: ("cmp", "dx,0x31"),
    0xD09BD: ("jl", "0xd099f"),
    0xD09BF: ("imul", "esi,esi,0x64"),
    0xD09C2: ("movzx", "ecx,byte ptr [ebx+0x114]"),
    0xD09C9: ("imul", "ecx,ecx,0x64"),
    0xD09D0: ("movzx", "ecx,byte ptr [ebx+0xe2]"),
    0xD09D7: ("movzx", "ecx,byte ptr [ecx+0xcd4ba]"),
    0xD09DE: ("add", "ecx,0x64"),
    0xD09E1: ("imul", "eax,ecx"),
    0xD09E4: ("add", "eax,0x1388"),
    0xD09E9: ("mov", "ecx,0x2710"),
    0xD09EF: ("idiv", "ecx"),
    0xD09F1: ("mov", "byte ptr [ebx+0xf2],al"),
    0xD09F7: ("movzx", "ax,byte ptr [ebx+0xf2]"),
    0xD09FF: ("mov", "dx,word ptr [ebx+0xed]"),
    0xD0A06: ("sub", "eax,edx"),
    0xD0A08: ("mov", "word ptr [ebx+0xf9],ax"),
    0xD0A0F: ("jmp", "0xd1f97"),
    0xD1F97: ("leave", ""),
    0xD1F9D: ("ret", ""),
    0x1341F: ("cmp", "byte ptr ds:0x22c86,0x2"),
    0x13428: ("cmp", "byte ptr ds:0x22c86,0x4"),
    0x13431: ("cmp", "byte ptr ds:0x22c86,0x6"),
    0x13441: ("mov", "eax,ds:0x1ab18"),
    0x1344B: ("imul", "eax,eax,0x11"),
    0x13454: ("movzx", "ax,byte ptr [edx+eax*1+0x2]"),
    0x1345A: ("cmp", "ax,word ptr ds:0x22c88"),
    0x13463: ("mov", "eax,0x1"),
    0x1346A: ("xor", "eax,eax"),
}
RX = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$", re.I)

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def rows(name):
    with (ROOT / "decompilation" / name).open(newline="") as file:
        return list(csv.DictReader(file))

def check_instructions(code):
    count = 0
    for at, expected in OPS.items():
        p = subprocess.run(
            ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel",
             f"--start-address=0x{at:x}", f"--stop-address=0x{at+16:x}", str(code)],
            check=True, capture_output=True, text=True,
        )
        found = None
        for line in p.stdout.splitlines():
            m = RX.match(line)
            if m and int(m[1], 16) == at:
                found = (m[3].lower(), m[4].strip().lower())
                break
        if found != expected:
            raise ValueError(f"CODE at {at:#x}: expected {expected}; got {found}")
        count += 1
    return count

def signed16(word):
    return word if word < 0x8000 else word - 0x10000

def trunc_div(numer, denom):
    if denom <= 0:
        raise ValueError("positive divisor required")
    return (1 if numer >= 0 else -1) * (abs(numer) // denom)

def arithmetic(building_flags, building_maintenance, extra, climate, paid):
    """Reference for observed integer arithmetic only; inputs are controlled fixtures."""
    if len(building_flags) != BUILDINGS_COUNT or len(building_maintenance) != BUILDINGS_COUNT:
        raise ValueError("source uses 49 building entries")
    if not 0 <= climate < len(CLIMATE_MODIFIERS):
        raise ValueError("climate index outside verified table; original bounds not established")
    if not 0 <= extra <= 255:
        raise ValueError("extra byte outside domain")
    total = sum(v for active, v in zip(building_flags, building_maintenance) if active)
    raw = ((total + extra) * 100) * (100 + CLIMATE_MODIFIERS[climate]) + 5000
    # For these fixed fixtures, intermediates must stay within signed 32-bit source arithmetic.
    if not -(1<<31) <= raw < (1<<31):
        raise ValueError("32-bit signed overflow not modeled")
    bc = trunc_div(raw, 10000) & 0xFF
    net_word = (bc - (paid & 0xFFFF)) & 0xFFFF
    return bc, signed16(net_word)

def audit(exe_path, code_path, data_path):
    exe, code, data = (p.read_bytes() for p in (exe_path, code_path, data_path))
    for name, blob, digest in (
        ("original EXE", exe, EXE_SHA), ("LE CODE", code, CODE_SHA),
        ("LE initialized DATA", data, DATA_SHA)
    ):
        if sha(blob) != digest:
            raise ValueError(f"{name} SHA256 differs from authenticated source")
    if len(code) != 1410709 or len(data) != 81920:
        raise ValueError("LE segment length mismatch")
    fs = {r["name"]: r for r in rows("functions.csv")}
    for name, start, size, digest in (
        ("Colony_BC_Maintenance_", MAIN_START, MAIN_SIZE, MAIN_SHA),
        ("Event_Check_Space_Anomaly_", EVENT_START, EVENT_SIZE, EVENT_SHA),
    ):
        r = fs[name]
        if (int(r["offset"]), int(r["inferred_size"])) != (start, size):
            raise ValueError(f"source function extent differs: {name}")
        if sha(code[start:start+size]) != digest:
            raise ValueError(f"complete original function bytes differ: {name}")
    syms = {(r["name"], r["segment"]): int(r["offset"]) for r in rows("symbols.csv")}
    for name, segment, off in (
        ("_buildings", "2", BUILDINGS_START),
        ("_colony", "2", 0x1AB18),
        ("_planet", "2", 0x1B0D4),
        ("_climate_maintenance_modifiers", "1", CLIMATE_START),
    ):
        if syms.get((name, segment)) != off:
            raise ValueError(f"symbol identity mismatch: {name}")
    table = data[BUILDINGS_START:BUILDINGS_START+BUILDINGS_COUNT*BUILDINGS_STRIDE]
    if sha(table) != BUILDINGS_SHA:
        raise ValueError("49-building original DATA table changed")
    maintenance = [struct.unpack_from("<h", table, n*BUILDINGS_STRIDE+12)[0]
                   for n in range(BUILDINGS_COUNT)]
    if tuple(code[CLIMATE_START:CLIMATE_START+5]) != CLIMATE_MODIFIERS:
        raise ValueError("five climate maintenance modifiers changed")
    checkpoints = check_instructions(code_path)
    # Controlled independent fixtures: source's rounding, byte store and signed WORD net.
    flags = [False]*49
    assert arithmetic(flags, maintenance, 0, 2, 0) == (0, 0)
    flags[1] = True   # source maintenance 1
    assert arithmetic(flags, maintenance, 0, 2, 0) == (1, 1)
    assert arithmetic(flags, maintenance, 0, 0, 2) == (2, 0)
    assert arithmetic(flags, maintenance, 0, 2, 4) == (1, -3)
    return {
        "status":"source-verified-static-reconstruction",
        "original_EXE_SHA256":EXE_SHA,
        "authenticated_CODE_SHA256":CODE_SHA,
        "authenticated_initialized_DATA_SHA256":DATA_SHA,
        "full_named_bodies":[
            {"name":"Colony_BC_Maintenance_","offset":hex(MAIN_START),"bytes":MAIN_SIZE,"sha256":MAIN_SHA},
            {"name":"Event_Check_Space_Anomaly_","offset":hex(EVENT_START),"bytes":EVENT_SIZE,"sha256":EVENT_SHA},
        ],
        "verified_instruction_checkpoints":checkpoints,
        "building_maintenance_DATA":{"symbol":"_buildings","offset":hex(BUILDINGS_START),
            "record_stride":BUILDINGS_STRIDE,"count":BUILDINGS_COUNT,
            "maintenance_signed_WORD_offset":12,"values":maintenance,
            "table_SHA256":BUILDINGS_SHA},
        "climate_CODE":{"symbol":"_climate_maintenance_modifiers",
                        "offset":hex(CLIMATE_START),"values":list(CLIMATE_MODIFIERS)},
        "observed_event_gate":"Event_Check_Space_Anomaly_ returns nonzero only for event code 2/4/6 and matching planet anomaly ID",
        "observed_maintenance":"zero when colony BYTE+0x0a=0 or Event_Check_Space_Anomaly_ returns nonzero; otherwise 49 buildings + BYTE+0x114 scaled by climate modifier with +5000 then signed divide by 10000, stored low 8 bits at +0xf2",
        "observed_net":"BYTE+0xf2 minus WORD+0xed; low WORD stored at +0xf9",
        "source_shared_epilogue":"unconditional JMP 0xd1f97 to leave/pop/pop/pop/pop/pop/ret",
        "controlled_arithmetic_fixtures":4,
        "limitations":["No DOS runtime differential test", "No guarantee of in-game input ranges",
                       "No claim that this procedure accounts for all upkeep paths"],
    }

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--code", required=True, type=Path)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args=parser.parse_args()
    result=audit(args.exe,args.code,args.data)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
