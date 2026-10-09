"""Conservative public-file credential pattern scan; not a complete secret audit."""
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATTERNS=(
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    r'gh[pousr]_[A-Za-z0-9]{30,}',
    r'github_pat_[A-Za-z0-9_]{30,}',
    r'AKIA[0-9A-Z]{16}',
    r'(?i)["\x27]?(?:password|client_secret|api_key|access_token)["\x27]?\s*[:=]\s*["\x27][^"\x27\s]{8,}["\x27]',
)

def main():
    completed=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,capture_output=True,check=True)
    paths=sorted(set(completed.stdout.decode().split('\0'))- {''})
    suspicious=[]
    for name in paths:
        path=ROOT/name
        if not path.is_file(): continue
        try: text=path.read_text(encoding='utf-8')
        except UnicodeError: continue
        if any(re.search(pattern,text) for pattern in PATTERNS): suspicious.append(name)
    if suspicious:
        # Never print matched values.
        raise SystemExit('Credential patterns detected in files: '+', '.join(suspicious))
    print(f'PASS: {len(paths)} public files scanned; no credential-pattern matches. Not a comprehensive secret audit.')

if __name__=='__main__': main()
