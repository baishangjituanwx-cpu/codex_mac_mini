#!/usr/bin/env python3
"""Detect and configure Codex's HTTP/HTTPS proxy environment variables."""

from __future__ import annotations

import argparse
import os
import platform
import re
import socket
import subprocess
import sys
import shutil
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


@dataclass
class Candidate:
    source: str
    http: str
    https: str


def run_command(args: list[str]) -> str:
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            check=False,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return ""
    return (result.stdout or "") + (result.stderr or "")


def env_value(name: str) -> str:
    for key, value in os.environ.items():
        if key.lower() == name.lower() and value.strip():
            return value.strip()
    return ""


def normalize_proxy(value: str) -> str | None:
    value = value.strip().strip('"').strip("'")
    if not value or value.lower() in {"direct", "none", "off"}:
        return None
    if "://" not in value:
        value = "http://" + value
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname or not parsed.port:
        return None
    # Preserve credentials for the file, but never include them in display output.
    return urlunsplit((parsed.scheme.lower(), parsed.netloc, "", "", ""))


def pair_from_values(http_value: str, https_value: str, source: str) -> Candidate | None:
    http = normalize_proxy(http_value)
    https = normalize_proxy(https_value)
    if not http and not https:
        return None
    # A single detected system proxy normally serves both HTTP and HTTPS.
    http = http or https
    https = https or http
    if not http or not https:
        return None
    return Candidate(source, http, https)


def pair_from_proxy_spec(spec: str, source: str) -> Candidate | None:
    spec = spec.strip().strip('"').strip("'")
    mappings: dict[str, str] = {}
    if ";" in spec or re.search(r"(?:^|;)\s*(?:http|https|socks)=", spec, re.I):
        for item in spec.split(";"):
            if "=" in item:
                key, value = item.split("=", 1)
                mappings[key.strip().lower()] = value.strip()
    if mappings:
        return pair_from_values(mappings.get("http", ""), mappings.get("https", ""), source)
    return pair_from_values(spec, spec, source)


def detect_environment() -> Candidate | None:
    http = env_value("HTTP_PROXY") or env_value("http_proxy")
    https = env_value("HTTPS_PROXY") or env_value("https_proxy")
    return pair_from_values(http, https, "environment")


def detect_macos() -> Candidate | None:
    text = run_command(["scutil", "--proxy"])
    if not text:
        return None
    values: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z0-9]+)\s*:\s*(.*?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2)

    http = ""
    https = ""
    if values.get("HTTPEnable") == "1":
        http = f"{values.get('HTTPProxy', '')}:{values.get('HTTPPort', '')}"
    if values.get("HTTPSEnable") == "1":
        https = f"{values.get('HTTPSProxy', '')}:{values.get('HTTPSPort', '')}"
    return pair_from_values(http, https, "macOS system proxy")


def registry_value(name: str) -> str:
    key = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    text = run_command(["reg", "query", key, "/v", name])
    for line in text.splitlines():
        if re.search(rf"\b{re.escape(name)}\b", line, re.I):
            parts = re.split(r"\s+", line.strip(), maxsplit=2)
            if len(parts) == 3:
                return parts[2].strip()
    return ""


def detect_windows() -> list[Candidate]:
    candidates: list[Candidate] = []
    if registry_value("ProxyEnable").lower() in {"0x1", "1", "true"}:
        spec = registry_value("ProxyServer")
        candidate = pair_from_proxy_spec(spec, "Windows user proxy")
        if candidate:
            candidates.append(candidate)

    # WinHTTP output varies by Windows locale; search for an endpoint rather than a label.
    text = run_command(["netsh", "winhttp", "show", "proxy"])
    for line in text.splitlines():
        match = re.search(r"((?:https?://)?(?:\[[^\]]+\]|[A-Za-z0-9_.-]+):\d+)", line)
        if match:
            candidate = pair_from_proxy_spec(match.group(1), "Windows WinHTTP proxy")
            if candidate:
                candidates.append(candidate)
                break
    return candidates


def dedupe(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[tuple[str, str]] = set()
    result: list[Candidate] = []
    for candidate in candidates:
        key = (candidate.http, candidate.https)
        if key not in seen:
            seen.add(key)
            result.append(candidate)
    return result


def redacted(value: str) -> str:
    parsed = urlsplit(value)
    host = parsed.hostname or "?"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{host}{port}"


def local_port_open(proxy_url: str) -> bool | None:
    parsed = urlsplit(proxy_url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return None
    try:
        with socket.create_connection((parsed.hostname, parsed.port), timeout=2):
            return True
    except OSError:
        return False


def probe(candidate: Candidate) -> tuple[bool, str]:
    for value in (candidate.https, candidate.http):
        local = local_port_open(value)
        if local is False:
            return False, f"local proxy port is not listening ({redacted(value)})"

    # Prefer curl because it uses the platform trust store. Local proxy clients
    # often perform TLS inspection with a CA that Python's default bundle does
    # not know, which would otherwise produce a false negative.
    curl = shutil.which("curl")
    if curl:
        try:
            result = subprocess.run(
                [
                    curl,
                    "--proxy",
                    candidate.https,
                    "--connect-timeout",
                    "5",
                    "--max-time",
                    "12",
                    "--silent",
                    "--show-error",
                    "--output",
                    os.devnull,
                    "--write-out",
                    "%{http_code}",
                    "https://chatgpt.com/",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return False, type(error).__name__
        status = (result.stdout or "").strip()
        if result.returncode == 0 and re.fullmatch(r"[1-5]\d\d", status):
            return True, f"HTTP {status} (curl)"
        return False, "curl transport failure"

    # Fallback for minimal Windows installations without curl. This context is
    # used only for connectivity probing; it is not used by Codex itself.
    https_handler = urllib.request.HTTPSHandler(
        context=ssl._create_unverified_context()
    )
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": candidate.http, "https": candidate.https}),
        https_handler,
    )
    request = urllib.request.Request(
        "https://chatgpt.com/",
        headers={"User-Agent": "codex-proxy-setup/1.0"},
    )
    try:
        with opener.open(request, timeout=12) as response:
            return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        # The proxy route reached the service; auth/anti-bot responses are still connectivity success.
        return True, f"HTTP {error.code}"
    except Exception as error:  # noqa: BLE001 - report a bounded diagnostic to the agent
        return False, type(error).__name__


def env_path(override: str = "") -> Path:
    if override:
        return Path(override).expanduser()
    codex_home = env_value("CODEX_HOME")
    base = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return base / ".env"


def update_env_file(path: Path, http: str, https: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = original.splitlines(keepends=True)
    replacements = {"HTTP_PROXY": http, "HTTPS_PROXY": https}
    found: set[str] = set()
    pattern = re.compile(r"^(\s*(?:export\s+)?)(HTTP_PROXY|HTTPS_PROXY)(\s*=\s*).*$", re.I)
    updated: list[str] = []
    for line in lines:
        match = pattern.match(line.rstrip("\r\n"))
        if match:
            key = match.group(2).upper()
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            updated.append(f"{match.group(1)}{key}={replacements[key]}{newline}")
            found.add(key)
        else:
            updated.append(line)
    if updated and not updated[-1].endswith(("\n", "\r")):
        updated[-1] += "\n"
    for key in ("HTTP_PROXY", "HTTPS_PROXY"):
        if key not in found:
            updated.append(f"{key}={replacements[key]}\n")
    path.write_text("".join(updated), encoding="utf-8")
    if os.name != "nt":
        try:
            path.chmod(0o600)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="detect and verify without writing .env")
    parser.add_argument("--proxy", help="use one explicit HTTP proxy for both HTTP and HTTPS")
    parser.add_argument("--http-proxy", help="explicit HTTP proxy URL")
    parser.add_argument("--https-proxy", help="explicit HTTPS proxy URL")
    parser.add_argument("--env-file", help="override the Codex .env path")
    args = parser.parse_args()

    system = platform.system()
    candidates: list[Candidate] = []
    if args.proxy or args.http_proxy or args.https_proxy:
        candidate = pair_from_values(
            args.proxy or args.http_proxy or args.https_proxy or "",
            args.proxy or args.https_proxy or args.http_proxy or "",
            "explicit override",
        )
        if candidate:
            candidates.append(candidate)
    else:
        environment = detect_environment()
        if environment:
            candidates.append(environment)
        if system == "Darwin":
            macos = detect_macos()
            if macos:
                candidates.append(macos)
        elif system == "Windows":
            candidates.extend(detect_windows())

    candidates = dedupe(candidates)
    if not candidates:
        print(f"No HTTP/HTTPS proxy detected on {system}.")
        return 2

    selected = candidates[0]
    selected_probe = (False, "not tested")
    for candidate in candidates:
        result = probe(candidate)
        print(f"Detected {candidate.source}: {redacted(candidate.http)} / {redacted(candidate.https)} -> {result[1]}")
        if result[0] and not selected_probe[0]:
            selected, selected_probe = candidate, result
        elif selected is candidate:
            selected_probe = result

    destination = env_path(args.env_file)
    if args.dry_run:
        print(f"Dry run: would write {destination}")
        return 0 if selected_probe[0] else 3

    update_env_file(destination, selected.http, selected.https)
    print(f"Wrote {destination}")
    print(f"HTTP_PROXY={redacted(selected.http)}")
    print(f"HTTPS_PROXY={redacted(selected.https)}")
    if selected_probe[0]:
        print("Proxy verification succeeded; restart Codex for the variables to take effect.")
        return 0
    print(f"Proxy was detected and written, but verification failed: {selected_probe[1]}")
    return 3


if __name__ == "__main__":
    sys.exit(main())
