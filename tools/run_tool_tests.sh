#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "${MOO2_V131_EXE:-}" ]]; then
  python3 tools/test_original_probe.py "$MOO2_V131_EXE"
  python3 tools/test_rea_direct_calls.py "$MOO2_V131_EXE"
  python3 tools/test_rea_colony_yields.py "$MOO2_V131_EXE"
  python3 tools/test_rea_colony_tax.py "$MOO2_V131_EXE"
else
  echo "original_probe integration test: SKIP (set MOO2_V131_EXE to a lawful local ORION2.EXE)"
fi
python3 tools/relocate_le_v131.py --self-test
python3 tools/test_lbx_graphics.py
python3 tools/test_export_lbx_animation.py
if [[ -n "${MOO2_V131_EXE:-}" ]] && command -v as >/dev/null && command -v ld >/dev/null; then
  rea_test_tmp="$(mktemp -d)"
  trap 'rm -rf "$rea_test_tmp"' EXIT
  python3 tools/relocate_le_v131.py "$MOO2_V131_EXE" "$rea_test_tmp/relocated"
  python3 tools/build_rea_window.py "$MOO2_V131_EXE" "$rea_test_tmp/relocated" "$rea_test_tmp/window"
  python3 tools/build_rea_window.py "$MOO2_V131_EXE" "$rea_test_tmp/relocated" "$rea_test_tmp/window-cross-boundary" --first-page 205 --page-count 7 --entry-symbol Planet_Max_Population_For_Player_
  MOO2_REA_WINDOW="$rea_test_tmp/window-cross-boundary" python3 - <<'PY'
import json
import os
import struct
from pathlib import Path

root = Path(os.environ["MOO2_REA_WINDOW"])
m = json.loads((root / "analysis.manifest.json").read_text())
assert m["code_window_vaddr"] == "0xdd000"
assert m["analysis_entry_vaddr"] == "0xe0b4f"
assert m["elf_sha256"] == "5afad26278a40de4c0cecf9047dff2e3bb4d7993bcff43d03df24d475c4efeec"
b = (root / "analysis.elf").read_bytes()
fields = struct.unpack_from("<HHIIIIIHHHHHH", b, 16)
loads = [x for i in range(fields[9]) if (x := struct.unpack_from("<IIIIIIII", b, fields[4] + i * fields[8]))[0] == 1]
code = next(x for x in loads if x[2] == 0xdd000)
destination = 0xdeb17
assert code[2] <= destination and destination + 6 <= code[2] + code[4]
offset = code[1] + destination - code[2]
assert b[offset:offset + 6] == bytes.fromhex("c95f5e595bc3")
print("REA cross-function epilogue coverage: PASS")
PY
else
  echo "REA ELF integration: SKIP (requires MOO2_V131_EXE and binutils)"
fi
python3 tools/test_save_inspect.py
