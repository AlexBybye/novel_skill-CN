"""Strategy index and finder tests: structure, anchors, search. No prose assertions."""
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
MANIFEST = json.loads((ROOT / "skill-manifest.json").read_text(encoding="utf-8"))

SPEC = importlib.util.spec_from_file_location("novel_package_check", SCRIPTS / "check_package.py")
package_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package_check)


class StrategyIndexTests(unittest.TestCase):
    def test_manifest_version_matches_skill(self):
        front = (ROOT / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        version = re.search(r'^\s+version:\s*[\'"]?([0-9.]+)', front, re.M).group(1)
        self.assertEqual(MANIFEST["version"], version)

    def test_entrypoints_exist(self):
        for name, relative in MANIFEST["entrypoints"].items():
            with self.subTest(entry=name):
                self.assertTrue((ROOT / relative).is_file(), f"{name}: {relative}")

    def test_ids_unique_and_fields_present(self):
        ids = [item["id"] for item in MANIFEST["strategies"]]
        self.assertEqual(len(ids), len(set(ids)))
        for item in MANIFEST["strategies"]:
            for field in ("id", "name", "one_line", "when", "file"):
                self.assertTrue(item.get(field), f"{item.get('id')}: 缺 {field}")

    def test_files_and_anchors_resolve(self):
        for item in MANIFEST["strategies"]:
            path = ROOT / item["file"]
            with self.subTest(strategy=item["id"]):
                self.assertTrue(path.is_file(), item["file"])
                if item.get("anchor"):
                    anchors = package_check.heading_ids(path.read_text(encoding="utf-8"))
                    self.assertIn(item["anchor"], anchors, f"{item['file']}#{item['anchor']}")

    def test_quickstart_and_index_cover_core_strategies(self):
        quickstart = (ROOT / "START-HERE.md").read_text(encoding="utf-8")
        index = (ROOT / "references/strategy-index.md").read_text(encoding="utf-8")
        for name in ("场景五问", "四道门", "平均用力", "解释性内心", "声音三问", "摘要测试"):
            self.assertIn(name, quickstart)
            self.assertIn(name, index)

    def test_cards_have_multiple_strategies(self):
        cards = (ROOT / "references/strategy-cards.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## (.+)$", cards, re.M)
        self.assertGreaterEqual(len(headings), 10)
        self.assertIn("场景五问", headings)
        self.assertIn("四道门", headings)


class FindStrategyTests(unittest.TestCase):
    def run_finder(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "find_strategy.py"), *args],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
        )

    def test_check_passes(self):
        result = self.run_finder("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)

    def test_search_voice(self):
        result = self.run_finder("声音", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        items = json.loads(result.stdout)
        self.assertTrue(items)
        self.assertEqual(items[0]["id"], "voice-three")
        self.assertEqual(items[0]["file"], "references/chapter-shape.md")

    def test_search_scene(self):
        result = self.run_finder("场景", "--limit", "3", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        items = json.loads(result.stdout)
        self.assertTrue(items)
        self.assertTrue(any(item["id"].startswith("scene-") for item in items))

    def test_list_all(self):
        result = self.run_finder("--list", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        items = json.loads(result.stdout)
        self.assertEqual(len(items), len(MANIFEST["strategies"]))


if __name__ == "__main__":
    unittest.main()
