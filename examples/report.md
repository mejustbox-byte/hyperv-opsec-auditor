# Hyper-V offline posture report

Scope: fictional-lab
Evidence: 2026-10-09T00:00:00Z; as of: 2026-10-09T00:00:00Z
Tool: 0.1.0a1; policy: mvp-baseline-1.0

**SYNTHETIC EVIDENCE — no real infrastructure validation.**

pass: 1 | fail: 9 | unknown: 0 | not_run: 0

## Limitations

- Offline evaluation of supplied evidence; no live Hyper-V, WinRM, network or backup access.
- Support, effective rights, isolation and restore attestations are supplied by the evidence owner, not independently verified.
- Synthetic results do not validate real infrastructure. Actual Windows Hyper-V/HGS and recovery tests are NOT RUN.
- No configuration changes or remediation are executed. Reports can contain sensitive pseudonymous evidence.

## HV-01 / fictional-lab: pass

Host support and updates — severity: high

All required supplied evidence for this rule matches the baseline.

Evidence:

- /host/hyperv\_role\_enabled: true; expected: true
- /host/supported\_configuration: true; expected: true
- /host/supported\_build: true; expected: true
- /host/security\_updates\_current: true; expected: true

Recommendation (manual review only): Review the supported host/build profile, enable the approved Hyper-V role and apply approved security updates.

## HV-02 / fictional-lab: fail

Management privileges — severity: critical

Evidence violates the baseline: unapproved administrators.

Evidence:

- /administration/effective\_rights\_reviewed: true; expected: true
- /administration/separate\_management\_accounts: true; expected: true
- /administration/management\_network\_isolated: true; expected: true
- /administration/actual\_admins: \[&quot;lab-admin&quot;, &quot;unexpected-admin&quot;\]; expected: \[&quot;lab-admin&quot;\]

Recommendation (manual review only): Review effective administrator rights, remove unapproved grants through an authorized change, and separate management accounts and networks.

## HV-03 / fictional-lab: fail

WinRM management security — severity: high

Evidence violates the baseline: allow\_unencrypted.

Evidence:

- /winrm/enabled: true; expected: true
- /winrm/https\_only: true; expected: true
- /winrm/certificate\_valid: true; expected: true
- /winrm/firewall\_scoped: true; expected: true
- /winrm/delegation\_restricted: true; expected: true
- /winrm/basic\_auth\_enabled: false; expected: false
- /winrm/allow\_unencrypted: true; expected: false

Recommendation (manual review only): Review HTTPS/certificate, disable Basic and unencrypted management, restrict firewall scope and delegation through an authorized change.

## HV-04 / fictional-lab: fail

Virtual network isolation — severity: high

Evidence violates the baseline: VLAN outside approved scope or empty VLAN set.

Evidence:

- /network/topology\_reviewed: true; expected: true
- /network/adapters/0/switch\_type: &quot;internal&quot;; expected: &quot;internal&quot;
- /network/adapters/0/vlans: \[99\]; expected: \[42\]
- /network/adapters/0/trunk: false; expected: false
- /network/adapters/0/sriov: false; expected: false

Recommendation (manual review only): Review the approved topology, VLAN allowlist, switch type, trunk and SR-IOV exceptions; validate isolation in the lab.

## HV-05 / vm-demo: fail

VM Secure Boot — severity: high

Evidence violates the baseline: secure\_boot\_enabled.

Evidence:

- /virtual\_machines/vms/0/generation: 2
- /virtual\_machines/vms/0/profile\_supported: true
- /virtual\_machines/vms/0/require\_secure\_boot: true; expected: true
- /virtual\_machines/vms/0/secure\_boot\_enabled: false; expected: true
- /virtual\_machines/vms/0/secure\_boot\_template\_approved: true; expected: true

Recommendation (manual review only): For supported generation 2 profiles, enable the approved Secure Boot trust template through a reviewed change.

## HV-06 / vm-demo: fail

VM TPM and shielding — severity: high

Evidence violates the baseline: shielded.

Evidence:

- /virtual\_machines/vms/0/generation: 2
- /virtual\_machines/vms/0/profile\_supported: true
- /virtual\_machines/vms/0/require\_vtpm: true
- /virtual\_machines/vms/0/require\_shielding: true
- /virtual\_machines/vms/0/vtpm\_enabled: true; expected: true
- /virtual\_machines/vms/0/shielded: false; expected: true
- /virtual\_machines/vms/0/key\_protector\_valid: true; expected: true
- /virtual\_machines/vms/0/hgs\_attestation\_valid: true; expected: true

Recommendation (manual review only): Review vTPM requirements separately from shielding; verify key protection and HGS trust in a supported lab.

## HV-07 / fictional-lab: fail

Virtual storage protection — severity: critical

Evidence violates the baseline: unapproved\_principals.

Evidence:

- /storage/assets/0/effective\_acl\_reviewed: true; expected: true
- /storage/assets/0/unapproved\_principals: \[&quot;broad-access&quot;\]; expected: \[\]
- /storage/assets/0/require\_encryption: true
- /storage/assets/0/encrypted: true; expected: true

Recommendation (manual review only): Review effective VHDX/checkpoint/config/backup access, remove unapproved principals and enforce approved encryption.

## HV-08 / fictional-lab: fail

Independent protected backups — severity: critical

Evidence violates the baseline: checkpoint\_only.

Evidence:

- /backup/independent\_copy: true; expected: true
- /backup/immutable\_or\_offline: true; expected: true
- /backup/separate\_identity: true; expected: true
- /backup/checkpoint\_only: true; expected: false

Recommendation (manual review only): Use independent immutable or offline copies and separate backup identities. Checkpoints are not backups.

## HV-09 / fictional-lab: fail

Audit logging — severity: medium

Evidence violates the baseline: central\_delivery\_verified.

Evidence:

- /logging/audit\_enabled: true; expected: true
- /logging/central\_delivery\_verified: false; expected: true
- /logging/tamper\_protection: true; expected: true
- /logging/retention\_days: 90; expected: 30

Recommendation (manual review only): Enable approved auditing, validate central delivery and tamper protection, and meet the required retention period.

## HV-10 / fictional-lab: fail

Verified recovery readiness — severity: critical

Evidence violates the baseline: RTO exceeds target.

Evidence:

- /recovery/drill\_performed\_at: &quot;2026-10-01T00:00:00Z&quot;
- /recovery/runbook\_reviewed: true; expected: true
- /recovery/integrity\_verified: true; expected: true
- /recovery/isolated\_restore: true; expected: true
- /recovery/reviewer\_approved: true; expected: true
- /recovery/measured\_rpo\_hours: 1; expected: 4
- /recovery/measured\_rto\_hours: 10; expected: 8

Recommendation (manual review only): Perform an authorized isolated restore drill without malware; verify integrity and document measured RPO/RTO, reviewer and runbook.
