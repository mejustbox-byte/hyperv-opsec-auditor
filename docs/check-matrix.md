# Матрица offline правил и платформенной приемки

Все семейства реализованы и покрыты синтетическими тестами. Реальные Windows Hyper-V/HGS/restore проверки НЕ ВЫПОЛНЕНЫ.

| ID | Evidence / offline baseline | Applicability / unknown | Windows acceptance |
|---|---|---|---|
| HV-01 | Role, supported configuration/build, updates=true | Missing/null/error/stale → unknown | Проверить support по конкретному build/hardware |
| HV-02 | Reviewed effective rights, actual admins subset approved, separate accounts/network | Отсутствие review не дает pass | AD nesting/delegation/PAW/права |
| HV-03 | HTTPS/cert/firewall/delegation=true, Basic/unencrypted=false | Disabled → not_run | Listeners, effective policies, expired certificate |
| HV-04 | Reviewed complete adapter inventory, allowed VLAN/switch/trunk/SR-IOV | Incomplete → unknown; no adapters → not_run | External/internal/private, trunk, runtime isolation |
| HV-05 | Supported Gen2, require Secure Boot, enabled + approved template | Gen1/unsupported/require=false → not_run | Supported guest/trust template и boot |
| HV-06 | Required vTPM; shielding additionally requires shielded/key protector/HGS | vTPM alone does not pass shielding; profile missing → unknown | HGS trust, key recovery, supported VM |
| HV-07 | Complete storage inventory, reviewed ACL/no unapproved principals, required encryption | Missing effective review → unknown | VHDX/AVHDX/config/SMB ACL и encryption |
| HV-08 | Independent immutable/offline copy, separate identity, not checkpoint-only | Vendor evidence missing → unknown | Реальные backup rights/immutability |
| HV-09 | Audit, external delivery, tamper protection, sufficient retention | Missing delivery → unknown | Event channels, sink/retention/переполнение |
| HV-10 | Fresh dated drill, runbook/integrity/isolation/reviewer, measured RPO/RTO within target | No/stale drill → unknown | Изолированное recovery exercise без malware |

Pass требует всех обязательных фактов. Подтвержденное нарушение доминирует над отсутствием иных фактов; stale evidence целиком не используется. Incomplete VM inventory имеет отдельный unknown finding наряду с per-VM результатами. Freshness limits и версии включены в JSON отчет. Политика задается владельцем через expected/allowed/required поля, а не загружается из внешнего executable файла. Полное покрытие инфраструктуры не заявляется.
