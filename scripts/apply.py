#!/usr/bin/env python3
"""Preview or add Harness templates without replacing existing project files."""
import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path('.agents/skills/clear-with-lessons')


def plan(target):
    if target.is_symlink():
        raise ValueError('대상 폴더는 심링크일 수 없습니다.')
    target = target.resolve()
    if not target.is_dir():
        raise ValueError('대상 프로젝트 폴더가 존재해야 합니다.')
    if target == ROOT or ROOT in target.parents:
        raise ValueError('Harness 원본 또는 그 하위에는 적용할 수 없습니다.')
    if any(ord(c) < 32 for c in target.name):
        raise ValueError('프로젝트 이름에 제어 문자를 사용할 수 없습니다.')
    sources = [(p, p.relative_to(ROOT / 'templates/project'))
               for p in sorted((ROOT / 'templates/project').rglob('*')) if p.is_file()]
    skill_exists = os.path.lexists(target / SKILL)
    if not skill_exists:
        sources += [(p, SKILL / p.relative_to(ROOT / SKILL))
                    for p in sorted((ROOT / SKILL).rglob('*')) if p.is_file()]
    actions = []
    for src, rel in sources:
        dst = target / rel
        state = 'ADD'
        for parent in [dst, *dst.parents]:
            if parent == target:
                break
            if parent.is_symlink():
                state = 'CONFLICT'
                break
            if parent.exists() and ((parent == dst and parent.is_dir()) or
                                    (parent != dst and not parent.is_dir())):
                state = 'CONFLICT'
                break
        if state == 'ADD' and dst.exists():
            state = 'SKIP'
        data = src.read_bytes()
        if rel.suffix == '.md' and not str(rel).startswith('.agents/'):
            data = data.decode().replace('{{PROJECT_NAME}}', target.name).encode()
        actions.append((state, dst, data))
    return target, actions, skill_exists


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path)
    parser.add_argument('--apply', action='store_true', help='신규 파일 생성 (기본은 미리보기)')
    args = parser.parse_args(argv)
    try:
        target, actions, skill_exists = plan(args.target)
        for state, path, _ in actions:
            print(f'{state}: {path.relative_to(target)}')
        if skill_exists:
            print(f'SKIP: {SKILL} (기존 스킬 전체 보존)')
        if any(state == 'CONFLICT' for state, _, _ in actions):
            print('경로 충돌을 해결한 후 다시 실행하세요. 파일을 생성하지 않았습니다.', file=sys.stderr)
            return 1
        if args.apply:
            for state, path, data in actions:
                if state != 'ADD':
                    continue
                # Recheck before each creation; never follow an existing symlink.
                for parent in path.parents:
                    if parent == target:
                        break
                    if parent.is_symlink():
                        raise ValueError(f'경로가 변경됐습니다: {parent}')
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(data)
            print('신규 파일 적용 완료.')
        else:
            print('미리보기입니다. 적용하려면 --apply를 추가하세요.')
        if any(state == 'SKIP' and path.name == 'AGENTS.md' for state, path, _ in actions):
            print('기존 AGENTS.md에 docs/index.md와 회고 스킬 참조를 검토 후 병합하세요.')
        if any(state == 'SKIP' and path.name == 'index.md' for state, path, _ in actions):
            print('기존 docs/index.md에 신규 문서 링크를 검토 후 병합하세요.')
        print('기존 파일은 수정하지 않습니다. 전역 스킬과 MCP 설정은 포함하지 않습니다.')
        return 0
    except (OSError, ValueError) as exc:
        print(f'적용 실패: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
