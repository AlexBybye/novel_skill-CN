"""Package behavior: broken references and archives, not prose assertions."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

SPEC = importlib.util.spec_from_file_location(
    'novel_package_check', Path(__file__).resolve().parents[1] / 'scripts/check_package.py')
package_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package_check)


class PackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='novel-package-test-')
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name).resolve()
        self.root = self.parent / 'skill'
        self.write('SKILL.md', '---\nname: sample-skill\nmetadata:\n  version: "2.0.0"\n---\n'
                   '# 入口\n[细则](references/detail.md#适用条件)\n')
        self.write('references/detail.md', '# 详细方法\n## 适用条件\n保留条件。\n')

    def write(self, name, text):
        file = self.root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding='utf-8', newline='\n')

    def test_real_target_and_heading_are_required(self):
        self.assertEqual(package_check.check(self.root)['errors'], [])
        self.write('references/detail.md', '# 新标题\n原锚点已被移走。\n')
        self.assertTrue(any('锚点' in e for e in package_check.check(self.root)['errors']))
        (self.root / 'references/detail.md').unlink()
        self.assertTrue(any('文件不存在' in e for e in package_check.check(self.root)['errors']))

    def test_code_examples_are_not_treated_as_runtime_links(self):
        self.write('references/detail.md', '# 详细方法\n## 适用条件\n'
                   '```markdown\n[代码中的占位](不存在.md)\n```\n')
        self.assertEqual(package_check.check(self.root)['errors'], [])

    def test_archive_keeps_all_sources_and_excludes_private_git_and_cache(self):
        self.write('.git/config', 'PRIVATE_GIT_VALUE')
        self.write('__pycache__/cache.pyc', 'CACHE_ONLY')
        output = self.parent / 'sample.zip'
        package_check.archive(self.root, output, 'sample-skill')
        with ZipFile(output) as package:
            self.assertFalse(any('/.git/' in n or '__pycache__' in n for n in package.namelist()))
            self.assertEqual(package.read('sample-skill/references/detail.md'),
                             (self.root / 'references/detail.md').read_bytes())
        with self.assertRaisesRegex(ValueError, '目录外'):
            package_check.archive(self.root, self.root / 'bad.zip', 'sample-skill')


if __name__ == '__main__':
    unittest.main()
