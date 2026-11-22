#!/usr/bin/env python3
"""按关键词查找写作策略，输出一句话、位置与检查问题。只读，不改文件。"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "skill-manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def haystack(item: dict) -> str:
    fields = [item.get("id", ""), item.get("name", ""), item.get("one_line", ""),
              item.get("when", "")]
    fields.extend(item.get("aliases", []))
    return " ".join(fields).lower()


def score(item: dict, terms: list[str]) -> int:
    text = haystack(item)
    total = 0
    for term in terms:
        term = term.lower().strip()
        if not term:
            continue
        if term == item.get("id", "").lower() or term == item.get("name", "").lower():
            total += 5
        elif any(term == alias.lower() for alias in item.get("aliases", [])):
            total += 4
        elif term in text:
            total += 1
    return total


def format_item(item: dict) -> str:
    anchor = f"#{item['anchor']}" if item.get("anchor") else ""
    return (f"[{item['name']}] {item['id']}\n"
            f"  一句话：{item['one_line']}\n"
            f"  何时用：{item['when']}\n"
            f"  位置：{item['file']}{anchor}")


def check_manifest() -> list[str]:
    """校验每个策略的文件与标题锚点是否存在。"""
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_package import heading_ids  # noqa: WPS433

    manifest = load_manifest()
    errors = []
    seen = set()
    for item in manifest["strategies"]:
        if item["id"] in seen:
            errors.append(f"重复 id：{item['id']}")
        seen.add(item["id"])
        path = ROOT / item["file"]
        if not path.is_file():
            errors.append(f"{item['id']}：文件不存在 {item['file']}")
            continue
        anchor = item.get("anchor")
        if anchor:
            anchors = heading_ids(path.read_text(encoding="utf-8"))
            if anchor not in anchors:
                errors.append(f"{item['id']}：锚点不存在 {item['file']}#{anchor}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="*", help="关键词，例如 声音、场景、对白、结尾")
    parser.add_argument("--list", action="store_true", help="列出全部策略")
    parser.add_argument("--check", action="store_true", help="校验清单文件与锚点")
    parser.add_argument("--limit", type=int, default=5, help="最多显示几个结果")
    parser.add_argument("--json", action="store_true", help="输出 ASCII JSON，便于程序读取")
    args = parser.parse_args()

    if args.check:
        errors = check_manifest()
        if errors:
            print("\n".join(errors))
            return 1
        print(f"OK：{len(load_manifest()['strategies'])} 个策略，文件与锚点均可解析。")
        return 0

    manifest = load_manifest()
    if args.list or not args.terms:
        if args.json:
            print(json.dumps(manifest["strategies"], ensure_ascii=True, indent=2))
            return 0
        for item in manifest["strategies"]:
            print(f"- {item['name']}（{item['id']}）：{item['one_line']}")
        return 0

    ranked = sorted(((score(item, args.terms), item) for item in manifest["strategies"]),
                    key=lambda pair: pair[0], reverse=True)
    hits = [(points, item) for points, item in ranked if points > 0][: args.limit]
    if not hits:
        print("没有匹配。用 --list 查看全部策略，或换一个更宽的关键词。")
        return 0
    if args.json:
        print(json.dumps([item for _, item in hits], ensure_ascii=True, indent=2))
        return 0
    for _, item in hits:
        print(format_item(item))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
