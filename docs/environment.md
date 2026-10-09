# Облачная среда разработки

Рабочий checkout: `/workspace/hyperv-opsec-auditor`. Использовать существующий checkout; отдельный worktree создается только по явному запросу. Документация находится в `docs/`; внешняя папка onboarding не используется.

## Установка с нуля

Из checkout: `bash tools/setup_env.sh`. Script создает `.venv`, устанавливает exact hashed build/test dependencies из `requirements-dev.lock`, editable CLI и запускает validate synthetic fixture. Сохраненный venv не нужен; существующий venv можно переиспользовать. Для чистой установки задайте новый checkout либо сохраните/удалите только venv, созданный вами. Исходные файлы и lockfile не меняются установкой.

Python 3.12+ уже предоставлен cloud runtime. Runtime продукта без сторонних dependencies; build/test dependencies требуют PyPI (`pypi.org`, `files.pythonhosted.org`). Подписей/checksums/TLS bypass нет.

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

Нет фоновых сервисов, портов, платных ресурсов и real credentials. Для реального evidence используйте текущее UTC; фиксированный as-of предназначен для synthetic example. Linux и hosted Windows CI не заменяют Windows Server Hyper-V/HGS/backup/recovery стенд.

Сохраненные `install_script`/`start_skill` описывают этот workflow. Draft save не исполняет script, не публикует среду и не создает credentials. В draft добавлены `api.github.com` и `uploads.github.com` для GitHub API/release; настройки не содержат secret values. Доступность Git push/API подтверждается отдельно; authenticated API может оставаться недоступным независимо от read-only public API и Git push.
