"""Reference admission and retrieval tests; no model or literary-quality assertions."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_context import context


class ExemplarTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='prose-exemplar-test-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.config = {'version': 1, 'handoff': 'handoff.md', 'catalog_roots': ['cards'],
                       'prose_exemplars': ['cards/examples.md']}
        self.write('handoff.md', '# 工作面\nHANDOFF_FACT_ONLY')
        self.write('cards/examples.md', '# 私有范例\n')
        self.save_config()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')

    def save_config(self):
        self.write('novel-workspace.json', json.dumps(self.config))

    def example(self, number='101', body='示范正文。', heading='人物需要', **overrides):
        meta = {'id': 'EX-' + number, 'kind': 'exemplar', 'origin': 'private',
                'status': 'approved', 'usage': 'expression-only', 'sanitized': True,
                'approval': '测试夹具：虚构作者已认可表达参考，不是现实作者认可',
                'aliases': ['陌生人互助', '真实需要'], 'sources': ['private/source.md:10']}
        meta.update(overrides)
        return ('\n## ' + heading + '\n<!-- novel-meta: ' + json.dumps(meta, ensure_ascii=False) +
                ' -->\n原稿：说明情绪。\n改写：' + body + '\n### 机制与适用\n说明机制。\n'
                '### 不适用与错误模仿\nBOUNDARY_KEEP_不要照搬动作。\n')

    def put(self, *examples):
        self.write('cards/examples.md', '# 私有范例\n' + ''.join(examples))

    def packet(self, **kwargs):
        return context.build_exemplar_packet(self.root, self.config, bundled=False, **kwargs)

    def test_mechanism_alias_and_situation_select_complete_group(self):
        self.put(self.example(body='NEED_EXAMPLE'))
        packet = self.packet(query='陌生人互助 真实需要')
        self.assertIn('NEED_EXAMPLE', packet)
        self.assertIn('BOUNDARY_KEEP', packet)
        self.assertNotIn('HANDOFF_FACT_ONLY', packet)

    def test_ids_and_heading_selectors_reuse_complete_topics(self):
        self.put(self.example(body='SELECTED'), self.example('102', 'UNSELECTED', '其他'))
        for kwargs in ({'ids': ['EX-101']},
                       {'select': ['cards/examples.md#人物需要']}):
            packet = self.packet(**kwargs)
            self.assertIn('SELECTED', packet)
            self.assertNotIn('UNSELECTED', packet)
            self.assertIn('BOUNDARY_KEEP', packet)

    def test_unapproved_and_rejected_samples_cannot_be_selected(self):
        for status in ('candidate', 'plan', 'rejected', 'superseded', 'resolved'):
            with self.subTest(status=status):
                self.put(self.example(body='DRAFT_ONLY_SECRET', status=status))
                self.assertNotIn('DRAFT_ONLY_SECRET', self.packet(query='真实需要'))
                with self.assertRaisesRegex(context.ContextError, '未认可'):
                    self.packet(ids=['EX-101'])
                with self.assertRaisesRegex(context.ContextError, '未认可'):
                    self.packet(select=['cards/examples.md#人物需要'])

    def test_accepted_prose_is_not_automatically_a_style_reference(self):
        for missing in ({'approval': ''}, {'usage': 'story'}, {'sources': []},
                        {'sanitized': False}, {'origin': 'unknown'}):
            with self.subTest(missing=missing):
                self.put(self.example(body='UNADMITTED', status='accepted', **missing))
                self.assertNotIn('UNADMITTED', self.packet(query='真实需要'))

    def test_private_sample_cannot_masquerade_as_public_illustration(self):
        self.put(self.example(body='PRIVATE_DRAFT', origin='synthetic', status='illustrative'))
        self.assertNotIn('PRIVATE_DRAFT', self.packet(query='真实需要'))

    def test_unsanitized_future_excerpt_and_its_sources_are_never_loaded(self):
        self.write('private/source.md', 'FUTURE_SOURCE_SECRET')
        self.put(self.example(body='FUTURE_EXCERPT_SECRET', source_chapter=37, sanitized=False))
        packet = self.packet(query='真实需要')
        self.assertNotIn('FUTURE_EXCERPT_SECRET', packet)
        self.assertNotIn('FUTURE_SOURCE_SECRET', packet)

    def test_source_chapter_does_not_become_state_effective_chapter(self):
        self.put(self.example(body='ANONYMOUS_MECHANISM', source_chapter=37, chapter=37))
        self.write('cards/future.md', '<!-- novel-meta: {"kind":"state","status":"accepted",'
                   '"chapter":37} -->\n真实需要 FUTURE_PLOT_SECRET')
        reference = self.packet(ids=['EX-101'])
        self.assertIn('ANONYMOUS_MECHANISM', reference)
        self.assertNotIn('FUTURE_PLOT_SECRET', reference)
        story = context.build_packet(self.root, self.config, mode='review', at_chapter=2,
                                     query='真实需要 ANONYMOUS_MECHANISM')
        self.assertNotIn('ANONYMOUS_MECHANISM', story)
        self.assertNotIn('FUTURE_PLOT_SECRET', story)

    def test_exemplars_are_excluded_from_every_story_mode(self):
        self.put(self.example(body='REFERENCE_NOT_FACT'))
        self.write('cards/brief.md', '<!-- novel-meta: {"kind":"brief","status":"approved",'
                   '"chapter":2} -->\n授权测试场景')
        for mode in context.MODES:
            with self.subTest(mode=mode):
                kwargs = {'at_chapter': 2} if mode in ('draft', 'review') else {}
                if mode == 'draft':
                    kwargs['brief'] = 'cards/brief.md'
                packet = context.build_packet(self.root, self.config, mode=mode,
                                               query='REFERENCE_NOT_FACT', **kwargs)
                self.assertNotIn('REFERENCE_NOT_FACT', packet)
        for kwargs in ({'include': ['cards/examples.md']},
                       {'select': ['cards/examples.md#人物需要']}):
            with self.assertRaisesRegex(context.ContextError, '不兼容'):
                context.build_packet(self.root, self.config, **kwargs)

    def test_no_examples_and_no_matches_are_valid(self):
        self.config.pop('prose_exemplars')
        self.assertIn('选入 0 组', self.packet(query='不存在的情境'))
        self.put(self.example())
        self.config['prose_exemplars'] = ['cards/examples.md']
        self.assertIn('选入 0 组', self.packet())

    def test_old_config_can_use_bundled_illustrations_without_new_fields(self):
        self.config.pop('prose_exemplars')
        packet = context.build_exemplar_packet(self.root, self.config, ids=['EX-001'])
        self.assertIn('@skill/references/prose-exemplars.md', packet)
        self.assertIn('未获特定作者认可', packet)

    def test_explicit_oversized_reference_is_never_truncated(self):
        self.put(self.example(body='不可切开。' * 1500))
        with self.assertRaisesRegex(context.ContextError, '未截断'):
            self.packet(ids=['EX-101'], budget=1800)

    def test_implicit_oversized_reference_is_omitted_and_other_groups_remain_whole(self):
        self.put(self.example(body='LARGE_ONLY' * 1500),
                 self.example('102', 'SMALL_COMPLETE', '真实需要'))
        packet = self.packet(query='真实需要', budget=1800)
        self.assertLessEqual(len(packet), 1800)
        self.assertIn('SMALL_COMPLETE', packet)
        self.assertIn('BOUNDARY_KEEP', packet)
        self.assertNotIn('LARGE_ONLY', packet)
        self.assertIn('未纳入 1 组', packet)

    def test_limit_and_explicit_overselection(self):
        self.put(*(self.example(str(i), f'BODY_{i}', f'组{i}') for i in range(101, 105)))
        packet = self.packet(query='真实需要', limit=3, budget=5000)
        self.assertIn('选入 3 组', packet)
        self.assertEqual(sum(f'BODY_{i}' in packet for i in range(101, 105)), 3)
        with self.assertRaisesRegex(context.ContextError, '数量上限'):
            self.packet(ids=['EX-101', 'EX-102', 'EX-103'], limit=2)
        for invalid in (0, 4, True):
            with self.assertRaises(context.ContextError):
                self.packet(limit=invalid)

    def test_sources_are_traceable_but_not_automatically_read(self):
        self.write('private/source.md', 'RAW_NOVEL_NEVER_LOAD')
        self.put(self.example(body='SANITIZED_SAMPLE'))
        packet = self.packet(ids=['EX-101'])
        self.assertIn('SANITIZED_SAMPLE', packet)
        self.assertNotIn('RAW_NOVEL_NEVER_LOAD', packet)

    def test_changed_file_is_reread(self):
        self.put(self.example(body='OLD_SAMPLE'))
        old = self.packet(ids=['EX-101'])
        self.put(self.example(body='NEW_SAMPLE'))
        new = self.packet(ids=['EX-101'])
        self.assertIn('OLD_SAMPLE', old)
        self.assertNotIn('OLD_SAMPLE', new)
        self.assertIn('NEW_SAMPLE', new)

    def test_paths_registration_and_config_type_are_enforced(self):
        for selector in ('../outside.md', '@skill/other.md', 'cards/unregistered.md'):
            with self.assertRaises(context.ContextError):
                self.packet(select=[selector])
        for paths in ('cards/examples.md', [9], ['../outside.md']):
            self.config['prose_exemplars'] = paths
            self.save_config()
            with self.assertRaises(context.ContextError):
                context.read_config(self.root)

    def test_missing_file_duplicate_ids_and_unknown_targets_are_reported(self):
        self.put(self.example(), self.example(heading='重复ID'))
        with self.assertRaisesRegex(context.ContextError, 'ID 重复'):
            self.packet(query='真实需要')
        self.put(self.example())
        with self.assertRaisesRegex(context.ContextError, '范例 ID'):
            self.packet(ids=['EX-404'])
        with self.assertRaisesRegex(context.ContextError, '主题不存在'):
            self.packet(select=['cards/examples.md#不存在'])
        self.config['prose_exemplars'] = ['missing.md']
        with self.assertRaisesRegex(context.ContextError, '文件不存在'):
            self.packet()

    def test_cli_selection_output_and_unauthorized_cache_target(self):
        self.put(self.example(body='CLI_SAMPLE'))
        command = [sys.executable, '-X', 'utf8', '-B', str(context.__file__),
                   'exemplars', '--root', str(self.root), '--ids', 'EX-101', '--limit', '1']
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CLI_SAMPLE', result.stdout)
        saved = subprocess.run(command + ['--output', '.novel-cache/example.md'],
                               capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(saved.returncode, 0, saved.stderr)
        self.assertIn('CLI_SAMPLE', (self.root / '.novel-cache/example.md').read_text(encoding='utf-8'))
        blocked = subprocess.run(command + ['--output', 'handoff.md'],
                                 capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(blocked.returncode, 2)
        self.assertIn('HANDOFF_FACT_ONLY', (self.root / 'handoff.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
