"""CLI for offline evidence; no credentials or infrastructure connections."""
import argparse
import os
import sys
from pathlib import Path
from . import __version__
from .validation import InputError, load_json, validate_evidence
from .rules import RULES, audit
from .reporting import json_report, markdown_report


def _days(text):
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError('must be an integer from 1 to 3650') from None
    if not 1 <= value <= 3650:
        raise argparse.ArgumentTypeError('must be an integer from 1 to 3650')
    return value


def _write(path, text):
    if path is None:
        sys.stdout.write(text)
        return
    # O_EXCL rejects existing files and symlinks, with private mode on POSIX.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
        stream.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only offline Hyper-V posture evaluator. No host connections or remediation.')
    parser.add_argument('--version', action='version', version=__version__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('rules', help='List implemented rule families')
    validate = commands.add_parser('validate', help='Validate an evidence JSON file')
    validate.add_argument('input', type=Path)
    evaluate = commands.add_parser('audit', help='Evaluate supplied evidence offline')
    evaluate.add_argument('input', type=Path)
    evaluate.add_argument('--format', choices=('json','markdown'), default='markdown')
    evaluate.add_argument('--output', type=Path, help='Create a new report file; existing paths are never overwritten')
    evaluate.add_argument('--as-of', help='UTC timestamp YYYY-MM-DDTHH:MM:SSZ; default current UTC')
    evaluate.add_argument('--max-evidence-age-days', type=_days, default=30)
    evaluate.add_argument('--max-restore-age-days', type=_days, default=90)
    evaluate.add_argument('--exclude', action='append', choices=tuple(RULES), default=[])
    evaluate.add_argument('--fail-on', choices=('none','fail','incomplete'), default='none', help='Exit 1 for fail, or fail/unknown/not_run with incomplete')
    args = parser.parse_args(argv)
    try:
        if args.command == 'rules':
            for key,(title,severity,_) in RULES.items():
                print(f'{key} [{severity}] {title}')
            return 0
        document = validate_evidence(load_json(args.input))
        if args.command == 'validate':
            print('Valid evidence 1.0; structure only, not infrastructure verification.')
            return 0
        report = audit(document, as_of=args.as_of, max_evidence_age_days=args.max_evidence_age_days,
                       max_restore_age_days=args.max_restore_age_days, exclude=args.exclude)
        text = json_report(report) if args.format == 'json' else markdown_report(report)
        _write(args.output, text)
        counts = report['summary']
        failed = counts['fail'] > 0 or (args.fail_on == 'incomplete' and (counts['unknown'] > 0 or counts['not_run'] > 0))
        return int(args.fail_on != 'none' and failed)
    except InputError as error:
        print('Input error: '+str(error), file=sys.stderr)
        return 2
    except OSError:
        print('I/O error: report could not be created; existing paths are never overwritten.', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
