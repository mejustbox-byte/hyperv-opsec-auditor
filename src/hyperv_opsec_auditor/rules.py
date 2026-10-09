"""Deterministic offline rules. No host access or remediation execution."""
from datetime import datetime, timezone
from . import __version__
from .validation import InputError, parse_utc, validate_evidence

POLICY_VERSION = 'mvp-baseline-1.0'
RULES = {
    'HV-01': ('Host support and updates', 'high', 'Review the supported host/build profile, enable the approved Hyper-V role and apply approved security updates.'),
    'HV-02': ('Management privileges', 'critical', 'Review effective administrator rights, remove unapproved grants through an authorized change, and separate management accounts and networks.'),
    'HV-03': ('WinRM management security', 'high', 'Review HTTPS/certificate, disable Basic and unencrypted management, restrict firewall scope and delegation through an authorized change.'),
    'HV-04': ('Virtual network isolation', 'high', 'Review the approved topology, VLAN allowlist, switch type, trunk and SR-IOV exceptions; validate isolation in the lab.'),
    'HV-05': ('VM Secure Boot', 'high', 'For supported generation 2 profiles, enable the approved Secure Boot trust template through a reviewed change.'),
    'HV-06': ('VM TPM and shielding', 'high', 'Review vTPM requirements separately from shielding; verify key protection and HGS trust in a supported lab.'),
    'HV-07': ('Virtual storage protection', 'critical', 'Review effective VHDX/checkpoint/config/backup access, remove unapproved principals and enforce approved encryption.'),
    'HV-08': ('Independent protected backups', 'critical', 'Use independent immutable or offline copies and separate backup identities. Checkpoints are not backups.'),
    'HV-09': ('Audit logging', 'medium', 'Enable approved auditing, validate central delivery and tamper protection, and meet the required retention period.'),
    'HV-10': ('Verified recovery readiness', 'critical', 'Perform an authorized isolated restore drill without malware; verify integrity and document measured RPO/RTO, reviewer and runbook.'),
}
SECTIONS = {'HV-01':'host','HV-02':'administration','HV-03':'winrm','HV-04':'network','HV-05':'virtual_machines','HV-06':'virtual_machines','HV-07':'storage','HV-08':'backup','HV-09':'logging','HV-10':'recovery'}
LIMITATIONS = [
    'Offline evaluation of supplied evidence; no live Hyper-V, WinRM, network or backup access.',
    'Support, effective rights, isolation and restore attestations are supplied by the evidence owner, not independently verified.',
    'Synthetic results do not validate real infrastructure. Actual Windows Hyper-V/HGS and recovery tests are NOT RUN.',
    'No configuration changes or remediation are executed. Reports can contain sensitive pseudonymous evidence.',
]

class Checks:
    def __init__(self, data, pointer):
        self.data, self.pointer = data, pointer
        self.evidence, self.failures, self.missing = [], [], []

    def expect(self, key, expected):
        value = self.data.get(key)
        self.evidence.append({'pointer':f'{self.pointer}/{key}', 'observed':value, 'expected':expected})
        if value is None:
            self.missing.append(key)
        elif value != expected:
            self.failures.append(key)

    def compare(self, key, expected_key, predicate, explanation):
        value, expected = self.data.get(key), self.data.get(expected_key)
        self.evidence.append({'pointer':f'{self.pointer}/{key}', 'observed':value, 'expected_pointer':f'{self.pointer}/{expected_key}', 'expected':expected})
        if value is None or expected is None:
            self.missing.append(key + '/' + expected_key)
        elif not predicate(value, expected):
            self.failures.append(explanation)

    def result(self):
        if self.failures:
            return 'fail', 'Evidence violates the baseline: ' + ', '.join(self.failures) + '.'
        if self.missing:
            return 'unknown', 'Required evidence is missing or null: ' + ', '.join(self.missing) + '.'
        return 'pass', 'All required supplied evidence for this rule matches the baseline.'

def finding(rule_id, asset, status, rationale, evidence=()):
    title, severity, remediation = RULES[rule_id]
    return {'rule_id':rule_id,'asset':asset,'title':title,'status':status,'severity':severity,'rationale':rationale,'evidence':list(evidence),'remediation':remediation}

def from_checks(rule_id, asset, checks):
    return finding(rule_id, asset, *checks.result(), checks.evidence)

def _vm_findings(rule, section, document):
    result = []
    vms = section.get('vms')
    if section.get('inventory_complete') is not True:
        result.append(finding(rule, document['scope'], 'unknown', 'VM inventory completeness is not confirmed.'))
    if vms is None:
        return result or [finding(rule, document['scope'], 'unknown', 'VM inventory is missing.')]
    if not vms:
        return result or [finding(rule, document['scope'], 'not_run', 'Complete inventory declares no VMs; no VM configuration was tested.')]
    host_supported = document.get('host', {}).get('supported_configuration')
    host_state = document.get('host', {}).get('state')
    for index, vm in enumerate(vms):
        pointer = f'/virtual_machines/vms/{index}'
        evidence = [{'pointer':pointer+'/generation','observed':vm['generation']},
                    {'pointer':pointer+'/profile_supported','observed':vm.get('profile_supported')}]
        if vm['generation'] == 1:
            result.append(finding(rule, vm['id'], 'not_run', 'Generation 1 is outside the Secure Boot/vTPM/shielding applicability profile.', evidence))
            continue
        if vm.get('profile_supported') is False or host_supported is False:
            result.append(finding(rule, vm['id'], 'not_run', 'Declared unsupported profile; VM protection is not validated.', evidence))
            continue
        if vm.get('profile_supported') is not True or host_supported is not True or host_state != 'ok':
            result.append(finding(rule, vm['id'], 'unknown', 'Supported VM and host profile evidence is incomplete.', evidence))
            continue
        checks = Checks(vm, pointer)
        checks.evidence.extend(evidence)
        if rule == 'HV-05':
            required = vm.get('require_secure_boot')
            if required is False:
                result.append(finding(rule, vm['id'], 'not_run', 'Secure Boot is not required by the supplied profile.', evidence))
                continue
            if required is None:
                result.append(finding(rule, vm['id'], 'unknown', 'Secure Boot applicability requirement is missing.', evidence))
                continue
            checks.expect('require_secure_boot', True)
            checks.expect('secure_boot_enabled', True)
            checks.expect('secure_boot_template_approved', True)
        else:
            tpm, shielding = vm.get('require_vtpm'), vm.get('require_shielding')
            if tpm is False and shielding is False:
                result.append(finding(rule, vm['id'], 'not_run', 'Neither vTPM nor shielding is required by the supplied profile.', evidence))
                continue
            for name in ('require_vtpm','require_shielding'):
                if vm.get(name) is None:
                    checks.missing.append(name)
                checks.evidence.append({'pointer':pointer+'/'+name, 'observed':vm.get(name)})
            if tpm is True or shielding is True:
                checks.expect('vtpm_enabled', True)
            if shielding is True:
                for name in ('shielded','key_protector_valid','hgs_attestation_valid'):
                    checks.expect(name, True)
        result.append(from_checks(rule, vm['id'], checks))
    return result

def _evaluate(rule, data, document, as_of, max_restore_age_days):
    scope = document['scope']
    if rule in ('HV-05','HV-06'):
        return _vm_findings(rule, data, document)
    c = Checks(data, '/'+SECTIONS[rule])
    if rule == 'HV-01':
        for key in ('hyperv_role_enabled','supported_configuration','supported_build','security_updates_current'):
            c.expect(key, True)
    elif rule == 'HV-02':
        for key in ('effective_rights_reviewed','separate_management_accounts','management_network_isolated'):
            c.expect(key, True)
        c.compare('actual_admins','approved_admins',lambda a,b:set(a)<=set(b),'unapproved administrators')
    elif rule == 'HV-03':
        if data.get('enabled') is False:
            return [finding(rule, scope, 'not_run', 'WinRM is declared disabled; no active listener was tested.', [{'pointer':'/winrm/enabled','observed':False}])]
        c.expect('enabled', True)
        for key in ('https_only','certificate_valid','firewall_scoped','delegation_restricted'):
            c.expect(key, True)
        c.expect('basic_auth_enabled', False)
        c.expect('allow_unencrypted', False)
    elif rule == 'HV-04':
        c.expect('topology_reviewed', True)
        # Incomplete inventories are unknown, not a confirmed insecure setting.
        if data.get('inventory_complete') is not True:
            c.missing.append('complete adapter inventory')
        adapters = data.get('adapters')
        if adapters is None:
            c.missing.append('adapters')
        elif not adapters and not c.missing and not c.failures:
            return [finding(rule, scope, 'not_run', 'Complete inventory declares no network adapters.')]
        else:
            for index, adapter in enumerate(adapters):
                part = Checks(adapter, f'/network/adapters/{index}')
                part.compare('switch_type','expected_switch_type',lambda a,b:a==b,'switch type mismatch')
                part.compare('vlans','allowed_vlans',lambda a,b:bool(a) and set(a)<=set(b),'VLAN outside approved scope or empty VLAN set')
                part.compare('trunk','allow_trunk',lambda a,b:not a or b,'unapproved trunk')
                part.compare('sriov','allow_sriov',lambda a,b:not a or b,'unapproved SR-IOV')
                c.evidence.extend(part.evidence); c.failures.extend(part.failures); c.missing.extend(part.missing)
    elif rule == 'HV-07':
        if data.get('inventory_complete') is not True:
            c.missing.append('complete storage inventory')
        assets = data.get('assets')
        if assets is None:
            c.missing.append('assets')
        elif not assets and not c.missing:
            return [finding(rule, scope, 'not_run', 'Complete inventory declares no storage assets.')]
        else:
            for index, asset in enumerate(assets):
                part = Checks(asset, f'/storage/assets/{index}')
                part.expect('effective_acl_reviewed', True)
                part.expect('unapproved_principals', [])
                required = asset.get('require_encryption')
                part.evidence.append({'pointer':part.pointer+'/require_encryption','observed':required})
                if required is None:
                    part.missing.append('require_encryption')
                elif required:
                    part.expect('encrypted', True)
                c.evidence.extend(part.evidence); c.failures.extend(part.failures); c.missing.extend(part.missing)
    elif rule == 'HV-08':
        for key in ('independent_copy','immutable_or_offline','separate_identity'):
            c.expect(key, True)
        c.expect('checkpoint_only', False)
    elif rule == 'HV-09':
        for key in ('audit_enabled','central_delivery_verified','tamper_protection'):
            c.expect(key, True)
        c.compare('retention_days','required_retention_days',lambda a,b:a>=b,'insufficient log retention')
    elif rule == 'HV-10':
        drill = data.get('drill_performed_at')
        c.evidence.append({'pointer':'/recovery/drill_performed_at','observed':drill})
        # A stale or absent drill cannot establish recovery readiness, including failure.
        if drill is None:
            return [finding(rule, scope, 'unknown', 'No dated restore drill evidence was supplied.', c.evidence)]
        age = (as_of - parse_utc(drill)).total_seconds()/86400
        if age < 0 or age > max_restore_age_days:
            return [finding(rule, scope, 'unknown', 'Restore drill is outside the allowed freshness window.', c.evidence)]
        for key in ('runbook_reviewed','integrity_verified','isolated_restore','reviewer_approved'):
            c.expect(key, True)
        for metric in ('rpo','rto'):
            c.compare(f'measured_{metric}_hours',f'target_{metric}_hours',lambda a,b:a<=b,f'{metric.upper()} exceeds target')
    return [from_checks(rule, scope, c)]

def audit(document, *, as_of=None, max_evidence_age_days=30, max_restore_age_days=90, exclude=()):
    """Validate and evaluate evidence; timestamps and policy bounds are explicit."""
    validate_evidence(document)
    if as_of is None:
        as_of = datetime.now(timezone.utc).replace(microsecond=0)
    elif isinstance(as_of, str):
        as_of = parse_utc(as_of)
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise InputError('as_of must be a timezone-aware datetime or UTC string')
    for limit in (max_evidence_age_days,max_restore_age_days):
        if type(limit) is not int or not 1 <= limit <= 3650:
            raise InputError('Freshness limits must be integers between 1 and 3650 days')
    if not set(exclude) <= RULES.keys():
        raise InputError('Unknown excluded rule ID')
    as_of = as_of.astimezone(timezone.utc)
    age = (as_of-parse_utc(document['collected_at'])).total_seconds()/86400
    results = []
    for rule in RULES:
        section = document.get(SECTIONS[rule])
        if rule in exclude:
            results.append(finding(rule, document['scope'], 'not_run', 'Explicitly excluded by the operator.'))
        elif section is None or section['state'] == 'not_collected':
            results.append(finding(rule, document['scope'], 'not_run', 'Evidence section was not collected.'))
        elif age < 0 or age > max_evidence_age_days:
            results.append(finding(rule, document['scope'], 'unknown', 'Evidence is outside the allowed freshness window.'))
        elif section['state'] == 'error':
            results.append(finding(rule, document['scope'], 'unknown', 'Evidence collection failed; supplied values were not evaluated.'))
        else:
            results.extend(_evaluate(rule,section,document,as_of,max_restore_age_days))
    counts = {status:sum(item['status']==status for item in results) for status in ('pass','fail','unknown','not_run')}
    return {'schema_version':'1.0','tool_version':__version__,'policy_version':POLICY_VERSION,
            'scope':document['scope'],'synthetic':document['synthetic'],'evidence_source':document['evidence_source'],
            'collected_at':document['collected_at'],'as_of':as_of.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'policy':{'max_evidence_age_days':max_evidence_age_days,'max_restore_age_days':max_restore_age_days,'excluded_rules':sorted(set(exclude))},
            'summary':counts,'limitations':LIMITATIONS.copy(),'findings':results}
