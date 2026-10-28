#!/usr/bin/env python3
"""Minimal deterministic structural guard for dialogue-only novel editing.

Does NOT judge naturalness, dialogue correctness, plot truth or non-dialogue diffs.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import json
import sys

HEADING = re.compile(r'^\s{0,3}#{1,6}\s+.*$', re.M)
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
IMAGE = re.compile(
    r'!\[[^\]\n]*\]\([^\n]*?\)'  # Markdown inline images
    r'|!\[[^\]\n]*\]\[[^\]\n]*\]'  # Markdown reference images
    r'|!\[\[[^\]\n]+\]\]'          # Obsidian image embed
    r'|<img\b[^>]*>'                 # HTML img
    r'|<image\b[^>]*>'               # SVG/HTML image
    r'|(?<!\w)[^\s()<>"\']+\.(?:png|jpe?g|webp|gif|svg)(?:\?[^\s)<>"\']*)?',
    re.I)
COMMENT = re.compile(r'<!--.*?-->', re.S)


def lock_frontmatter(text: str) -> str:
    if not text.startswith('---\n'):
        return ''
    finish = text.find('\n---\n', 4)
    return text[:finish + 5] if finish >= 0 else ''


def image_references(text: str) -> list[str]:
    """Preserve exact source spelling and order (not line numbers)."""
    in_fence: tuple[str, int] | None = None
    result = []
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            mark = m.group(1)
            if in_fence is None:
                in_fence = (mark[0], len(mark))
            elif mark[0] == in_fence[0] and len(mark) >= in_fence[1]:
                in_fence = None
            continue
        if in_fence is None:
            result.extend(m.group() for m in IMAGE.finditer(line))
    return result


def files(root: Path) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in root.rglob('*.md') if p.is_file()}


def compare(src: Path, dst: Path) -> dict:
    errors, warnings = [], []
    original, revised = files(src), files(dst)
    for rel in sorted(original.keys() - revised.keys()):
        errors.append(f'缺失 Markdown 文件：{rel}')
    for rel in sorted(revised.keys() - original.keys()):
        errors.append(f'新增 Markdown 文件/文件名变化：{rel}')
    checked = 0
    for rel in sorted(original.keys() & revised.keys()):
        checked += 1
        before = original[rel].read_text(encoding='utf-8-sig')
        after = revised[rel].read_text(encoding='utf-8-sig')
        if HEADING.findall(before) != HEADING.findall(after):
            errors.append(f'{rel}: 章节/小节标题变化')
        if lock_frontmatter(before) != lock_frontmatter(after):
            errors.append(f'{rel}: frontmatter 变化')
        if COMMENT.findall(before) != COMMENT.findall(after):
            errors.append(f'{rel}: HTML 注释/元数据变化')
        if image_references(before) != image_references(after):
            errors.append(f'{rel}: 图片引用内容、语法或出现顺序变化')
        if before and len(after) / len(before) < 0.65:
            warnings.append(f'{rel}: 长度降低超过35%，请人工检查是否截断或误删叙述')
    return {
        'source_markdown_count': len(original),
        'revised_markdown_count': len(revised),
        'matched_files_checked': checked,
        'errors': errors,
        'warnings': warnings,
        'notice': '只验证结构；不能证明对白自然、人物一致，也不能判断未授权修改。',
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--revised', type=Path, required=True)
    args = parser.parse_args()
    if not args.source.is_dir() or not args.revised.is_dir():
        print('source/revised 必须是存在的目录', file=sys.stderr)
        return 2
    report = compare(args.source.resolve(), args.revised.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report['errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
