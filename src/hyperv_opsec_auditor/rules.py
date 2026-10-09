"""Детерминированные автономные правила без доступа к хосту и исправления настроек."""
from datetime import datetime, timezone
from . import __version__
from .validation import InputError, parse_utc, validate_evidence

POLICY_VERSION = 'mvp-baseline-1.0'
RULES = {
    'HV-01': ('Поддержка хоста и обновления', 'high', 'Проверьте поддерживаемость хоста и сборки; в рамках разрешенного изменения включите утвержденную роль Hyper-V и установите утвержденные обновления безопасности.'),
    'HV-02': ('Права управления', 'critical', 'Проверьте эффективные административные права; разрешенным изменением удалите неутвержденные права и разделите учетные записи и сети управления.'),
    'HV-03': ('Безопасность управления WinRM', 'high', 'Проверьте HTTPS и сертификат; разрешенным изменением отключите Basic и незашифрованное управление, ограничьте правила межсетевого экрана и делегирование.'),
    'HV-04': ('Изоляция виртуальной сети', 'high', 'Проверьте утвержденную топологию, разрешенные VLAN, тип коммутатора, исключения для транков и SR-IOV; подтвердите изоляцию на стенде.'),
    'HV-05': ('Secure Boot виртуальной машины', 'high', 'Для поддерживаемых профилей Gen2 включите утвержденный шаблон доверия Secure Boot в рамках проверенного изменения.'),
    'HV-06': ('vTPM и защита Shielded VM', 'high', 'Проверьте требования vTPM отдельно от Shielded VM; подтвердите защиту ключей и доверие HGS на поддерживаемом стенде.'),
    'HV-07': ('Защита виртуального хранилища', 'critical', 'Проверьте эффективный доступ к VHDX, контрольным точкам, конфигурациям и копиям; удалите неутвержденные права и обеспечьте требуемое шифрование разрешенным изменением.'),
    'HV-08': ('Независимые защищенные резервные копии', 'critical', 'Используйте независимые неизменяемые или автономные копии и отдельные учетные записи резервного копирования. Контрольные точки не являются резервными копиями.'),
    'HV-09': ('Журналирование аудита', 'medium', 'Включите утвержденный аудит, подтвердите централизованную доставку и защиту от подмены, обеспечьте требуемый срок хранения.'),
    'HV-10': ('Проверенная готовность к восстановлению', 'critical', 'Проведите разрешенное изолированное учебное восстановление без вредоносных программ; проверьте целостность, документируйте RPO/RTO, проверяющего и инструкцию.'),
}
SECTIONS = {'HV-01':'host','HV-02':'administration','HV-03':'winrm','HV-04':'network','HV-05':'virtual_machines','HV-06':'virtual_machines','HV-07':'storage','HV-08':'backup','HV-09':'logging','HV-10':'recovery'}
LIMITATIONS = [
    'Автономная оценка предоставленных данных без доступа к Hyper-V, WinRM, сети и резервным копиям.',
    'Поддержка, эффективные права, изоляция и восстановление подтверждаются владельцем данных, а не независимой проверкой аудитора.',
    'Синтетические результаты не проверяют реальную инфраструктуру. Реальные испытания Windows Hyper-V/HGS и восстановления НЕ ВЫПОЛНЕНЫ.',
    'Изменения и исправления настроек не выполняются. Отчеты могут содержать конфиденциальные данные даже с псевдонимами.',
]

class Checks:
    def __init__(self, data, pointer):
        self.data, self.pointer = data, pointer
        self.evidence, self.failures, self.missing = [], [], []

    def expect(self, key, expected):
        value = self.data.get(key)
        self.evidence.append({'pointer':f'{self.pointer}/{key}', 'observed':value, 'expected':expected})
        if value is None:
            self.missing.append(key)
        elif value != expected:
            self.failures.append(key)

    def compare(self, key, expected_key, predicate, explanation):
        value, expected = self.data.get(key), self.data.get(expected_key)
        self.evidence.append({'pointer':f'{self.pointer}/{key}', 'observed':value, 'expected_pointer':f'{self.pointer}/{expected_key}', 'expected':expected})
        if value is None or expected is None:
            self.missing.append(key + '/' + expected_key)
        elif not predicate(value, expected):
            self.failures.append(explanation)

    def result(self):
        if self.failures:
            return 'fail', 'Данные нарушают базовую политику: ' + ', '.join(self.failures) + '.'
        if self.missing:
            return 'unknown', 'Необходимые данные отсутствуют или равны null: ' + ', '.join(self.missing) + '.'
        return 'pass', 'Все необходимые предоставленные данные правила соответствуют базовой политике.'

def finding(rule_id, asset, status, rationale, evidence=()):
    title, severity, remediation = RULES[rule_id]
    return {'rule_id':rule_id,'asset':asset,'title':title,'status':status,'severity':severity,'rationale':rationale,'evidence':list(evidence),'remediation':remediation}

def from_checks(rule_id, asset, checks):
    return finding(rule_id, asset, *checks.result(), checks.evidence)

def _vm_findings(rule, section, document):
    result = []
    vms = section.get('vms')
    if section.get('inventory_complete') is not True:
        result.append(finding(rule, document['scope'], 'unknown', 'Полнота перечня VM не подтверждена.'))
    if vms is None:
        return result or [finding(rule, document['scope'], 'unknown', 'Перечень VM отсутствует.')]
    if not vms:
        return result or [finding(rule, document['scope'], 'not_run', 'Полный перечень не содержит VM; конфигурации VM не проверялись.')]
    host_supported = document.get('host', {}).get('supported_configuration')
    host_state = document.get('host', {}).get('state')
    for index, vm in enumerate(vms):
        pointer = f'/virtual_machines/vms/{index}'
        evidence = [{'pointer':pointer+'/generation','observed':vm['generation']},
                    {'pointer':pointer+'/profile_supported','observed':vm.get('profile_supported')}]
        if vm['generation'] == 1:
            result.append(finding(rule, vm['id'], 'not_run', 'Gen1 вне профиля применимости Secure Boot/vTPM/Shielded VM.', evidence))
            continue
        if vm.get('profile_supported') is False or host_supported is False:
            result.append(finding(rule, vm['id'], 'not_run', 'Заявлен неподдерживаемый профиль; защита VM не проверена.', evidence))
            continue
        if vm.get('profile_supported') is not True or host_supported is not True or host_state != 'ok':
            result.append(finding(rule, vm['id'], 'unknown', 'Данные о поддерживаемом профиле VM и хоста неполны.', evidence))
            continue
        checks = Checks(vm, pointer)
        checks.evidence.extend(evidence)
        if rule == 'HV-05':
            required = vm.get('require_secure_boot')
            if required is False:
                result.append(finding(rule, vm['id'], 'not_run', 'Secure Boot не требуется предоставленным профилем.', evidence))
                continue
            if required is None:
                result.append(finding(rule, vm['id'], 'unknown', 'Требование применимости Secure Boot отсутствует.', evidence))
                continue
            checks.expect('require_secure_boot', True)
            checks.expect('secure_boot_enabled', True)
            checks.expect('secure_boot_template_approved', True)
        else:
            tpm, shielding = vm.get('require_vtpm'), vm.get('require_shielding')
            if tpm is False and shielding is False:
                result.append(finding(rule, vm['id'], 'not_run', 'Предоставленный профиль не требует vTPM или Shielded VM.', evidence))
                continue
            for name in ('require_vtpm','require_shielding'):
                if vm.get(name) is None:
                    checks.missing.append(name)
                checks.evidence.append({'pointer':pointer+'/'+name, 'observed':vm.get(name)})
            if tpm is True or shielding is True:
                checks.expect('vtpm_enabled', True)
            if shielding is True:
                for name in ('shielded','key_protector_valid','hgs_attestation_valid'):
                    checks.expect(name, True)
        result.append(from_checks(rule, vm['id'], checks))
    return result

def _evaluate(rule, data, document, as_of, max_restore_age_days):
    scope = document['scope']
    if rule in ('HV-05','HV-06'):
        return _vm_findings(rule, data, document)
    c = Checks(data, '/'+SECTIONS[rule])
    if rule == 'HV-01':
        for key in ('hyperv_role_enabled','supported_configuration','supported_build','security_updates_current'):
            c.expect(key, True)
    elif rule == 'HV-02':
        for key in ('effective_rights_reviewed','separate_management_accounts','management_network_isolated'):
            c.expect(key, True)
        c.compare('actual_admins','approved_admins',lambda a,b:set(a)<=set(b),'неутвержденные администраторы')
    elif rule == 'HV-03':
        if data.get('enabled') is False:
            return [finding(rule, scope, 'not_run', 'WinRM заявлен выключенным; активные слушатели не проверялись.', [{'pointer':'/winrm/enabled','observed':False}])]
        c.expect('enabled', True)
        for key in ('https_only','certificate_valid','firewall_scoped','delegation_restricted'):
            c.expect(key, True)
        c.expect('basic_auth_enabled', False)
        c.expect('allow_unencrypted', False)
    elif rule == 'HV-04':
        c.expect('topology_reviewed', True)
        # Неполные перечни означают unknown, а не подтвержденное нарушение.
        if data.get('inventory_complete') is not True:
            c.missing.append('полный перечень адаптеров')
        adapters = data.get('adapters')
        if adapters is None:
            c.missing.append('adapters')
        elif not adapters and not c.missing and not c.failures:
            return [finding(rule, scope, 'not_run', 'Полный перечень не содержит сетевых адаптеров.')]
        else:
            for index, adapter in enumerate(adapters):
                part = Checks(adapter, f'/network/adapters/{index}')
                part.compare('switch_type','expected_switch_type',lambda a,b:a==b,'несоответствие типа коммутатора')
                part.compare('vlans','allowed_vlans',lambda a,b:bool(a) and set(a)<=set(b),'VLAN вне утвержденной области или пустой набор VLAN')
                part.compare('trunk','allow_trunk',lambda a,b:not a or b,'неутвержденный транк')
                part.compare('sriov','allow_sriov',lambda a,b:not a or b,'неутвержденный SR-IOV')
                c.evidence.extend(part.evidence); c.failures.extend(part.failures); c.missing.extend(part.missing)
    elif rule == 'HV-07':
        if data.get('inventory_complete') is not True:
            c.missing.append('полный перечень хранилища')
        assets = data.get('assets')
        if assets is None:
            c.missing.append('assets')
        elif not assets and not c.missing:
            return [finding(rule, scope, 'not_run', 'Полный перечень не содержит объектов хранилища.')]
        else:
            for index, asset in enumerate(assets):
                part = Checks(asset, f'/storage/assets/{index}')
                part.expect('effective_acl_reviewed', True)
                part.expect('unapproved_principals', [])
                required = asset.get('require_encryption')
                part.evidence.append({'pointer':part.pointer+'/require_encryption','observed':required})
                if required is None:
                    part.missing.append('require_encryption')
                elif required:
                    part.expect('encrypted', True)
                c.evidence.extend(part.evidence); c.failures.extend(part.failures); c.missing.extend(part.missing)
    elif rule == 'HV-08':
        for key in ('independent_copy','immutable_or_offline','separate_identity'):
            c.expect(key, True)
        c.expect('checkpoint_only', False)
    elif rule == 'HV-09':
        for key in ('audit_enabled','central_delivery_verified','tamper_protection'):
            c.expect(key, True)
        c.compare('retention_days','required_retention_days',lambda a,b:a>=b,'недостаточный срок хранения журналов')
    elif rule == 'HV-10':
        drill = data.get('drill_performed_at')
        c.evidence.append({'pointer':'/recovery/drill_performed_at','observed':drill})
        # Устаревшее или отсутствующее испытание не устанавливает результат готовности.
        if drill is None:
            return [finding(rule, scope, 'unknown', 'Датированные данные учебного восстановления не предоставлены.', c.evidence)]
        age = (as_of - parse_utc(drill)).total_seconds()/86400
        if age < 0 or age > max_restore_age_days:
            return [finding(rule, scope, 'unknown', 'Учебное восстановление вне допустимого срока актуальности.', c.evidence)]
        for key in ('runbook_reviewed','integrity_verified','isolated_restore','reviewer_approved'):
            c.expect(key, True)
        for metric in ('rpo','rto'):
            c.compare(f'measured_{metric}_hours',f'target_{metric}_hours',lambda a,b:a<=b,f'{metric.upper()} превышает цель')
    return [from_checks(rule, scope, c)]

def audit(document, *, as_of=None, max_evidence_age_days=30, max_restore_age_days=90, exclude=()):
    """Проверка и оценка данных с явными датами и границами политики."""
    validate_evidence(document)
    if as_of is None:
        as_of = datetime.now(timezone.utc).replace(microsecond=0)
    elif isinstance(as_of, str):
        as_of = parse_utc(as_of)
    if not isinstance(as_of, datetime) or as_of.tzinfo is None or as_of.utcoffset() is None:
        raise InputError('as_of должен быть датой с часовым поясом или строкой UTC')
    for limit in (max_evidence_age_days,max_restore_age_days):
        if type(limit) is not int or not 1 <= limit <= 3650:
            raise InputError('Лимиты актуальности должны быть целыми числами от 1 до 3650 дней')
    if not set(exclude) <= RULES.keys():
        raise InputError('Неизвестный идентификатор исключенного правила')
    as_of = as_of.astimezone(timezone.utc)
    age = (as_of-parse_utc(document['collected_at'])).total_seconds()/86400
    results = []
    for rule in RULES:
        section = document.get(SECTIONS[rule])
        if rule in exclude:
            results.append(finding(rule, document['scope'], 'not_run', 'Явно исключено оператором.'))
        elif section is None or section['state'] == 'not_collected':
            results.append(finding(rule, document['scope'], 'not_run', 'Данные раздела не собраны.'))
        elif age < 0 or age > max_evidence_age_days:
            results.append(finding(rule, document['scope'], 'unknown', 'Данные вне допустимого срока актуальности.'))
        elif section['state'] == 'error':
            results.append(finding(rule, document['scope'], 'unknown', 'Сбой сбора данных; предоставленные значения не оценивались.'))
        else:
            results.extend(_evaluate(rule,section,document,as_of,max_restore_age_days))
    counts = {status:sum(item['status']==status for item in results) for status in ('pass','fail','unknown','not_run')}
    return {'schema_version':'1.0','tool_version':__version__,'policy_version':POLICY_VERSION,
            'scope':document['scope'],'synthetic':document['synthetic'],'evidence_source':document['evidence_source'],
            'collected_at':document['collected_at'],'as_of':as_of.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'policy':{'max_evidence_age_days':max_evidence_age_days,'max_restore_age_days':max_restore_age_days,'excluded_rules':sorted(set(exclude))},
            'summary':counts,'limitations':LIMITATIONS.copy(),'findings':results}
