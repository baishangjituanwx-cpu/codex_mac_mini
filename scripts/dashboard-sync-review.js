#!/usr/bin/env node
"use strict";

const fs = require("fs");
const { spawnSync } = require("child_process");
const path = require("path");
const { loadDashboardEnv } = require("./lib/load-dashboard-env");
const {
  resolveRepoRoot,
  resolveDashboardSyncDir,
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

class SyncError extends Error {
  constructor(stage, message) {
    super(message);
    this.name = "SyncError";
    this.stage = stage;
  }
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

function ensureDir(absPath) {
  fs.mkdirSync(absPath, { recursive: true });
}

function appendJsonl(absPath, payload) {
  fs.appendFileSync(absPath, `${JSON.stringify(payload)}\n`, "utf-8");
}

function readJson(absPath) {
  return JSON.parse(fs.readFileSync(absPath, "utf-8"));
}

function formatStatusMarkdown(summary) {
  const lines = [
    `# Dashboard Sync Status`,
    ``,
    `- 状态：${summary.status === "success" ? "成功" : "失败"}`,
    `- 复盘日期：${summary.reviewDate || "-"}`,
    `- 阶段：${summary.stage || "-"}`,
    `- 开始时间：${summary.startedAt || "-"}`,
    `- 结束时间：${summary.finishedAt || "-"}`,
    `- 耗时毫秒：${summary.durationMs ?? "-"}`,
    `- companion export：${summary.exportPath || "-"}`,
    `- latest.json：${summary.latestPath || "-"}`,
    `- latest.meta.json：${summary.latestMetaPath || "-"}`,
    `- 目标工作账号：${summary.workspaceName || "-"}`,
    `- 目标账号组：${summary.accountName || "-"}`,
    `- 目标账号组 ID：${summary.accountId || "-"}`,
    `- 上传批次：${summary.sourceBatch || "-"}`,
    `- 上传时间：${summary.uploadedAt || "-"}`,
  ];
  if (summary.error) {
    lines.push(`- 错误：${summary.error}`);
  }
  return `${lines.join("\n")}\n`;
}

function writeSyncAudit(rootDir, summary) {
  const auditDir = resolveDashboardSyncDir(rootDir);
  ensureDir(auditDir);
  const latestJson = path.join(auditDir, "latest-status.json");
  const latestMd = path.join(auditDir, "latest-status.md");
  const historyJsonl = path.join(auditDir, "history.jsonl");
  fs.writeFileSync(latestJson, `${JSON.stringify(summary, null, 2)}\n`, "utf-8");
  fs.writeFileSync(latestMd, formatStatusMarkdown(summary), "utf-8");
  appendJsonl(historyJsonl, summary);
  return {
    auditDir,
    latestJson,
    latestMd,
    historyJsonl,
  };
}

function runNodeScript(stage, scriptAbs, args, cwd) {
  const result = spawnSync(process.execPath, [scriptAbs, ...args], {
    cwd,
    encoding: "utf-8",
    env: process.env,
  });
  if (result.status !== 0) {
    const stderr = (result.stderr || "").trim();
    const stdout = (result.stdout || "").trim();
    throw new SyncError(stage, stderr || stdout || `Command failed: ${path.basename(scriptAbs)}`);
  }
  return (result.stdout || "").trim();
}

function pushOptional(args, key, out) {
  const value = args[key];
  if (value && value !== true) {
    out.push(`--${key}`, String(value));
  }
}

function main() {
  const args = parseArgs(process.argv);
  const rootDir = resolveRepoRoot(__dirname);
  loadDashboardEnv(rootDir);
  const reviewDate = String(args["review-date"] || "").trim();
  if (!reviewDate) {
    fail("Missing required arg: --review-date YYYY-MM-DD");
  }

  const startedAt = new Date().toISOString();
  let stage = "export";
  let exportPath = "";
  let uploadMeta = {};

  try {
    const exportScript = path.join(rootDir, "scripts", "dashboard-export-review.js");
    const validateScript = path.join(rootDir, "scripts", "validate-dashboard-export.js");
    const uploadScript = path.join(rootDir, "scripts", "dashboard-upload.js");

    const exportArgs = ["--review-date", reviewDate];
    pushOptional(args, "batch", exportArgs);
    const exportOutput = runNodeScript("export", exportScript, exportArgs, rootDir);
    exportPath = exportOutput.split("\n").filter(Boolean).at(-1) || "";
    if (!exportPath) {
      throw new SyncError("export", "dashboard-export-review.js did not return an export path.");
    }

    const exportPayload = readJson(exportPath);
    if (exportPayload?.meta?.mode === "local-package-review-export") {
      throw new SyncError(
        "export",
        "dashboard export is still in local-package-review-export mode. Refuse to sync placeholder package-only data to the dashboard."
      );
    }

    stage = "validate";
    runNodeScript("validate", validateScript, ["--file", exportPath], rootDir);

    stage = "upload";
    const uploadArgs = ["--export", exportPath];
    for (const key of ["api-base", "account-name", "workspace-name", "admin-username", "admin-password"]) {
      pushOptional(args, key, uploadArgs);
    }
    const uploadOutput = runNodeScript("upload", uploadScript, uploadArgs, rootDir);

    try {
      uploadMeta = JSON.parse(uploadOutput);
    } catch {
      throw new SyncError("upload", `dashboard-upload.js did not return JSON.\n${uploadOutput}`);
    }

    const finishedAt = new Date().toISOString();
    const summary = {
      status: "success",
      reviewDate,
      stage: "upload",
      startedAt,
      finishedAt,
      durationMs: Date.parse(finishedAt) - Date.parse(startedAt),
      exportPath,
      validation: "ok",
      latestPath: uploadMeta.latest || "",
      latestMetaPath: uploadMeta.meta || "",
      accountId: uploadMeta.accountId || "",
      accountName: uploadMeta.accountName || "",
      workspaceName: uploadMeta.workspaceName || "",
      uploadedAt: uploadMeta.uploadedAt || "",
      sourceBatch: uploadMeta.sourceBatch || "",
      error: "",
    };
    const audit = writeSyncAudit(rootDir, summary);

    console.log(
      JSON.stringify(
        {
          ...summary,
          syncAuditJson: audit.latestJson,
          syncAuditMarkdown: audit.latestMd,
          syncAuditHistory: audit.historyJsonl,
        },
        null,
        2,
      ),
    );
  } catch (error) {
    const finishedAt = new Date().toISOString();
    const summary = {
      status: "failed",
      reviewDate,
      stage: error instanceof SyncError ? error.stage : stage,
      startedAt,
      finishedAt,
      durationMs: Date.parse(finishedAt) - Date.parse(startedAt),
      exportPath,
      validation: exportPath ? "pending_or_failed" : "not_started",
      latestPath: uploadMeta.latest || "",
      latestMetaPath: uploadMeta.meta || "",
      accountId: uploadMeta.accountId || "",
      accountName: uploadMeta.accountName || "",
      workspaceName: uploadMeta.workspaceName || "",
      uploadedAt: uploadMeta.uploadedAt || "",
      sourceBatch: uploadMeta.sourceBatch || "",
      error: error instanceof Error ? error.message : String(error),
    };
    const audit = writeSyncAudit(rootDir, summary);
    fail(
      [
        `dashboard sync failed at stage: ${summary.stage}`,
        summary.error,
        `audit json: ${audit.latestJson}`,
        `audit markdown: ${audit.latestMd}`,
      ].join("\n"),
    );
  }
}

main();
