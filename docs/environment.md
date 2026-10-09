# Облачная среда разработки

Рабочая копия: `/workspace/hyperv-opsec-auditor`. Используйте существующую копию; отдельное рабочее дерево Git создается только по явному запросу. Документация находится в `docs/`, внешняя папка onboarding не используется.

## Установка с нуля

Из корня выполните `bash tools/setup_env.sh`. Скрипт создает `.venv`, устанавливает закрепленные с хешами инструменты из `requirements-dev.lock`, CLI в режиме разработки и проверяет синтетический пример командой `validate`. Сохраненная виртуальная среда не требуется; существующую можно использовать повторно. Для чистой установки сохраняйте или удаляйте только созданную вами среду, не чужие файлы. Исходники и файл зависимостей установкой не меняются.

Python 3.12+ предоставлен облачной платформой. Сторонних зависимостей выполнения нет; сборка и тесты используют PyPI (`pypi.org`, `files.pythonhosted.org`). Проверки TLS, подписей и контрольных сумм не отключаются.

## Проверки и запуск

```bash
.venv/bin/python -m coverage run --source=hyperv_opsec_auditor -m unittest discover -s tests -v
.venv/bin/python -m coverage report --fail-under=85
.venv/bin/python tools/validate_docs.py
.venv/bin/python tools/scan_secrets.py
.venv/bin/python tools/build_release.py
.venv/bin/python tools/package_smoke.py
.venv/bin/hyperv-opsec-auditor audit fixtures/healthy.json --as-of 2026-10-09T00:00:00Z --format json --fail-on incomplete
```

Нет фоновых служб, портов, платных ресурсов и производственных учетных данных. Для реальных предоставленных сведений используйте текущее UTC; фиксированный `--as-of` предназначен для синтетического примера. Linux и CI Python на Windows не заменяют Windows Server Hyper-V/HGS и стенд резервного копирования/восстановления.

`install_script` и `start_skill` сохранены на русском языке и описывают этот порядок работы. Сохранение черновика не исполняет скрипт, не публикует среду и не создает секреты. Сетевые настройки для GitHub API, загрузки файлов и журналов сохраняются без значений учетных данных; доступ Git/API проверяется отдельно. Workflow нового предварительного выпуска описан в `docs/development.md`.
