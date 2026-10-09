import copy
import json
import tempfile
import unittest
from pathlib import Path
from hyperv_opsec_auditor.validation import InputError, MAX_BYTES, load_json, schema, validate_evidence

ROOT = Path(__file__).resolve().parents[1]

def healthy():
    return json.loads((ROOT/'fixtures/healthy.json').read_text())

class ValidationTests(unittest.TestCase):
    def assert_invalid(self, data):
        with self.assertRaises(InputError):
            validate_evidence(data)

    def test_all_fixtures(self):
        for filename in ('healthy','unsafe','partial'):
            with self.subTest(filename=filename):
                validate_evidence(load_json(ROOT/f'fixtures/{filename}.json'))

    def test_required_fields(self):
        for key in ('schema_version','synthetic','scope','collected_at','evidence_source'):
            data=healthy(); del data[key]
            with self.subTest(key=key): self.assert_invalid(data)

    def test_types_and_unknown_fields(self):
        cases=[('synthetic',1),('scope','<script>'),('collected_at','2026-02-30T00:00:00Z'),('schema_version','2.0'),('host',{'state':'ok','unexpected':'value'})]
        for key,value in cases:
            data=healthy(); data[key]=value
            with self.subTest(key=key): self.assert_invalid(data)
        for value in ('false',1,0):
            data=healthy(); data['host']['supported_build']=value
            self.assert_invalid(data)

    def test_bounds_duplicates_and_inventory_ids(self):
        for vlan in (0,4095,True):
            data=healthy(); data['network']['adapters'][0]['vlans']=[vlan]
            self.assert_invalid(data)
        data=healthy(); data['network']['adapters'][0]['vlans']=[42,42]; self.assert_invalid(data)
        data=healthy(); data['network']['adapters'][0]['vlans']=[42,42.0]; self.assert_invalid(data)
        data=healthy(); vm=copy.deepcopy(data['virtual_machines']['vms'][0]); vm['vtpm_enabled']=False
        data['virtual_machines']['vms'].append(vm); self.assert_invalid(data)
        data=healthy(); data['scope']='x'*65; self.assert_invalid(data)
        data=healthy(); data['administration']['actual_admins']=['u'+str(i) for i in range(1001)]; self.assert_invalid(data)

    def test_drill_future_relative_to_collection(self):
        data=healthy(); data['recovery']['drill_performed_at']='2026-10-10T00:00:00Z'; self.assert_invalid(data)

    def test_duplicate_json_nonfinite_invalid_unicode_and_size(self):
        contents=[b'{"schema_version":"1.0","schema_version":"2"}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1e999}',b'\xff',b'{} trailing',b'['*2000+b']'*2000,b' '* (MAX_BYTES+1)]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'input.json'
            for index,raw in enumerate(contents):
                path.write_bytes(raw)
                with self.subTest(index=index), self.assertRaises(InputError): load_json(path)

    def test_external_jsonschema_parity(self):
        from jsonschema import Draft202012Validator
        external=Draft202012Validator(schema()); external.check_schema(schema())
        inputs=[healthy(), {'synthetic':True}]
        for key,value in [('synthetic',1),('scope','evil|text'),('scope','a\n'),('host',{'state':'ok','extra':True})]:
            data=healthy(); data[key]=value; inputs.append(data)
        for field in ('generation',):
            for value in (1,2,True,1.0,2.5):
                data=healthy(); data['virtual_machines']['vms'][0][field]=value; inputs.append(data)
        for data in inputs:
            with self.subTest(data_type=type(data).__name__):
                expected=external.is_valid(data)
                try: validate_evidence(data); actual=True
                except InputError: actual=False
                self.assertEqual(actual,expected)

if __name__=='__main__': unittest.main()
