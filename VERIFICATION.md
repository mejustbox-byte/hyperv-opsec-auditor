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
| Linux/Windows CI | Успешны Ubuntu/Windows на commit 9641130; точные ссылки ниже, после обновления протокола требуется новый CI | POSIX тест ссылок Windows пропускается |
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

## Фактически проверенные удаленные запуски

Код локализации, полной документации, безопасности и лицензирования проверен в [PR #3](https://github.com/mejustbox-byte/hyperv-opsec-auditor/pull/3): исходный commit [9641130c78742987f8ebdc885a1da7028fde392f](https://github.com/mejustbox-byte/hyperv-opsec-auditor/commit/9641130c78742987f8ebdc885a1da7028fde392f). [CI push](https://github.com/mejustbox-byte/hyperv-opsec-auditor/actions/runs/37928698259) и [CI PR](https://github.com/mejustbox-byte/hyperv-opsec-auditor/actions/runs/37928740999) завершены успешно на Ubuntu 24.04 и Windows 2022. По полученным журналам: Ubuntu — 42 теста прошли; Windows — 42 обнаружены, 41 прошел, один POSIX тест ссылки пропущен; покрытие обеих ОС 96%. На обеих ОС прошли ссылки, поиск известных секретов, сборка, license metadata/файлы, чистая установка wheel и пересборка/установка sdist.

Эта запись добавляется следующим документальным commit; результаты выше относятся строго к указанному SHA. Финальный commit PR и merge/main должны получить собственные успешные CI до выпуска. Release workflow фиксирует точный опубликованный SHA и свою ссылку в публичных русских сведениях о выпуске; файлы после публикации проверяются отдельно. Существующий v0.1.0a1 по-прежнему указывает на 911113e338f3873e29fe9ab78be263112daf4174; у него переведены только название/описание, все 11 assets сохранены.
