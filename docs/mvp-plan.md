# План и границы первого MVP

## Реализуемый vertical slice
1. Публичная документация требований, угроз, архитектуры и ADR.
2. JSON Schema 1.0 и strict offline ingestion, три синтетических сценария.
3. CLI validate/rules/audit и 10 семейств правил, JSON/Markdown, безопасный output.
4. Unit tests каждого семейства и статусов; CLI integration, malformed inputs, packaging smoke.
5. Hashed lockfile, CI на Linux/Windows для offline тестов, wheel/sdist/checksums.
6. PR и merge после доступных проверок; prerelease с ясными ограничениями.

## Отложено до лабораторной приемки
Live collector PowerShell 5.1, supported-version profiles Microsoft, effective group/ACL resolution, WinRM integration, runtime isolation, HGS attestation, vendor backup и подписанный restore protocol. Приемка включает сравнение состояния до/после, поддерживаемые bare-metal/nested конфигурации, отказ доступа и backup restore без malware. Продукт не исправляет настройки.

## Условие выпуска
Доступные offline проверки и package install должны пройти; секреты не допускаются. Windows Hyper-V/реальное восстановление остаются NOT RUN и требуют prerelease. Локальные тесты не равны remote CI; release notes фиксируют фактические результаты, а недоступные GitHub операции блокируют соответствующую часть выпуска.
