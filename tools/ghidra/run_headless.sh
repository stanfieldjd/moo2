#!/usr/bin/env bash
set -euo pipefail
: "${GHIDRA_HOME:?Set GHIDRA_HOME to the Ghidra installation directory}"
: "${MOO2_V131_EXE:?Set MOO2_V131_EXE to the verified official v1.31 ORION2.EXE}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="${ROOT}/.ghidra-projects"
PROJECT_NAME="moo2-v131"
mkdir -p "$PROJECT_DIR" "${ROOT}/decompilation/ghidra"
exec "${GHIDRA_HOME}/support/analyzeHeadless" \
  "$PROJECT_DIR" "$PROJECT_NAME" \
  -import "$MOO2_V131_EXE" \
  -overwrite \
  -analysisTimeoutPerFile 1800 \
  -scriptPath "${ROOT}/ghidra_scripts" \
  -postScript ExportDecompiledFunctions.java "${ROOT}/decompilation/ghidra"
