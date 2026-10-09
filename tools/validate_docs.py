"""Validate documentation links and the current synthetic input contract."""
import re
from pathlib import Path
from hyperv_opsec_auditor.validation import load_json, validate_evidence
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('requirements.md','threat-model.md','architecture.md','check-matrix.md','lab.md','adr/0001-stack.md','development.md','mvp-plan.md','input-contract.md','user-guide.md','environment.md')

def main():
    for name in REQUIRED:
        path=ROOT/'docs'/name
        if not path.is_file() or len(path.read_text(encoding='utf-8').strip())<100:
            raise ValueError('Missing/empty required document: '+name)
    paths=[ROOT/'README.md',ROOT/'SECURITY.md',ROOT/'CHANGELOG.md',*sorted((ROOT/'docs').rglob('*.md'))]
    for path in paths:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'): continue
            local=target.split('#',1)[0]
            if local and not (path.parent/local).is_file(): raise ValueError('Broken local link in '+str(path.relative_to(ROOT)))
    count=0
    for path in sorted((ROOT/'fixtures').glob('*.json')):
        data=validate_evidence(load_json(path))
        if data['synthetic'] is not True: raise ValueError('Public fixtures must be synthetic')
        count+=1
    if count<3: raise ValueError('Missing synthetic scenarios')
    print(f'PASS: {len(REQUIRED)} required documents, local links and {count} synthetic fixtures.')
    print('Real Windows Hyper-V/HGS/restore tests: NOT RUN')

if __name__=='__main__': main()
