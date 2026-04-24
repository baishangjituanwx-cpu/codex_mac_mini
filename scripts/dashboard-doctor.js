#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { loadDashboardEnv } = require("./lib/load-dashboard-env");
const {
  resolveRepoRoot,
  resolveContentRoot,
  resolveReviewRoot,
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

function findLatestReviewReport(reviewRoot, reviewDate) {
  if (!reviewDate || !fs.existsSync(reviewRoot)) {
    return "";
  }
  const entries = fs.readdirSync(reviewRoot).filter((name) => name.startsWith(`${reviewDate}-`) && name.endsWith("-review.md"));
  if (entries.length === 0) return "";
  const ranked = entries
    .map((name) => {
      const abs = path.join(reviewRoot, name);
      const stat = fs.statSync(abs);
      return { abs, mtimeMs: stat.mtimeMs };
    })
    .sort((a, b) => b.mtimeMs - a.mtimeMs);
  return ranked[0].abs;
}

function collectMissingEnv(keys) {
  return keys.filter((key) => !String(process.env[key] || "").trim());
}

function printCheck(ok, label, detail) {
  const prefix = ok ? "[ok]" : "[missing]";
  if (detail) {
    console.log(`${prefix} ${label}: ${detail}`);
    return;
  }
  console.log(`${prefix} ${label}`);
}

function main() {
  const args = parseArgs(process.argv);
  const rootDir = resolveRepoRoot(__dirname);
  const loadedEnvFiles = loadDashboardEnv(rootDir);
  const contentRoot = resolveContentRoot(rootDir);
  const reviewRoot = resolveReviewRoot(rootDir);
  const reviewDate = String(args["review-date"] || "").trim();

  const nodeMajor = Number(process.versions.node.split(".")[0] || "0");
  let ok = true;

  console.log(`# Dashboard Doctor`);
  console.log(`- repo root: ${rootDir}`);
  console.log(`- content root: ${contentRoot}`);
  console.log(`- node version: ${process.versions.node}`);

  if (loadedEnvFiles.length > 0) {
    printCheck(true, "dashboard env", loadedEnvFiles.join(", "));
  } else {
    printCheck(false, "dashboard env", "create .env.dashboard or .env.dashboard.local from .env.dashboard.example");
    ok = false;
  }

  if (nodeMajor >= 18) {
    printCheck(true, "node runtime", "Node.js 18+");
  } else {
    printCheck(false, "node runtime", "Node.js 18+ is required because dashboard upload uses fetch");
    ok = false;
  }

  const requiredEnv = [
    "DASHBOARD_API_BASE",
    "DASHBOARD_ACCOUNT_NAME",
    "DASHBOARD_ADMIN_USERNAME",
    "DASHBOARD_ADMIN_PASSWORD",
  ];
  const missingEnv = collectMissingEnv(requiredEnv);
  if (missingEnv.length === 0) {
    printCheck(true, "dashboard credentials", requiredEnv.join(", "));
  } else {
    printCheck(false, "dashboard credentials", `missing ${missingEnv.join(", ")}`);
    ok = false;
  }

  const requiredScripts = [
    "dashboard-export-review.js",
    "dashboard-sync-review.js",
    "dashboard-upload.js",
    "validate-dashboard-export.js",
  ];
  for (const scriptName of requiredScripts) {
    const abs = path.join(rootDir, "scripts", scriptName);
    if (fs.existsSync(abs)) {
      printCheck(true, scriptName, abs);
    } else {
      printCheck(false, scriptName, abs);
      ok = false;
    }
  }

  if (reviewDate) {
    const reviewAbs = findLatestReviewReport(reviewRoot, reviewDate);
    if (reviewAbs) {
      printCheck(true, "review report", reviewAbs);
    } else {
      printCheck(false, "review report", `no ${reviewDate}-*-review.md under ${reviewRoot}`);
      ok = false;
    }
  } else {
    printCheck(true, "review report", "pass --review-date YYYY-MM-DD to verify a specific review file");
  }

  if (!ok) {
    process.exit(1);
  }
}

main();
