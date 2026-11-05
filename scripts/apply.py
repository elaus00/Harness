#!/usr/bin/env python3
"""Copy selected Harness files to a separate project without overwriting files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path('.agents/skills/clear-with-lessons')
PROTECTED = {'readme.md', 'ai_collaboration.md'}


def path_conflict(dst, target, directory=False):
    """Reject symlinks, file/directory collisions and ambiguous case spellings."""
    current = target
    parts = dst.relative_to(target).parts
    for i, part in enumerate(parts):
        if current.is_dir():
            if any(p.name != part and p.name.casefold() == part.casefold()
                   for p in current.iterdir()):
                return True
        current = current / part
        if current.is_symlink():
            return True
        if current.exists():
            need_dir = i < len(parts) - 1 or directory
            if need_dir != current.is_dir():
                return True
    return False


def verified_files(folder, entries):
    files = []
    for entry in entries:
        rel = Path(entry['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('배포 기록에 잘못된 상대 경로가 있습니다.')
        src = folder / rel
        if any(p.is_symlink() for p in [src, *src.parents] if p != ROOT.parent):
            raise ValueError(f'원본 심링크를 복사하지 않습니다: {rel}')
        if hashlib.sha256(src.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'원본 해시 불일치: {src.relative_to(ROOT)}')
        files.append((src, rel))
    return files


def plan(target, skills_only=False, profile='project'):
    if target.is_symlink():
        raise ValueError('대상 폴더는 심링크일 수 없습니다.')
    target = target.resolve()
    if not target.is_dir():
        raise ValueError('대상 프로젝트 폴더가 존재해야 합니다.')
    if target == ROOT or ROOT in target.parents:
        raise ValueError('Harness 원본 또는 그 하위에는 적용할 수 없습니다.')
    if any(ord(c) < 32 for c in target.name):
        raise ValueError('프로젝트 이름에 제어 문자를 사용할 수 없습니다.')
    sources, actions, skipped_skills = [], [], []
    strict = profile in {'exam', 'docs'}
    if not skills_only:
        if strict:
            folder = ROOT / 'templates/exam'
            manifest = json.loads((ROOT / 'exam-files.json').read_text())
            for src, rel in verified_files(folder, manifest['files']):
                if rel.name.casefold() in PROTECTED:
                    raise ValueError('응시 원문은 배포할 수 없습니다.')
                if profile == 'docs' and not (
                    rel.parts[0] in {'docs', 'prompts'}
                    or rel.as_posix() in {'AGENTS.md', 'HOW_TO_RUN.md'}
                ):
                    continue
                sources.append((src, rel))
        else:
            folder = ROOT / 'templates/project'
            sources = [(p, p.relative_to(folder))
                       for p in sorted(folder.rglob('*')) if p.is_file()]
    bundle = json.loads((ROOT / 'skills-bundle.lock.json').read_text())
    for skill in bundle['skills']:
        rel = Path(skill['location'])
        if rel != Path('.agents/skills') / skill['name']:
            raise ValueError('스킬 배포 경로가 올바르지 않습니다.')
        files = verified_files(ROOT / rel, skill['files'])
        if path_conflict(target / rel, target, directory=True):
            actions.append(('CONFLICT', target / rel, b''))
        elif os.path.lexists(target / rel):
            skipped_skills.append(rel)
        else:
            sources.extend((src, rel / child) for src, child in files)
    for src, rel in sources:
        if rel.name.casefold() in PROTECTED:
            raise ValueError('응시 원문은 배포할 수 없습니다.')
        dst = target / rel
        data = src.read_bytes()
        if profile == 'project' and rel.suffix == '.md' and rel.parts[0] != '.agents':
            data = data.decode().replace('{{PROJECT_NAME}}', target.name).encode()
        state = 'ADD'
        if path_conflict(dst, target):
            state = 'CONFLICT'
        elif dst.exists():
            state = 'CONFLICT' if strict and dst.read_bytes() != data else 'SKIP'
        actions.append((state, dst, data))
    return target, actions, skipped_skills


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path)
    parser.add_argument('--apply', action='store_true', help='신규 파일 생성 (기본은 미리보기)')
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument('--skills-only', action='store_true', help='동봉 스킬만 설치')
    choice.add_argument('--profile', choices=['project', 'docs', 'exam'], default='project',
                        help='기존 개인 템플릿 / 시험 문서 / 시험 문서와 선택적 앱')
    args = parser.parse_args(argv)
    try:
        target, actions, skipped = plan(args.target, args.skills_only, args.profile)
        for state, path, _ in actions:
            print(f'{state}: {path.relative_to(target)}')
        for skill in skipped:
            print(f'SKIP: {skill} (기존 스킬 전체 보존)')
        if any(state == 'CONFLICT' for state, _, _ in actions):
            print('경로·내용 충돌을 해결한 후 다시 실행하세요. 파일을 생성하지 않았습니다.',
                  file=sys.stderr)
            return 1
        if args.apply:
            for state, path, data in actions:
                if state != 'ADD':
                    continue
                if path_conflict(path, target):
                    raise ValueError(f'적용 중 경로가 변경됐습니다: {path}')
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(data)
            print('신규 파일 적용 완료.')
        else:
            print('미리보기입니다. 적용하려면 --apply를 추가하세요.')
        if any(state == 'SKIP' and path.name == 'AGENTS.md' for state, path, _ in actions):
            print('기존 AGENTS.md에 필요한 규칙과 스킬 참조를 검토 후 병합하세요.')
        print('원문·기존 스킬·전역 설정을 보존합니다. Docker는 적용 대상이 아닙니다.')
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f'적용 실패: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
