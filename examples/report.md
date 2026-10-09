# Автономный отчет о защите Hyper-V

Область: fictional-lab
Данные: 2026-10-09T00:00:00Z; момент оценки: 2026-10-09T00:00:00Z
Инструмент: 0.1.0a2; политика: mvp-baseline-1.0

**СИНТЕТИЧЕСКИЕ ДАННЫЕ — реальная инфраструктура не проверялась.**

pass: 1 | fail: 9 | unknown: 0 | not_run: 0

## Ограничения

- Автономная оценка предоставленных данных без доступа к Hyper-V, WinRM, сети и резервным копиям.
- Поддержка, эффективные права, изоляция и восстановление подтверждаются владельцем данных, а не независимой проверкой аудитора.
- Синтетические результаты не проверяют реальную инфраструктуру. Реальные испытания Windows Hyper-V/HGS и восстановления НЕ ВЫПОЛНЕНЫ.
- Изменения и исправления настроек не выполняются. Отчеты могут содержать конфиденциальные данные даже с псевдонимами.

## HV-01 / fictional-lab: pass

Поддержка хоста и обновления — критичность: high

Все необходимые предоставленные данные правила соответствуют базовой политике.

Данные:

- /host/hyperv\_role\_enabled: true; ожидается: true
- /host/supported\_configuration: true; ожидается: true
- /host/supported\_build: true; ожидается: true
- /host/security\_updates\_current: true; ожидается: true

Рекомендация (только для ручной проверки): Проверьте поддерживаемость хоста и сборки; в рамках разрешенного изменения включите утвержденную роль Hyper-V и установите утвержденные обновления безопасности.

## HV-02 / fictional-lab: fail

Права управления — критичность: critical

Данные нарушают базовую политику: неутвержденные администраторы.

Данные:

- /administration/effective\_rights\_reviewed: true; ожидается: true
- /administration/separate\_management\_accounts: true; ожидается: true
- /administration/management\_network\_isolated: true; ожидается: true
- /administration/actual\_admins: \[&quot;lab-admin&quot;, &quot;unexpected-admin&quot;\]; ожидается: \[&quot;lab-admin&quot;\]

Рекомендация (только для ручной проверки): Проверьте эффективные административные права; разрешенным изменением удалите неутвержденные права и разделите учетные записи и сети управления.

## HV-03 / fictional-lab: fail

Безопасность управления WinRM — критичность: high

Данные нарушают базовую политику: allow\_unencrypted.

Данные:

- /winrm/enabled: true; ожидается: true
- /winrm/https\_only: true; ожидается: true
- /winrm/certificate\_valid: true; ожидается: true
- /winrm/firewall\_scoped: true; ожидается: true
- /winrm/delegation\_restricted: true; ожидается: true
- /winrm/basic\_auth\_enabled: false; ожидается: false
- /winrm/allow\_unencrypted: true; ожидается: false

Рекомендация (только для ручной проверки): Проверьте HTTPS и сертификат; разрешенным изменением отключите Basic и незашифрованное управление, ограничьте правила межсетевого экрана и делегирование.

## HV-04 / fictional-lab: fail

Изоляция виртуальной сети — критичность: high

Данные нарушают базовую политику: VLAN вне утвержденной области или пустой набор VLAN.

Данные:

- /network/topology\_reviewed: true; ожидается: true
- /network/adapters/0/switch\_type: &quot;internal&quot;; ожидается: &quot;internal&quot;
- /network/adapters/0/vlans: \[99\]; ожидается: \[42\]
- /network/adapters/0/trunk: false; ожидается: false
- /network/adapters/0/sriov: false; ожидается: false

Рекомендация (только для ручной проверки): Проверьте утвержденную топологию, разрешенные VLAN, тип коммутатора, исключения для транков и SR-IOV; подтвердите изоляцию на стенде.

## HV-05 / vm-demo: fail

Secure Boot виртуальной машины — критичность: high

Данные нарушают базовую политику: secure\_boot\_enabled.

Данные:

- /virtual\_machines/vms/0/generation: 2
- /virtual\_machines/vms/0/profile\_supported: true
- /virtual\_machines/vms/0/require\_secure\_boot: true; ожидается: true
- /virtual\_machines/vms/0/secure\_boot\_enabled: false; ожидается: true
- /virtual\_machines/vms/0/secure\_boot\_template\_approved: true; ожидается: true

Рекомендация (только для ручной проверки): Для поддерживаемых профилей Gen2 включите утвержденный шаблон доверия Secure Boot в рамках проверенного изменения.

## HV-06 / vm-demo: fail

vTPM и защита Shielded VM — критичность: high

Данные нарушают базовую политику: shielded.

Данные:

- /virtual\_machines/vms/0/generation: 2
- /virtual\_machines/vms/0/profile\_supported: true
- /virtual\_machines/vms/0/require\_vtpm: true
- /virtual\_machines/vms/0/require\_shielding: true
- /virtual\_machines/vms/0/vtpm\_enabled: true; ожидается: true
- /virtual\_machines/vms/0/shielded: false; ожидается: true
- /virtual\_machines/vms/0/key\_protector\_valid: true; ожидается: true
- /virtual\_machines/vms/0/hgs\_attestation\_valid: true; ожидается: true

Рекомендация (только для ручной проверки): Проверьте требования vTPM отдельно от Shielded VM; подтвердите защиту ключей и доверие HGS на поддерживаемом стенде.

## HV-07 / fictional-lab: fail

Защита виртуального хранилища — критичность: critical

Данные нарушают базовую политику: unapproved\_principals.

Данные:

- /storage/assets/0/effective\_acl\_reviewed: true; ожидается: true
- /storage/assets/0/unapproved\_principals: \[&quot;broad-access&quot;\]; ожидается: \[\]
- /storage/assets/0/require\_encryption: true
- /storage/assets/0/encrypted: true; ожидается: true

Рекомендация (только для ручной проверки): Проверьте эффективный доступ к VHDX, контрольным точкам, конфигурациям и копиям; удалите неутвержденные права и обеспечьте требуемое шифрование разрешенным изменением.

## HV-08 / fictional-lab: fail

Независимые защищенные резервные копии — критичность: critical

Данные нарушают базовую политику: checkpoint\_only.

Данные:

- /backup/independent\_copy: true; ожидается: true
- /backup/immutable\_or\_offline: true; ожидается: true
- /backup/separate\_identity: true; ожидается: true
- /backup/checkpoint\_only: true; ожидается: false

Рекомендация (только для ручной проверки): Используйте независимые неизменяемые или автономные копии и отдельные учетные записи резервного копирования. Контрольные точки не являются резервными копиями.

## HV-09 / fictional-lab: fail

Журналирование аудита — критичность: medium

Данные нарушают базовую политику: central\_delivery\_verified.

Данные:

- /logging/audit\_enabled: true; ожидается: true
- /logging/central\_delivery\_verified: false; ожидается: true
- /logging/tamper\_protection: true; ожидается: true
- /logging/retention\_days: 90; ожидается: 30

Рекомендация (только для ручной проверки): Включите утвержденный аудит, подтвердите централизованную доставку и защиту от подмены, обеспечьте требуемый срок хранения.

## HV-10 / fictional-lab: fail

Проверенная готовность к восстановлению — критичность: critical

Данные нарушают базовую политику: RTO превышает цель.

Данные:

- /recovery/drill\_performed\_at: &quot;2026-10-01T00:00:00Z&quot;
- /recovery/runbook\_reviewed: true; ожидается: true
- /recovery/integrity\_verified: true; ожидается: true
- /recovery/isolated\_restore: true; ожидается: true
- /recovery/reviewer\_approved: true; ожидается: true
- /recovery/measured\_rpo\_hours: 1; ожидается: 4
- /recovery/measured\_rto\_hours: 10; ожидается: 8

Рекомендация (только для ручной проверки): Проведите разрешенное изолированное учебное восстановление без вредоносных программ; проверьте целостность, документируйте RPO/RTO, проверяющего и инструкцию.
