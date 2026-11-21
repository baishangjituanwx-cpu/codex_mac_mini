#!/usr/bin/env node
"use strict";

const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawn, spawnSync } = require("child_process");
const { loadDashboardEnv } = require("./lib/load-dashboard-env");
const { resolveRepoRoot } = require("./lib/workspace-paths");

function fail(message) {
  console.error(message);
  process.exit(1);
}

function runCommand(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd,
    env: options.env,
    encoding: "utf-8",
  });
  if (result.status !== 0) {
    fail(
      [
        `Command failed: ${command} ${args.join(" ")}`,
        result.stdout || "",
        result.stderr || "",
      ]
        .filter(Boolean)
        .join("\n"),
    );
  }
  return result.stdout.trim();
}

async function startMockServer(port, captureFile) {
  const serverCode = `
    const fs = require("fs");
    const http = require("http");
    const port = Number(process.env.FIXTURE_PORT);
    const captureFile = process.env.CAPTURE_FILE;
    const account = { id: "acct_fixture", name: "Fixture Account", workspaceName: "Fixture Workspace" };
    const server = http.createServer((req, res) => {
      let body = "";
      req.on("data", (chunk) => { body += chunk; });
      req.on("end", () => {
        res.setHeader("Content-Type", "application/json");
        res.setHeader("Connection", "close");
        if (req.url === "/api/admin/login" && req.method === "POST") {
          res.end(JSON.stringify({ adminToken: "fixture-token" }));
          return;
        }
        if (req.url === "/api/dashboard/index" && req.method === "GET") {
          res.end(JSON.stringify({ accounts: [account] }));
          return;
        }
        if (req.url === "/api/admin/accounts/" + account.id + "/dashboard" && req.method === "POST") {
          fs.writeFileSync(captureFile, body || "{}", "utf-8");
          res.end(JSON.stringify({ updatedAt: "2026-04-25T12:34:56.000Z", sourceBatch: "dashboard-fixture", mode: "admin" }));
          return;
        }
        res.statusCode = 404;
        res.end(JSON.stringify({ detail: "not found" }));
      });
    });
    server.listen(port, "127.0.0.1", () => {
      process.stdout.write("ready\\n");
    });
    process.on("SIGTERM", () => {
      if (typeof server.closeAllConnections === "function") {
        server.closeAllConnections();
      }
      server.close(() => process.exit(0));
    });
  `;

  const child = spawn(process.execPath, ["-e", serverCode], {
    env: {
      ...process.env,
      FIXTURE_PORT: String(port),
      CAPTURE_FILE: captureFile,
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  await new Promise((resolve, reject) => {
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += String(chunk);
    });
    child.stdout.on("data", (chunk) => {
      if (String(chunk).includes("ready")) {
        resolve();
      }
    });
    child.on("exit", (code) => {
      if (code !== null && code !== 0) {
        reject(new Error(`mock server exited early: ${stderr || code}`));
      }
    });
  });

  return {
    dispose: () => {
      child.kill("SIGTERM");
    },
    getUploadedPayload: () => {
      if (!fs.existsSync(captureFile)) return null;
      return JSON.parse(fs.readFileSync(captureFile, "utf-8"));
    },
  };
}

async function main() {
  const rootDir = resolveRepoRoot(__dirname);
  loadDashboardEnv(rootDir);

  const fixtureRoot = path.join(rootDir, "tests", "dashboard-fixture");
  const expectedExportAbs = path.join(fixtureRoot, "expected-export.json");
  const sourceContentRoot = path.join(fixtureRoot, "content-library");
  const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), "dashboard-fixture-"));
  const contentRoot = path.join(tmpRoot, "content-library");
  const captureFile = path.join(tmpRoot, "uploaded-payload.json");
  fs.cpSync(sourceContentRoot, contentRoot, { recursive: true });

  const port = 20000 + Math.floor(Math.random() * 10000);
  const mock = await startMockServer(port, captureFile);
  const env = {
    ...process.env,
    CONTENT_LIBRARY_ROOT: contentRoot,
    DASHBOARD_API_BASE: `http://127.0.0.1:${port}`,
    DASHBOARD_ACCOUNT_NAME: "Fixture Account",
    DASHBOARD_WORKSPACE_NAME: "Fixture Workspace",
    DASHBOARD_ADMIN_USERNAME: "fixture-admin",
    DASHBOARD_ADMIN_PASSWORD: "fixture-pass",
  };

  try {
    runCommand(process.execPath, [path.join(rootDir, "scripts", "dashboard-doctor.js"), "--review-date", "2026-04-25"], {
      cwd: rootDir,
      env,
    });

    runCommand(process.execPath, [path.join(rootDir, "scripts", "dashboard-sync-review.js"), "--review-date", "2026-04-25"], {
      cwd: rootDir,
      env,
    });

    const actualExportAbs = path.join(contentRoot, "logs", "review", "dashboard-export", "dashboard-fixture-dashboard-export.json");
    const latestStatusAbs = path.join(contentRoot, "logs", "review", "dashboard-sync", "latest-status.json");
    const latestMetaAbs = path.join(contentRoot, "logs", "review", "dashboard-export", "latest.meta.json");

    const expectedExport = JSON.parse(fs.readFileSync(expectedExportAbs, "utf-8"));
    const actualExport = JSON.parse(fs.readFileSync(actualExportAbs, "utf-8"));
    const latestStatus = JSON.parse(fs.readFileSync(latestStatusAbs, "utf-8"));
    const latestMeta = JSON.parse(fs.readFileSync(latestMetaAbs, "utf-8"));

    assert.deepStrictEqual(actualExport, expectedExport);
    assert.strictEqual(latestStatus.status, "success");
    assert.strictEqual(latestStatus.accountName, "Fixture Account");
    assert.strictEqual(latestStatus.sourceBatch, "dashboard-fixture");
    assert.strictEqual(latestMeta.account_name, "Fixture Account");
    assert.strictEqual(latestMeta.uploaded_source_batch, "dashboard-fixture");

    const uploadedPayload = mock.getUploadedPayload();
    assert(uploadedPayload && uploadedPayload.payload, "mock server did not receive uploaded dashboard payload");
    assert.deepStrictEqual(uploadedPayload.payload, expectedExport);

    console.log("dashboard fixture smoke: ok");
  } finally {
    mock.dispose();
    fs.rmSync(tmpRoot, { recursive: true, force: true });
  }
}

main().catch((error) => fail(error instanceof Error ? error.stack || error.message : String(error)));
