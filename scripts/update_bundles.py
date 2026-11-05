#!/usr/bin/env python3
"""Refresh local bundle hashes after reviewing source changes."""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.venv', '__pycache__', '.pytest_cache', '.ruff_cache', '.git', 'data'}


def inventory(folder):
    result = []
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(part in IGNORED for part in rel.parts) or not path.is_file():
            continue
        if path.name == '.env' or path.name.endswith(('.sqlite3', '.pyc')):
            continue
        if path.is_symlink():
            raise ValueError(f'Symlink in source: {path}')
        data = path.read_bytes()
        result.append({'path': rel.as_posix(), 'sha256': hashlib.sha256(data).hexdigest(),
                       'bytes': len(data)})
    return result


def update(checked_at):
    path = ROOT / 'skills-bundle.lock.json'
    previous = {s['name']: s for s in json.loads(path.read_text())['skills']}
    skills = []
    for folder in sorted((ROOT / '.agents/skills').iterdir()):
        if not (folder / 'SKILL.md').is_file():
            continue
        entry = previous.get(folder.name, {
            'name': folder.name, 'source': 'Harness project-local skill',
            'upstream_commit': None, 'upstream_version': None,
        })
        entry['location'] = folder.relative_to(ROOT).as_posix()
        entry['files'] = inventory(folder)
        skills.append(entry)
    path.write_text(json.dumps({'schema_version': 1, 'kind': 'vendored-project-skills',
                                'checked_at': checked_at, 'skills': skills},
                               ensure_ascii=False, indent=2) + '\n')
    files = inventory(ROOT / 'templates/exam')
    forbidden = [f['path'] for f in files if (
        Path(f['path']).name.lower() in {'readme.md', 'ai_collaboration.md',
                                       'compose.yaml', 'docker-compose.yml'}
        or Path(f['path']).name.lower().startswith('dockerfile')
    )]
    if forbidden:
        raise ValueError(f'Protected files in exam bundle: {forbidden}')
    (ROOT / 'exam-files.json').write_text(json.dumps({
        'schema_version': 1, 'kind': 'exam-extraction-files',
        'checked_at': checked_at, 'files': files,
    }, ensure_ascii=False, indent=2) + '\n')
    print(f'{len(skills)} skills, {len(files)} exam files recorded.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True, type=date.fromisoformat)
    args = parser.parse_args()
    update(args.date.isoformat())
