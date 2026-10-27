#!/usr/bin/env python3
"""Check local package links and build an archive. No literary-quality scoring."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile, ZIP_DEFLATED

EXCLUDED = {'.git', '__pycache__', '.novel-cache', '.pytest_cache', '.DS_Store', 'Thumbs.db'}
LINK = re.compile(r'\[[^\]\n]*\]\(([^)\n]+)\)')


def source_files(root: Path) -> list[Path]:
    result = []
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if EXCLUDED.intersection(relative.parts) or path.suffix in {'.pyc', '.pyo'}:
            continue
        if path.is_file():
            if not path.resolve().is_relative_to(root):
                raise ValueError(f'包内文件指向目录外：{relative}')
            result.append(path)
    return sorted(result)


def prose_lines(text: str):
    """Yield line numbers and prose outside code fences."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'\s*(`{3,}|~{3,})', line)
        if marker:
            mark = marker.group(1)
            if fence is None:
                fence = (mark[0], len(mark))
            elif mark[0] == fence[0] and len(mark) >= fence[1]:
                fence = None
        elif fence is None:
            yield number, line


def heading_ids(text: str) -> set[str]:
    result, counts = set(), {}
    for _, line in prose_lines(text):
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match:
            continue
        title = re.sub(r'<[^>]+>', '', match.group(1)).strip().lower()
        title = re.sub(r'[^\w\s-]', '', title)
        slug = re.sub(r'\s', '-', title)
        count = counts.get(slug, 0)
        result.add(slug + (f'-{count}' if count else ''))
        counts[slug] = count + 1
    return result


def package_identity(root: Path) -> tuple[str, str]:
    content = (root / 'SKILL.md').read_text(encoding='utf-8')
    if not content.startswith('---\n'):
        raise ValueError('SKILL.md 缺少YAML frontmatter。')
    front = content.split('---', 2)[1]
    name = re.search(r'^name:\s*([a-z0-9-]+)\s*$', front, re.M)
    version = re.search(r'^\s+version:\s*[\'"]?([0-9]+\.[0-9]+\.[0-9]+)', front, re.M)
    if not name or not version:
        raise ValueError('缺少合法的技能名或版本号。')
    return name.group(1), version.group(1)


def check(root: Path) -> dict:
    root = root.resolve()
    name, version = package_identity(root)
    files = source_files(root)
    errors = []
    markdown = {}
    for path in files:
        if path.suffix == '.md':
            markdown[path] = path.read_text(encoding='utf-8')
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
    anchors = {path: heading_ids(text) for path, text in markdown.items()}
    for path, content in markdown.items():
        for number, line in prose_lines(content):
            for target in LINK.findall(line):
                target = target.strip().strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc:
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
                location = f'{path.relative_to(root).as_posix()}:{number}'
                if not destination.is_relative_to(root):
                    errors.append(f'{location} 包外相对链接：{target}')
                elif not destination.is_file():
                    errors.append(f'{location} 文件不存在：{target}')
                elif parsed.fragment and destination in anchors:
                    if unquote(parsed.fragment) not in anchors[destination]:
                        errors.append(f'{location} 标题锚点不存在：{target}')
    return {'name': name, 'version': version, 'files': len(files),
            'markdown_files': len(markdown), 'errors': errors}


def archive(root: Path, output: Path, name: str) -> None:
    root, output = root.resolve(), output.resolve()
    if output.suffix != '.zip' or output.is_relative_to(root):
        raise ValueError('压缩包必须是技能目录外的.zip文件，不能覆盖包内源文件。')
    output.parent.mkdir(parents=True, exist_ok=True)
    files = source_files(root)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with ZipFile(temporary, 'w', ZIP_DEFLATED) as package:
            for path in files:
                package.write(path, (Path(name) / path.relative_to(root)).as_posix())
        with ZipFile(temporary) as package:
            if package.testzip() is not None:
                raise ValueError('压缩包校验失败。')
            for path in files:
                key = (Path(name) / path.relative_to(root)).as_posix()
                if package.read(key) != path.read_bytes():
                    raise ValueError(f'压缩包与源文件不一致：{key}')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--archive', type=Path, help='校验通过后生成此ZIP，不安装、不运行外部代码')
    args = parser.parse_args()
    try:
        result = check(args.root)
        if not result['errors'] and args.archive:
            archive(args.root, args.archive, result['name'])
            result['archive'] = str(args.archive.resolve())
    except (ValueError, OSError) as exc:
        print(json.dumps({'errors': [str(exc)]}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
