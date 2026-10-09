# hyperv-opsec-auditor

Аудитор состояния защиты Hyper-V **только для чтения**, работающий автономно с предоставленными данными JSON. Версия `0.1.0a2` — предварительный выпуск: сбор данных с Windows, подключение к хостам и автоматическое исправление настроек не реализованы.

Проверяются предоставленные сведения о поддерживаемости хоста и обновлениях, правах управления, WinRM, изоляции VM/vSwitch/VLAN, Secure Boot/vTPM/Shielded VM, защите VHDX/контрольных точек/резервных копий, журналировании и проверенном восстановлении. Статус `pass` означает соответствие предоставленных данных базовой политике, а не независимую проверку инфраструктуры. Реальные испытания Hyper-V/HGS и восстановления **НЕ ВЫПОЛНЕНЫ**.

## Установка и запуск

Требуется Python 3.12 или новее. Сторонних зависимостей для выполнения нет. Из рабочей копии исходников:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/hyperv-opsec-auditor validate fixtures/healthy.json
.venv/bin/hyperv-opsec-auditor audit fixtures/healthy.json --as-of 2026-10-09T00:00:00Z --format markdown
.venv/bin/hyperv-opsec-auditor audit fixtures/unsafe.json --as-of 2026-10-09T00:00:00Z --format json --fail-on fail
```

Последняя команда намеренно завершается с кодом 1. Все примеры вымышлены. Фиксированный `--as-of` делает демонстрацию воспроизводимой; для реальных предоставленных данных опустите его, чтобы использовать текущее UTC. [Руководство пользователя](docs/user-guide.md) содержит команды для Windows, установку wheel без сети, описание статусов, кодов завершения и подготовки данных.

## Проверки и разработка

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/validate_docs.py
.venv/bin/python tools/scan_secrets.py
.venv/bin/python tools/build_release.py
.venv/bin/python tools/package_smoke.py
```

[Документация проекта](docs/README.md): требования, модель угроз, архитектура, ADR, матрица правил, [план MVP](docs/mvp-plan.md) и [лабораторная процедура Windows](docs/lab.md). CI использует синтетические данные на предоставленных GitHub исполнителях, включая автономные тесты Python на Windows; это не проверка платформы Hyper-V. Не помещайте реальные секреты и необработанные производственные данные в публичный репозиторий. [Правила участия](CONTRIBUTING.md).

## Полный индекс документации

| Раздел | Самостоятельный документ | Дополнительные материалы |
|---|---|---|
| Назначение и границы | [README](README.md) | [Требования](docs/requirements.md) |
| Компоненты и поток | [ARCHITECTURE](ARCHITECTURE.md) | [Архитектура MVP](docs/architecture.md) |
| Стек и точные версии | [TECH-STACK](TECH-STACK.md) | [ADR](docs/adr/0001-stack.md) |
| Установка/проверка/удаление | [INSTALL](INSTALL.md) | [Руководство](docs/user-guide.md) |
| Разработка и review | [CONTRIBUTING](CONTRIBUTING.md) | [Разработка/CI](docs/development.md) |
| Этапы и приемка | [ROADMAP](ROADMAP.md) | [План MVP](docs/mvp-plan.md) |
| Угрозы и безопасность | [THREAT-MODEL](THREAT-MODEL.md), [SECURITY](SECURITY.md) | [Подробная модель](docs/threat-model.md) |
| CLI/JSON/библиотека | [CORE-CONTRACT](CORE-CONTRACT.md) | [Вход](docs/input-contract.md), [правила](docs/check-matrix.md) |
| Эксплуатация/ошибки/приватность | [RUNBOOK](RUNBOOK.md) | [Руководство](docs/user-guide.md) |
| Облачная установка/публикация/восстановление | [CLOUD-DEVELOPMENT](CLOUD-DEVELOPMENT.md) | [Среда](docs/environment.md) |
| Локальный Windows стенд | [LOCAL-PC](LOCAL-PC.md) | [Лаборатория](docs/lab.md) |
| Фактические проверки | [VERIFICATION](VERIFICATION.md), [VALIDATION](VALIDATION.md) | [CI](https://github.com/mejustbox-byte/hyperv-opsec-auditor/actions) |
| Выпуск и суммы | [RELEASE-CHECKLIST](RELEASE-CHECKLIST.md), [RELEASE-NOTES](RELEASE-NOTES.md) | [CHANGELOG](CHANGELOG.md) |

Прежние материалы `docs/` сохранены, связаны ссылками и уточняют основные документы. HTTP API и функции других проектов не заявляются.

## Лицензия и документы безопасности

Код и документация проекта распространяются по MIT. Канонический английский [LICENSE](LICENSE) и [русский перевод/пояснение](LICENSE.ru.md) включены в wheel и sdist. Сторонние лицензии не заменяются лицензией проекта.

| Документ | Назначение |
|---|---|
| [SECURITY](SECURITY.md) | Поддерживаемые prerelease, сообщение об уязвимости, границы доверия |
| [SECURITY-DATA](SECURITY-DATA.md) | Минимизация, доступ, хранение, retention и утечки evidence/отчетов |
| [SUPPLY-CHAIN](SUPPLY-CHAIN.md) | Точные зависимости/лицензии, обновления, целостность выпуска |
| [SECURITY-TESTING](SECURITY-TESTING.md) | Автономные security проверки и не выполненные лабораторные gates |
| [AGENTS](AGENTS.md) | Правила следующих циклов и фактической проверки результатов |
| [LICENSE.ru](LICENSE.ru.md) | Права MIT, отказ от гарантий и ссылка на оригинал |
