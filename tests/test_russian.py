"""Проверки пользовательского языка и неизменности машинного контракта."""
import json
import os
import re
import subprocess
import sys
import unittest
from hyperv_opsec_auditor import __version__
from hyperv_opsec_auditor.reporting import json_report, markdown_report
from hyperv_opsec_auditor.rules import RULES, audit
from hyperv_opsec_auditor.validation import InputError, schema, validate_evidence
from test_validation import healthy

class RussianTests(unittest.TestCase):
    def test_rule_descriptions_and_all_results_are_russian(self):
        for title,severity,remediation in RULES.values():
            self.assertRegex(title,r'[А-Яа-яЁё]')
            self.assertRegex(remediation,r'[А-Яа-яЁё]')
            self.assertIn(severity,('high','critical','medium'))
        report=audit(healthy(),as_of='2026-10-09T00:00:00Z')
        self.assertEqual(report['tool_version'],'0.1.0a2')
        self.assertEqual(set(report['summary']),{'pass','fail','unknown','not_run'})
        for item in report['findings']: self.assertRegex(item['rationale'],r'[А-Яа-яЁё]')
        for item in report['limitations']: self.assertRegex(item,r'[А-Яа-яЁё]')

    def test_schema_descriptions_and_utf8_report(self):
        spec=schema()
        self.assertRegex(spec['title'],r'[А-Яа-яЁё]')
        def check(value):
            if isinstance(value,dict):
                for field in value.get('properties',{}).values(): self.assertRegex(field['description'],r'[А-Яа-яЁё]')
                for child in value.values(): check(child)
            elif isinstance(value,list):
                for child in value: check(child)
        check(spec)
        report=audit(healthy(),as_of='2026-10-09T00:00:00Z')
        text=json_report(report)
        self.assertIn('Поддержка хоста',text)
        self.assertEqual(json.loads(text),report)
        self.assertIn('СИНТЕТИЧЕСКИЕ ДАННЫЕ',markdown_report(report))
        report['synthetic']=False
        self.assertIn('независимой проверки инфраструктуры не было',markdown_report(report))

    def test_cli_help_and_utf8_under_non_utf8_default(self):
        environment=os.environ.copy(); environment['PYTHONUTF8']='0'; environment['PYTHONIOENCODING']='ascii'
        for arguments in (['--help'],['audit','--help']):
            result=subprocess.run([sys.executable,'-m','hyperv_opsec_auditor',*arguments],env=environment,capture_output=True,check=True)
            text=result.stdout.decode('utf-8')
            self.assertIn('Использование:',text)
            self.assertNotIn('show program',text)
            self.assertNotIn('show this help',text)
        result=subprocess.run([sys.executable,'-m','hyperv_opsec_auditor','audit','--bad-option'],env=environment,capture_output=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('ошибка:',result.stderr.decode('utf-8'))

    def test_input_error_is_russian_without_values(self):
        data=healthy();data['scope']='DO_NOT_ECHO_SECRET'
        data['host']['extra']='DO_NOT_ECHO_SECRET'
        with self.assertRaises(InputError) as context: validate_evidence(data)
        self.assertRegex(str(context.exception),r'[А-Яа-яЁё]')
        self.assertNotIn('DO_NOT_ECHO_SECRET',str(context.exception))

if __name__=='__main__': unittest.main()
