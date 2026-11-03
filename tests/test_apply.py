import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('apply', Path(__file__).resolve().parents[1] / 'scripts/apply.py')
apply = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apply)


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / '한글 project'
        self.target.mkdir()

    def test_preview_has_no_writes(self):
        self.assertEqual(apply.main([str(self.target)]), 0)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_apply_and_repeat_preserve_user_content(self):
        self.assertEqual(apply.main([str(self.target), '--apply']), 0)
        agents = self.target / 'AGENTS.md'
        self.assertIn('한글 project', agents.read_text())
        agents.write_text('사용자 규칙')
        skill = self.target / apply.SKILL / 'SKILL.md'
        skill.write_text('사용자 스킬')
        self.assertEqual(apply.main([str(self.target), '--apply']), 0)
        self.assertEqual(agents.read_text(), '사용자 규칙')
        self.assertEqual(skill.read_text(), '사용자 스킬')

    def test_existing_skill_is_not_mixed(self):
        skill = self.target / apply.SKILL
        skill.mkdir(parents=True)
        (skill / 'custom.txt').write_text('keep')
        self.assertEqual(apply.main([str(self.target), '--apply']), 0)
        self.assertEqual([p.name for p in skill.iterdir()], ['custom.txt'])

    def test_symlink_parent_prevents_all_writes(self):
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        (self.target / 'docs').symlink_to(outside, target_is_directory=True)
        self.assertEqual(apply.main([str(self.target), '--apply']), 1)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.target / 'AGENTS.md').exists())

    def test_file_directory_collision(self):
        (self.target / 'docs').write_text('keep')
        self.assertEqual(apply.main([str(self.target), '--apply']), 1)
        self.assertFalse((self.target / 'AGENTS.md').exists())

    def test_invalid_targets(self):
        self.assertEqual(apply.main([str(self.target / 'missing'), '--apply']), 1)
        self.assertEqual(apply.main([str(apply.ROOT), '--apply']), 1)


if __name__ == '__main__':
    unittest.main()
