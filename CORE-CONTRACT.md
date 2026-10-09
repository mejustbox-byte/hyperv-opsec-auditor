# Контракты CLI, JSON и библиотеки

HTTP API, сервер и удаленные плагины отсутствуют. Вход — локальный файл; результаты — stdout или новый файл. Идентификаторы и ключи ниже не переводятся.

## CLI

| Команда | Поведение | Результат |
|---|---|---|
| `rules` | Вывод HV-01..HV-10 с названием и критичностью | Код 0 |
| `validate INPUT` | Структура JSON, даты и уникальность | 0 при успехе, 2 при ошибке; свежесть не проверяет |
| `audit INPUT` | Валидация, применимость, правила, отчет | Коды зависят от --fail-on |

`audit`: `--format json/markdown` (по умолчанию markdown), `--output` (новый файл), `--as-of` (UTC YYYY-MM-DDTHH:MM:SSZ, по умолчанию сейчас), `--max-evidence-age-days 30`, `--max-restore-age-days 90` (1..3650), повторяемый `--exclude HV-XX`, `--fail-on none/fail/incomplete`. Код 0 означает успешную обработку, а не безопасность. `fail` дает 1 при нарушении, `incomplete` — также при unknown/not_run. Ошибки ввода/аргументов/записи — 2. При ошибке записи файл может быть неполным.

## Вход и выход

Обязательны `schema_version="1.0"`, `synthetic` (boolean), псевдонимы `scope`/`evidence_source`, `collected_at`. Разделы необязательны; внутри обязателен `state=ok/error/not_collected`. Максимум файла — 2 MiB, вложенность — 16, массив — 1000 уникальных элементов; псевдонимы — 1..64 ASCII букв/цифр/`_.-`, VLAN — 1..4094. Повторные ключи/идентификаторы, неизвестные поля, неверные даты, неограниченные числа запрещены. Политика — в require/approved/allowed/expected полях владельца. [Полная схема](src/hyperv_opsec_auditor/evidence.schema.json), [разделы](docs/input-contract.md).

Выход содержит `schema_version`, `tool_version`, `policy_version`, `scope`, `synthetic`, `evidence_source`, `collected_at`, `as_of`, `policy`, `summary`, `limitations`, `findings`. Результат: `rule_id`, `asset`, `title`, `status`, `severity`, `rationale`, `evidence`, `remediation`. Статусы `pass/fail/unknown/not_run`; критичность `critical/high/medium`. Ссылки evidence — указатели `pointer`, наблюдаемое `observed`, ожидаемые `expected`/`expected_pointer`. Русский текст UTF-8; JSON ключи и статусы совместимы с 1.0.

## Библиотека

```python
from hyperv_opsec_auditor.validation import load_json, validate_evidence, InputError
from hyperv_opsec_auditor.rules import audit
from hyperv_opsec_auditor.reporting import json_report, markdown_report

document = validate_evidence(load_json("fixtures/healthy.json"))
report = audit(document, as_of="2026-10-09T00:00:00Z",
               max_evidence_age_days=30, max_restore_age_days=90, exclude=())
text = json_report(report)
```

`load_json(path)` ограничивает загрузку; `validate_evidence(value)` проверяет структуру и возвращает тот же объект. `audit` повторно проверяет документ, не изменяет вход; `as_of` принимает строку UTC или datetime с часовым поясом, по умолчанию текущий UTC. Ошибки данных/политики дают `InputError`. Рендереры возвращают строку; запись и код завершения — ответственность вызывающего. Прямой объект библиотеки не эквивалентен ограниченной файловой загрузке: для недоверенного файла используйте `load_json`.

## Расширение правил

Измените `RULES` (ID, русское название, машинная критичность, ручная рекомендация), `SECTIONS`, ветку `_evaluate` или обработку VM. При новых входных полях обновите встроенную схему и русские описания, оцените изменение версии контракта. Не вводите импорт модулей/команд из JSON. Добавьте проверки pass/fail/unknown/not_run, отказа сбора, null, актуальности и применимости, затем матрицу и модель угроз. Внешних точек входа плагинов нет; эти функции внутренние и не обещают стабильности расширения без review.
