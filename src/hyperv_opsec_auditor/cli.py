"""CLI для автономной оценки данных без учетных данных и подключений."""
import argparse
import os
import sys
from pathlib import Path
from . import __version__
from .validation import InputError, load_json, validate_evidence
from .rules import RULES, audit
from .reporting import json_report, markdown_report


class RussianFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, prefix='Использование: ')

class RussianParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('formatter_class', RussianFormatter)
        super().__init__(*args, **kwargs)
        self._positionals.title = 'Аргументы'
        self._optionals.title = 'Параметры'
        for action in self._actions:
            if isinstance(action, argparse._HelpAction):
                action.help = 'Показать справку и завершить работу'

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f'{self.prog}: ошибка: недопустимые аргументы; см. --help.\n')


def _days(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError('требуется целое число от 1 до 3650') from None
    if not 1 <= value <= 3650:
        raise argparse.ArgumentTypeError('требуется целое число от 1 до 3650')
    return value


def _write(path, text):
    if path is None:
        sys.stdout.write(text)
        return
    # O_EXCL отклоняет существующие файлы и ссылки; на POSIX права приватные.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
        stream.write(text)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = RussianParser(description='Автономный аудитор Hyper-V только для чтения. Без подключения к хостам и исправления настроек.')
    parser.add_argument('--version', action='version', version=__version__, help='Показать версию и завершить работу')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('rules', help='Показать реализованные семейства правил')
    validate = commands.add_parser('validate', help='Проверить структуру файла данных JSON')
    validate.add_argument('input', type=Path)
    evaluate = commands.add_parser('audit', help='Автономно оценить предоставленные данные')
    evaluate.add_argument('input', type=Path)
    evaluate.add_argument('--format', choices=('json','markdown'), default='markdown')
    evaluate.add_argument('--output', type=Path, help='Создать новый файл отчета; существующие пути не перезаписываются')
    evaluate.add_argument('--as-of', help='Момент UTC YYYY-MM-DDTHH:MM:SSZ; по умолчанию текущий UTC')
    evaluate.add_argument('--max-evidence-age-days', type=_days, default=30)
    evaluate.add_argument('--max-restore-age-days', type=_days, default=90)
    evaluate.add_argument('--exclude', action='append', choices=tuple(RULES), default=[])
    evaluate.add_argument('--fail-on', choices=('none','fail','incomplete'), default='none', help='Код 1 при fail; режим incomplete также учитывает unknown/not_run')
    args = parser.parse_args(argv)
    try:
        if args.command == 'rules':
            for key,(title,severity,_) in RULES.items():
                print(f'{key} [{severity}] {title}')
            return 0
        document = validate_evidence(load_json(args.input))
        if args.command == 'validate':
            print('Данные 1.0 корректны по структуре; это не проверка инфраструктуры.')
            return 0
        report = audit(document, as_of=args.as_of, max_evidence_age_days=args.max_evidence_age_days,
                       max_restore_age_days=args.max_restore_age_days, exclude=args.exclude)
        text = json_report(report) if args.format == 'json' else markdown_report(report)
        _write(args.output, text)
        counts = report['summary']
        failed = counts['fail'] > 0 or (args.fail_on == 'incomplete' and (counts['unknown'] > 0 or counts['not_run'] > 0))
        return int(args.fail_on != 'none' and failed)
    except InputError as error:
        print('Ошибка входных данных: '+str(error), file=sys.stderr)
        return 2
    except OSError:
        print('Ошибка ввода-вывода: отчет не создан; существующие пути не перезаписываются.', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
