# Architecture

## Data flow

```text
Feishu Bot
  -> lark-cli event subscription
  -> bridge.js
  -> codex exec / codex exec resume
  -> lark-cli message reply
```

## Runtime state

- `state.json`
  Stores chat bindings, active thread markers, thread lists, and recent mirrored history.

- `mirrors/*.md`
  Human-readable mirrored chat history per Feishu conversation.

- `mirrors/*.jsonl`
  Structured mirrored chat history per Feishu conversation.

## Busy-thread protection

When the bridge is actively running a task against a bound thread, the bridge marks that thread as busy in `state.json`. Subsequent inbound messages for the same thread are rejected with a wait message instead of being executed concurrently.

## Local desktop thread monitoring

The bridge also polls local Codex session files for bound threads that are continued manually inside Codex Desktop.

- Feishu-bound threads can push milestone updates back into Feishu even when the user resumes the same thread from the desktop app.
- The bridge seeds a baseline cursor on first watch so historical session logs are not replayed as fresh notifications after a restart.
- Current milestone coverage focuses on task start, reasoning summaries, patch application, completion, interruption, and error events.

## Mirror viewer

The mirror viewer is intentionally separate from the Codex App UI:

- lower risk than mutating Codex session files
- stable on machines where Codex internals change
- sufficient for operators who need a local read view of Feishu-side conversations

## Operational limits

- Best for private Feishu chats
- Not designed as a real-time dual-UI sync client
- Thread context is shared, but message presentation is not automatically mirrored inside the Codex App UI
