#!/usr/bin/env python3
"""Render final vertical and horizontal cover images from a selected still frame."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from typing import Any


RUNTIME_PYTHON_CANDIDATES = [
    pathlib.Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    pathlib.Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
]
FONT_CANDIDATES = [
    pathlib.Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    pathlib.Path("C:/Windows/Fonts/msyh.ttc"),
    pathlib.Path("C:/Windows/Fonts/msyhbd.ttc"),
    pathlib.Path("C:/Windows/Fonts/simhei.ttf"),
    pathlib.Path("C:/Windows/Fonts/simsun.ttc"),
    pathlib.Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    pathlib.Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
]


def ensure_pillow_runtime() -> None:
    try:
        import PIL  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    if os.environ.get("SEEDANCE_RENDER_BOOTSTRAPPED") == "1":
        return

    current = pathlib.Path(sys.executable).resolve()
    for candidate in RUNTIME_PYTHON_CANDIDATES:
        if candidate.exists() and candidate.resolve() != current:
            env = os.environ.copy()
            env["SEEDANCE_RENDER_BOOTSTRAPPED"] = "1"
            os.execve(str(candidate), [str(candidate), __file__, *sys.argv[1:]], env)


ensure_pillow_runtime()

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as exc:
    raise SystemExit("错误: 当前 Python 缺少 Pillow，且未找到 Codex bundled runtime。") from exc


VERTICAL_NAME = "cover-vertical-3x4.png"
HORIZONTAL_NAME = "cover-horizontal-4x3.png"
MANIFEST_NAME = "cover-manifest.json"
CANDIDATE_JSON_NAME = "cover-candidates.json"


class CoverRenderError(RuntimeError):
    """User-facing cover render error."""


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def validate_file(path: pathlib.Path) -> pathlib.Path:
    path = path.expanduser().resolve()
    if not path.exists():
        raise CoverRenderError(f"找不到文件: {path}")
    if not path.is_file():
        raise CoverRenderError(f"不是文件: {path}")
    return path


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CoverRenderError(f"找不到 JSON 文件: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CoverRenderError(f"JSON 解析失败: {path}\n{exc}") from exc
    if not isinstance(data, dict):
        raise CoverRenderError(f"JSON 顶层必须是 object: {path}")
    return data


def resolve_font_path(font_file: str | None) -> pathlib.Path:
    if font_file:
        return validate_file(pathlib.Path(font_file))
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise CoverRenderError("未找到可用中文字体，请通过 --font-file 传入字体文件路径。")


def load_titles(package_dir: pathlib.Path, args: argparse.Namespace) -> tuple[str, str]:
    if args.main_title and args.subtitle:
        return args.main_title.strip(), args.subtitle.strip()
    manifest = load_json(package_dir / MANIFEST_NAME)
    titles = manifest.get("titles")
    if not isinstance(titles, dict):
        raise CoverRenderError("manifest 中不存在 titles 字段，且未通过命令行传入标题。")
    main_title = args.main_title or titles.get("main_title")
    subtitle = args.subtitle or titles.get("subtitle")
    if not isinstance(main_title, str) or not main_title.strip():
        raise CoverRenderError("主标题缺失。")
    if not isinstance(subtitle, str) or not subtitle.strip():
        raise CoverRenderError("副标题缺失。")
    return main_title.strip(), subtitle.strip()


def choose_source_image(package_dir: pathlib.Path, args: argparse.Namespace) -> tuple[pathlib.Path, dict[str, Any] | None]:
    if args.image:
        return validate_file(pathlib.Path(args.image)), None

    frames = load_json(package_dir / CANDIDATE_JSON_NAME).get("frames")
    if not isinstance(frames, list) or not frames:
        raise CoverRenderError("候选帧列表为空，请先运行 extract_cover_candidates.py。")

    candidate_index = args.candidate_index or 1
    for item in frames:
        if isinstance(item, dict) and item.get("index") == candidate_index and isinstance(item.get("path"), str):
            return validate_file(pathlib.Path(item["path"])), item
    raise CoverRenderError(f"找不到候选帧索引: {candidate_index}")


def maybe_warn(label: str, text: str, min_len: int, max_len: int) -> None:
    size = len(text.strip())
    if size < min_len or size > max_len:
        print(f"[warn] {label} 当前长度为 {size}，建议控制在 {min_len}-{max_len} 个字符。", file=sys.stderr)


def title_size(length: int, large: int, medium: int, small: int) -> int:
    if length <= 8:
        return large
    if length <= 10:
        return medium
    return small


def load_font(font_path: pathlib.Path, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(font_path), size=size)
    except OSError as exc:
        raise CoverRenderError(f"字体加载失败: {font_path}") from exc


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: pathlib.Path,
    initial_size: int,
    min_size: int,
    max_width: int,
    stroke_width: int,
) -> ImageFont.FreeTypeFont:
    size = initial_size
    while size >= min_size:
        font = load_font(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 2
    return load_font(font_path, min_size)


def crop_cover_image(source: Image.Image, *, target_w: int, target_h: int, crop_y_bias: float) -> Image.Image:
    src_w, src_h = source.size
    if src_w <= 0 or src_h <= 0:
        raise CoverRenderError("源图片尺寸异常。")

    target_ratio = target_w / target_h
    src_ratio = src_w / src_h
    if src_ratio > target_ratio:
        crop_h = src_h
        crop_w = min(int(round(crop_h * target_ratio)), src_w)
        left = max(0, (src_w - crop_w) // 2)
        top = 0
    else:
        crop_w = src_w
        crop_h = min(int(round(crop_w / target_ratio)), src_h)
        extra_h = max(0, src_h - crop_h)
        left = 0
        top = min(max(int(round(extra_h * crop_y_bias)), 0), extra_h)

    return source.crop((left, top, left + crop_w, top + crop_h)).resize((target_w, target_h), Image.Resampling.LANCZOS)


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    *,
    text: str,
    center_x: float,
    center_y: float,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    stroke_fill: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
    shadow_offset: tuple[int, int] = (0, 4),
    shadow_fill: tuple[int, int, int, int] = (0, 0, 0, 86),
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = center_x - ((bbox[2] - bbox[0]) / 2)
    y = center_y - ((bbox[3] - bbox[1]) / 2)
    if shadow_fill[3] > 0:
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_fill)
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def render_cover(
    source: Image.Image,
    *,
    target_w: int,
    target_h: int,
    crop_y_bias: float,
    font_path: pathlib.Path,
    main_title: str,
    subtitle: str,
    tag: str | None,
    main_font_size: int,
    subtitle_font_size: int,
    tag_font_size: int,
    output_path: pathlib.Path,
) -> None:
    canvas = crop_cover_image(source, target_w=target_w, target_h=target_h, crop_y_bias=crop_y_bias).convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    band_y = int(round(target_h * 0.70))
    draw.rectangle((0, band_y, target_w, target_h), fill=(0, 0, 0, 144))

    main_stroke = 6 if main_font_size >= 90 else 5
    subtitle_stroke = 3
    main_font = fit_font(draw, main_title, font_path, main_font_size, max(54, main_font_size - 30), target_w - 140, main_stroke)
    subtitle_font = fit_font(draw, subtitle, font_path, subtitle_font_size, max(28, subtitle_font_size - 18), target_w - 180, subtitle_stroke)

    if tag:
        tag_font = fit_font(draw, tag, font_path, tag_font_size, max(20, tag_font_size - 10), 240, 0)
        tag_bbox = draw.textbbox((0, 0), tag, font=tag_font)
        tag_w = max(180, min(320, (tag_bbox[2] - tag_bbox[0]) + 56))
        tag_h = max(62, (tag_bbox[3] - tag_bbox[1]) + 32)
        tag_x = 70
        tag_y = int(round(target_h * 0.725))
        draw.rounded_rectangle((tag_x, tag_y, tag_x + tag_w, tag_y + tag_h), radius=20, fill=(233, 138, 41, 247))
        draw_centered_text(draw, text=tag, center_x=tag_x + (tag_w / 2), center_y=tag_y + (tag_h / 2), font=tag_font, fill=(255, 255, 255, 255), shadow_fill=(0, 0, 0, 0))

    draw_centered_text(draw, text=main_title, center_x=target_w / 2, center_y=target_h * 0.772, font=main_font, fill=(255, 255, 255, 255), stroke_fill=(0, 0, 0, 148), stroke_width=main_stroke, shadow_offset=(0, 6), shadow_fill=(0, 0, 0, 76))
    draw_centered_text(draw, text=subtitle, center_x=target_w / 2, center_y=target_h * 0.853, font=subtitle_font, fill=(229, 195, 107, 255), stroke_fill=(0, 0, 0, 114), stroke_width=subtitle_stroke, shadow_offset=(0, 3), shadow_fill=(0, 0, 0, 52))

    final_image = Image.alpha_composite(canvas, overlay).convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_image.save(output_path, format="PNG")


def update_manifest(package_dir: pathlib.Path, source_image: pathlib.Path, source_candidate: dict[str, Any] | None, main_title: str, subtitle: str, tag: str | None) -> None:
    manifest_path = package_dir / MANIFEST_NAME
    if not manifest_path.exists():
        return
    manifest = load_json(manifest_path)
    manifest["selected_cover_source"] = {"image_path": str(source_image), "candidate": source_candidate}
    manifest["rendered_covers"] = {
        "vertical": str(package_dir / VERTICAL_NAME),
        "horizontal": str(package_dir / HORIZONTAL_NAME),
        "main_title": main_title,
        "subtitle": subtitle,
        "tag": tag,
        "renderer": "pillow",
    }
    manifest_path.write_text(dump_json(manifest) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据候选帧或指定截图生成最终封面 PNG。")
    parser.add_argument("--package-dir", required=True, help="封面包目录，包含 manifest 或候选帧信息。")
    parser.add_argument("--image", help="直接指定截图路径。与 --candidate-index 二选一。")
    parser.add_argument("--candidate-index", type=int, help="使用候选帧索引。默认 1。")
    parser.add_argument("--main-title", help="封面主标题。默认从 manifest 读取。")
    parser.add_argument("--subtitle", help="封面副标题。默认从 manifest 读取。")
    parser.add_argument("--tag", help="可选的小橙色标签文字。")
    parser.add_argument("--font-file", help="中文字体文件路径。默认自动探测 macOS / Windows 常见字体。")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.image and args.candidate_index:
            raise CoverRenderError("--image 和 --candidate-index 不能同时使用。")

        package_dir = pathlib.Path(args.package_dir).expanduser().resolve()
        package_dir.mkdir(parents=True, exist_ok=True)
        font_path = resolve_font_path(args.font_file)
        source_image_path, source_candidate = choose_source_image(package_dir, args)
        main_title, subtitle = load_titles(package_dir, args)
        maybe_warn("主标题", main_title, 6, 10)
        maybe_warn("副标题", subtitle, 4, 8)

        with Image.open(source_image_path) as source:
            source = source.convert("RGB")
            render_cover(source, target_w=1080, target_h=1440, crop_y_bias=0.18, font_path=font_path, main_title=main_title, subtitle=subtitle, tag=args.tag, main_font_size=title_size(len(main_title), 112, 98, 90), subtitle_font_size=title_size(len(subtitle), 56, 52, 48), tag_font_size=30, output_path=package_dir / VERTICAL_NAME)
            render_cover(source, target_w=1440, target_h=1080, crop_y_bias=0.12, font_path=font_path, main_title=main_title, subtitle=subtitle, tag=args.tag, main_font_size=title_size(len(main_title), 96, 88, 80), subtitle_font_size=title_size(len(subtitle), 48, 44, 40), tag_font_size=28, output_path=package_dir / HORIZONTAL_NAME)

        update_manifest(package_dir, source_image_path, source_candidate, main_title, subtitle, args.tag)
        print(f"[ok] 竖版封面: {package_dir / VERTICAL_NAME}")
        print(f"[ok] 横版封面: {package_dir / HORIZONTAL_NAME}")
        print(f"[ok] 使用字体: {font_path}")
        return 0
    except CoverRenderError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断。", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
