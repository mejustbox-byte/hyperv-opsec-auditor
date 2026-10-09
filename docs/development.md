# Разработка и CI

Использовать существующий checkout `/workspace/hyperv-opsec-auditor`; не создавать worktree без явного запроса. Python >=3.12, Git. Runtime зависимостей нет, build/test tools зафиксированы с hashes в requirements-dev.lock. Secrets и службы не нужны.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/python -m coverage run --source=hyperv_opsec_auditor -m unittest discover -s tests -v
.venv/bin/python -m coverage report --fail-under=85
.venv/bin/python tools/validate_docs.py
.venv/bin/python tools/scan_secrets.py
.venv/bin/python tools/build_release.py
.venv/bin/python tools/package_smoke.py
```

CI на Ubuntu и Windows hosted runners запускает offline тесты, проверку документации/секретов, pinned build, sdist rebuild и установку wheel в clean venv. Linux coverage порог 85% для модулей, CLI дополнительно проверяется subprocess integration tests. Никаких real Hyper-V/WinRM/HGS/backup connections или self-hosted runners. Windows POSIX-symlink case skipped с явной причиной. Actions pinned SHA. Недоверенные PR не должны запускаться на будущем приватном стенде.

Тесты имеют pass/fail/unknown/not_run сценарии, malformed inputs, JSON Schema parity, state/freshness и output safety. Нулевой test run не допускается как readiness. `tools/build_release.py` готовит wheel/sdist, copies synthetic examples/schema/release notes и SHA256SUMS; `tools/package_smoke.py` проверяет повторную сборку из sdist и install-only runtime без сторонних пакетов. Эти команды не публикуют release.

Перед commit: diff review и pattern secret scan, который не является гарантией отсутствия любых секретов. Реальные отчеты/evidence хранить вне checkout; игнорируемый reports/ не защищает от force-add. Проверки и публикация описываются по фактическому результату, local success не заменяет remote CI.

## Prerelease delivery

`.github/workflows/release.yml` is manually dispatched only on `main`. It checks out the exact dispatch SHA, verifies the package version, runs the offline tests/checks/build/clean-install smoke and publishes `v0.1.0a1` with all `dist/` assets. Only its publish job has contents:write; the GitHub-issued short-lived token is supplied only to the publish step, never stored in source. Checkout does not persist credentials. A rerun can replace this version's assets only if its existing tag resolves to the same source SHA; a mismatched tag stops publication.

Cloud `gh` upload authentication can differ from Git/API access. Use the Actions workflow through an authorized GitHub connection rather than extracting or copying credentials. No production credentials are needed. This publishes a GitHub prerelease, not the cloud environment; environment draft review/publication remains a separate product operation.
