# hyperv-opsec-auditor

Read-only **offline** Hyper-V security posture auditing from supplied JSON evidence. Version `0.1.0a1` is an alpha/prerelease: no live Windows collector, no host connections and no automatic remediation.

Covers supplied evidence for host support/updates, management privileges, WinRM, VM/vSwitch/VLAN isolation, Secure Boot/vTPM/shielding, VHDX/checkpoint/backup protection, audit logging and verified recovery readiness. A pass means the supplied evidence matches the baseline, not that infrastructure was independently inspected. Real Hyper-V/HGS/restore tests are **NOT RUN**.

## Install and run

Python 3.12 or newer. Runtime has no third-party dependencies. From the source checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/hyperv-opsec-auditor validate fixtures/healthy.json
.venv/bin/hyperv-opsec-auditor audit fixtures/healthy.json --as-of 2026-10-09T00:00:00Z --format markdown
.venv/bin/hyperv-opsec-auditor audit fixtures/unsafe.json --as-of 2026-10-09T00:00:00Z --format json --fail-on fail
```

The final command intentionally exits 1. The fixtures are fictional. A fixed `--as-of` makes this demonstration repeatable; omit it to use current UTC for real supplied evidence. See [user guide](docs/user-guide.md) for Windows, wheel/offline installation, status/exit codes and input preparation.

## Validation and development

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/validate_docs.py
.venv/bin/python tools/scan_secrets.py
.venv/bin/python tools/build_release.py
.venv/bin/python tools/package_smoke.py
```

[Project documentation](docs/README.md) includes requirements, threat model, architecture, ADR, rule matrix, [MVP plan](docs/mvp-plan.md) and [Windows lab procedure](docs/lab.md). CI uses synthetic data on hosted runners, including Windows offline Python tests; this is not Hyper-V platform validation. Do not put real credentials or raw production evidence in this public repository.
