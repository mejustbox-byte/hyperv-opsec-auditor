"""Rebuild own sdist and test wheel installation without runtime dependencies."""
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(command,**kwargs):
    return subprocess.run(command,check=True,**kwargs)

def smoke(wheel,folder):
    folder.mkdir()
    venv.create(folder/'venv',with_pip=True)
    python=folder/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    run([str(python),'-m','pip','install','--no-index','--no-deps',str(wheel)],cwd=folder)
    run([str(python),'-m','hyperv_opsec_auditor','validate',str(ROOT/'fixtures/healthy.json')],cwd=folder)
    report=subprocess.run([str(python),'-m','hyperv_opsec_auditor','audit',str(ROOT/'fixtures/healthy.json'),'--as-of','2026-10-09T00:00:00Z','--format','json','--fail-on','incomplete'],cwd=folder,check=True,capture_output=True,text=True)
    assert json.loads(report.stdout)['summary']['pass']==10
    packages=subprocess.run([str(python),'-m','pip','list','--format','json'],cwd=folder,check=True,capture_output=True,text=True)
    names={p['name'] for p in json.loads(packages.stdout)}
    assert names <= {'pip','setuptools','hyperv-opsec-auditor'}, names

def main():
    sums=ROOT/'dist/SHA256SUMS'
    for line in sums.read_text().splitlines():
        expected,name=line.split('  ',1)
        assert hashlib.sha256((ROOT/'dist'/name).read_bytes()).hexdigest()==expected, name
    wheel=ROOT/'dist/hyperv_opsec_auditor-0.1.0a1-py3-none-any.whl'
    with tempfile.TemporaryDirectory(prefix='hyperv-package-') as temporary:
        folder=Path(temporary)
        smoke(wheel,folder/'wheel')
        # Only the artifact just built from this repository is extracted, using the safe data filter.
        with tarfile.open(ROOT/'dist/hyperv_opsec_auditor-0.1.0a1.tar.gz') as archive:
            archive.extractall(folder/'source',filter='data')
        source=folder/'source/hyperv_opsec_auditor-0.1.0a1'
        run([sys.executable,'-m','build','--no-isolation','--wheel','--outdir',str(folder/'rebuilt')],cwd=source)
        rebuilt=next((folder/'rebuilt').glob('*.whl'))
        smoke(rebuilt,folder/'sdist')
    print('PASS: checksums, clean wheel install, sdist rebuild/clean install, CLI audit; no runtime dependencies.')
    print('Real Hyper-V/HGS/recovery validation: NOT RUN')

if __name__=='__main__': main()
