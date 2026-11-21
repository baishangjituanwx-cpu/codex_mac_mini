#!/usr/bin/env python3
"""Extract candidate still frames for post-generation video covers."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import shutil
import subprocess
import sys
from typing import Any


CONTACT_SHEET_NAME = "cover-contact-sheet.jpg"
CANDIDATE_JSON_NAME = "cover-candidates.json"
CANDIDATE_DIR_NAME = "cover-candidates"
MANIFEST_NAME = "cover-manifest.json"


class CoverCandidateError(RuntimeError):
    """User-facing cover-candidate error."""


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise CoverCandidateError(f"缺少依赖命令: {name}")
    return path


def validate_file(path: pathlib.Path) -> pathlib.Path:
    path = path.expanduser().resolve()
    if not path.exists():
        raise CoverCandidateError(f"找不到视频文件: {path}")
    if not path.is_file():
        raise CoverCandidateError(f"不是文件: {path}")
    return path


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def read_duration(ffprobe_path: str, video_path: pathlib.Path) -> float:
    cmd = [
        ffprobe_path,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = run_command(cmd)
    if result.returncode != 0:
        raise CoverCandidateError(f"ffprobe 读取时长失败:\n{result.stderr.strip() or result.stdout.strip()}")
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise CoverCandidateError(f"无法解析视频时长: {result.stdout.strip()}") from exc
    if duration <= 0:
        raise CoverCandidateError(f"视频时长异常: {duration}")
    return duration


def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def build_timestamps(duration: float, count: int, start_ratio: float, end_ratio: float) -> list[float]:
    if count == 1:
        return [duration * ((start_ratio + end_ratio) / 2)]
    span = end_ratio - start_ratio
    return [duration * (start_ratio + span * (index / (count - 1))) for index in range(count)]


def extract_frame(ffmpeg_path: str, video_path: pathlib.Path, output_path: pathlib.Path, timestamp: float) -> None:
    cmd = [
        ffmpeg_path,
        "-y",
        "-ss",
        f"{timestamp:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ]
    result = run_command(cmd)
    if result.returncode != 0:
        raise CoverCandidateError(f"抽帧失败: {output_path.name}\n{result.stderr.strip() or result.stdout.strip()}")


def make_contact_sheet(ffmpeg_path: str, candidate_dir: pathlib.Path, count: int, output_path: pathlib.Path) -> None:
    cols = min(3, count)
    rows = math.ceil(count / cols)
    cmd = [
        ffmpeg_path,
        "-y",
        "-framerate",
        "1",
        "-start_number",
        "1",
        "-i",
        str(candidate_dir / "candidate-%02d.png"),
        "-frames:v",
        "1",
        "-vf",
        f"scale=480:-1,tile={cols}x{rows}",
        str(output_path),
    ]
    result = run_command(cmd)
    if result.returncode != 0:
        raise CoverCandidateError(f"生成联系表失败:\n{result.stderr.strip() or result.stdout.strip()}")


def load_existing_manifest(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def build_candidate_payload(
    video_path: pathlib.Path,
    candidate_dir: pathlib.Path,
    contact_sheet_path: pathlib.Path,
    duration: float,
    timestamps: list[float],
) -> dict[str, Any]:
    frames = [
        {
            "index": index,
            "timestamp_seconds": round(timestamp, 3),
            "timestamp_hms": format_timestamp(timestamp),
            "path": str(candidate_dir / f"candidate-{index:02d}.png"),
        }
        for index, timestamp in enumerate(timestamps, start=1)
    ]
    return {
        "source_video": str(video_path),
        "duration_seconds": round(duration, 3),
        "contact_sheet": str(contact_sheet_path),
        "candidate_directory": str(candidate_dir),
        "frame_count": len(frames),
        "frames": frames,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从成片中抽取封面候选帧，并生成联系表。")
    parser.add_argument("--video", required=True, help="最终视频文件路径。")
    parser.add_argument("--output-dir", required=True, help="封面包输出目录。会写入候选帧、联系表和候选清单。")
    parser.add_argument("--count", type=int, default=6, help="候选帧数量。默认 6。")
    parser.add_argument("--start-ratio", type=float, default=0.12, help="抽帧起始比例，默认 0.12。")
    parser.add_argument("--end-ratio", type=float, default=0.88, help="抽帧结束比例，默认 0.88。")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.count < 1:
            raise CoverCandidateError("--count 必须大于等于 1。")
        if not (0 <= args.start_ratio < args.end_ratio <= 1):
            raise CoverCandidateError("--start-ratio 和 --end-ratio 必须满足 0 <= start < end <= 1。")

        ffmpeg_path = require_binary("ffmpeg")
        ffprobe_path = require_binary("ffprobe")
        video_path = validate_file(pathlib.Path(args.video))
        output_dir = pathlib.Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        candidate_dir = output_dir / CANDIDATE_DIR_NAME
        candidate_dir.mkdir(parents=True, exist_ok=True)
        contact_sheet_path = output_dir / CONTACT_SHEET_NAME
        candidate_json_path = output_dir / CANDIDATE_JSON_NAME
        manifest_path = output_dir / MANIFEST_NAME

        duration = read_duration(ffprobe_path, video_path)
        timestamps = build_timestamps(duration, args.count, args.start_ratio, args.end_ratio)

        for index, timestamp in enumerate(timestamps, start=1):
            extract_frame(ffmpeg_path, video_path, candidate_dir / f"candidate-{index:02d}.png", timestamp)

        make_contact_sheet(ffmpeg_path, candidate_dir, len(timestamps), contact_sheet_path)

        candidate_payload = build_candidate_payload(
            video_path=video_path,
            candidate_dir=candidate_dir,
            contact_sheet_path=contact_sheet_path,
            duration=duration,
            timestamps=timestamps,
        )
        candidate_json_path.write_text(dump_json(candidate_payload) + "\n", encoding="utf-8")

        manifest = load_existing_manifest(manifest_path)
        if manifest is not None:
            manifest["candidate_frames"] = candidate_payload
            manifest_path.write_text(dump_json(manifest) + "\n", encoding="utf-8")

        print(f"[ok] 候选帧目录: {candidate_dir}")
        print(f"[ok] 联系表: {contact_sheet_path}")
        print(f"[ok] 候选清单: {candidate_json_path}")
        if manifest is not None:
            print(f"[ok] 已更新封面 manifest: {manifest_path}")
        return 0
    except CoverCandidateError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
