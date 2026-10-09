"""Ограниченная загрузка JSON и проверка поддерживаемого набора JSON Schema.

Удаленные ссылки, разрешение форматов и исполняемые входные данные не поддерживаются.
"""
import json
import math
import re
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 16

class InputError(ValueError):
    """Некорректный или недоступный ввод; сообщения не раскрывают его значения."""

def parse_utc(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value):
        raise InputError('Ожидается момент UTC YYYY-MM-DDTHH:MM:SSZ')
    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    except ValueError:
        raise InputError('Некорректная календарная дата UTC') from None

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError('Повторный ключ объекта JSON')
        result[key] = value
    return result

def _constant(_):
    raise InputError('Неограниченное числовое значение JSON')

def _float(text):
    value = float(text)
    if not math.isfinite(value):
        raise InputError('Неограниченное числовое значение JSON')
    return value

def _bounded_tree(value, depth=0):
    if depth > MAX_DEPTH:
        raise InputError('Превышен лимит вложенности входных данных')
    if isinstance(value, dict):
        for item in value.values(): _bounded_tree(item, depth+1)
    elif isinstance(value, list):
        for item in value: _bounded_tree(item, depth+1)

def load_json(path):
    try:
        with Path(path).open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise InputError('Превышен лимит входных данных 2 MiB')
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)
        _bounded_tree(value)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, InputError):
            raise
        raise InputError('Не удалось прочитать корректный JSON в UTF-8') from None
    return value

def schema():
    return json.loads(files('hyperv_opsec_auditor').joinpath('evidence.schema.json').read_text())

def _type(value, name):
    return {
        'object': isinstance(value, dict), 'array': isinstance(value, list),
        'string': isinstance(value, str), 'boolean': type(value) is bool,
        'null': value is None, 'integer': type(value) is int or (type(value) is float and math.isfinite(value) and value.is_integer()),
        'number': type(value) in (int, float),
    }.get(name, False)

def _canonical(value):
    if type(value) is float and value.is_integer(): return int(value)
    if isinstance(value, list): return [_canonical(item) for item in value]
    if isinstance(value, dict): return {key:_canonical(item) for key,item in value.items()}
    return value

def _validate(value, spec, path='$', depth=0):
    if depth > MAX_DEPTH:
        raise InputError('Превышен лимит вложенности входных данных')
    kinds = spec.get('type', [])
    if isinstance(kinds, str):
        kinds = [kinds]
    if kinds and not any(_type(value, kind) for kind in kinds):
        raise InputError(f'{path}: неверный тип')
    if 'const' in spec and (value != spec['const'] or type(value) is not type(spec['const'])):
        raise InputError(f'{path}: неверная константа')
    if 'enum' in spec and not any(value == item and (type(value) is type(item) or (type(value) in (int, float) and type(item) in (int, float))) for item in spec['enum']):
        raise InputError(f'{path}: значение вне перечисления')
    if isinstance(value, dict):
        props = spec.get('properties', {})
        if any(key not in props for key in value) and spec.get('additionalProperties') is False:
            raise InputError(f'{path}: неизвестное поле')
        if any(key not in value for key in spec.get('required', [])):
            raise InputError(f'{path}: отсутствует обязательное поле')
        for key, item in value.items():
            if key in props:
                _validate(item, props[key], f'{path}.{key}', depth + 1)
    elif isinstance(value, list):
        if len(value) > spec.get('maxItems', 1000) or len(value) < spec.get('minItems', 0):
            raise InputError(f'{path}: длина массива вне допустимых границ')
        for index, item in enumerate(value):
            _validate(item, spec.get('items', {}), f'{path}[{index}]', depth + 1)
        if spec.get('uniqueItems'):
            normalized = [json.dumps(_canonical(item), sort_keys=True, allow_nan=False) for item in value]
            if len(set(normalized)) != len(normalized):
                raise InputError(f'{path}: повторный элемент массива')
    elif isinstance(value, str):
        if not spec.get('minLength', 0) <= len(value) <= spec.get('maxLength', 4096):
            raise InputError(f'{path}: длина строки вне допустимых границ')
        if 'pattern' in spec and not re.fullmatch(spec['pattern'], value, flags=re.ASCII):
            raise InputError(f'{path}: строка не соответствует требуемому шаблону')
    elif type(value) in (int, float):
        if (type(value) is float and not math.isfinite(value)) or not spec.get('minimum', -math.inf) <= value <= spec.get('maximum', math.inf):
            raise InputError(f'{path}: число вне допустимых границ')

def validate_evidence(value):
    _validate(value, schema())
    collected = parse_utc(value['collected_at'])
    recovery = value.get('recovery', {})
    drill = recovery.get('drill_performed_at')
    if drill is not None and parse_utc(drill) > collected:
        raise InputError('Дата учебного восстановления позже даты сбора')
    for section, array in [('virtual_machines', 'vms'), ('network', 'adapters'), ('storage', 'assets')]:
        items = value.get(section, {}).get(array, [])
        ids = [item['id'] for item in items]
        if len(ids) != len(set(ids)):
            raise InputError(f'$.{section}: повторный идентификатор объекта')
    return value
