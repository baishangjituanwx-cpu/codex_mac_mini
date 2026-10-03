#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { loadDashboardEnv } = require("./lib/load-dashboard-env");
const {
  resolveRepoRoot,
  resolveDashboardExportDir,
  resolveFromRoot,
} = require("./lib/workspace-paths");

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (next && !next.startsWith("--")) {
      args[key] = next;
      i += 1;
    } else {
      args[key] = true;
    }
  }
  return args;
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

function readJson(absPath) {
  return JSON.parse(fs.readFileSync(absPath, "utf-8"));
}

function pickArg(args, key, envKey, fallback = "") {
  return String(args[key] || process.env[envKey] || fallback).trim();
}

function requireConfig(value, message) {
  if (!value) {
    fail(message);
  }
  return value;
}

async function requestJson(url, { method = "GET", body, headers = {} } = {}) {
  const response = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await response.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`);
  }
  return data;
}

function resolveAccount(index, { accountName, workspaceName }) {
  const matches = (index.accounts || []).filter((account) => {
    if (account.name !== accountName) return false;
    if (workspaceName && account.workspaceName !== workspaceName) return false;
    return true;
  });
  if (matches.length === 0) {
    const scope = workspaceName ? `${workspaceName} / ${accountName}` : accountName;
    fail(`Could not find target dashboard account: ${scope}`);
  }
  if (matches.length > 1) {
    fail(`Found multiple accounts named "${accountName}". Please pass --workspace-name as well.`);
  }
  return matches[0];
}

async function main() {
  const args = parseArgs(process.argv);
  const rootDir = resolveRepoRoot(__dirname);
  loadDashboardEnv(rootDir);
  const exportPath = args.export;
  if (!exportPath) {
    console.error("Missing required arg: --export /absolute/or/relative/path/to/dashboard-export.json");
    process.exit(2);
  }

  const exportAbs = path.isAbsolute(exportPath) ? exportPath : resolveFromRoot(rootDir, exportPath);
  if (!fs.existsSync(exportAbs)) {
    console.error(`Export file not found: ${exportAbs}`);
    process.exit(2);
  }

  const exportPayload = readJson(exportAbs);
  const outDir = resolveDashboardExportDir(rootDir);
  fs.mkdirSync(outDir, { recursive: true });

  const latestAbs = path.join(outDir, "latest.json");
  fs.copyFileSync(exportAbs, latestAbs);

  const apiBase = requireConfig(
    pickArg(args, "api-base", "DASHBOARD_API_BASE"),
    "Missing dashboard API base. Pass --api-base or set DASHBOARD_API_BASE in .env.dashboard."
  );
  const accountName = requireConfig(
    pickArg(args, "account-name", "DASHBOARD_ACCOUNT_NAME"),
    "Missing dashboard account name. Pass --account-name or set DASHBOARD_ACCOUNT_NAME in .env.dashboard."
  );
  const workspaceName = pickArg(args, "workspace-name", "DASHBOARD_WORKSPACE_NAME", "");
  const adminUsername = requireConfig(
    pickArg(args, "admin-username", "DASHBOARD_ADMIN_USERNAME"),
    "Missing dashboard admin username. Pass --admin-username or set DASHBOARD_ADMIN_USERNAME in .env.dashboard."
  );
  const adminPassword = requireConfig(
    pickArg(args, "admin-password", "DASHBOARD_ADMIN_PASSWORD"),
    "Missing dashboard admin password. Pass --admin-password or set DASHBOARD_ADMIN_PASSWORD in .env.dashboard."
  );

  const login = await requestJson(`${apiBase}/api/admin/login`, {
    method: "POST",
    body: { username: adminUsername, password: adminPassword },
  });
  const index = await requestJson(`${apiBase}/api/dashboard/index`, {
    headers: { "X-Admin-Token": login.adminToken },
  });
  const account = resolveAccount(index, { accountName, workspaceName });
  const upload = await requestJson(`${apiBase}/api/admin/accounts/${account.id}/dashboard`, {
    method: "POST",
    headers: { "X-Admin-Token": login.adminToken },
    body: {
      deviceToken: "admin-upload",
      payload: exportPayload,
    },
  });

  const metaAbs = path.join(outDir, "latest.meta.json");
  const meta = {
    updated_at: new Date().toISOString(),
    source_export: exportAbs,
    api_base: apiBase,
    account_id: account.id,
    account_name: account.name,
    workspace_name: account.workspaceName || "",
    uploaded_at: upload.updatedAt,
    uploaded_source_batch: upload.sourceBatch,
    upload_mode: upload.mode || "admin",
  };
  fs.writeFileSync(metaAbs, `${JSON.stringify(meta, null, 2)}\n`, "utf-8");

  console.log(
    JSON.stringify(
      {
        latest: latestAbs,
        meta: metaAbs,
        accountId: account.id,
        accountName: account.name,
        workspaceName: account.workspaceName || "",
        uploadedAt: upload.updatedAt,
        sourceBatch: upload.sourceBatch,
      },
      null,
      2,
    ),
  );
}

main().catch((error) => fail(error instanceof Error ? error.message : String(error)));
