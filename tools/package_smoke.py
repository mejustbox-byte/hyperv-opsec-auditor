"""Пересборка собственного sdist и проверка установки wheel без зависимостей выполнения."""
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from email.parser import BytesParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(command,**kwargs):
    return subprocess.run(command,check=True,**kwargs)

def verify_wheel_license(wheel):
    with zipfile.ZipFile(wheel) as archive:
        metadata_name=next(n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))
        metadata=BytesParser().parsebytes(archive.read(metadata_name))
        assert metadata['License-Expression']=='MIT'
        assert set(metadata.get_all('License-File',[]))=={'LICENSE','LICENSE.ru.md'}
        prefix=metadata_name.rsplit('/',1)[0]+'/licenses/'
        for name in ('LICENSE','LICENSE.ru.md'):
            assert archive.read(prefix+name)==(ROOT/name).read_bytes(), name
        assert not metadata.get_all('Requires-Dist'), 'Неожиданная зависимость выполнения'

def smoke(wheel,folder):
    verify_wheel_license(wheel)
    folder.mkdir()
    venv.create(folder/'venv',with_pip=True)
    python=folder/'venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    run([str(python),'-m','pip','install','--no-index','--no-deps',str(wheel)],cwd=folder)
    run([str(python),'-m','hyperv_opsec_auditor','validate',str(ROOT/'fixtures/healthy.json')],cwd=folder)
    report=subprocess.run([str(python),'-m','hyperv_opsec_auditor','audit',str(ROOT/'fixtures/healthy.json'),'--as-of','2026-10-09T00:00:00Z','--format','json','--fail-on','incomplete'],cwd=folder,check=True,capture_output=True,text=True,encoding='utf-8')
    assert json.loads(report.stdout)['summary']['pass']==10
    packages=subprocess.run([str(python),'-m','pip','list','--format','json'],cwd=folder,check=True,capture_output=True,text=True,encoding='utf-8')
    names={p['name'] for p in json.loads(packages.stdout)}
    assert names <= {'pip','setuptools','hyperv-opsec-auditor'}, names

def main():
    sums=ROOT/'dist/SHA256SUMS'
    for line in sums.read_text().splitlines():
        expected,name=line.split('  ',1)
        assert hashlib.sha256((ROOT/'dist'/name).read_bytes()).hexdigest()==expected, name
    wheel=ROOT/'dist/hyperv_opsec_auditor-0.1.0a2-py3-none-any.whl'
    with tempfile.TemporaryDirectory(prefix='hyperv-package-') as temporary:
        folder=Path(temporary)
        smoke(wheel,folder/'wheel')
        # Извлекается только созданный этим репозиторием архив с безопасным фильтром data.
        with tarfile.open(ROOT/'dist/hyperv_opsec_auditor-0.1.0a2.tar.gz') as archive:
            archive.extractall(folder/'source',filter='data')
        source=folder/'source/hyperv_opsec_auditor-0.1.0a2'
        for name in ('LICENSE',*[p.name for p in ROOT.glob('*.md')]):
            assert (source/name).read_bytes()==(ROOT/name).read_bytes(), name
        metadata=BytesParser().parsebytes((source/'PKG-INFO').read_bytes())
        assert metadata['License-Expression']=='MIT'
        assert set(metadata.get_all('License-File',[]))=={'LICENSE','LICENSE.ru.md'}
        run([sys.executable,'-m','build','--no-isolation','--wheel','--outdir',str(folder/'rebuilt')],cwd=source)
        rebuilt=next((folder/'rebuilt').glob('*.whl'))
        smoke(rebuilt,folder/'sdist')
    print('ПРОЙДЕНО: контрольные суммы, MIT метаданные/обе лицензии/документы в пакетах, чистая установка wheel, пересборка/установка sdist и аудит CLI; сторонних зависимостей выполнения нет.')
    print('Реальные испытания Hyper-V/HGS/восстановления: НЕ ВЫПОЛНЕНЫ')

if __name__=='__main__': main()
