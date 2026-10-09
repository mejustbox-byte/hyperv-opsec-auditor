import json
import io
from contextlib import redirect_stdout, redirect_stderr
from hyperv_opsec_auditor.cli import main
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from hyperv_opsec_auditor.reporting import markdown_report
from hyperv_opsec_auditor.rules import audit
from test_validation import healthy, ROOT

AS_OF='2026-10-09T00:00:00Z'

class CliTests(unittest.TestCase):
    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-m','hyperv_opsec_auditor',*map(str,args)],capture_output=True,text=True,encoding='utf-8',cwd=ROOT)

    def test_help_version_rules_validate(self):
        for args,expected in [(('--help',),'Автономный'),(('--version',),'0.1.0a2'),(('rules',),'HV-10'),(('validate','fixtures/healthy.json'),'Данные 1.0 корректны')]:
            result=self.run_cli(*args)
            with self.subTest(args=args): self.assertEqual(result.returncode,0); self.assertIn(expected,result.stdout)

    def test_json_and_markdown_end_to_end(self):
        original=(ROOT/'fixtures/healthy.json').read_bytes()
        result=self.run_cli('audit','fixtures/healthy.json','--as-of',AS_OF,'--format','json','--fail-on','incomplete')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['summary']['pass'],10)
        result=self.run_cli('audit','fixtures/unsafe.json','--as-of',AS_OF,'--fail-on','fail')
        self.assertEqual(result.returncode,1); self.assertIn('СИНТЕТИЧЕСКИЕ',result.stdout); self.assertIn('Рекомендация',result.stdout)
        self.assertEqual((ROOT/'fixtures/healthy.json').read_bytes(),original)

    def test_partial_exit_modes(self):
        for mode,code in [('none',0),('fail',0),('incomplete',1)]:
            result=self.run_cli('audit','fixtures/partial.json','--as-of',AS_OF,'--fail-on',mode,'--format','json')
            with self.subTest(mode=mode): self.assertEqual(result.returncode,code)
        report=json.loads(result.stdout)
        self.assertGreater(report['summary']['not_run'],0); self.assertGreater(report['summary']['unknown'],0)

    def test_stale_evidence_default_as_of(self):
        result=self.run_cli('audit','fixtures/healthy.json','--as-of','2027-01-01T00:00:00Z','--format','json','--fail-on','incomplete')
        self.assertEqual(result.returncode,1)
        self.assertEqual(json.loads(result.stdout)['summary']['unknown'],10)

    def test_output_exclusive_and_private(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'report.json'
            args=('audit','fixtures/healthy.json','--as-of',AS_OF,'--format','json','--output',path)
            first=self.run_cli(*args); self.assertEqual(first.returncode,0,first.stderr); self.assertEqual(first.stdout,'')
            before=path.read_bytes(); second=self.run_cli(*args)
            self.assertEqual(second.returncode,2); self.assertEqual(before,path.read_bytes())
            if os.name=='posix': self.assertEqual(path.stat().st_mode & 0o777,0o600)

    @unittest.skipUnless(os.name=='posix','Права символических ссылок проверяются только на POSIX')
    def test_output_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder)/'target'; target.write_text('keep')
            link=Path(folder)/'link'; link.symlink_to(target)
            result=self.run_cli('audit','fixtures/healthy.json','--as-of',AS_OF,'--output',link)
            self.assertEqual(result.returncode,2); self.assertEqual(target.read_text(),'keep')

    def test_invalid_input_no_traceback_or_values(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'input.json'
            for content in ['{"scope":"DO_NOT_ECHO_SECRET"}','{"x": NaN}','{"x": 1e999}','{"scope":"x","scope":"y"}','[]']:
                path.write_text(content)
                result=self.run_cli('audit',path,'--as-of',AS_OF)
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertEqual(result.stdout,''); self.assertNotIn('Traceback',result.stderr); self.assertNotIn('DO_NOT_ECHO_SECRET',result.stderr)
        self.assertEqual(self.run_cli('validate','no-such-file').returncode,2)

    def test_invalid_arguments(self):
        for arguments in [('--as-of','bad'),('--max-evidence-age-days','0'),('--exclude','HV-99')]:
            result=self.run_cli('audit','fixtures/healthy.json',*arguments)
            self.assertEqual(result.returncode,2); self.assertNotIn('Traceback',result.stderr)

    def test_in_process_cli_reports_and_exit_modes(self):
        for args,code in [
            (['rules'],0),
            (['validate',str(ROOT/'fixtures/healthy.json')],0),
            (['audit',str(ROOT/'fixtures/healthy.json'),'--as-of',AS_OF,'--format','json'],0),
            (['audit',str(ROOT/'fixtures/unsafe.json'),'--as-of',AS_OF,'--fail-on','fail'],1),
            (['audit',str(ROOT/'fixtures/partial.json'),'--as-of',AS_OF,'--fail-on','incomplete'],1),
        ]:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(args),code)

    def test_in_process_cli_input_and_output_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'report.json'
            args=['audit',str(ROOT/'fixtures/healthy.json'),'--as-of',AS_OF,'--output',str(path)]
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(args),0)
                self.assertEqual(main(args),2)
                self.assertEqual(main(['validate',str(path/'missing')]),2)
                self.assertEqual(main(['audit',str(ROOT/'fixtures/healthy.json'),'--as-of','invalid']),2)

    def test_renderer_escapes_untrusted_text(self):
        report=audit(healthy(),as_of=AS_OF)
        report['findings'][0]['rationale']='<script>alert(1)</script> [click](evil) | x'
        rendered=markdown_report(report)
        self.assertNotIn('<script>',rendered); self.assertIn('&lt;script&gt;',rendered)
        self.assertNotIn('[click]',rendered); self.assertIn('\\|',rendered)

if __name__=='__main__': unittest.main()
