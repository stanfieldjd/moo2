#!/usr/bin/env python3
"""Development-only disassembler for verified official MOO2 v1.31 routines."""
import argparse, subprocess, tempfile
from pathlib import Path
import original_probe as probe


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('exe', type=Path)
    ap.add_argument('symbol')
    ap.add_argument('--bytes', type=int, default=2048, dest='count')
    a=ap.parse_args()
    r=probe.inspect(a.exe)
    if not r['official_v131_reference']:
        raise SystemExit('refusing to disassemble an unverified executable')
    sym=r['gameplay_functions'].get(a.symbol)
    if not sym:
        raise SystemExit(f'unknown/unresolved gameplay symbol: {a.symbol}')
    data=a.exe.read_bytes(); start=sym['file_offset']; blob=data[start:start+a.count]
    with tempfile.NamedTemporaryFile() as f:
        f.write(blob); f.flush()
        cp=subprocess.run(['objdump','-D','-b','binary','-m','i386','-M','intel',f.name], text=True, capture_output=True, check=True)
    print(f'# {a.symbol} {sym["segment"]:04x}:{sym["offset"]:08x} file=0x{start:x}')
    lines=cp.stdout.splitlines()
    # Strip objdump temp-file banner while preserving the actual instruction listing.
    marker=next((i for i,x in enumerate(lines) if x.startswith('Disassembly of section')),0)
    print('\n'.join(lines[marker:]))

if __name__=='__main__': main()
