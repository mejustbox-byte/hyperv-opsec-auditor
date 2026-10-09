"""Проверка ссылок документации и текущего синтетического контракта."""
import re
from pathlib import Path
from hyperv_opsec_auditor.validation import load_json, validate_evidence
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('requirements.md','threat-model.md','architecture.md','check-matrix.md','lab.md','adr/0001-stack.md','development.md','mvp-plan.md','input-contract.md','user-guide.md','environment.md')

ROOT_REQUIRED=('CHANGELOG.md', 'README.md', 'SECURITY.md', 'VALIDATION.md', 'CONTRIBUTING.md', 'ROADMAP.md', 'CLOUD-DEVELOPMENT.md', 'VERIFICATION.md', 'INSTALL.md', 'RELEASE-CHECKLIST.md', 'RUNBOOK.md', 'CORE-CONTRACT.md', 'ARCHITECTURE.md', 'SUPPLY-CHAIN.md', 'TECH-STACK.md', 'LICENSE.ru.md', 'LOCAL-PC.md', 'SECURITY-TESTING.md', 'SECURITY-DATA.md', 'AGENTS.md', 'RELEASE-NOTES.md', 'THREAT-MODEL.md')

def main():
    for name in ROOT_REQUIRED:
        path=ROOT/name
        if not path.is_file() or len(path.read_text(encoding="utf-8").strip())<100:
            raise ValueError("Отсутствует или пуст корневой документ: "+name)
    for name in REQUIRED:
        path=ROOT/'docs'/name
        if not path.is_file() or len(path.read_text(encoding='utf-8').strip())<100:
            raise ValueError('Отсутствует или пуст обязательный документ: '+name)
    paths=[*sorted(ROOT.glob('*.md')),*sorted((ROOT/'docs').rglob('*.md')),*sorted((ROOT/'.github').rglob('*.md'))]
    for path in paths:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'): continue
            local=target.split('#',1)[0]
            if local and not (path.parent/local).is_file(): raise ValueError('Неработающая локальная ссылка в '+str(path.relative_to(ROOT)))
    count=0
    for path in sorted((ROOT/'fixtures').glob('*.json')):
        data=validate_evidence(load_json(path))
        if data['synthetic'] is not True: raise ValueError('Публичные примеры должны быть синтетическими')
        count+=1
    if count<3: raise ValueError('Отсутствуют синтетические сценарии')
    print(f'ПРОЙДЕНО: {len(REQUIRED)+len(ROOT_REQUIRED)} обязательных документов, локальные ссылки и {count} синтетических сценария.')
    print('Реальные испытания Windows Hyper-V/HGS/восстановления: НЕ ВЫПОЛНЕНЫ')

if __name__=='__main__': main()
