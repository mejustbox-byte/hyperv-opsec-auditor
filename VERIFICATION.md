# Проверки и доказательства

## Область текущего цикла

Изменение документации и русских пользовательских текстов для пакета 0.1.0a2. Исходная проверенная база — commit `911113e338f3873e29fe9ab78be263112daf4174`, старый тег v0.1.0a1. SHA нового кода фиксируется PR/CI и в тексте публикации workflow, а не выдумывается до commit. Локальные проверки выполняются в Linux, Python 3.12.14.

| Проверка | Фактическое локальное свидетельство | Ограничение |
|---|---|---|
| Модульные/интеграционные тесты | 42 теста прошли, включая четыре проверки русского текста/UTF-8 | Только предоставленные синтетические данные |
| Покрытие | 96%, порог 85% | Не доказывает безопасность инфраструктуры |
| Схема | Совпадение с jsonschema 4.26.0 и русские описания | Структура, не истинность данных |
| Документация/секреты | Проверка внутренних ссылок и известных шаблонов | Не полный аудит секретов |
| Установка/артефакты | Сборка, обе лицензии MIT/metadata, полные документы sdist, чистая установка wheel и пересборка/установка sdist прошли tools/package_smoke.py | Публикация/скачивание проверяются отдельно |
| Linux/Windows CI | Новый запуск проверяется после PR, результаты не переносятся из a1 | POSIX тест ссылок Windows пропускается |
| Новый снимок облачной среды | НЕ ПРОВЕРЕН | Сохраненный draft не равен восстановлению новой задачи |
| Реальный Hyper-V/HGS/восстановление | НЕ ВЫПОЛНЕНО | Требуется LOCAL-PC.md |

## Воспроизводимые команды

```bash
bash tools/setup_env.sh
.venv/bin/python -m coverage run --source=hyperv_opsec_auditor -m unittest discover -s tests -v
.venv/bin/python -m coverage report --fail-under=85
.venv/bin/python tools/validate_docs.py
.venv/bin/python tools/scan_secrets.py
.venv/bin/python tools/build_release.py
.venv/bin/python tools/package_smoke.py
git diff --check
```

Проверяются и установленные команды по [INSTALL](INSTALL.md), JSON/Markdown примеры и библиотечный пример [контракта](CORE-CONTRACT.md). Ссылки на PR, commit, CI и выпуск фиксируются после фактического успеха. [Текущие запуски CI](https://github.com/mejustbox-byte/hyperv-opsec-auditor/actions), [протокол](VALIDATION.md).

## Сравнение полноты документации

Пользователь сообщил общий набор прежних пяти проектов: README/ARCHITECTURE/TECH-STACK/INSTALL/CONTRIBUTING/ROADMAP/SECURITY/CHANGELOG и расширенные угрозы, контракт, эксплуатация, облако, локальный стенд, проверки и выпуск. Для сравнения прочитаны публичные main документы honeypot-grid INSTALL/RUNBOOK/CLOUD-DEVELOPMENT/LOCAL-PC/RELEASE-CHECKLIST и redblue-arena VERIFICATION/MODULE-API. Заимствован перечень смысловых разделов, не стек, функции и результаты. В этом проекте нет Docker/VM адаптера, сетевой доставки, SQLite или HTTP API из других проектов. Полное соответствие разделов — [индекс README](README.md).
