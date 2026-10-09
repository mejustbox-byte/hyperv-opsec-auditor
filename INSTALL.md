# Установка, проверка и удаление

## Поддерживаемый сценарий

Python >=3.12, автономный CLI из wheel или исходников. Linux проверен в облаке; Windows проверяется автономным CI Python. Реальный Hyper-V не проверен, macOS отдельно не проверялся. Ни права администратора, ни роль Hyper-V для CLI не нужны.

## Wheel без сети

Из [выпуска v0.1.0a2](https://github.com/mejustbox-byte/hyperv-opsec-auditor/releases/tag/v0.1.0a2) скачайте wheel, `SHA256SUMS` и нужный вымышленный пример в `dist/`. На POSIX можно проверить скачанные файлы командой `sha256sum --check SHA256SUMS` из каталога со всеми перечисленными файлами. На Windows сравните `Get-FileHash -Algorithm SHA256` с соответствующими строками `SHA256SUMS`. Если скачан только wheel, сравнивайте только его строку, не игнорируйте несовпадение. Неподписанная сумма из того же источника проверяет целостность, а не личность издателя.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./dist/hyperv_opsec_auditor-0.1.0a2-py3-none-any.whl
.venv/bin/hyperv-opsec-auditor --version
.venv/bin/hyperv-opsec-auditor validate fixtures/healthy.json
```

Последняя команда предполагает рабочую копию с `fixtures/`; для скачанного отдельного примера замените путь на `dist/healthy.json`.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --no-deps .\dist\hyperv_opsec_auditor-0.1.0a2-py3-none-any.whl
.\.venv\Scripts\hyperv-opsec-auditor.exe --version
.\.venv\Scripts\hyperv-opsec-auditor.exe validate .\dist\healthy.json
```

## Из исходников

Новую копию можно получить по точному тегу после публикации; существующие изменения не сбрасывайте:

```bash
git clone --branch v0.1.0a2 --single-branch https://github.com/mejustbox-byte/hyperv-opsec-auditor.git
cd hyperv-opsec-auditor
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps .
```

На Windows используйте те же `git` команды и замените команды установки:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-build-isolation --no-deps .
```

Для разработки вместо последней команды применяйте `-e .`. На облачном Linux эквивалент — `bash tools/setup_env.sh`; Bash не предполагается на Windows. Версии и хеши — в [стеке](TECH-STACK.md).

## Функциональная проверка

```bash
.venv/bin/hyperv-opsec-auditor audit fixtures/healthy.json --as-of 2026-10-09T00:00:00Z --format json --fail-on incomplete
.venv/bin/hyperv-opsec-auditor audit fixtures/unsafe.json --as-of 2026-10-09T00:00:00Z --format markdown --fail-on fail
```

Ожидается версия `0.1.0a2`, первый аудит — десять `pass` и код 0, второй — выявленные нарушения и код 1. Это вымышленные данные, не приемка Hyper-V. Для Windows замените путь исполняемого файла на `.\.venv\Scripts\hyperv-opsec-auditor.exe`. Полная проверка — [VERIFICATION](VERIFICATION.md).

## Удаление и обновление

Удаляется только пакет из выбранной виртуальной среды:

```bash
.venv/bin/python -m pip uninstall -y hyperv-opsec-auditor
```

```powershell
.\.venv\Scripts\python.exe -m pip uninstall -y hyperv-opsec-auditor
```

Инструменты разработки и приватные отчеты при этом сохраняются. Весь каталог `.venv` удаляйте вручную лишь после проверки, что он создан вами и не содержит нужных данных. Отчеты автоматически не удаляются. Обновление: сохраните старый отчет и параметры, проверьте контрольную сумму нового wheel, установите его в новую среду, повторите пример и проверьте контракт. Не перемещайте старые теги.
