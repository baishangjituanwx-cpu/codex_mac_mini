#!/usr/bin/env python3
"""Initialize a reusable post-generation cover package brief."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


VERTICAL_NAME = "cover-vertical-3x4.png"
HORIZONTAL_NAME = "cover-horizontal-4x3.png"
BRIEF_NAME = "cover-brief.md"
MANIFEST_NAME = "cover-manifest.json"


class CoverPackageError(RuntimeError):
    """User-facing cover package error."""


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def validate_file(path: pathlib.Path) -> pathlib.Path:
    path = path.expanduser().resolve()
    if not path.exists():
        raise CoverPackageError(f"找不到视频文件: {path}")
    if not path.is_file():
        raise CoverPackageError(f"不是文件: {path}")
    return path


def validate_text_length(label: str, value: str, min_len: int, max_len: int) -> str | None:
    count = len(value.strip())
    if count < min_len or count > max_len:
        return f"{label} 当前长度为 {count}，建议控制在 {min_len}-{max_len} 个字符。"
    return None


def build_manifest(args: argparse.Namespace, video_path: pathlib.Path, output_dir: pathlib.Path) -> dict[str, Any]:
    return {
        "source_video": str(video_path),
        "subject": args.subject,
        "angle": args.angle,
        "titles": {
            "main_title": args.main_title,
            "subtitle": args.subtitle,
        },
        "deliverables": {
            "vertical_cover": {
                "filename": VERTICAL_NAME,
                "size": "1080x1440",
                "ratio": "3:4",
                "format": "PNG",
                "path": str(output_dir / VERTICAL_NAME),
            },
            "horizontal_cover": {
                "filename": HORIZONTAL_NAME,
                "size": "1440x1080",
                "ratio": "4:3",
                "format": "PNG",
                "path": str(output_dir / HORIZONTAL_NAME),
            },
        },
        "frame_rules": [
            "封面截图必须来自最终视频，不要使用原始参考图作为背景。",
            "人物脸必须清晰，不能糊、闭眼、嘴型尴尬或明显运动模糊。",
            "优先真实办公环境里的半身或近景镜头。",
            "底部约 30% 留给标题带，关键五官不要落进遮罩区。",
        ],
        "layout_rules": [
            "底部深色半透明信息带。",
            "主标题居中大字白色。",
            "副标题一行，放在主标题下方，偏金黄色。",
            "视觉重心是真人脸和大字标题，不要贴太多元素。",
        ],
        "naming": {
            "brief": str(output_dir / BRIEF_NAME),
            "manifest": str(output_dir / MANIFEST_NAME),
        },
    }


def build_brief(manifest: dict[str, Any]) -> str:
    titles = manifest["titles"]
    deliverables = manifest["deliverables"]
    vertical = deliverables["vertical_cover"]
    horizontal = deliverables["horizontal_cover"]
    return f"""# 封面执行 Brief

## 基本信息

- 源视频：`{manifest["source_video"]}`
- 主体：`{manifest["subject"]}`
- 角度：`{manifest["angle"]}`
- 主标题：`{titles["main_title"]}`
- 副标题：`{titles["subtitle"]}`

## 固定交付

- 竖版：`{vertical["filename"]}`，`{vertical["size"]}`，`{vertical["ratio"]}`，`{vertical["format"]}`
- 横版：`{horizontal["filename"]}`，`{horizontal["size"]}`，`{horizontal["ratio"]}`，`{horizontal["format"]}`

## 截帧要求

- 封面必须取自最终视频，不要直接拿参考图做封面背景
- 人物脸必须清晰，不能糊、闭眼、嘴型变形
- 优先半身或近景，真实办公环境
- 人物脸和上半身尽量处于中上区域
- 底部约 `30%` 必须预留给标题带

## 版式要求

- 底部做深色半透明信息带
- 主标题居中大字，白色，描边清晰
- 副标题放主标题下方，一行小字，偏金黄色
- 重点是“真人脸 + 大字标题”，不要做花

## 当前文案

- 主标题：`{titles["main_title"]}`
- 副标题：`{titles["subtitle"]}`

## 输出路径

- 竖版封面：`{vertical["path"]}`
- 横版封面：`{horizontal["path"]}`
- 清单文件：`{manifest["naming"]["manifest"]}`

## 执行检查

- [ ] 已从最终视频挑出清晰关键帧
- [ ] 已确认人物主体是 {manifest["subject"]}
- [ ] 已确认真实办公环境，没有舞台感 / 直播间感
- [ ] 已导出 `3:4` 竖版 PNG
- [ ] 已导出 `4:3` 横版 PNG
- [ ] 已加底部信息带
- [ ] 已放入主标题和副标题
- [ ] 已确认缩略图尺寸下仍能看清真人脸和标题
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="为 Seedance 成片初始化固定封面包 brief。")
    parser.add_argument("--video", required=True, help="最终视频文件路径。")
    parser.add_argument("--output-dir", required=True, help="封面包输出目录，会生成 brief 和 manifest。")
    parser.add_argument("--main-title", required=True, help="封面主标题。建议 6-10 字。")
    parser.add_argument("--subtitle", required=True, help="封面副标题。建议 4-8 字。")
    parser.add_argument("--subject", default="大陈", help="封面主体姓名。默认大陈。")
    parser.add_argument("--angle", default="平台执行类", help="封面角度，如平台执行类 / 老板痛点类 / 转化收益类。")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        video_path = validate_file(pathlib.Path(args.video))
        output_dir = pathlib.Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        warnings: list[str] = []
        for warning in (
            validate_text_length("主标题", args.main_title, 6, 10),
            validate_text_length("副标题", args.subtitle, 4, 8),
        ):
            if warning:
                warnings.append(warning)

        manifest = build_manifest(args, video_path, output_dir)
        brief = build_brief(manifest)

        brief_path = output_dir / BRIEF_NAME
        manifest_path = output_dir / MANIFEST_NAME
        brief_path.write_text(brief, encoding="utf-8")
        manifest_path.write_text(dump_json(manifest) + "\n", encoding="utf-8")

        print(f"[ok] 已生成: {brief_path}")
        print(f"[ok] 已生成: {manifest_path}")
        print(f"[next] 竖版封面目标: {output_dir / VERTICAL_NAME}")
        print(f"[next] 横版封面目标: {output_dir / HORIZONTAL_NAME}")

        for item in warnings:
            print(f"[warn] {item}", file=sys.stderr)
        return 0
    except CoverPackageError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
