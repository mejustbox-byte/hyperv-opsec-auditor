#!/usr/bin/env bash
set -euo pipefail
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "Требуется Python >=3.12")'
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/hyperv-opsec-auditor validate fixtures/healthy.json
