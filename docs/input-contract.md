# Контракт evidence 1.0

Авторитетная схема: [evidence.schema.json](../src/hyperv_opsec_auditor/evidence.schema.json). Содержит точные типы, enum и ограничения. Runtime validator поддерживает только keywords этого bundled schema; произвольная схема или remote $ref не принимается. JSON Schema parity проверяется внешним jsonschema в tests.

Обязательные поля: schema_version="1.0", synthetic=true/false, scope и evidence_source (псевдонимы 1..64 ASCII букв/цифр/_.-), collected_at YYYY-MM-DDTHH:MM:SSZ. Никаких паролей, real hostname, IP, имен пользователей или ключей. Разделы необязательны; state обязателен при наличии: ok, error, not_collected. Каждый array <=1000 unique элементов, input <=2 MiB; неизвестные поля и повторные JSON keys запрещены. Inventory IDs уникальны внутри раздела; VLAN 1..4094.

Boolean null/отсутствие — unknown, а не false. Для ожидаемых требований используются require_*, approved_*, allowed_* и expected_* поля: владелец предварительно утверждает их. `supported_configuration`, `supported_build`, `profile_supported`, `effective_rights_reviewed`, `effective_acl_reviewed`, `central_delivery_verified` — внешние reviewed attestations; аудитор не проверяет их истинность.

Разделы:
- host: роль Hyper-V, support конфигурации/build и актуальность updates.
- administration: actual_admins и approved_admins псевдонимы, effective review, разделение accounts/network.
- winrm: enabled; если включен — HTTPS/certificate/firewall/delegation, запрет Basic и unencrypted.
- network: complete reviewed inventory adapters; switch_type/expected_switch_type, фактические vlans/allowed_vlans, trunk/allow_trunk и sriov/allow_sriov.
- virtual_machines: полный inventory vms, generation и supported profile; отдельные require_secure_boot/require_vtpm/require_shielding и фактические настройки. Шаблон Secure Boot approved отдельно.
- storage: assets с reviewed effective ACL, unapproved_principals и encryption policy; отдельно перечислять VHDX, AVHDX, VM config и backup assets.
- backup: independent copy, immutable/offline, separate identity, checkpoint_only.
- logging: audit, внешняя delivery, tamper protection, actual/required retention_days.
- recovery: reviewed runbook, drill_performed_at, integrity/isolated/reviewer attestations, measured/target RPO/RTO в часах. Drill позже collection запрещен.

Freshness: --as-of задает UTC момент оценки; default текущее UTC. --max-evidence-age-days default 30; --max-restore-age-days default 90. Future evidence или старше лимита дает unknown; граница включительна. Для воспроизводимых examples всегда задается фиксированное as-of. Replaying fixture с as-of 2026-10-09 не подтверждает свежесть реального host.

Отсутствующий/not_collected раздел → not_run. Error state → unknown. Неполный inventory не дает pass; отдельный известный breach может дать fail. Gen1/unsupported VM или отключенное требование → not_run с причиной. Исключение через --exclude HV-XX отображается, не скрывается. Not_run не равен безопасному состоянию. Некорректный input прекращает аудит с exit 2, без partial report.
