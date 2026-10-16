#!/usr/bin/env python3
"""Audit MOO2 v1.31 Colony_Food_Maintenance_ against the authentic EXE/LE CODE.

Verifies complete named-body bytes, global symbol identity, opcode anchors and
a controlled source-derived classification model. Fixtures are NOT DOS runtime
differential tests, and unproven gameplay meanings are not assigned.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE_SHA = "4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA = "f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
START, SIZE = 0xCEB4B, 330
BODY_SHA = "005961c516ea2f30e4534b7e7c5eb4ede279dc9c53d89a49fd2f5214b5f84030"
ANOMALY_START, ANOMALY_SIZE = 0x1341E, 80
ANOMALY_SHA = "dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4"
RX = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$", re.I)

# A selection covering both original exception branches, source DATA pointers,
# 8-byte initialization, player-flag triage, 4 independent counters, rounding,
# register-preserving final jump and its shared return tail.
ANCHORS = {
    0xCEB4B: ("push", "ebx"),
    0xCEB50: ("enter", "0x8,0x0"),
    0xCEB56: ("movsx", "ax,byte ptr [eax]"),
    0xCEB5F: ("sub", "eax,dword ptr ds:0x1ab18"),
    0xCEB65: ("mov", "edi,0x169"),
    0xCEB6B: ("idiv", "edi"),
    0xCEB6D: ("cwde", ""),
    0xCEB6E: ("call", "0x1341e"),
    0xCEB73: ("test", "ax,ax"),
    0xCEB76: ("je", "0xceb84"),
    0xCEB78: ("mov", "byte ptr [ecx+0xef],0x0"),
    0xCEB7F: ("jmp", "0xd1f97"),
    0xCEB84: ("mov", "ebx,0x8"),
    0xCEB89: ("lea", "eax,[ecx+0x104]"),
    0xCEB8F: ("xor", "edx,edx"),
    0xCEB91: ("call", "0x119c70"),
    0xCEB96: ("mov", "byte ptr [ecx+0xfc],0x0"),
    0xCEB9D: ("mov", "byte ptr [ecx+0xff],0x0"),
    0xCEBA4: ("xor", "esi,esi"),
    0xCEBA6: ("mov", "byte ptr [ecx+0xfe],0x0"),
    0xCEBAD: ("lea", "edi,[ecx+0xc]"),
    0xCEBB0: ("mov", "byte ptr [ecx+0xfd],0x0"),
    0xCEBB7: ("jmp", "0xcec4f"),
    0xCEBBC: ("movsx", "eax,si"),
    0xCEBBF: ("mov", "edx,dword ptr [edi+eax*4]"),
    0xCEBC2: ("mov", "eax,dword ptr [edi+eax*4]"),
    0xCEBC5: ("shl", "eax,0x15"),
    0xCEBC8: ("shr", "eax,0x1f"),
    0xCEBCB: ("and", "edx,0xf"),
    0xCEBD1: ("cmp", "dx,0x8"),
    0xCEBD5: ("jge", "0xcec3d"),
    0xCEBDE: ("imul", "eax,eax,0xea9"),
    0xCEBE4: ("mov", "ebx,dword ptr ds:0x1ff98"),
    0xCEBEC: ("cmp", "byte ptr [eax+0x8b0],0x0"),
    0xCEBF3: ("je", "0xcebfc"),
    0xCEBF5: ("mov", "eax,0x1"),
    0xCEBFA: ("jmp", "0xcec0e"),
    0xCEBFC: ("cmp", "byte ptr [eax+0x8b1],0x0"),
    0xCEC03: ("je", "0xcec09"),
    0xCEC05: ("xor", "eax,eax"),
    0xCEC07: ("jmp", "0xcec0e"),
    0xCEC09: ("mov", "eax,0x2"),
    0xCEC0E: ("cmp", "dx,word ptr [ebp-0x4]"),
    0xCEC12: ("jne", "0xcec1c"),
    0xCEC14: ("add", "byte ptr [ecx+0xfc],al"),
    0xCEC1C: ("cmp", "word ptr [ebp-0x8],0x0"),
    0xCEC21: ("je", "0xcec2b"),
    0xCEC23: ("add", "byte ptr [ecx+0xfe],al"),
    0xCEC2B: ("add", "byte ptr [ecx+0xfd],al"),
    0xCEC34: ("add", "byte ptr [ecx+edx*1+0x104],al"),
    0xCEC3D: ("cmp", "dx,0x9"),
    0xCEC41: ("jne", "0xcec4e"),
    0xCEC43: ("mov", "eax,0x2"),
    0xCEC48: ("add", "byte ptr [ecx+0xff],al"),
    0xCEC4E: ("inc", "esi"),
    0xCEC4F: ("movzx", "ax,byte ptr [ecx+0xa]"),
    0xCEC57: ("jl", "0xcebbc"),
    0xCEC5D: ("movzx", "dx,byte ptr [ecx+0xfc]"),
    0xCEC65: ("movzx", "ax,byte ptr [ecx+0xff]"),
    0xCEC6D: ("add", "edx,eax"),
    0xCEC6F: ("movzx", "ax,byte ptr [ecx+0xfe]"),
    0xCEC77: ("add", "eax,edx"),
    0xCEC79: ("movzx", "dx,byte ptr [ecx+0xfd]"),
    0xCEC81: ("add", "eax,edx"),
    0xCEC83: ("cwde", ""),
    0xCEC84: ("inc", "eax"),
    0xCEC85: ("cdq", ""),
    0xCEC86: ("sub", "eax,edx"),
    0xCEC88: ("sar", "eax,1"),
    0xCEC8A: ("mov", "byte ptr [ecx+0xef],al"),
    0xCEC90: ("jmp", "0xd1f97"),
    0xD1F97: ("leave", ""),
    0xD1F9D: ("ret", ""),
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source_instruction(code_path, address):
    p = subprocess.run(
        ["objdump", "-D", "-b", "binary", "-m", "i386", "-M", "intel",
         f"--start-address=0x{address:x}", f"--stop-address=0x{address+16:x}",
         str(code_path)],
        check=True, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        m = RX.match(line)
        if m and int(m[1], 16) == address:
            return m[3].lower(), m[4].strip().lower()
    raise ValueError(f"No full instruction at CODE {address:#x}")

def model_food(entries, signed_owner, flags, anomaly=False, prior=None):
    """Controlled reproduction of observed branch/byte-write behavior.

    The synthetic tuples in flags are exactly two boolean player fields,
    not assumed gameplay race attributes.
    """
    if len(flags) != 8 or not (-128 <= signed_owner <= 127):
        raise ValueError("Expected 8 player records and signed BYTE owner")
    if len(entries) > 255:
        raise ValueError("Source colony count is one unsigned byte")
    if prior is None:
        prior = {"category": [0, 0, 0, 0], "per_player": [0] * 8}
    if anomaly:
        return {"value_F0": 0, "category": prior["category"][:],
                "per_player": prior["per_player"][:]}
    # +0xfc, +0xff, +0xfd, +0xfe are distinct physical byte counters.
    categories = [0] * 4
    per_player = [0] * 8
    for entry in entries:
        if not 0 <= entry <= 0xffffffff:
            raise ValueError("Source list elements are DWORDs")
        tag = entry & 0xf
        bit10 = (entry >> 10) & 1
        if tag < 8:
            first, second = flags[tag]
            amount = 1 if first else (0 if second else 2)
            ix = 0 if tag == signed_owner else (3 if bit10 else 2)
            categories[ix] = (categories[ix] + amount) & 0xff
            per_player[tag] = (per_player[tag] + amount) & 0xff
        elif tag == 9:
            categories[1] = (categories[1] + 2) & 0xff
    # Four BYTE counters are zero-extended and summed; CWDE sign-extends AX.
    # Here each category <=255, so the 16-bit result cannot overflow.
    total = sum(categories)
    return {"value_F0": ((total + 1) // 2) & 0xff,
            "category": categories, "per_player": per_player}

def fixtures():
    all_first = [(True, False)] * 8
    none = [(False, False)] * 8
    second_only = [(False, True)] * 8
    assert model_food([], 0, none)["value_F0"] == 0
    own = model_food([0], 0, all_first)
    assert own == {"value_F0": 1, "category": [1, 0, 0, 0],
                   "per_player": [1, 0, 0, 0, 0, 0, 0, 0]}
    assert model_food([1], 0, second_only)["category"] == [0, 0, 0, 0]
    assert model_food([1], 0, none)["category"] == [0, 0, 2, 0]
    assert model_food([1 | 0x400], 0, none)["category"] == [0, 0, 0, 2]
    assert model_food([9], 0, all_first)["category"] == [0, 2, 0, 0]
    assert model_food([8, 10, 15], 0, all_first)["value_F0"] == 0
    assert model_food([0, 9], 0, all_first)["value_F0"] == 2
    bulk = model_food([9] * 255, 0, none)
    assert bulk["category"] == [0, 254, 0, 0] and bulk["value_F0"] == 127
    previous = {"category": [5, 7, 11, 13], "per_player": [9] * 8}
    out = model_food([0], 0, all_first, anomaly=True, prior=previous)
    assert out["value_F0"] == 0 and out["category"] == previous["category"]
    assert out["per_player"] == previous["per_player"]
    return 10

def audit(exe_path, code_path):
    exe, code = exe_path.read_bytes(), code_path.read_bytes()
    if digest(exe) != EXE_SHA:
        raise ValueError("Original executable hash mismatch")
    if len(code) != 1410709 or digest(code) != CODE_SHA:
        raise ValueError("Original Watcom LE CODE identity mismatch")
    functions = {r["name"]: r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    for name, start, size, expected_hash in (
        ("Colony_Food_Maintenance_", START, SIZE, BODY_SHA),
        ("Event_Check_Space_Anomaly_", ANOMALY_START, ANOMALY_SIZE, ANOMALY_SHA),
    ):
        original = functions[name]
        if (int(original["offset"]), int(original["inferred_size"])) != (start, size):
            raise ValueError(f"Watcom named function extent changed: {name}")
        if digest(code[start:start+size]) != expected_hash:
            raise ValueError(f"Full original machine-code digest changed: {name}")
    symbols = {(r["name"], r["segment"]): int(r["offset"])
               for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for key, original_address in {
        ("_colony", "2"): 0x1AB18, ("_player", "2"): 0x1FF98
    }.items():
        if symbols.get(key) != original_address:
            raise ValueError(f"Watcom global symbol mismatch: {key}")
    for address, expected in ANCHORS.items():
        got = source_instruction(code_path, address)
        if got != expected:
            raise ValueError(f"CODE {address:#x}: {got}, expected {expected}")
    checks = fixtures()
    return {
        "status": "source-verified-static-reconstruction",
        "source_sha256": EXE_SHA, "LE_CODE_sha256": CODE_SHA,
        "named_full_bodies": [
            {"name": "Colony_Food_Maintenance_", "CODE_offset": hex(START),
             "bytes": SIZE, "sha256": BODY_SHA},
            {"name": "Event_Check_Space_Anomaly_", "CODE_offset": hex(ANOMALY_START),
             "bytes": ANOMALY_SIZE, "sha256": ANOMALY_SHA}],
        "instruction_checkpoints": len(ANCHORS),
        "independent_controlled_fixtures": checks,
        "exception": "anomaly event -> zero BYTE +0xef, preserve existing four category and eight per-player bytes",
        "non_exception": "zero four BYTE counters at +0xfc/+0xff/+0xfe/+0xfd and 8 bytes +0x104..+0x10b; traverse DWORD entries from +0x0c with BYTE+0x0a count",
        "player_states": "for tag 0..7: player BYTE+0x8b0 nonzero ->1; otherwise BYTE+0x8b1 nonzero ->0; otherwise ->2",
        "classification": "owner==tag -> BYTE+0xfc; otherwise bit10=1 -> BYTE+0xfe; otherwise -> BYTE+0xfd; per-tag BYTE+0x104+tag always also increments",
        "special_tag": "tag 9 increments BYTE+0xff by 2; tags 8,10..15 have no effect",
        "output": "sum of four zero-extended category bytes, ceil(total/2) for nonnegative counters; low result byte -> BYTE+0xef",
        "shared_tail": "CODE 0xd1f97 leave;pop edi;pop esi;pop edx;pop ecx;pop ebx;ret",
        "limitations": [
            "No original DOS dynamic differential execution",
            "Underlying gameplay meanings of player flags and list DWORD remain unverified",
            "No native implementation or game-wide feature completion claimed",
        ],
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--code", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(args.exe, args.code)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
