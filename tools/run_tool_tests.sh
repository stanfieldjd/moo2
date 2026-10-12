#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "${MOO2_V131_EXE:-}" ]]; then
  python3 tools/test_original_probe.py "$MOO2_V131_EXE"
else
  echo "original_probe integration test: SKIP (set MOO2_V131_EXE to a lawful local ORION2.EXE)"
fi
python3 tools/relocate_le_v131.py --self-test
if [[ -n "${MOO2_V131_EXE:-}" ]] && command -v as >/dev/null && command -v ld >/dev/null; then
  rea_test_tmp="$(mktemp -d)"
  trap 'rm -rf "$rea_test_tmp"' EXIT
  python3 tools/relocate_le_v131.py "$MOO2_V131_EXE" "$rea_test_tmp/relocated"
  python3 tools/build_rea_window.py "$MOO2_V131_EXE" "$rea_test_tmp/relocated" "$rea_test_tmp/window"
else
  echo "REA ELF integration: SKIP (requires MOO2_V131_EXE and binutils)"
fi
python3 tools/test_save_inspect.py
