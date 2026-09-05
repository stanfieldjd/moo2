#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "${MOO2_V131_EXE:-}" ]]; then
  python3 tools/test_original_probe.py "$MOO2_V131_EXE"
else
  echo "original_probe integration test: SKIP (set MOO2_V131_EXE to a lawful local ORION2.EXE)"
fi
python3 tools/test_save_inspect.py
