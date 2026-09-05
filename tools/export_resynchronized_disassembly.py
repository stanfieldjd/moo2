#!/usr/bin/env python3
"""Disassemble each known CODE-symbol interval from its exact entry address.

A single linear objdump pass loses synchronization when Watcom embeds switch/data
tables in the code object.  Restarting decoding at every surviving CODE symbol
restores those authoritative entry points without changing the binary.
"""
import csv,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; BIN=ROOT/'decompilation/code_object_1.bin'; FUN=ROOT/'decompilation/functions.csv'
OUT=ROOT/'decompilation/code_object_1_resynced.disasm'; MAN=ROOT/'decompilation/resynced_disassembly.json'
rows=list(csv.DictReader(FUN.open())); starts=sorted({int(r['offset']) for r in rows}); size=BIN.stat().st_size
parts=[]; failed=[]
for i,start in enumerate(starts):
 end=starts[i+1] if i+1<len(starts) else size
 # Empty/duplicate intervals were removed by set above.
 p=subprocess.run(['objdump','-D','-b','binary','-m','i386','-M','intel',f'--start-address={start}',f'--stop-address={end}',str(BIN)],text=True,capture_output=True)
 if p.returncode: failed.append(start); continue
 lines=[]
 for line in p.stdout.splitlines():
  if line.lstrip().startswith(tuple('0123456789abcdefABCDEF')) and ':' in line: lines.append(line)
 parts.append(f';; ENTRY 0x{start:x} STOP 0x{end:x}\n'+'\n'.join(lines)+'\n')
OUT.write_text('\n'.join(parts))
MAN.write_text(json.dumps({'unique_code_entries':len(starts),'intervals_exported':len(parts),'failed_intervals':len(failed),
 'method':'GNU objdump i386 restarted at every surviving Watcom CODE-symbol entry to prevent embedded-data desynchronization'},indent=2)+'\n')
print(MAN.read_text(),end='')
