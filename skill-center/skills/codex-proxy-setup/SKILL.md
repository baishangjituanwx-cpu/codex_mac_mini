---
name: codex-proxy-setup
description: Diagnose and repair Codex stream/network failures by detecting the active local HTTP/HTTPS proxy on macOS or Windows, verifying the proxy endpoint, and updating Codex's global .env with HTTP_PROXY and HTTPS_PROXY. Use when Codex reports stream disconnected, reconnecting, error sending request, connection reset, or when the user asks to find the local proxy port and configure Codex.
---

# Codex Proxy Setup

Use this skill when Codex cannot maintain its response stream and a local HTTP/HTTPS proxy may be involved. The intended result is a working pair of uppercase `HTTP_PROXY` and `HTTPS_PROXY` variables in Codex's global environment file.

## Operating rules

- Inspect first; never invent a proxy address or port.
- Support macOS and Windows. Prefer the bundled script, which uses only Python's standard library plus native OS commands.
- Use `CODEX_HOME/.env` when `CODEX_HOME` is set; otherwise use `~/.codex/.env` (Windows: `%USERPROFILE%\.codex\.env`).
- Preserve all existing `.env` content and update only `HTTP_PROXY` and `HTTPS_PROXY`.
- Do not print proxy credentials or full authenticated URLs. Treat proxy URLs as sensitive.
- Do not configure `ALL_PROXY` or a SOCKS-only listener as an HTTP proxy. Use an HTTP listener such as the common Clash HTTP port when one is available.
- If no proxy is detected, do not create a guessed configuration. Report that the user must start/configure the proxy or provide an explicit endpoint.

## Standard workflow

1. Run the detector/writer:

   macOS/Linux:

   ```sh
   python3 <skill-dir>/scripts/configure_proxy.py
   ```

   Windows:

   ```powershell
   py -3 <skill-dir>\scripts\configure_proxy.py
   ```

   If `py` is unavailable, use `python`.

2. Let the script inspect, in order: explicit `HTTP_PROXY`/`HTTPS_PROXY` environment variables, macOS `scutil --proxy`, Windows user proxy settings, Windows WinHTTP settings, and the supplied manual override if present.

3. Prefer a detected candidate whose endpoint can be reached. A `401` or `403` response from `https://chatgpt.com/` still proves that the proxy route reached the server; it is not by itself a proxy failure.

4. The script writes the selected pair to Codex's global `.env`. Tell the user the exact path and values, redacting credentials if any.

5. Tell the user to fully quit and restart the Codex desktop app or IDE extension. Existing processes do not inherit newly written environment variables. Start a new task after restart.

## Useful modes

Use `--dry-run` to inspect and verify without writing:

```sh
python3 <skill-dir>/scripts/configure_proxy.py --dry-run
```

Use an explicit endpoint only when the user supplies or confirms it:

```sh
python3 <skill-dir>/scripts/configure_proxy.py --proxy http://127.0.0.1:7897
```

Separate endpoints are also supported with `--http-proxy` and `--https-proxy`.

## Failure handling

- If no candidate is found, explain that the system proxy is disabled or not discoverable and ask the user to start the proxy client or provide its HTTP port.
- If a candidate is detected but the probe fails, report the endpoint and verification error without exposing credentials; do not silently replace it with another guessed port. The script may still write the detected system configuration, but clearly label the verification as failed.
- If the same error continues after restart, check the proxy client logs, try another network, and inspect the Codex app logs. On macOS the usual app log directory is `~/Library/Logs/com.openai.codex/YYYY/MM/DD`; on Windows use the app's local log directory. Review logs for secrets before sharing them.

## Result summary

Report four facts concisely: operating system, detected proxy host/port, whether the endpoint probe succeeded, and the `.env` path written. End with the required restart step.
