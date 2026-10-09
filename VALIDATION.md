# Validation record — 0.1.0a1

Current cloud machine: Linux, Python 3.12.14. All evidence is fictional.

- Unit/integration suite: 38 tests passed, including malformed input, every rule family, freshness, no-mutation and exclusive output checks.
- External JSON Schema validation parity tested using pinned jsonschema 4.26.0.
- Coverage: 96% (minimum 85%); documentation links and three schema-valid synthetic fixtures passed.
- Public-file credential-pattern scan: no matches; this is not a comprehensive secret audit.
- Pinned/hash-verified dependencies installed in a fresh venv; wheel installed without runtime dependencies. Own sdist rebuilt and installed in a second clean venv; both ran validate/audit successfully.
- SHA256SUMS checked against every prepared local asset.
- GitHub Actions workflow is configured for Ubuntu and Windows hosted offline tests. Actual remote run status must be checked separately.
- Real Windows Server Hyper-V, WinRM, AD/effective ACL, VLAN isolation, supported Secure Boot/vTPM/Shielded/HGS and backup/recovery tests: NOT RUN.

A pass in synthetic evidence is not a statement about a real host. Release candidate files are local until GitHub release publication is verified.
