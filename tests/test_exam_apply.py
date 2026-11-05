import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'exam_apply', Path(__file__).resolve().parents[1] / 'scripts/apply.py')
apply = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apply)


class ExamApplyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name).resolve() / 'exam project'
        self.target.mkdir()
        self.original = {'README.md': b'official\r\n',
                         'AI_COLLABORATION.md': b'official form\n'}
        for name, data in self.original.items():
            (self.target / name).write_bytes(data)

    def test_extract_repeat_and_protected_documents(self):
        args = [str(self.target), '--profile', 'exam', '--apply']
        self.assertEqual(apply.main(args), 0)
        self.assertEqual(apply.main(args), 0)
        for name, data in self.original.items():
            self.assertEqual((self.target / name).read_bytes(), data)
        for path in ['AGENTS.md', 'docs/DECISION.md', 'docs/INDEX.md',
                     'engine/__init__.py', 'validator/__init__.py',
                     'app/frontend/app.js', 'datasets/original/.gitkeep', 'uv.lock']:
            self.assertTrue((self.target / path).is_file(), path)
        self.assertFalse(list(self.target.rglob('Dockerfile*')))
        self.assertFalse(list(self.target.rglob('compose.yaml')))
        self.assertFalse((self.target / '.env').exists())
        self.assertFalse((self.target / '.venv').exists())
        self.assertEqual(list(self.target.rglob('README.md')), [self.target / 'README.md'])

    def test_docs_profile_and_preview_have_no_app(self):
        self.assertEqual(apply.main([str(self.target), '--profile', 'docs']), 0)
        self.assertEqual(set(p.name for p in self.target.iterdir()), set(self.original))
        self.assertEqual(apply.main([str(self.target), '--profile', 'docs', '--apply']), 0)
        self.assertTrue((self.target / 'docs/PRD.md').is_file())
        self.assertTrue((self.target / '.agents/skills/exam-resume/SKILL.md').is_file())
        self.assertFalse((self.target / 'app').exists())
        self.assertFalse((self.target / 'pyproject.toml').exists())

    def test_content_conflict_prevents_all_additions(self):
        (self.target / 'AGENTS.md').write_text('original rules')
        self.assertEqual(apply.main([str(self.target), '--profile', 'exam', '--apply']), 1)
        self.assertEqual((self.target / 'AGENTS.md').read_text(), 'original rules')
        self.assertFalse((self.target / 'app').exists())
        self.assertFalse((self.target / '.agents').exists())

    def test_case_conflict_prevents_all_additions(self):
        (self.target / 'docs').mkdir()
        (self.target / 'docs/index.md').write_text('existing lowercase index')
        self.assertEqual(apply.main([str(self.target), '--profile', 'exam', '--apply']), 1)
        self.assertFalse((self.target / 'AGENTS.md').exists())
        self.assertFalse((self.target / '.agents').exists())

    def test_invalid_source_hash_fails_before_target_changes(self):
        source = Path(self.tmp.name).resolve() / 'fake-source'
        payload = source / 'templates/exam'
        payload.mkdir(parents=True)
        (payload / 'AGENTS.md').write_text('modified source')
        (source / 'exam-files.json').write_text(json.dumps({'files': [{
            'path': 'AGENTS.md', 'sha256': hashlib.sha256(b'original').hexdigest(),
        }]}))
        with patch.object(apply, 'ROOT', source):
            self.assertEqual(apply.main([str(self.target), '--profile', 'exam', '--apply']), 1)
        self.assertEqual(set(p.name for p in self.target.iterdir()), set(self.original))


if __name__ == '__main__':
    unittest.main()
