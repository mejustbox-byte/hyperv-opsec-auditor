# Лаборатория и проверка восстановления

## Два контура
Linux cloud: Git, Python 3.12, документация, синтетические JSON и проверка их контракта. Команды: `.venv/bin/python -m unittest discover -s tests -v` и `.venv/bin/python tools/package_smoke.py`. Они тестируют offline evaluator и CLI, не Hyper-V.

Windows: выделенный Windows Server с ролью Hyper-V и поддерживаемой конфигурацией аппаратной или nested virtualization. Владелец проверяет поддержку CPU/SLAT, firmware virtualization, версии/редакции хоста, гостевых ОС и конкретной вложенной платформы по Microsoft documentation. Произвольная cloud VM не считается пригодной. HGS/Shielded сценарии требуют отдельной поддерживаемой инфраструктуры и доверия; отсутствие HGS не имитируется успешной проверкой.

## Подготовка и сценарии
1. Зафиксировать owner, письменный scope, build/patch level, hardware, supported profile и ожидаемую топологию. Только вымышленные учетные записи и тестовые данные; отключить маршруты в production.
2. Создать раздельные management, VM и backup сегменты; тестовые Gen1/Gen2 VM и подходящие гости; approved Secure Boot/vTPM и отдельный shielding профиль при поддержке.
3. Задать baseline прав, WinRM, storage ACL, журналирования и backup. Создать варианты нарушений средствами владельца лаборатории, вне auditor. Продукт их не изменяет.
4. Зафиксировать состояние до сбора; предоставить reviewed evidence с помощью отдельно разрешенных read-only инструментов; запустить offline CLI; проверить ожидаемые результаты матрицы, отказ доступа, timeout и redaction; сравнить состояние после. Audit events от чтения учитывать отдельно.
5. Восстановить baseline вручную; сохранить протокол и очищенные evidence вне публичного репозитория.

## Restore drill без ransomware
Не запускать malware. В изолированном recovery контуре моделировать недоступность исходного хранилища и основных credentials административным сценарием. Восстановить VM из независимой копии по runbook; проверить boot, приложения, контрольные суммы тестовых данных, network isolation и отсутствие reinfection prerequisites. Измерить фактические RPO/RTO относительно утвержденных целей. Checkpoints не заменяют backup. Отдельно проверить восстановление ключей/доверия для защищенных VM в поддерживаемом профиле.

Протокол: UTC timestamps, scope/build, backup ID без секретов, роли исполнителей, утвержденные цели, шаги, evidence целостности, измерения, отклонения, reviewer, expiry. Разрушительные шаги требуют отдельного разрешения владельца стенда. Сейчас все Windows/restore проверки не выполнены.

## Авторитетные источники для утверждения профилей
- [Hyper-V requirements](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/host-hardware-requirements)
- [Nested virtualization](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/enable-nested-virtualization)
- [Guarded fabric and shielded VMs](https://learn.microsoft.com/en-us/windows-server/security/guarded-fabric-shielded-vm/guarded-fabric-and-shielded-vms)
- [WinRM security](https://learn.microsoft.com/en-us/windows/win32/winrm/security)

Ссылки — отправная точка; совместимость конкретного стенда еще не подтверждена.

## Протокол приемки MVP на Windows
1. Установить wheel в Python 3.12 venv; проверить CLI version, validate и audit synthetic fixtures с фиксированным as-of. Это только offline smoke.
2. На поддерживаемом стенде подготовить реальные pseudonymous evidence для каждого HV-01..HV-10; отдельно утвердить expected/allowed policy и external review. Не копировать реальный evidence в Git.
3. Зафиксировать timestamps/build/profile, права доступа, исходное состояние; выполнить CLI audit с текущим UTC, затем проверить findings против независимой оценки администратора.
4. Проверить Gen1/Gen2, supported/unsupported profiles, Secure Boot guest templates, vTPM без shielding и supported HGS сценарий; не заменять unavailable case pass.
5. Независимо подтвердить сетевую изоляцию, effective AD/storage rights, forwarding и backup immutability. MVP только потребляет результаты этих проверок.
6. Выполнить описанный restore drill и сравнить RPO/RTO/integrity с отчетом; зафиксировать evidence freshness и отказ/неполноту.
7. Сравнить состояние до/после. CLI не выполняет инфраструктурные операции; будущий collector нуждается в отдельной приемке read-only allowlist.

Статус: Linux синтетические тесты выполняются; Windows hosted offline CI не равен этой процедуре. Все реальные пункты 2..7, supported nested virtualization и HGS/restore НЕ ВЫПОЛНЕНЫ.
