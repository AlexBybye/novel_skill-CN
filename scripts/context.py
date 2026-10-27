#!/usr/bin/env python3
"""Local, bounded retrieval of coherent Markdown sections. No model/API calls."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import sys

META = re.compile(r'<!--\s*novel-meta:\s*(\{[^\n]*\})\s*-->')
ID = re.compile(r'(?<![A-Za-z0-9])(?:P|E|F|R|W|O|N|Q)\d{2,}(?:-[A-Z0-9]+)?(?![A-Za-z0-9])')
TABLE_ID = re.compile(r'^\|\s*((?:P|E|F|R|W|O|N|Q)\d{2,})\s*\|', re.M)
MODES = ('discuss', 'next', 'character', 'clues', 'draft', 'review', 'style')
TEMPORAL = {'character', 'event', 'clue', 'state', 'delta', 'snapshot', 'prose'}
CATALOG_ARCHIVES = {'.git', '.novel-cache', '__pycache__', '备份', '修订备份', '草稿记录'}


class ContextError(ValueError):
    pass


def local_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ContextError('路径必须为工作区内的非空相对路径。')
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root):
        raise ContextError(f'拒绝工作区外路径: {relative}')
    return path


def read_config(root: Path) -> dict:
    path = local_path(root, 'novel-workspace.json')
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    if config.get('version') != 1:
        raise ContextError('不支持的工作区配置版本。')
    for key in ('handoff', 'style'):
        if config.get(key):
            local_path(root, config[key])
    for folder in config.get('catalog_roots', []):
        local_path(root, folder)
    exclusions = config.get('catalog_exclude', [])
    if not isinstance(exclusions, list) or not all(isinstance(p, str) for p in exclusions):
        raise ContextError('catalog_exclude 必须为工作区内相对文件或目录路径数组。')
    for relative in exclusions:
        local_path(root, relative)
    examples = config.get('prose_exemplars', [])
    if not isinstance(examples, list) or not all(isinstance(p, str) for p in examples):
        raise ContextError('prose_exemplars 必须为工作区内相对文件路径数组。')
    for relative in examples:
        local_path(root, relative)
    return config


def metadata_matches(text: str) -> list[re.Match]:
    """Ignore literal metadata in fenced examples; keep source offsets intact."""
    matches = []
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r'\s*(`{3,}|~{3,})', line)
        if marker:
            mark = marker.group(1)
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1]:
                fence = None
        elif fence is None:
            matches.extend(META.finditer(text, offset, offset + len(line)))
        offset += len(line)
    return matches


def metadata(text: str) -> dict:
    matches = metadata_matches(text)
    if not matches:
        return {}
    if len(matches) > 1:
        raise ContextError('一个主题小节只应有一条 novel-meta 注释。')
    value = json.loads(matches[0].group(1))
    if not isinstance(value, dict):
        raise ContextError('novel-meta 必须为 JSON 对象。')
    if 'chapter' in value and value['chapter'] is not None:
        chapter = value['chapter']
        if type(chapter) is not int or chapter < 0:
            raise ContextError('chapter 必须为非负整数或 null。')
    for key in ('entities', 'aliases', 'sources'):
        if key in value and (not isinstance(value[key], list) or
                             not all(isinstance(x, str) for x in value[key])):
            raise ContextError(f'{key} 必须为字符串数组。')
    return value


@dataclass
class Block:
    path: str
    heading: str
    start: int
    end: int
    text: str
    meta: dict
    sha: str
    ids: set[str] = field(default_factory=set)

    @property
    def key(self) -> str:
        return f'{self.path}:{self.start}'

    def render(self) -> str:
        state = {key: self.meta[key] for key in ('kind', 'status', 'chapter') if key in self.meta}
        return (f'\n---\n来源: {self.path}:{self.start}-{self.end} | '
                f'sha256={self.sha[:12]} | {json.dumps(state, ensure_ascii=False)}\n'
                + self.text.strip() + '\n')


def default_meta(relative: str) -> dict:
    folder = relative.split('/')[0]
    kind = {'01_设定': 'rules', '02_人物': 'character', '03_事件': 'event',
            '04_伏笔': 'clue', '05_素材': 'material', '10_正文': 'prose'}.get(folder, 'note')
    found = ID.search(Path(relative).stem)
    result = {'kind': kind, 'status': 'plan'}
    if found:
        result['id'] = found.group()
    return result


def parse_file(root: Path, path: Path) -> list[Block]:
    path = local_path(root, path.relative_to(root).as_posix())
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig')
    lines = text.splitlines(keepends=True)
    relative = path.relative_to(root).as_posix()
    sha = hashlib.sha256(raw).hexdigest()
    # H1 starts a new document scope inside rich, historically prepended cards.
    # H2 keeps a complete topic, including its H3s and all qualifications.
    starts = [0]
    fence = None
    outside = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        f = re.match(r'(`{3,}|~{3,})', stripped)
        outside.append(fence is None and not f)
        if f:
            mark = f.group()
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1]:
                fence = None
            continue
        if fence is None and i and re.match(r'^#{1,2}\s+', line):
            start = i
            # Old cards also put the root metadata directly BEFORE their H1.
            # Attach it to that heading, without stealing a prior heading's
            # immediately following declaration from an otherwise empty topic.
            previous = i - 1
            while previous >= 0 and not lines[previous].strip():
                previous -= 1
            if previous >= 0 and outside[previous] and META.fullmatch(lines[previous].strip()):
                before = previous - 1
                while before >= 0 and not lines[before].strip():
                    before -= 1
                if before < 0 or not re.match(r'^#{1,2}\s+', lines[before]):
                    following = i + 1
                    while following < len(lines) and not lines[following].strip():
                        following += 1
                    has_own = (following < len(lines)
                               and META.fullmatch(lines[following].strip()))
                    if line.startswith('## ') and has_own:
                        # Legacy rich cards may insert a file declaration
                        # between dated sections, with no separate H1 title.
                        # Keep that declaration separate from the next topic.
                        if previous not in starts:
                            starts.append(previous)
                    else:
                        start = previous
            if start not in starts:
                starts.append(start)
    starts.append(len(lines))
    base = default_meta(relative)
    first_heading = next((i for i, line in enumerate(lines)
                          if outside[i] and re.match(r'^#{1,2}\s+', line)), len(lines))
    if first_heading:
        try:
            base.update(metadata(''.join(lines[:first_heading])))
        except (ContextError, json.JSONDecodeError) as exc:
            raise ContextError(f'{relative}:1: {exc}') from exc
    active = dict(base)
    blocks = []
    for index, (start, stop) in enumerate(zip(starts, starts[1:])):
        body = ''.join(lines[start:stop])
        if not body.strip():
            continue
        try:
            own = metadata(body)
        except (ContextError, json.JSONDecodeError) as exc:
            raise ContextError(f'{relative}:{start + 1}: {exc}') from exc
        matches = metadata_matches(body)
        clean = body
        for match in reversed(matches):
            clean = clean[:match.start()] + clean[match.end():]
        clean = clean.strip()
        if not clean:
            active = dict(base)
            active.update(own)
            continue
        heading = next((line for line in clean.splitlines()
                        if re.match(r'^#{1,2}\s+', line)), '')
        if heading.startswith('# '):
            active = dict(base)
            active.update(own)
        elif not heading and index == 0:
            base.update(own)
            active = dict(base)
        meta = dict(active)
        meta.update(own)
        head = next((re.sub(r'^#+\s*', '', s).strip() for s in clean.splitlines()
                     if s.startswith('#')), Path(relative).stem)
        declared = set(TABLE_ID.findall(clean))
        if meta.get('id'):
            declared.add(meta['id'])
        blocks.append(Block(relative, head, start + 1, stop, clean, meta, sha, declared))
    return blocks


def collect(root: Path, config: dict, extra: list[str] | None = None) -> list[Block]:
    paths = set()
    exclusions = [local_path(root, p) for p in config.get('catalog_exclude', [])]
    for folder in config.get('catalog_roots', []):
        target = local_path(root, folder)
        if target.is_file():
            paths.add(target)
        elif target.is_dir():
            for path in target.rglob('*.md'):
                checked = local_path(root, path.relative_to(root).as_posix())
                if (CATALOG_ARCHIVES.intersection(path.relative_to(root).parts)
                        or any(checked == p or checked.is_relative_to(p) for p in exclusions)):
                    continue
                paths.add(checked)
    for relative in [config['handoff'], config.get('style'), *(extra or [])]:
        if relative:
            target = local_path(root, relative)
            if not target.is_file():
                raise ContextError(f'资料文件不存在: {relative}')
            paths.add(target)
    blocks = []
    for path in sorted(paths):
        blocks.extend(parse_file(root, path))
    return blocks


def tokens(query: str) -> set[str]:
    result = set(re.findall(r'[A-Za-z][A-Za-z0-9_-]+', query.lower()))
    for phrase in re.findall(r'[\u3400-\u9fff]+', query):
        result.add(phrase)
        result.update(phrase[i:i + 2] for i in range(len(phrase) - 1))
    return result


def eligible(block: Block, mode: str, chapter: int | None, handoff: str) -> bool:
    if block.meta.get('kind') == 'exemplar':
        return False  # Expression references never enter a story-fact packet.
    if block.path == handoff:
        return True  # Operational context, never evidence of character knowledge.
    when = block.meta.get('chapter')
    if chapter is not None and when is not None and when > chapter:
        return False
    if mode in ('draft', 'review'):
        status = block.meta.get('status')
        if block.meta.get('kind') == 'style':
            return True  # Candidate profile is explicitly provisional.
        if status not in ('canonical', 'approved', 'accepted'):
            return False
        if block.meta.get('kind') in TEMPORAL and when is None:
            return False
    elif block.meta.get('status') == 'superseded':
        return False
    return True


def score(block: Block, query: str, wanted: set[str], mode: str) -> int:
    text = block.text.lower()
    value = sum(2 + (4 if term in block.heading.lower() else 0)
                for term in tokens(query) if term in text)
    value += 15 * len(wanted.intersection(block.meta.get('entities', [])))
    value += 8 * len(wanted.intersection(ID.findall(block.text)))
    value += 12 * sum(alias in query for alias in block.meta.get('aliases', []) if alias)
    preferred = {'character': 'character', 'clues': 'clue', 'style': 'style'}.get(mode)
    if value > 0 and block.meta.get('kind') == preferred:
        value += 8
    return value


def split_selector(value: str) -> tuple[str, str | None]:
    path, marker, heading = value.partition('#')
    return path.replace('\\', '/'), heading if marker else None


def build_packet(root: Path, config: dict, *, mode='discuss', query='', ids=None,
                 include=None, select=None, budget=9000, at_chapter=None, brief=None) -> str:
    if budget < 1500:
        raise ContextError('资料包预算至少 1500 字符；关键主题簇不能静默截断。')
    if mode in ('draft', 'review') and at_chapter is None:
        raise ContextError('写作或按时点审稿必须指定 --at-chapter。')
    selectors = [split_selector(s) for s in (select or [])]
    extras = [*(include or []), *(p for p, _ in selectors)]
    if brief:
        extras.append(brief)
    blocks = collect(root, config, extras)
    canonical_extras = {local_path(root, p).relative_to(root).as_posix() for p in (include or [])}
    selectors = [(local_path(root, p).relative_to(root).as_posix(), h) for p, h in selectors]
    brief_path = local_path(root, brief).relative_to(root).as_posix() if brief else None
    if mode == 'draft':
        task = next((b for b in blocks if b.path == brief_path), None)
        if task is None or task.meta.get('kind') != 'brief' or task.meta.get('status') != 'approved':
            raise ContextError('缺少已获用户授权的任务卡；讨论不自动授权写作。')
        if task.meta.get('chapter') != at_chapter:
            raise ContextError('任务卡章节与目标章节不同。')
    wanted = set(ids or [])
    required, optional, excluded = [], [], []
    seen_ids, found_selectors = set(), set()
    for block in blocks:
        matches = {i for i, (path, heading) in enumerate(selectors)
                   if block.path == path and (heading is None or block.heading == heading)}
        direct_ids = block.ids.intersection(wanted)
        must = (block.path == config['handoff'] or block.path in canonical_extras or
                block.path == brief_path or bool(matches) or bool(direct_ids))
        if mode in ('draft', 'review', 'style') and block.path == config.get('style'):
            must = True
        if not eligible(block, mode, at_chapter, config['handoff']):
            if matches or block.path in canonical_extras or block.path == brief_path:
                raise ContextError(f'指定资料与目标时点/状态不兼容: {block.key}')
            if must:
                excluded.append(block.key)
            continue
        seen_ids.update(direct_ids)
        found_selectors.update(matches)
        if must:
            required.append(block)
        else:
            relevance = score(block, query, wanted, mode)
            if relevance > 0:
                optional.append((relevance, block))
    if wanted - seen_ids:
        raise ContextError('目标 ID 没有适用时点的主档: ' + ', '.join(sorted(wanted - seen_ids)) +
                           '；检查元数据或先建立该场景的状态，不把未来计划当事实。')
    if len(found_selectors) != len(selectors):
        raise ContextError('指定主题标题不存在，请先运行 index 确认精确标题。')
    optional.sort(key=lambda item: (-item[0], item[1].path, item[1].start))
    required.sort(key=lambda b: (b.path != config['handoff'], b.path, b.start))
    header = (f'# 本次资料包 | {config.get("title", "小说")} | {mode}\n'
              f'目标章节: {at_chapter if at_chapter is not None else "未限定（作者讨论）"}\n'
              '原文摘取，按主题簇保留上下文；规划、角色所知与客观事实必须区分。\n'
              '接续卡是作者工作状态，不是角色的记忆。未检索到不代表不存在。\n')
    def render(chosen: list[Block], omitted: list[Block]) -> str:
        tail = (f'\n检索说明：加载 {len(chosen)} 个主题簇；'
                f'相关但预算未纳入 {len(omitted)} 个；时点/状态排除的指定簇 {len(excluded)} 个。\n'
                '字符预算只限制这个资料包，不含已有聊天、系统提示和后续回查；不是精确 token 计费。\n')
        for block in omitted[:4]:
            tail += f'待按需回查: {block.path}:{block.start}（{block.heading}）\n'
        return header + ''.join(b.render() for b in chosen) + tail
    candidates = [b for _, b in optional]
    if len(render(required, candidates)) > budget:
        largest = sorted(required, key=lambda b: len(b.text), reverse=True)[:3]
        details = '; '.join(f'{b.path}#{b.heading}: {len(b.text)} 字符' for b in largest)
        raise ContextError(f'必要资料超过 {budget} 字符预算，未截断。用 --select 选择完整主题簇或调整任务范围。{details}')
    chosen, omitted = list(required), []
    for i, block in enumerate(candidates):
        pending = omitted + candidates[i + 1:]
        if len(render(chosen + [block], pending)) <= budget:
            chosen.append(block)
        else:
            omitted.append(block)
    packet = render(chosen, omitted)
    if len(packet) > budget:
        raise ContextError('资料包元数据超过预算；请缩小选取范围。')
    return packet


def usable_exemplar(block: Block) -> bool:
    """Metadata is admission evidence, not semantic proof of anonymization/quality."""
    meta = block.meta
    if (meta.get('kind') != 'exemplar' or
            not str(meta.get('id', '')).startswith('EX-') or not meta.get('sources')):
        return False
    if meta.get('origin') == 'synthetic':
        return (block.path == '@skill/references/prose-exemplars.md' and
                meta.get('status') == 'illustrative')
    return (meta.get('origin') == 'private' and
            meta.get('status') in ('approved', 'accepted') and
            meta.get('usage') == 'expression-only' and meta.get('sanitized') is True and
            isinstance(meta.get('approval'), str) and bool(meta['approval'].strip()))


def build_exemplar_packet(root: Path, config: dict, *, query='', ids=None, select=None,
                          budget=4000, limit=2, bundled=True) -> str:
    """Reuse topic parsing, lexical scoring and selectors, isolated from story retrieval."""
    if budget < 1500:
        raise ContextError('范例预算至少 1500 字符；不截断范例的适用边界。')
    if type(limit) is not int or not 1 <= limit <= 3:
        raise ContextError('每次范例数量须为 1—3 组。')
    blocks, registered = [], set()
    for relative in config.get('prose_exemplars', []):
        path = local_path(root, relative)
        if not path.is_file():
            raise ContextError(f'范例文件不存在: {relative}')
        registered.add(path.relative_to(root).as_posix())
        blocks.extend(parse_file(root, path))
    skill_root = Path(__file__).resolve().parents[1]
    bundled_label = '@skill/references/prose-exemplars.md'
    if bundled:
        public = parse_file(skill_root, skill_root / 'references/prose-exemplars.md')
        for block in public:
            block.path = '@skill/' + block.path
        blocks.extend(public)
        registered.add(bundled_label)
    selectors = []
    for value in select or []:
        path, heading = split_selector(value)
        if not path.startswith('@skill/'):
            path = local_path(root, path).relative_to(root).as_posix()
        if path not in registered:
            raise ContextError(f'只可选择已配置的私有范例或内置范例: {path}')
        selectors.append((path, heading))
    wanted = set(ids or [])
    required, optional = [], []
    found_ids, found_selectors, admitted = set(), set(), set()
    rejected = 0
    for block in blocks:
        direct = block.ids.intersection(wanted)
        matches = {i for i, (p, h) in enumerate(selectors)
                   if block.path == p and (h is None or block.heading == h)}
        if not usable_exemplar(block):
            if direct or (matches and block.meta.get('kind') == 'exemplar'):
                raise ContextError(f'指定范例未认可、未隔离作品事实或缺少来源: {block.key}')
            rejected += block.meta.get('kind') == 'exemplar'
            continue
        example_id = block.meta['id']
        if example_id in admitted:
            raise ContextError(f'范例 ID 重复，请给私有组使用独立 ID: {example_id}')
        admitted.add(example_id)
        found_ids.update(direct)
        found_selectors.update(matches)
        if direct or matches:
            required.append(block)
        else:
            relevance = score(block, query, set(), 'style')
            if relevance:
                optional.append((relevance, block))
    if wanted - found_ids:
        raise ContextError('没有可用的范例 ID: ' + ', '.join(sorted(wanted - found_ids)))
    if len(found_selectors) != len(selectors):
        raise ContextError('指定的完整范例主题不存在或不可用。')
    if len(required) > limit:
        raise ContextError('显式选择的范例超过数量上限，请缩小 --ids/--select 范围。')
    # At equal relevance, an approved work-specific reference precedes a public illustration.
    optional.sort(key=lambda pair: (-pair[0], pair[1].path.startswith('@skill/'),
                                    pair[1].path, pair[1].start))
    candidates = [block for _, block in optional]
    header = ('# 表达参考包（独立于剧情事实）\n'
              '只迁移写法机制；人物、事件、物品、关系和来源章号均不成为当前剧情或角色知识。\n'
              'source_chapter/chapter 在此仅标示范例出处，不表示当前人物状态生效。\n'
              '内置 illustrative 只是原创示意，未获作者认可，也没有效果验证。\n')

    def render(chosen, omitted):
        rendered = []
        for block in chosen:
            provenance = {key: block.meta[key] for key in
                          ('id', 'origin', 'usage', 'sanitized', 'source_chapter', 'approval', 'sources')
                          if key in block.meta}
            rendered.append(block.render() + '范例记录（仅表达参考）: ' +
                            json.dumps(provenance, ensure_ascii=False) + '\n')
        return (header + ''.join(rendered) +
                f'\n选入 {len(chosen)} 组；相关但数量/预算未纳入 {len(omitted)} 组；'
                f'未认可或未隔离的范例排除 {rejected} 组。\n'
                '无相关可用范例时直接按当前人物与文风写，不补造认可或强套示例。\n')

    if len(render(required, candidates)) > budget:
        raise ContextError('指定完整范例超过预算，未截断；缩小选择或增加范例独立预算。')
    chosen, omitted = list(required), []
    for i, block in enumerate(candidates):
        pending = omitted + candidates[i + 1:]
        if len(chosen) < limit and len(render(chosen + [block], pending)) <= budget:
            chosen.append(block)
        else:
            omitted.append(block)
    packet = render(chosen, omitted)
    if len(packet) > budget:
        raise ContextError('范例包元数据超过预算，未截断。')
    return packet


def save_cache(root: Path, relative: str, text: str) -> Path:
    path = local_path(root, relative)
    cache = local_path(root, '.novel-cache')
    if not path.is_relative_to(cache) or path == cache:
        raise ContextError('生成文件只能保存到 .novel-cache/，不得覆盖小说资料。')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('index', 'build'):
        command = sub.add_parser(name)
        command.add_argument('--root', required=True)
        if name == 'build':
            command.add_argument('--mode', choices=MODES, default='discuss')
            command.add_argument('--query', default='')
            command.add_argument('--ids', nargs='*', default=[])
            command.add_argument('--include', action='append', default=[])
            command.add_argument('--select', action='append', default=[])
            command.add_argument('--budget', type=int, default=9000)
            command.add_argument('--at-chapter', type=int)
            command.add_argument('--brief')
            command.add_argument('--output', help='Optional path under .novel-cache/')
    examples = sub.add_parser('exemplars', help='独立选取少量表达范例，不加载剧情资料')
    examples.add_argument('--root', required=True)
    examples.add_argument('--query', default='')
    examples.add_argument('--ids', nargs='*', default=[])
    examples.add_argument('--select', action='append', default=[])
    examples.add_argument('--budget', type=int, default=4000)
    examples.add_argument('--limit', type=int, default=2)
    examples.add_argument('--output', help='Optional path under .novel-cache/')
    args = parser.parse_args()
    try:
        root = Path(args.root).resolve(strict=True)
        config = read_config(root)
        if args.command == 'index':
            blocks = collect(root, config)
            entries = [{'path': b.path, 'heading': b.heading, 'lines': [b.start, b.end],
                        'sha256': b.sha, 'characters': len(b.text), 'meta': b.meta,
                        'ids': sorted(b.ids)} for b in blocks]
            path = save_cache(root, '.novel-cache/index.json',
                              json.dumps({'version': 1, 'blocks': entries}, ensure_ascii=False, indent=2))
            print(f'已索引 {len(entries)} 个主题簇；索引不含正文。{path}')
        else:
            if args.command == 'exemplars':
                packet = build_exemplar_packet(root, config, query=args.query, ids=args.ids,
                                               select=args.select, budget=args.budget,
                                               limit=args.limit)
            else:
                packet = build_packet(root, config, mode=args.mode, query=args.query, ids=args.ids,
                                      include=args.include, select=args.select, budget=args.budget,
                                      at_chapter=args.at_chapter, brief=args.brief)
            if args.output:
                path = save_cache(root, args.output, packet)
                print(f'已生成 {len(packet)} 字符资料包（上限 {args.budget}），请读取：{path}')
            else:
                print(packet, end='')
        return 0
    except (ContextError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f'资料检索未完成：{exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    raise SystemExit(main())
