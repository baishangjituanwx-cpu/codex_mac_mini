# Downstream Compatibility Audit

Use this audit before every upstream EdgeTunnel Production upgrade. Base every finding on complete code and configuration snapshots. Treat version identifiers only as labels.

## 1. Establish exact inputs

Collect and identify:

| Snapshot | Required contents |
|---|---|
| Current Production upstream | Complete deployed source, all modules/assets that affect runtime behavior, routes, bindings, variables names, compatibility date/flags, and deployment identifier |
| Proposed upstream | Complete Worker.js or extracted Pages artifact, all modules/assets, Wrangler/Pages configuration, bindings expectations, compatibility date/flags, and artifact hash |
| Current downstream Worker | Complete deployed source, custom authentication and subscription logic, bindings/configuration, deployment/revision identifier, and tests |
| Current NAS parser | Complete subscription fetch/parse/transform code, credential handling, expiry enforcement, NAS communication path, revision identifier, and tests |

Require evidence that each snapshot matches the running or proposed artifact. Prefer deployment exports, repository commits tied to deployments, or cryptographic hashes. Do not infer running code from an unverified working tree.

If any snapshot is missing, partial, minified beyond meaningful mapping without a source map, or not tied to the running deployment, conclude `兼容性尚未确定` and block Production deployment.

## 2. Compare complete upstream code

Perform a full tree and configuration diff. Use tools such as `git diff --no-index`, `diff -ru`, `rg`, language-aware symbol search, and artifact hashes as appropriate.

For every behavior-changing delta, record:

- Old file and function/symbol
- New file and function/symbol
- Configuration or binding keys involved
- Input/output or state transition that changed
- Error, close, retry, timeout, and fallback behavior
- Security impact
- Evidence from code, not release notes

Do not limit the comparison to named release highlights. Include deletions, renamed symbols, default changes, constant changes, reordered routing, validation changes, and compatibility-setting changes.

### Windows handoff notes

When the audit is reviewed on Windows, keep source, ZIP, screenshot, and evidence paths quoted and in `C:/Users/<name>/...` form. If this mirror is installed locally, the typical skill path is `%USERPROFILE%\\.codex\\skills\\update-edgetunnel-pages\\`.

Prefer `git diff --no-index` and `rg` on Windows too. If a shell-only fallback is needed in PowerShell, use `Compare-Object` for file lists or `fc.exe /n` for single-file line comparisons rather than inventing a separate wrapper script.

Do not convert the audit into persistent PowerShell automation. The Windows equivalent remains a human-reviewed comparison workflow using the same evidence and gate criteria.

## 3. Map changes to downstream code

Trace each upstream delta through the downstream data path even when functions have different names. Locate the downstream Worker and NAS equivalents by inputs, outputs, protocol fields, routes, headers, socket APIs, and call sites.

Complete every mandatory scope:

| Scope | Inspect in old/new upstream | Map in downstream Worker | Map in NAS parser |
|---|---|---|---|
| VLESS parsing | Header length, version, UUID/user validation, command, port, address type/length, IPv4/IPv6/domain decoding, malformed-input errors | VLESS request parser and validation functions | URI/config field parser if VLESS data is consumed |
| WebSocket upgrade and data channel | Upgrade checks, protocol negotiation, WebSocketPair/101 response, stream piping, backpressure, close/error propagation, retry | Upgrade router, WebSocket handler, socket bridge, stream lifecycle | Subscription fields that construct WS transport parameters |
| TCP/UDP/DNS | Socket connect/write/read, UDP framing, DNS-only restrictions, DoH request/response, timeout and failure behavior | Outbound TCP/UDP/DNS functions and framing | DNS/UDP-related node fields or parser assumptions |
| ProxyIP | Selection precedence, path/env overrides, host/port and IPv6 parsing, fallback/retry, connection target | ProxyIP resolver, retry and fallback functions | ProxyIP configuration fields or generated paths |
| Early Data | Header source, base64/base64url decoding, padding, byte/size limits, validation and replay exposure | Early Data extraction and first-packet handling | URI `ed`/path/header fields and encoding logic |
| Request paths and routing | Admin, subscription, config, proxy, static asset and fallback routes; method/host/path matching | Custom auth, subscription and proxy route ordering | Fetch endpoints, path templates and response expectations |
| Host/SNI | Host header, SNI/TLS fields, target-host validation, case/encoding and fallback rules | Host/SNI extraction and generated node parameters | Host/SNI parsing, preservation and rendering |
| Subscription output structure | Output formats, field names/types, URI query keys, encoding, node ordering, auth/token handling | Subscription generation/transformation and credentials | Fetch, decode, schema parsing, transformation and storage |
| Cloudflare settings | Binding names/types, module format, compatibility date/flags, runtime API assumptions, Pages vs Worker differences | Downstream bindings/config and runtime compatibility | Any build/deploy assumptions that affect NAS integration |
| Security fixes | Authentication bypass, input validation, SSRF/open-proxy exposure, injection, secret leakage, unsafe fallback, resource exhaustion, size limits, dependency/runtime fixes | Equivalent attack surface and missing guards | Credential exposure, unsafe parsing, command/path injection, expiry bypass |

For each scope, state one of:

- `No upstream delta`, with file/function evidence.
- `Delta mapped and compatible`, with both upstream and downstream evidence.
- `Delta requires downstream change`, with exact target files/functions.
- `Unresolved`, with the missing evidence and resulting block.

## 4. Assign decisions

Use one or more of these exact conclusions:

### `下游 Worker 无需更新`

Use only when all mandatory scopes are resolved and code evidence proves either no relevant upstream delta or behavioral compatibility. Do not use when material is missing, a security fix is absent downstream, or only connectivity was tested.

### `下游 Worker 建议更新`

Use for non-breaking reliability, performance, diagnostics, maintainability, or optional parity changes whose absence does not create protocol, correctness, security, or supported-configuration risk. Name the recommended files/functions and expected benefit.

### `下游 Worker 必须更新`

Use when the upstream delta changes a consumed protocol/schema/path/runtime contract; fixes a relevant security weakness; prevents incorrect routing, parsing, socket behavior, authentication, expiry enforcement, or supported deployment behavior; or makes the existing downstream implementation unsafe or incompatible. Name every required target file/function and the precise failure/risk.

### `NAS 需要更新`

Use when subscription output, URI/query encoding, paths, credentials, expiry signals, response formats, field types, ordering assumptions, or NAS communication behavior changes. Name the NAS files/functions and parser/enforcement behavior to change.

### `兼容性尚未确定`

Use whenever required code/configuration is missing, snapshot provenance is uncertain, a mandatory scope is unresolved, or behavior cannot be mapped. This status blocks Production and cannot be combined with `下游 Worker 无需更新`.

Treat a relevant security fix as `必须更新` even if the old downstream still establishes connections. Connectivity does not demonstrate confidentiality, authorization, validation, or resource-safety equivalence.

## 5. Constrain downstream changes

When a downstream change is authorized:

1. Extract only the upstream proxy-core hunks needed for the mapped deltas.
2. Port them into the downstream architecture and naming conventions.
3. Preserve account authentication, subscription credentials, expiry hard stop, NAS communication, custom routing, observability, and other downstream-only features.
4. Do not replace the downstream entry file or codebase with the complete upstream source.
5. If upstream refactoring makes direct hunk transfer unsafe, implement a minimal equivalent adapter and document the mapping.
6. Review the final diff for accidental deletion of business logic, bindings, secrets references, routes, tests, and enforcement checks.
7. Keep downstream and NAS changes out of scope until the user explicitly authorizes those systems.

## 6. Run the minimum validation checklist

Use non-production previews, fixtures, or staging wherever possible before upstream cutover. Never alter real credentials or expiry dates merely to create a test.

| Check | Minimum evidence | Required status |
|---|---|---|
| Upstream raw subscription | Proposed upstream returns the expected raw subscription structure and transport fields without exposing credentials in logs | Pass before rollout completion |
| Downstream subscription retrieval | Downstream successfully retrieves, authenticates, parses and transforms the proposed structure | Pass before rollout completion |
| Random node connection | Select at least one node from the actual generated set without hard-coding the first item; complete WebSocket and proxy data transfer | Pass before rollout completion |
| ProxyIP | Exercise configured selection plus fallback/retry behavior and verify the intended connection target handling | Pass before rollout completion |
| Expiry hard stop | Use a safe expired fixture or existing test account to prove downstream and NAS deny access after expiry | Pass before rollout completion |

Add focused tests for every changed mandatory scope. Record failures and unverified checks. Do not report the rollout complete while a minimum check is failed or unverified.

## 7. Produce the audit decision report

Use this template. Mask sensitive labels and never include passwords, domains, subscription tokens, node URIs, KV IDs, or full account IDs.

```markdown
# EdgeTunnel Downstream Compatibility Audit

## Snapshot provenance

| Role | Provenance | Revision/deployment/hash | Complete code | Config/bindings included |
|---|---|---|---|---|
| Current Production upstream | ... | ... | Yes/No | Yes/No |
| Proposed upstream | ... | ... | Yes/No | Yes/No |
| Current downstream Worker | ... | ... | Yes/No | Yes/No |
| Current NAS parser | ... | ... | Yes/No | Yes/No |

## Upstream change ledger

| ID | Old file/function | New file/function | Behavioral delta | Mandatory scope | Security impact |
|---|---|---|---|---|---|
| U-001 | ... | ... | ... | ... | ... |

## Downstream mapping

| Change ID | Downstream Worker file/function | NAS file/function | Compatibility evidence | Required action |
|---|---|---|---|---|
| U-001 | ... | ... | ... | ... |

## Mandatory scope findings

| Scope | Finding | File/function evidence | Decision impact |
|---|---|---|---|
| VLESS parsing | ... | ... | ... |
| WebSocket upgrade/data channel | ... | ... | ... |
| TCP/UDP/DNS | ... | ... | ... |
| ProxyIP | ... | ... | ... |
| Early Data | ... | ... | ... |
| Request paths/routing | ... | ... | ... |
| Host/SNI | ... | ... | ... |
| Subscription output structure | ... | ... | ... |
| Cloudflare bindings/compatibility | ... | ... | ... |
| Security fixes | ... | ... | ... |

## Conclusions

- Exact conclusion(s): 下游 Worker 无需更新 / 下游 Worker 建议更新 / 下游 Worker 必须更新 / NAS 需要更新 / 兼容性尚未确定
- NAS mapping when `NAS 需要更新` is not triggered: concrete no-impact evidence, not an invented extra conclusion label
- Evidence: concrete files/functions and reasons
- Minimal proxy-core ports: exact files/functions/hunks
- Preserved downstream-only behavior: authentication, credentials, expiry hard stop, NAS communication, other custom logic

## Minimum validation

| Check | Result | Evidence or blocker |
|---|---|---|
| Upstream raw subscription | Pass/Fail/Unverified | ... |
| Downstream subscription retrieval | Pass/Fail/Unverified | ... |
| Random node connection | Pass/Fail/Unverified | ... |
| ProxyIP | Pass/Fail/Unverified | ... |
| Expiry hard stop | Pass/Fail/Unverified | ... |

## Production gate

- Gate: PASSED / BLOCKED
- Blocking material or action: ...
- Audited upstream artifact hash: ...
- Deployment artifact hash matches audit: Yes/No
```

Never set the gate to `PASSED` from version equality alone.
