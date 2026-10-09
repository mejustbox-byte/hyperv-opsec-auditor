# Release notes

## 0.1.0a1 — alpha / prerelease candidate

First useful offline CLI: audit/validate/rules, bundled JSON Schema 1.0, ten rule families HV-01..HV-10, JSON and readable Markdown reports, evidence pointers, severity, manual remediation, pass/fail/unknown/not_run, freshness limits and visible exclusions. Input is bounded and rejects malformed data, duplicate keys/IDs, non-finite numbers and unsupported fields. Output files are created exclusively without overwriting existing paths.

Includes synthetic healthy/unsafe/partial fixtures, unit and subprocess integration tests, hashed build/test lock, wheel/sdist packaging, clean-install smoke tests, hosted Linux/Windows offline CI and full design/user/lab documentation.

**Platform validation NOT RUN:** real Windows Server Hyper-V, effective AD/WinRM/storage configuration, VM/vSwitch/VLAN runtime isolation, Secure Boot supported guests, vTPM/Shielded VM/HGS attestation/key recovery, backup immutability and real ransomware-recovery drill/RPO/RTO. No live collector is included. Synthetic and hosted Windows offline tests are not real infrastructure validation. The release must remain a prerelease until that acceptance is completed.

Installation: Python >=3.12; verify SHA256SUMS, then `python -m pip install --no-index --no-deps hyperv_opsec_auditor-0.1.0a1-py3-none-any.whl`. Run `hyperv-opsec-auditor audit healthy.json --as-of 2026-10-09T00:00:00Z --format json` using the attached fictional sample. Source installation and real-evidence preparation are documented in docs/user-guide.md. Runtime dependencies: none.

Actual local validation results are stored in VALIDATION.md. A local build or Git tag is not evidence of PR merge, remote CI or GitHub Release publication; those operations must be verified separately.
