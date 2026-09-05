#!/usr/bin/env python3
"""Direct API CLI for Volcengine Ark Seedance video generation tasks."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "expired"}
DEFAULT_TIMEOUT_SECONDS = 30 * 60
DEFAULT_POLL_INTERVAL_SECONDS = 10


class SeedanceCLIError(RuntimeError):
    """User-facing CLI error."""


def stderr(message: str) -> None:
    print(message, file=sys.stderr)


def load_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SeedanceCLIError(f"找不到文件: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SeedanceCLIError(f"JSON 解析失败: {path}\n{exc}") from exc


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False)


def require_api_key(args: argparse.Namespace) -> str:
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise SeedanceCLIError(
            "未找到 API Key。请先在本地环境中设置 ARK_API_KEY，再执行命令。"
        )
    return api_key


def resolve_base_url(args: argparse.Namespace) -> str:
    return (args.base_url or os.getenv("ARK_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")


def is_probable_local_reference(value: str) -> bool:
    if value.startswith("local://"):
        return True
    if value.startswith(("http://", "https://", "asset://", "data:")):
        return False
    return os.path.exists(value)


def resolve_local_path(value: str, payload_dir: pathlib.Path) -> pathlib.Path:
    raw = value[len("local://") :] if value.startswith("local://") else value
    path = pathlib.Path(raw).expanduser()
    if not path.is_absolute():
        path = payload_dir / path
    return path.resolve()


def encode_file_as_data_uri(path: pathlib.Path, expected_group: str) -> str:
    if not path.exists():
        raise SeedanceCLIError(f"本地文件不存在: {path}")
    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        raise SeedanceCLIError(f"无法根据扩展名判断 MIME 类型: {path}")
    if not mime_type.startswith(f"{expected_group}/"):
        raise SeedanceCLIError(
            f"文件类型不匹配，期望 {expected_group} 文件，实际为 {mime_type}: {path}"
        )
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def resolve_url_value(field_type: str, value: str, payload_dir: pathlib.Path) -> str:
    if not is_probable_local_reference(value):
        return value

    path = resolve_local_path(value, payload_dir)
    if field_type == "image_url":
        return encode_file_as_data_uri(path, "image")
    if field_type == "audio_url":
        return encode_file_as_data_uri(path, "audio")
    if field_type == "video_url":
        raise SeedanceCLIError(
            "官方文档中 video_url.url 仅支持公网 URL 或 asset:// 素材 ID；"
            f"当前检测到本地视频文件 {path}，请先上传到可访问 URL 或素材库。"
        )
    return value


def resolve_local_refs(payload: Any, payload_dir: pathlib.Path) -> Any:
    if isinstance(payload, list):
        return [resolve_local_refs(item, payload_dir) for item in payload]
    if not isinstance(payload, dict):
        return payload

    resolved = dict(payload)
    item_type = resolved.get("type")

    if item_type in {"image_url", "video_url", "audio_url"}:
        key = item_type
        nested = resolved.get(key)
        if isinstance(nested, dict) and isinstance(nested.get("url"), str):
            nested = dict(nested)
            nested["url"] = resolve_url_value(item_type, nested["url"], payload_dir)
            resolved[key] = nested

    for key, value in list(resolved.items()):
        if key not in {"image_url", "video_url", "audio_url"}:
            resolved[key] = resolve_local_refs(value, payload_dir)

    return resolved


def validate_and_normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise SeedanceCLIError("payload 顶层必须是 JSON object。")
    if not isinstance(payload.get("model"), str) or not payload["model"].strip():
        raise SeedanceCLIError("payload.model 必填，且必须是字符串。")

    content = payload.get("content")
    if not isinstance(content, list) or not content:
        raise SeedanceCLIError("payload.content 必填，且必须是非空数组。")

    normalized_items: list[dict[str, Any]] = []
    image_items: list[dict[str, Any]] = []
    has_text = False
    has_video = False
    has_audio = False

    for item in content:
        if not isinstance(item, dict):
            raise SeedanceCLIError("payload.content 的每一项都必须是 object。")
        item_type = item.get("type")
        if not isinstance(item_type, str):
            raise SeedanceCLIError("payload.content[].type 必填，且必须是字符串。")

        normalized = dict(item)

        if item_type == "text":
            text = normalized.get("text")
            if not isinstance(text, str) or not text.strip():
                raise SeedanceCLIError("text 类型内容必须提供非空 content[].text。")
            has_text = True
        elif item_type == "image_url":
            image = normalized.get("image_url")
            if not isinstance(image, dict) or not isinstance(image.get("url"), str):
                raise SeedanceCLIError("image_url 类型内容必须提供 content[].image_url.url。")
            image_items.append(normalized)
        elif item_type == "video_url":
            video = normalized.get("video_url")
            if not isinstance(video, dict) or not isinstance(video.get("url"), str):
                raise SeedanceCLIError("video_url 类型内容必须提供 content[].video_url.url。")
            normalized.setdefault("role", "reference_video")
            has_video = True
        elif item_type == "audio_url":
            audio = normalized.get("audio_url")
            if not isinstance(audio, dict) or not isinstance(audio.get("url"), str):
                raise SeedanceCLIError("audio_url 类型内容必须提供 content[].audio_url.url。")
            normalized.setdefault("role", "reference_audio")
            has_audio = True
        elif item_type == "draft_task":
            draft_task = normalized.get("draft_task")
            if not isinstance(draft_task, dict) or not isinstance(draft_task.get("id"), str):
                raise SeedanceCLIError("draft_task 类型内容必须提供 content[].draft_task.id。")
        else:
            raise SeedanceCLIError(f"暂不支持的 content.type: {item_type}")

        normalized_items.append(normalized)

    if image_items:
        image_roles = [item.get("role") for item in image_items if item.get("role") is not None]
        if image_roles and len(image_roles) != len(image_items):
            raise SeedanceCLIError("图片输入的 role 不能只填一部分；要么全填，要么按默认规则自动补全。")
        if not image_roles:
            if len(image_items) == 1:
                image_items[0]["role"] = "first_frame"
            else:
                for item in image_items:
                    item["role"] = "reference_image"
            image_roles = [item["role"] for item in image_items]

        frame_roles = {"first_frame", "last_frame"}
        reference_roles = {"reference_image"}
        used_frame_roles = {role for role in image_roles if role in frame_roles}
        used_reference_roles = {role for role in image_roles if role in reference_roles}

        if used_frame_roles and used_reference_roles:
            raise SeedanceCLIError("官方文档要求首尾帧图片与多模态参考图片互斥，不能混用。")
        if used_frame_roles and (has_video or has_audio):
            raise SeedanceCLIError("官方文档要求首尾帧场景不能与参考视频/参考音频混用。")

    if not has_text and not image_items and not has_video and not has_audio:
        raise SeedanceCLIError("content 至少要包含文本、图片、视频或音频中的一种输入。")
    if has_audio and not (image_items or has_video):
        raise SeedanceCLIError("官方文档要求音频不能单独输入，至少同时包含 1 个图片或视频输入。")

    payload = dict(payload)
    payload["content"] = normalized_items
    return payload


def api_request(
    *,
    method: str,
    path: str,
    api_key: str,
    base_url: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    url = f"{base_url}{path}"
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    if payload is not None:
        data = dump_json(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw)
            detail = dump_json(error_payload)
        except json.JSONDecodeError:
            detail = raw
        raise SeedanceCLIError(f"HTTP {exc.code} 调用失败:\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise SeedanceCLIError(f"网络请求失败: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SeedanceCLIError(f"接口返回了非 JSON 数据:\n{raw}") from exc


def fetch_task(task_id: str, api_key: str, base_url: str) -> dict[str, Any]:
    task_id = urllib.parse.quote(task_id, safe="")
    result = api_request(
        method="GET",
        path=f"/contents/generations/tasks/{task_id}",
        api_key=api_key,
        base_url=base_url,
    )
    if not isinstance(result, dict):
        raise SeedanceCLIError("查询任务接口返回格式异常，预期为 JSON object。")
    return result


def wait_for_task(
    task_id: str,
    api_key: str,
    base_url: str,
    timeout_seconds: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    last_status = None

    while True:
        task = fetch_task(task_id, api_key, base_url)
        status = task.get("status")
        if status != last_status:
            stderr(f"[wait] 任务 {task_id} 当前状态: {status}")
            last_status = status
        if status in TERMINAL_STATUSES:
            return task
        if time.time() >= deadline:
            raise SeedanceCLIError(
                f"等待任务超时（>{timeout_seconds}s），最后状态为: {status}"
            )
        time.sleep(poll_interval_seconds)


def save_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(data) + "\n", encoding="utf-8")


def download_url(url: str, output_path: pathlib.Path) -> pathlib.Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            with output_path.open("wb") as file_obj:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    file_obj.write(chunk)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SeedanceCLIError(f"下载失败，HTTP {exc.code}:\n{body}") from exc
    except urllib.error.URLError as exc:
        raise SeedanceCLIError(f"下载失败: {exc}") from exc
    return output_path


def download_from_task(task: dict[str, Any], output_path: pathlib.Path, use_last_frame: bool) -> pathlib.Path:
    content = task.get("content")
    if not isinstance(content, dict):
        raise SeedanceCLIError("任务结果中不存在 content 字段，无法下载。")

    key = "last_frame_url" if use_last_frame else "video_url"
    asset_url = content.get(key)
    if not isinstance(asset_url, str) or not asset_url:
        raise SeedanceCLIError(f"任务结果中不存在可下载的 {key}。")
    return download_url(asset_url, output_path)


def handle_submit(args: argparse.Namespace) -> int:
    payload_path = pathlib.Path(args.payload).resolve()
    payload = load_json(payload_path)
    payload = resolve_local_refs(payload, payload_path.parent)
    payload = validate_and_normalize_payload(payload)

    if args.dry_run:
        print(dump_json(payload))
        return 0

    api_key = require_api_key(args)
    base_url = resolve_base_url(args)
    response = api_request(
        method="POST",
        path="/contents/generations/tasks",
        api_key=api_key,
        base_url=base_url,
        payload=payload,
    )
    if args.save_response:
        save_json(pathlib.Path(args.save_response).resolve(), response)
    print(dump_json(response))

    if not args.wait:
        return 0

    task_id = response.get("id")
    if not isinstance(task_id, str) or not task_id:
        raise SeedanceCLIError("创建成功后未拿到任务 ID，无法继续 wait。")

    task = wait_for_task(
        task_id=task_id,
        api_key=api_key,
        base_url=base_url,
        timeout_seconds=args.timeout,
        poll_interval_seconds=args.interval,
    )

    if args.save_task:
        save_json(pathlib.Path(args.save_task).resolve(), task)

    if args.download:
        output = pathlib.Path(args.download).resolve()
        output = download_from_task(task, output, use_last_frame=False)
        stderr(f"[download] 已保存视频到: {output}")

    print(dump_json(task))
    return 0


def handle_get(args: argparse.Namespace) -> int:
    api_key = require_api_key(args)
    base_url = resolve_base_url(args)
    task = fetch_task(args.task_id, api_key, base_url)
    if args.save_response:
        save_json(pathlib.Path(args.save_response).resolve(), task)
    print(dump_json(task))
    return 0


def handle_wait(args: argparse.Namespace) -> int:
    api_key = require_api_key(args)
    base_url = resolve_base_url(args)
    task = wait_for_task(
        task_id=args.task_id,
        api_key=api_key,
        base_url=base_url,
        timeout_seconds=args.timeout,
        poll_interval_seconds=args.interval,
    )
    if args.save_response:
        save_json(pathlib.Path(args.save_response).resolve(), task)
    if args.download:
        output = pathlib.Path(args.download).resolve()
        output = download_from_task(task, output, use_last_frame=False)
        stderr(f"[download] 已保存视频到: {output}")
    print(dump_json(task))
    return 0


def handle_download(args: argparse.Namespace) -> int:
    api_key = require_api_key(args)
    base_url = resolve_base_url(args)
    task = fetch_task(args.task_id, api_key, base_url)
    output = pathlib.Path(args.output).resolve()
    output = download_from_task(task, output, use_last_frame=args.last_frame)
    stderr(f"[download] 已保存文件到: {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Direct API CLI for Seedance 2.0 / 2.0 Fast on Volcengine Ark."
    )
    parser.add_argument(
        "--base-url",
        help=f"Ark 数据面 Base URL。默认读取 ARK_BASE_URL 或 {DEFAULT_BASE_URL}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    submit = subparsers.add_parser("submit", help="创建视频生成任务。")
    submit.add_argument("--payload", required=True, help="请求体 JSON 文件路径。")
    submit.add_argument("--dry-run", action="store_true", help="只解析并打印最终请求体，不发请求。")
    submit.add_argument("--save-response", help="把创建任务接口返回值保存到 JSON 文件。")
    submit.add_argument("--wait", action="store_true", help="创建任务后继续轮询直到结束。")
    submit.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="wait 最大等待秒数。")
    submit.add_argument("--interval", type=int, default=DEFAULT_POLL_INTERVAL_SECONDS, help="wait 轮询间隔秒数。")
    submit.add_argument("--save-task", help="wait 结束后，把最终任务结果保存到 JSON 文件。")
    submit.add_argument("--download", help="wait 成功后，把 video_url 下载到指定路径。")
    submit.set_defaults(handler=handle_submit)

    get_cmd = subparsers.add_parser("get", help="查询单个任务。")
    get_cmd.add_argument("task_id", help="任务 ID，例如 cgt-xxxx。")
    get_cmd.add_argument("--save-response", help="把查询结果保存到 JSON 文件。")
    get_cmd.set_defaults(handler=handle_get)

    wait_cmd = subparsers.add_parser("wait", help="轮询等待任务直到结束。")
    wait_cmd.add_argument("task_id", help="任务 ID，例如 cgt-xxxx。")
    wait_cmd.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="最大等待秒数。")
    wait_cmd.add_argument("--interval", type=int, default=DEFAULT_POLL_INTERVAL_SECONDS, help="轮询间隔秒数。")
    wait_cmd.add_argument("--save-response", help="把最终任务结果保存到 JSON 文件。")
    wait_cmd.add_argument("--download", help="任务成功后，把 video_url 下载到指定路径。")
    wait_cmd.set_defaults(handler=handle_wait)

    download = subparsers.add_parser("download", help="根据任务结果下载视频或尾帧。")
    download.add_argument("task_id", help="任务 ID，例如 cgt-xxxx。")
    download.add_argument("--output", required=True, help="输出文件路径。")
    download.add_argument("--last-frame", action="store_true", help="下载 last_frame_url，而不是 video_url。")
    download.set_defaults(handler=handle_download)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except SeedanceCLIError as exc:
        stderr(f"错误: {exc}")
        return 1
    except KeyboardInterrupt:
        stderr("已中断。")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
