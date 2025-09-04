#!/usr/bin/env python3

from pathlib import Path
import yaml
import sys


def main():
    script_dir = Path(__file__).parent
    inp = script_dir / 'cn-site-classical.yaml'
    outp = script_dir / 'cn-site.yaml'

    data = yaml.safe_load(inp.read_text(encoding='utf-8')) or {}
    # assume payload always exists
    payload = data['payload']

    # fail fast if forbidden rule types are present
    for item in payload:
        if isinstance(item, str):
            if item.startswith('DOMAIN-KEYWORD,') or item.startswith('DOMAIN-REGEX,') or item.startswith('PROCESS-NAME,'):
                print(f'Unsupported rule type present in payload: {item.split(",",1)[0]}', file=sys.stderr)
                sys.exit(1)

    new_payload = []
    for item in payload:
        if isinstance(item, str):
            if item.startswith('DOMAIN-SUFFIX,'):
                rest = item.split(',', 1)[1].strip()
                if rest:
                    new_payload.append('+.{}'.format(rest.lstrip('.')))
                    continue
            if item.startswith('DOMAIN,'):
                rest = item.split(',', 1)[1].strip()
                if rest:
                    new_payload.append(rest)
                    continue
        new_payload.append(item)

    data['payload'] = new_payload
    outp.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'Wrote: {outp}')


if __name__ == '__main__':
    main()