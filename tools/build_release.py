"""Build local release candidates with pinned backend; does not publish."""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'dist'; out.mkdir(exist_ok=True)
    # Only generated candidates from this project's fixed version are replaced.
    for name in ('hyperv_opsec_auditor-0.1.0a1-py3-none-any.whl','hyperv_opsec_auditor-0.1.0a1.tar.gz'):
        (out/name).unlink(missing_ok=True)
    environment=os.environ.copy(); environment.setdefault('SOURCE_DATE_EPOCH','1791504000')
    subprocess.run([sys.executable,'-m','build','--no-isolation','--sdist','--wheel','--outdir',str(out)],cwd=ROOT,env=environment,check=True)
    sources={'evidence.schema.json':ROOT/'src/hyperv_opsec_auditor/evidence.schema.json',
             'healthy.json':ROOT/'fixtures/healthy.json','unsafe.json':ROOT/'fixtures/unsafe.json','partial.json':ROOT/'fixtures/partial.json',
             'example-report.json':ROOT/'examples/report.json','example-report.md':ROOT/'examples/report.md',
             'RELEASE_NOTES.md':ROOT/'CHANGELOG.md','VALIDATION.md':ROOT/'VALIDATION.md'}
    for name,path in sources.items(): shutil.copyfile(path,out/name)
    names=['hyperv_opsec_auditor-0.1.0a1-py3-none-any.whl','hyperv_opsec_auditor-0.1.0a1.tar.gz',*sources.keys()]
    sums=''.join(hashlib.sha256((out/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in sorted(names))
    (out/'SHA256SUMS').write_text(sums,encoding='utf-8')
    print('Release candidates and SHA256SUMS created in dist/. No publication performed.')

if __name__=='__main__': main()
