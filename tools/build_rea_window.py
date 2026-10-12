#!/usr/bin/env python3
"""Build a bounded Ghidra/REA ELF32 analysis window from verified MOO2 LE images.

This creates a synthetic *analysis container*, not a playable or original ELF.
It writes only to a new local output directory. No game bytes are committed.
"""
import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RELOCATED


def digest(data):
    return hashlib.sha256(data).hexdigest()


def make_window(original, relocated_dir, output_dir, first_page, page_count, entry_symbol):
    if output_dir.exists():
        raise ValueError("output directory exists; refusing overwrite")
    info = probe.inspect(original)
    if info["sha256"] != probe.OFFICIAL_SHA256:
        raise ValueError("requires the official v1.31 executable")
    le = info["le_image"]
    if len(le["objects"]) != 2:
        raise ValueError("unexpected LE object count")
    code_obj, data_obj = le["objects"]
    code = (relocated_dir / "object_1.relocated.bin").read_bytes()
    data = (relocated_dir / "object_2.relocated.bin").read_bytes()
    if (digest(code), digest(data)) != EXPECTED_RELOCATED:
        raise ValueError("relocated image hashes do not match verified v1.31")
    if not shutil.which("as") or not shutil.which("ld"):
        raise RuntimeError("binutils assembler and linker are required")
    page_size = le["page_size"]
    start = first_page * page_size
    end = min(start + page_count * page_size, len(code))
    if first_page < 0 or page_count <= 0 or start >= len(code):
        raise ValueError("invalid bounded code page window")
    symbols = probe.global_symbols(original.read_bytes(), info["watcom"])
    entry = symbols.get(entry_symbol)
    if not entry or entry["segment"] != 1 or not start <= entry["offset"] < end:
        raise ValueError("the chosen entry symbol must be inside the window")
    relocated_code_window = code[start:end]
    mapped_data_size = data_obj["map_count"] * page_size
    if mapped_data_size > len(data) or any(data[mapped_data_size:]):
        raise ValueError("expected a zero-filled unmapped data tail")
    initialized_data = data[:mapped_data_size]
    base = code_obj["address"] + start
    entry_va = code_obj["address"] + entry["offset"]

    output_dir.mkdir(parents=True, exist_ok=False)
    try:
        code_path = output_dir / "code-window.bin"
        data_path = output_dir / "initialized-data.bin"
        asm = output_dir / "analysis.s"
        link = output_dir / "analysis.ld"
        objfile = output_dir / "analysis.o"
        elf = output_dir / "analysis.elf"
        code_path.write_bytes(relocated_code_window)
        data_path.write_bytes(initialized_data)
        lines = [".section .text,\"ax\",@progbits",
                 ".globl moo2_window_start", "moo2_window_start:",
                 f'.incbin "{code_path}"']
        aliases = {}
        for name, sym in symbols.items():
            if sym["segment"] != 1 or not (sym["kind"] & 4):
                continue
            offset = sym["offset"]
            if not start <= offset < end:
                continue
            alias = "moo2_" + re.sub(r"[^A-Za-z0-9_]", "_", name)
            if alias in aliases:
                alias = f"{alias}_{offset:x}"
            aliases[alias] = {"original": name, "vaddr": code_obj["address"] + offset}
            lines.extend([f".globl {alias}", f".type {alias},@function",
                          f".set {alias}, moo2_window_start+{offset - start}"])
        entry_alias = next((alias for alias, item in aliases.items()
                            if item["original"] == entry_symbol), None)
        if entry_alias is None:
            raise ValueError("entry is not an available code symbol")
        lines.extend([".section .data,\"aw\",@progbits",
                      ".globl moo2_data_start", "moo2_data_start:",
                      f'.incbin "{data_path}"',
                      ".section .bss,\"aw\",@nobits",
                      f".skip {len(data) - mapped_data_size}"])
        asm.write_text("\n".join(lines) + "\n")
        link.write_text(
            "OUTPUT_FORMAT(elf32-i386)\nOUTPUT_ARCH(i386)\n"
            f"ENTRY({entry_alias})\n"
            "PHDRS { code PT_LOAD FLAGS(5); data PT_LOAD FLAGS(6); }\n"
            "SECTIONS {\n"
            f" . = {hex(base)};\n .text : {{ *(.text) }} :code\n"
            f" . = {hex(data_obj['address'])};\n .data : {{ *(.data) }} :data\n"
            " .bss (NOLOAD) : { *(.bss) } :data\n"
            " /DISCARD/ : { *(.comment) *(.note*) }\n"
            "}\n"
        )
        subprocess.run(["as", "--32", "-o", str(objfile), str(asm)],
                       check=True, capture_output=True)
        subprocess.run(["ld", "-m", "elf_i386", "-T", str(link),
                        "-o", str(elf), str(objfile)], check=True, capture_output=True)
        result = elf.read_bytes()
        if result[:6] != b"\x7fELF\x01\x01":
            raise ValueError("output is not little-endian ELF32")
        fields = struct.unpack_from("<HHIIIIIHHHHHH", result, 16)
        if fields[1] != 3 or fields[3] != entry_va:
            raise ValueError("wrong ELF machine or entry point")
        segments = [struct.unpack_from("<IIIIIIII", result, fields[4] + i * fields[8])
                    for i in range(fields[9])]
        loads = [x for x in segments if x[0] == 1]
        if len(loads) != 2:
            raise ValueError("ELF must have exactly two load segments")
        a, b = loads
        if (a[2], a[4], a[5], a[6]) != (base, len(relocated_code_window), len(relocated_code_window), 5):
            raise ValueError("incorrect code memory mapping")
        if (b[2], b[4], b[5], b[6]) != (data_obj["address"], len(initialized_data), len(data), 6):
            raise ValueError("incorrect data/BSS mapping")
        if result[a[1]:a[1] + a[4]] != relocated_code_window:
            raise ValueError("code section byte comparison failed")
        if result[b[1]:b[1] + b[4]] != initialized_data:
            raise ValueError("initialized data section byte comparison failed")
        manifest = {
            "type": "synthetic static-analysis ELF32; not original game executable",
            "original_executable_sha256": info["sha256"],
            "code_object_relocated_sha256": digest(code),
            "data_object_relocated_sha256": digest(data),
            "elf_sha256": digest(result),
            "code_window_vaddr": hex(base),
            "code_window_size": len(relocated_code_window),
            "data_vaddr": hex(data_obj["address"]),
            "initialized_data_bytes": len(initialized_data),
            "zero_fill_bytes": len(data) - len(initialized_data),
            "analysis_entry_symbol": entry_symbol,
            "analysis_entry_vaddr": hex(entry_va),
            "labeled_code_symbol_count": len(aliases),
            "limitation": "Analysis entry is a symbol seed, not the original LE runtime entry; no DOS emulation.",
        }
        (output_dir / "analysis.manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        print(json.dumps(manifest, sort_keys=True))
    except BaseException:
        shutil.rmtree(output_dir)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("original", type=Path, help="lawfully supplied ORION2.EXE v1.31")
    p.add_argument("relocated_dir", type=Path, help="output directory of relocate_le_v131.py")
    p.add_argument("output_dir", type=Path, help="new local directory")
    p.add_argument("--first-page", type=int, default=208)
    p.add_argument("--page-count", type=int, default=4)
    p.add_argument("--entry-symbol", default="Colony_Pop_Grows_")
    args = p.parse_args()
    make_window(args.original, args.relocated_dir, args.output_dir,
                args.first_page, args.page_count, args.entry_symbol)


if __name__ == "__main__":
    main()
