"""Сериализация отчета с экранированием текста для Markdown."""
import html
import json

def json_report(report):
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+'\n'

def _escape(value):
    text = html.escape(str(value), quote=True)
    for character in ('\\','`','*','_','[',']','|','#'):
        text = text.replace(character, '\\'+character)
    return text.replace('\n', ' ').replace('\r', ' ')

def markdown_report(report):
    lines = ['# Автономный отчет о защите Hyper-V', '',
             f"Область: {_escape(report['scope'])}",
             f"Данные: {_escape(report['collected_at'])}; момент оценки: {_escape(report['as_of'])}",
             f"Инструмент: {_escape(report['tool_version'])}; политика: {_escape(report['policy_version'])}", '',
             '**СИНТЕТИЧЕСКИЕ ДАННЫЕ — реальная инфраструктура не проверялась.**' if report['synthetic'] else '**Предоставленные данные — независимой проверки инфраструктуры не было.**', '',
             ' | '.join(f'{key}: {value}' for key,value in report['summary'].items()), '',
             '## Ограничения', '']
    lines.extend('- '+_escape(value) for value in report['limitations'])
    for item in report['findings']:
        lines.extend(['',f"## {_escape(item['rule_id'])} / {_escape(item['asset'])}: {_escape(item['status'])}",'',
                      f"{_escape(item['title'])} — критичность: {_escape(item['severity'])}",'',_escape(item['rationale']),'',
                      'Данные:', ''])
        if item['evidence']:
            for evidence in item['evidence']:
                observed = json.dumps(evidence.get('observed'),ensure_ascii=False,sort_keys=True)
                line = f"- {_escape(evidence['pointer'])}: {_escape(observed)}"
                if 'expected' in evidence:
                    line += '; ожидается: '+_escape(json.dumps(evidence['expected'],ensure_ascii=False,sort_keys=True))
                lines.append(line)
        else:
            lines.append('- Оцененные данные отсутствуют.')
        lines.extend(['', 'Рекомендация (только для ручной проверки): '+_escape(item['remediation'])])
    return '\n'.join(lines)+'\n'
