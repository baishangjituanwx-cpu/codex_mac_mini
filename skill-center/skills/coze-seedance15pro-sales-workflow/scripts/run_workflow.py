#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Config file not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def keychain_pat(service: str) -> str | None:
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", ""), "-s", service, "-w"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    token = result.stdout.strip()
    return token or None


def resolve_pat(config: dict[str, Any]) -> tuple[str, str]:
    env_var = config.get("pat_env_var")
    if env_var:
        token = os.environ.get(env_var)
        if token:
            return token, f"env:{env_var}"

    service = config.get("pat_keychain_service")
    if service:
        token = keychain_pat(service)
        if token:
            return token, f"keychain:{service}"

    raise SystemExit(
        "PAT not configured. Set the configured environment variable or store the token in macOS Keychain."
    )


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def extract_video_url(data: Any) -> str | None:
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return data if data.startswith(("http://", "https://")) else None
        return extract_video_url(parsed)

    if isinstance(data, dict):
        for key in ("video", "video_url", "url", "output", "result"):
            value = data.get(key)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value
            if isinstance(value, (dict, list)):
                nested = extract_video_url(value)
                if nested:
                    return nested
        for value in data.values():
            nested = extract_video_url(value)
            if nested:
                return nested

    if isinstance(data, list):
        for item in data:
            nested = extract_video_url(item)
            if nested:
                return nested

    return None


def api_request(
    url: str,
    token: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Coze API HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error calling Coze API: {exc.reason}") from exc


def ensure_success(response: dict[str, Any]) -> dict[str, Any]:
    if response.get("code") != 0:
        raise SystemExit(f"Coze API error: {response.get('code')} - {response.get('msg')}")
    return response


def extract_execute_id(response: dict[str, Any]) -> str | None:
    value = response.get("execute_id")
    if isinstance(value, str) and value:
        return value
    data = response.get("data")
    if isinstance(data, dict):
        nested = data.get("execute_id")
        if isinstance(nested, str) and nested:
            return nested
    return None


def poll_history(
    base_url: str,
    token: str,
    workflow_id: str,
    execute_id: str,
    timeout: int,
    poll_interval: float,
    max_wait: float,
) -> dict[str, Any] | None:
    history_url = f"{base_url}/v1/workflows/{urllib.parse.quote(workflow_id)}/run_histories/{urllib.parse.quote(execute_id)}"
    deadline = time.monotonic() + max_wait
    latest: dict[str, Any] | None = None

    while True:
        response = ensure_success(api_request(history_url, token, method="GET", timeout=timeout))
        histories = response.get("data")
        if isinstance(histories, list) and histories:
            latest = histories[0]
            if latest.get("execute_status") != "Running":
                return latest
        if time.monotonic() >= deadline:
            return latest
        time.sleep(poll_interval)


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=120) as response, output_path.open("wb") as fh:
            fh.write(response.read())
    except urllib.error.URLError as exc:
        raise SystemExit(f"Failed to download video: {exc.reason}") from exc


def print_config(config: dict[str, Any]) -> None:
    token_source = "missing"
    try:
        _, token_source = resolve_pat(config)
    except SystemExit:
        pass

    payload = {
        "config_path": str(CONFIG_PATH),
        "workflow_id": config.get("workflow_id"),
        "coze_base_url": config.get("coze_base_url"),
        "pat_env_var": config.get("pat_env_var"),
        "pat_keychain_service": config.get("pat_keychain_service"),
        "default_output_dir": config.get("default_output_dir"),
        "pat_source": token_source,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the configured Coze Seedance workflow.")
    parser.add_argument("--prompt", help="Prompt to pass into the workflow.")
    parser.add_argument("--image-url", help="Optional image URL for image-to-video mode.")
    parser.add_argument("--bot-id", help="Optional Coze bot ID when the workflow is bound to a bot context.")
    parser.add_argument("--duration", type=float, default=5, help="Video duration in seconds.")
    parser.add_argument("--ratio", default="16:9", help="Aspect ratio, for example 16:9 or 9:16.")
    parser.add_argument("--resolution", default="720p", help="Resolution, for example 480p, 720p, or 1080p.")
    parser.add_argument(
        "--generate-audio",
        type=parse_bool,
        default=True,
        help="Whether to generate audio. Accepts true/false.",
    )
    parser.add_argument(
        "--async",
        action="store_true",
        dest="is_async",
        help="Use Coze asynchronous workflow execution and poll run history until completion.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=5.0,
        help="Seconds between async history polls.",
    )
    parser.add_argument(
        "--max-wait",
        type=float,
        default=900.0,
        help="Maximum seconds to wait for async history polling before returning the latest status.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=300,
        help="HTTP timeout in seconds for each Coze API request.",
    )
    parser.add_argument("--output-dir", help="Directory for downloaded video output.")
    parser.add_argument("--skip-download", action="store_true", help="Do not download the returned video URL.")
    parser.add_argument("--print-config", action="store_true", help="Print runtime configuration without secrets.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()

    if args.print_config:
        print_config(config)
        return

    if not args.prompt:
        parser.error("--prompt is required unless --print-config is used")

    token, token_source = resolve_pat(config)
    workflow_id = config["workflow_id"]
    base_url = config["coze_base_url"].rstrip("/")
    request_url = f"{base_url}/v1/workflow/run"

    parameters: dict[str, Any] = {
        "prompt": args.prompt,
        "duration": args.duration,
        "ratio": args.ratio,
        "resolution": args.resolution,
        "generate_audio": args.generate_audio,
    }
    if args.image_url:
        parameters["image_url"] = args.image_url

    request_payload: dict[str, Any] = {
        "workflow_id": workflow_id,
        "parameters": parameters,
    }
    if args.bot_id:
        request_payload["bot_id"] = args.bot_id
    if args.is_async:
        request_payload["is_async"] = True

    response = ensure_success(
        api_request(
            request_url,
            token,
            method="POST",
            payload=request_payload,
            timeout=args.request_timeout,
        )
    )

    execute_id = extract_execute_id(response)
    data = response.get("data")
    video_url = extract_video_url(data)
    history_entry: dict[str, Any] | None = None

    if args.is_async and execute_id:
        history_entry = poll_history(
            base_url=base_url,
            token=token,
            workflow_id=workflow_id,
            execute_id=execute_id,
            timeout=args.request_timeout,
            poll_interval=args.poll_interval,
            max_wait=args.max_wait,
        )
        if history_entry:
            history_output = history_entry.get("output")
            polled_video_url = extract_video_url(history_output)
            if polled_video_url:
                video_url = polled_video_url

    result: dict[str, Any] = {
        "workflow_id": workflow_id,
        "pat_source": token_source,
        "request_parameters": parameters,
        "request_options": {
            "bot_id": args.bot_id,
            "is_async": args.is_async,
            "poll_interval": args.poll_interval if args.is_async else None,
            "max_wait": args.max_wait if args.is_async else None,
        },
        "response_code": response.get("code"),
        "response_msg": response.get("msg"),
        "execute_id": execute_id,
        "debug_url": response.get("debug_url"),
        "token_usage": response.get("token"),
        "cost": response.get("cost"),
        "video_url": video_url,
    }

    if history_entry:
        result["history"] = {
            "execute_status": history_entry.get("execute_status"),
            "error_code": history_entry.get("error_code"),
            "error_message": history_entry.get("error_message"),
            "debug_url": history_entry.get("debug_url"),
            "update_time": history_entry.get("update_time"),
        }

    if video_url and not args.skip_download:
        output_dir = Path(args.output_dir or config.get("default_output_dir") or str(Path.home() / "Downloads"))
        filename = f"coze_video_{workflow_id}_{os.getpid()}.mp4"
        output_path = output_dir / filename
        download_file(video_url, output_path)
        result["downloaded_to"] = str(output_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
