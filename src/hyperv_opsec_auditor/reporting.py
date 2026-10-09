"""Report serialization; input text is escaped before Markdown rendering."""
import html
import json

def json_report(report):
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)+'\n'

def _escape(value):
    text = html.escape(str(value), quote=True)
    for character in ('\\','`','*','_','[',']','|','#'):
        text = text.replace(character, '\\'+character)
    return text.replace('\n', ' ').replace('\r', ' ')

def markdown_report(report):
    lines = ['# Hyper-V offline posture report', '',
             f"Scope: {_escape(report['scope'])}",
             f"Evidence: {_escape(report['collected_at'])}; as of: {_escape(report['as_of'])}",
             f"Tool: {_escape(report['tool_version'])}; policy: {_escape(report['policy_version'])}", '',
             '**SYNTHETIC EVIDENCE — no real infrastructure validation.**' if report['synthetic'] else '**Supplied evidence — not independently verified against infrastructure.**', '',
             ' | '.join(f'{key}: {value}' for key,value in report['summary'].items()), '',
             '## Limitations', '']
    lines.extend('- '+_escape(value) for value in report['limitations'])
    for item in report['findings']:
        lines.extend(['',f"## {_escape(item['rule_id'])} / {_escape(item['asset'])}: {_escape(item['status'])}",'',
                      f"{_escape(item['title'])} — severity: {_escape(item['severity'])}",'',_escape(item['rationale']),'',
                      'Evidence:', ''])
        if item['evidence']:
            for evidence in item['evidence']:
                observed = json.dumps(evidence.get('observed'),ensure_ascii=True,sort_keys=True)
                line = f"- {_escape(evidence['pointer'])}: {_escape(observed)}"
                if 'expected' in evidence:
                    line += '; expected: '+_escape(json.dumps(evidence['expected'],ensure_ascii=True,sort_keys=True))
                lines.append(line)
        else:
            lines.append('- No evaluated evidence.')
        lines.extend(['', 'Recommendation (manual review only): '+_escape(item['remediation'])])
    return '\n'.join(lines)+'\n'
