"""Behavior checks for retrieval; synthetic fixtures, not novel plot additions."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/context.py'
spec = importlib.util.spec_from_file_location('novel_context', SCRIPT)
context = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = context
spec.loader.exec_module(context)


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='novel-context-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = {'version': 1, 'title': '测试', 'handoff': 'handoff.md',
                       'catalog_roots': ['cards'], 'style': 'style.md'}
        self.write('novel-workspace.json', json.dumps(self.config))
        self.write('handoff.md', '# 工作面\n只作检索测试，不生成小说。')
        self.write('style.md', '# 风格待校准')

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def record(self, name, text, **meta):
        self.write(name, '<!-- novel-meta: ' + json.dumps(meta, ensure_ascii=False) + ' -->\n' + text)

    def build(self, **kwargs):
        return context.build_packet(self.root, self.config, **kwargs)

    def test_rich_topic_is_kept_with_motivation_and_exception(self):
        self.record('cards/P001.md', '# 人物\n\n## 选择与边界\n要保护同伴。\n'
                    '### 例外\n如果救援会伤害无关者，先寻找替代方案。\n'
                    '## 另一主题\n这里只是其他档案。', id='P001', kind='character', status='plan')
        packet = self.build(mode='character', select=['cards/P001.md#选择与边界'], budget=1800)
        self.assertIn('要保护同伴', packet)
        self.assertIn('先寻找替代方案', packet)
        self.assertNotIn('这里只是其他档案', packet)

    def test_limit_applies_to_complete_packet_including_manifest(self):
        for i in range(20):
            self.record(f'cards/E{i:03}.md', '# 事件\n调查证据。' + '有因有果。' * 50,
                        id=f'E{i:03}', status='plan', kind='event')
        packet = self.build(query='调查 证据', budget=2200)
        self.assertLessEqual(len(packet), 2200)
        self.assertIn('预算未纳入', packet)
        self.assertIn('待按需回查', packet)

    def test_required_cluster_is_never_silently_cut(self):
        self.record('cards/P001.md', '# 人物\n' + '必要限制。' * 1000,
                    id='P001', kind='character', status='plan')
        with self.assertRaisesRegex(context.ContextError, '未截断'):
            self.build(ids=['P001'], budget=1800)

    def test_later_chapter_and_candidate_are_not_current_facts(self):
        self.record('cards/history.md', '# 状态档案\n\n## 当前\n'
                    '<!-- novel-meta: {"id":"P001-S002","kind":"state","status":"accepted","chapter":2} -->\n'
                    '调查尚未完成。\n## 未来\n'
                    '<!-- novel-meta: {"id":"P001-S009","kind":"state","status":"accepted","chapter":9} -->\n'
                    'FUTURE_ONLY_秘密已揭晓。')
        self.record('cards/candidate.md', '# 候选\n调查CANDIDATE_ONLY',
                    kind='event', status='candidate', chapter=1)
        packet = self.build(mode='review', query='调查', at_chapter=3)
        self.assertIn('调查尚未完成', packet)
        self.assertNotIn('FUTURE_ONLY', packet)
        self.assertNotIn('CANDIDATE_ONLY', packet)

    def test_explicit_file_cannot_bypass_future_filter(self):
        self.record('cards/future.md', '# 尚未发生\n秘密', kind='state', status='accepted', chapter=8)
        with self.assertRaisesRegex(context.ContextError, '不兼容'):
            self.build(mode='review', at_chapter=2, include=['cards/future.md'])

    def test_discussion_does_not_require_or_invent_approval(self):
        self.assertIn('作者讨论', self.build(mode='discuss'))
        with self.assertRaisesRegex(context.ContextError, '授权'):
            self.build(mode='draft', at_chapter=1)
        self.record('cards/brief.md', '# 场景约定\n批准已有情节。',
                    kind='brief', status='approved', chapter=1)
        self.assertIn('批准已有情节', self.build(mode='draft', at_chapter=1, brief='cards/brief.md'))
        with self.assertRaisesRegex(context.ContextError, '章节'):
            self.build(mode='draft', at_chapter=2, brief='cards/brief.md')

    def test_unknown_ids_and_headings_are_reported(self):
        with self.assertRaisesRegex(context.ContextError, '目标 ID'):
            self.build(ids=['P999'])
        with self.assertRaisesRegex(context.ContextError, '标题不存在'):
            self.build(select=['style.md#没有这个标题'])

    def test_source_changes_are_read_without_trusting_old_cache(self):
        self.record('cards/P001.md', '# 人物\n旧描述', id='P001', kind='character', status='plan')
        before = self.build(ids=['P001'])
        self.write('.novel-cache/index.json', '{"stale":true}')
        self.record('cards/P001.md', '# 人物\n新描述', id='P001', kind='character', status='plan')
        after = self.build(ids=['P001'])
        self.assertIn('新描述', after)
        self.assertNotIn('旧描述', after)
        self.assertNotEqual(before, after)

    def test_archive_is_not_accidentally_loaded(self):
        self.write('00_来源/old.md', '# 旧来源\nARCHIVE_ONLY 调查')
        self.assertNotIn('ARCHIVE_ONLY', self.build(query='调查'))
        self.assertIn('ARCHIVE_ONLY', self.build(include=['00_来源/old.md']))

    def test_paths_and_outputs_stay_scoped(self):
        with self.assertRaises(context.ContextError):
            self.build(include=['../outside.md'])
        with self.assertRaises(context.ContextError):
            context.save_cache(self.root, 'handoff.md', '不得覆盖')
        self.assertIn('只作检索测试', (self.root / 'handoff.md').read_text(encoding='utf-8'))

    def test_table_ids_are_searchable_without_fragmenting_evidence(self):
        self.write('cards/clues.md', '# 伏笔\n\n## 尚未回收\n'
                   '| ID | 证据 |\n|---|---|\n| F002 | 候选线索，不是已埋 |\n')
        packet = self.build(ids=['F002'])
        self.assertIn('候选线索，不是已埋', packet)

    def test_existing_chinese_filenames_supply_stable_ids(self):
        self.write('02_人物/P001_哥哥.md', '# 哥哥\n\n## 知情\n尚未得知对方身份。')
        self.config['catalog_roots'].append('02_人物')
        packet = self.build(ids=['P001'])
        self.assertIn('尚未得知对方身份', packet)

    def test_code_fence_headings_do_not_split_a_topic(self):
        self.write('cards/code.md', '# 测试\n\n## 格式示例\n```markdown\n## 示例标题\n内容\n```\n真实限制\n')
        blocks = context.collect(self.root, self.config)
        selected = [b for b in blocks if b.path == 'cards/code.md']
        self.assertEqual(len(selected), 2)
        self.assertIn('真实限制', selected[1].text)


if __name__ == '__main__':
    unittest.main()
