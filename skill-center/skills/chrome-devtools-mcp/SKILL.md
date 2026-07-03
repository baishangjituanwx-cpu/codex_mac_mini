---
name: chrome-devtools-mcp
description: Use ChromeDevTools/chrome-devtools-mcp for browser automation, page inspection, screenshots, console/network debugging, performance analysis, and logged-in web app workflows. Trigger when the user says chrome-devtools MCP, ChromeDevTools/chrome-devtools-mcp, DevTools MCP, mcp__chrome_devtools, or asks to use this independent Chrome DevTools MCP instead of Codex's built-in browser/chrome/computer-use plugins.
---

# Chrome DevTools MCP

## Core Rule

Use the `mcp__chrome_devtools` tool namespace as the primary browser surface. Do not switch to Codex built-in `browser`, built-in `chrome`, `node_repl` browser clients, Playwright outside this MCP, or `computer-use` unless the user explicitly requests a fallback.

If `mcp__chrome_devtools` tools are not visible, call `tool_search` for `chrome-devtools mcp`. If still unavailable, tell the user the MCP is not loaded and suggest restarting Codex or opening a new thread after confirming the MCP server is configured.

## Basic Workflow

1. Start with `list_pages`.
2. Use `new_page` or `navigate_page` for the requested URL.
3. Use `take_snapshot` first for page structure and element `uid`s.
4. Use `take_screenshot` when visual state matters, especially canvas, CAPTCHA, dense tables, or loading spinners.
5. Use `evaluate_script` for bounded, read-only DOM inspection or page-state extraction when snapshots are too noisy.
6. Use `list_console_messages` and `list_network_requests` for debugging stalled pages, failed API calls, or frontend errors.
7. Use `get_network_request` only after identifying a specific request id.

Keep one selected page current with `select_page` when multiple tabs exist. Close temporary diagnostic tabs when done.

## Interaction Rules

Prefer:

- `fill_form` for multiple form fields.
- `fill` for one input.
- `click` only on current snapshot `uid`s.
- `press_key` for keyboard shortcuts, Escape, Enter, or reload recovery.
- `drag` only for normal element-to-element drag/drop. It may not satisfy sites that require true pointer movement.

Before mutating business data, confirm at action time. This includes price changes, stock changes, title edits, product publish/unpublish, deletions, account settings, permissions, uploads, financial actions, and submissions that affect third parties.

Read-only navigation, filtering, screenshots, console/network inspection, and table extraction are okay without extra confirmation when they directly follow the user's request.

For login, CAPTCHA, passwords, OTPs, QR confirmations, or security checks: stop and ask the user to complete the step or give narrow explicit authorization for that current challenge. Do not invent credentials or bypass security controls.

## Windows Repo Mirror Notes

This skill does not need a separate Windows PowerShell or `.cmd` launcher. The Windows-usable equivalent is the same `mcp__chrome_devtools` tool namespace inside Codex, so the repo mirror stays shared instead of forking shell wrappers.

When a workflow requires browser shortcuts through `press_key`, translate common macOS habits to Windows equivalents:

- use `Control+R` or `F5` instead of `Meta+R`
- use `Control+L` instead of `Meta+L`
- use `Control+A` instead of `Meta+A`
- use `Alt+Left` and `Alt+Right` for browser back/forward

If this mirror is synced onto a Windows machine, the user-scoped install path is typically `%USERPROFILE%\\.codex\\skills\\chrome-devtools-mcp\\`. Keep paths quoted when they contain spaces, but do not rewrite the MCP workflow into local shell automation.

## Debugging Loading Problems

When a page is stuck on loading:

1. Check `document.readyState`, main text, iframes, and visible candidate controls with `evaluate_script`.
2. Check console errors with `list_console_messages`.
3. Check document/script/stylesheet and fetch/xhr requests separately with `list_network_requests`.
4. Identify pending or failed critical chunks with `get_network_request`.
5. Test whether the same URL can load from the browser page with a short `fetch` in `evaluate_script`.

Use `Escape` to stop a hung load before retrying. Prefer opening a clean new tab over repeatedly reloading a poisoned tab.

## Pinduoduo MMS Notes

For `mms.pinduoduo.com` merchant backend work:

- First verify login state with `list_pages`, current URL, and `take_snapshot`.
- The goods list page may show a persistent spinner if dynamic chunks from `https://mms-static.pddpic.com/` hang.
- Test the same static asset on `https://mms-static-2.pddpic.com/`. If it succeeds, retry navigation with an `initScript` that rewrites static script/link URLs from `mms-static.pddpic.com` to `mms-static-2.pddpic.com`.

Compact fallback `initScript`:

```js
(() => {
  const rewrite = (v) =>
    typeof v === "string"
      ? v.replace("https://mms-static.pddpic.com/", "https://mms-static-2.pddpic.com/")
      : v;
  const patchUrlProp = (proto, prop) => {
    const d = Object.getOwnPropertyDescriptor(proto, prop);
    if (!d?.set || !d?.get) return;
    Object.defineProperty(proto, prop, {
      configurable: true,
      enumerable: d.enumerable,
      get: d.get,
      set(value) {
        return d.set.call(this, rewrite(value));
      },
    });
  };
  patchUrlProp(HTMLScriptElement.prototype, "src");
  patchUrlProp(HTMLLinkElement.prototype, "href");
  const origSetAttribute = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (name, value) {
    const n = String(name).toLowerCase();
    if ((this.tagName === "SCRIPT" && n === "src") || (this.tagName === "LINK" && n === "href")) {
      value = rewrite(value);
    }
    return origSetAttribute.call(this, name, value);
  };
})();
```

After the goods list loads, extract visible product rows from the snapshot or bounded DOM reads. For the current observed layout, useful fields include product name, ID, product code, price, total stock, health status, created time, sales state, and action labels.

## Output Style

Report what page was opened, what state was observed, and what actions were or were not performed. If the task involved live business systems, explicitly state when no data-changing action has been taken.
