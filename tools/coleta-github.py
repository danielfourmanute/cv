#!/usr/bin/env python3
"""
coleta-github.py — gera os numeros deste curriculo a partir da conta GitHub.

Uso:
    python3 tools/coleta-github.py                # escreve dados/github-stats.json
    python3 tools/coleta-github.py --owner outro  # outra conta

Requisitos: gh autenticado (gh auth status) e jq. Forks sao excluidos de todas
as contagens: eles inflariam commits, volume de codigo e numero de projetos.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date

QUERY = """
query($owner:String!,$cursor:String){
  repositoryOwner(login:$owner){
    repositories(first:100, after:$cursor, ownerAffiliations:OWNER){
      pageInfo{ hasNextPage endCursor }
      nodes{
        name isPrivate isFork createdAt pushedAt diskUsage url description
        primaryLanguage{ name }
        languages(first:10){ edges{ node{ name } size } }
        defaultBranchRef{ target{ ... on Commit { history { totalCount } } } }
      }
    }
  }
}
"""


def run(cmd: list[str], stdin: str | None = None) -> str:
    env = {'NO_COLOR': '1', 'GH_PAGER': 'cat', 'PATH': __import__('os').environ['PATH'],
           'HOME': __import__('os').environ['HOME'], 'GH_TOKEN': __import__('os').environ.get('GH_TOKEN', ''),
           'SystemPrompt': ''}
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        sys.exit(f"falha em {' '.join(cmd)}: {p.stderr.strip()[:400]}")
    return re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', p.stdout)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--owner', default='danielfourmanute')
    ap.add_argument('--out', default='dados/github-stats.json')
    args = ap.parse_args()

    cursor, nodes = '', []
    while True:
        raw = run(['gh', 'api', 'graphql', '-f', f'owner={args.owner}',
                   '-f', f'cursor={cursor}', '-f', f'query={QUERY}'])
        block = json.loads(raw)['data']['repositoryOwner']['repositories']
        nodes += block['nodes']
        page = block['pageInfo']
        if not page['hasNextPage']:
            break
        cursor = page['endCursor']

    own = [n for n in nodes if not n.get('isFork')]
    repos, langbytes = [], defaultdict(int)
    for n in own:
        hist = ((n.get('defaultBranchRef') or {}).get('target') or {}).get('history') or {}
        langs = {e['node']['name']: e['size'] for e in ((n.get('languages') or {}).get('edges') or [])}
        for k, v in langs.items():
            langbytes[k] += v
        repos.append({
            'name': n['name'],
            'private': n['isPrivate'],
            'primaryLanguage': (n.get('primaryLanguage') or {}).get('name'),
            'commits': hist.get('totalCount', 0),
            'diskMb': round((n.get('diskUsage') or 0) / 1024, 2),
            'createdAt': (n.get('createdAt') or '')[:10],
            'pushedAt': (n.get('pushedAt') or '')[:10],
        })

    repos.sort(key=lambda r: -r['commits'])
    totbytes = sum(langbytes.values()) or 1
    out = {
        'owner': args.owner,
        'geradoEm': str(date.today()),
        'metodo': ('GraphQL repositoryOwner(login).repositories(ownerAffiliations:OWNER); '
                   'forks excluidos; commits do branch padrao; volume por linguagem em bytes '
                   'atribuidos pelo GitHub Linguist.'),
        'resumo': {
            'repositoriosProprios': len(repos),
            'publicos': sum(1 for r in repos if not r['private']),
            'privados': sum(1 for r in repos if r['private']),
            'commits': sum(r['commits'] for r in repos),
            'volumeMb': round(sum(r['diskMb'] for r in repos), 1),
            'forksExcluidos': [n['name'] for n in nodes if n.get('isFork')],
        },
        'porLinguagemMb': {k: round(v / 1e6, 2) for k, v in
                           sorted(langbytes.items(), key=lambda kv: -kv[1])},
        'porLinguagemPct': {k: round(100 * v / totbytes, 1) for k, v in
                            sorted(langbytes.items(), key=lambda kv: -kv[1])},
        'repos': repos,
    }
    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    r = out['resumo']
    print(f"{r['repositoriosProprios']} repos | {r['commits']} commits | "
          f"{r['volumeMb']} MB -> {args.out}")


if __name__ == '__main__':
    main()
