#!/usr/bin/env python3
"""Run the full Seedance post-video cover-package pipeline in one command."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent


class CoverPipelineError(RuntimeError):
    """User-facing cover pipeline error."""


def run_step(cmd: list[str], label: str) -> None:
    print(f"[step] {label}")
    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "未知错误"
        raise CoverPipelineError(f"{label} 失败:\n{detail}")
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="一条命令完成封面 brief、候选帧和最终 PNG 封面输出。"
    )
    parser.add_argument("--video", required=True, help="最终视频文件路径。")
    parser.add_argument("--output-dir", required=True, help="封面包输出目录。")
    parser.add_argument("--main-title", required=True, help="封面主标题。")
    parser.add_argument("--subtitle", required=True, help="封面副标题。")
    parser.add_argument("--subject", default="大陈", help="封面主体姓名。默认大陈。")
    parser.add_argument("--angle", default="平台执行类", help="封面角度，如平台执行类 / 老板痛点类。")
    parser.add_argument("--tag", help="最终封面左上小标签。")
    parser.add_argument("--count", type=int, default=6, help="候选帧数量。默认 6。")
    parser.add_argument("--candidate-index", type=int, default=1, help="最终采用的候选帧索引。默认 1。")
    parser.add_argument("--start-ratio", type=float, default=0.12, help="候选帧抽取起始比例。默认 0.12。")
    parser.add_argument("--end-ratio", type=float, default=0.88, help="候选帧抽取结束比例。默认 0.88。")
    parser.add_argument("--font-file", help="自定义字体文件路径，传给最终封面渲染脚本。")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        python = sys.executable
        output_dir = str(pathlib.Path(args.output_dir).expanduser().resolve())
        video = str(pathlib.Path(args.video).expanduser().resolve())

        init_cmd = [
            python,
            str(SCRIPT_DIR / "init_cover_package.py"),
            "--video",
            video,
            "--output-dir",
            output_dir,
            "--main-title",
            args.main_title,
            "--subtitle",
            args.subtitle,
            "--subject",
            args.subject,
            "--angle",
            args.angle,
        ]
        extract_cmd = [
            python,
            str(SCRIPT_DIR / "extract_cover_candidates.py"),
            "--video",
            video,
            "--output-dir",
            output_dir,
            "--count",
            str(args.count),
            "--start-ratio",
            str(args.start_ratio),
            "--end-ratio",
            str(args.end_ratio),
        ]
        render_cmd = [
            python,
            str(SCRIPT_DIR / "render_cover_package.py"),
            "--package-dir",
            output_dir,
            "--candidate-index",
            str(args.candidate_index),
        ]
        if args.tag:
            render_cmd.extend(["--tag", args.tag])
        if args.font_file:
            render_cmd.extend(["--font-file", args.font_file])

        run_step(init_cmd, "初始化封面 brief")
        run_step(extract_cmd, "抽取候选帧")
        run_step(render_cmd, "渲染最终封面")
        print(f"[ok] 封面包目录: {output_dir}")
        return 0
    except CoverPipelineError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
