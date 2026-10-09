# ADR 0001: стек и границы выполнения

Статус: принято для offline MVP; Windows collector отложен.

## Решение
Проектировать Windows collector на PowerShell с native Hyper-V/CIM API; baseline PowerShell 5.1 для встроенного Windows Server окружения. PowerShell 7 совместимость не предполагается и проверяется отдельно. Offline evaluator реализован на Python 3.12 со структурированным JSON и unittest; runtime зависимостей нет. Bundled JSON Schema 2020-12 использует ограниченный набор keywords; встроенный validator проверяется на совпадение с jsonschema в CI. Build/test инструменты закреплены с SHA256 в requirements-dev.lock.

## Причины и альтернативы
PowerShell дает доступ к платформенным API без Linux эмуляции Hyper-V. Python удобен для переносимой детерминированной offline оценки и синтетических тестов. All-PowerShell уменьшает число runtime, но затрудняет независимую Linux проверку; .NET collector дает типизацию, но добавляет toolchain до подтверждения требований. Удаленный WinRM collector увеличивает границу credentials и отложен.

## Последствия и открытые вопросы
Нужен версионированный evidence contract, единый UTC формат и Windows/Python parity fixtures. Минимальные права, поддерживаемые Windows Server версии, signed distribution и packaging требуют Windows lab ADR/решений до реализации. PowerShell на Linux не заменяет Hyper-V module. Облачная среда не устанавливает Windows инструменты только ради наличия команды.
