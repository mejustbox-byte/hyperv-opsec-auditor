import copy
import json
import unittest
from datetime import datetime
from pathlib import Path
from hyperv_opsec_auditor.rules import RULES, SECTIONS, audit
from hyperv_opsec_auditor.validation import InputError
from test_validation import healthy

AS_OF='2026-10-09T00:00:00Z'

def evaluate(data,rule,**kwargs):
    return [item for item in audit(data,as_of=AS_OF,**kwargs)['findings'] if item['rule_id']==rule]

class RuleTests(unittest.TestCase):
    def test_healthy_all_ten_rules(self):
        report=audit(healthy(),as_of=AS_OF)
        self.assertEqual(report['summary'],{'pass':10,'fail':0,'unknown':0,'not_run':0})
        for result in report['findings']:
            self.assertTrue(result['evidence']); self.assertTrue(result['remediation'])
            self.assertIn(result['severity'],('critical','high','medium'))
        self.assertTrue(report['synthetic'])

    def test_every_rule_has_failure(self):
        data=healthy(); data['host']['security_updates_current']=False
        data['administration']['actual_admins']=['rogue']; data['winrm']['basic_auth_enabled']=True
        data['network']['adapters'][0]['vlans']=[99]
        data['virtual_machines']['vms'][0]['secure_boot_enabled']=False
        data['virtual_machines']['vms'][0]['shielded']=False
        data['storage']['assets'][0]['unapproved_principals']=['rogue']
        data['backup']['checkpoint_only']=True; data['logging']['retention_days']=1
        data['recovery']['measured_rto_hours']=100
        for result in audit(data,as_of=AS_OF)['findings']:
            with self.subTest(rule=result['rule_id']): self.assertEqual(result['status'],'fail')

    def test_unknown_for_each_collected_incomplete_section(self):
        for rule,section in SECTIONS.items():
            data=healthy(); data[section]={'state':'ok'}
            with self.subTest(rule=rule): self.assertEqual(evaluate(data,rule)[0]['status'],'unknown')

    def test_missing_uncollected_error_each_rule(self):
        for rule,section in SECTIONS.items():
            for state,expected in [('missing','not_run'),('not_collected','not_run'),('error','unknown')]:
                data=healthy()
                if state=='missing': del data[section]
                else: data[section]['state']=state
                with self.subTest(rule=rule,state=state): self.assertEqual(evaluate(data,rule)[0]['status'],expected)

    def test_null_never_passes_required_fields(self):
        data=healthy(); data['winrm']['https_only']=None
        self.assertEqual(evaluate(data,'HV-03')[0]['status'],'unknown')
        data['winrm']['allow_unencrypted']=True
        self.assertEqual(evaluate(data,'HV-03')[0]['status'],'fail')

    def test_freshness_future_stale_and_boundary(self):
        for date,status in [('2026-10-08T00:00:00Z','unknown'),('2026-11-09T00:00:00Z','unknown'),('2026-11-08T00:00:00Z','pass')]:
            report=audit(healthy(),as_of=date)
            with self.subTest(date=date): self.assertEqual(report['findings'][0]['status'],status)

    def test_exclusion_is_visible(self):
        result=evaluate(healthy(),'HV-02',exclude=['HV-02'])[0]
        self.assertEqual(result['status'],'not_run'); self.assertIn('excluded',result['rationale'])
        with self.assertRaises(InputError): audit(healthy(),as_of=AS_OF,exclude=['bad'])

    def test_winrm_disabled_is_not_run(self):
        data=healthy(); data['winrm']['enabled']=False
        self.assertEqual(evaluate(data,'HV-03')[0]['status'],'not_run')

    def test_network_policy_edges(self):
        for field,value in [('trunk',True),('sriov',True),('switch_type','external'),('vlans',[])]:
            data=healthy(); data['network']['adapters'][0][field]=value
            with self.subTest(field=field): self.assertEqual(evaluate(data,'HV-04')[0]['status'],'fail')
        data=healthy(); data['network']['inventory_complete']=False
        self.assertEqual(evaluate(data,'HV-04')[0]['status'],'unknown')
        data['network']['adapters'][0]['vlans']=[99]
        self.assertEqual(evaluate(data,'HV-04')[0]['status'],'fail')

    def test_gen1_unsupported_and_missing_profile_not_pass(self):
        for changes,status in [({'generation':1},'not_run'),({'profile_supported':False},'not_run'),({'profile_supported':None},'unknown')]:
            data=healthy(); data['virtual_machines']['vms'][0].update(changes)
            for rule in ('HV-05','HV-06'):
                with self.subTest(rule=rule,changes=changes): self.assertEqual(evaluate(data,rule)[0]['status'],status)
        data=healthy(); data['host']['supported_configuration']=False
        self.assertEqual(evaluate(data,'HV-06')[0]['status'],'not_run')

    def test_vtpm_is_not_shielding(self):
        data=healthy(); data['virtual_machines']['vms'][0]['shielded']=False
        result=evaluate(data,'HV-06')[0]
        self.assertEqual(result['status'],'fail'); self.assertIn('shielded',result['rationale'])
        for field in ('key_protector_valid','hgs_attestation_valid'):
            data=healthy(); del data['virtual_machines']['vms'][0][field]
            self.assertEqual(evaluate(data,'HV-06')[0]['status'],'unknown')

    def test_optional_vm_requirements(self):
        data=healthy(); vm=data['virtual_machines']['vms'][0]
        vm['require_secure_boot']=False; vm['require_vtpm']=False; vm['require_shielding']=False
        for rule in ('HV-05','HV-06'): self.assertEqual(evaluate(data,rule)[0]['status'],'not_run')
        vm['require_shielding']=None
        self.assertEqual(evaluate(data,'HV-06')[0]['status'],'unknown')

    def test_missing_secure_boot_applicability_is_unknown(self):
        data=healthy(); vm=data['virtual_machines']['vms'][0]
        vm['require_secure_boot']=None; vm['secure_boot_enabled']=False
        self.assertEqual(evaluate(data,'HV-05')[0]['status'],'unknown')

    def test_incomplete_inventory_does_not_claim_full_coverage(self):
        data=healthy(); data['virtual_machines']['inventory_complete']=False
        results=evaluate(data,'HV-05')
        self.assertEqual([i['status'] for i in results],['unknown','pass'])

    def test_no_assets_no_false_pass(self):
        for rule,section,key in [('HV-04','network','adapters'),('HV-05','virtual_machines','vms'),('HV-07','storage','assets')]:
            data=healthy(); data[section][key]=[]
            with self.subTest(rule=rule): self.assertEqual(evaluate(data,rule)[0]['status'],'not_run')

    def test_storage_encryption_and_acl(self):
        data=healthy(); data['storage']['assets'][0]['encrypted']=False
        self.assertEqual(evaluate(data,'HV-07')[0]['status'],'fail')
        data['storage']['assets'][0]['require_encryption']=False
        self.assertEqual(evaluate(data,'HV-07')[0]['status'],'pass')
        data['storage']['assets'][0]['effective_acl_reviewed']=None
        self.assertEqual(evaluate(data,'HV-07')[0]['status'],'unknown')

    def test_backup_presence_not_recovery_success(self):
        data=healthy(); del data['recovery']['drill_performed_at']
        self.assertEqual(evaluate(data,'HV-08')[0]['status'],'pass')
        self.assertEqual(evaluate(data,'HV-10')[0]['status'],'unknown')

    def test_restore_criteria_age_and_rpo_rto(self):
        for key,value,status in [('integrity_verified',False,'fail'),('reviewer_approved',None,'unknown'),('measured_rpo_hours',5,'fail'),('measured_rto_hours',9,'fail'),('drill_performed_at','2026-01-01T00:00:00Z','unknown')]:
            data=healthy(); data['recovery'][key]=value
            with self.subTest(key=key): self.assertEqual(evaluate(data,'HV-10')[0]['status'],status)
        data=healthy(); data['recovery']['measured_rto_hours']=8
        self.assertEqual(evaluate(data,'HV-10')[0]['status'],'pass')

    def test_invalid_policy_and_naive_datetime(self):
        for kwargs in ({'as_of':datetime(2026,10,9)}, {'max_evidence_age_days':0}, {'max_restore_age_days':True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(InputError): audit(healthy(),**kwargs)

    def test_deterministic_no_mutation(self):
        data=healthy(); before=copy.deepcopy(data)
        self.assertEqual(audit(data,as_of=AS_OF),audit(data,as_of=AS_OF))
        self.assertEqual(data,before)

if __name__=='__main__': unittest.main()
