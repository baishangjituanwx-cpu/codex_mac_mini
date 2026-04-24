"use strict";

const fs = require("fs");
const path = require("path");

function statSafe(absPath) {
  try {
    return fs.statSync(absPath);
  } catch {
    return null;
  }
}

function isDirectory(absPath) {
  const stat = statSafe(absPath);
  return Boolean(stat && stat.isDirectory());
}

function resolveFromRoot(rootDir, rawPath) {
  if (!rawPath) return "";
  return path.isAbsolute(rawPath) ? rawPath : path.join(rootDir, rawPath);
}

function resolveRepoRoot(scriptDir) {
  const override = process.env.PIPELINE_ROOT || "";
  if (override) {
    return path.resolve(override);
  }
  return path.resolve(scriptDir, "..");
}

function resolveContentRoot(rootDir) {
  const override = process.env.CONTENT_LIBRARY_ROOT || process.env.DASHBOARD_CONTENT_ROOT || "";
  if (override) {
    const abs = resolveFromRoot(rootDir, override);
    if (!isDirectory(abs)) {
      throw new Error(`Configured content library root does not exist: ${abs}`);
    }
    return abs;
  }

  const candidates = [
    path.join(rootDir, "workflow", "content-library"),
    path.join(rootDir, "content-library"),
  ];
  for (const candidate of candidates) {
    if (isDirectory(candidate)) {
      return candidate;
    }
  }

  throw new Error(
    `Could not resolve content library root under ${rootDir}. Checked workflow/content-library and content-library.`
  );
}

function resolveReviewRoot(rootDir) {
  return path.join(resolveContentRoot(rootDir), "logs", "review");
}

function resolveDashboardExportDir(rootDir) {
  return path.join(resolveReviewRoot(rootDir), "dashboard-export");
}

function resolveDashboardSyncDir(rootDir) {
  return path.join(resolveReviewRoot(rootDir), "dashboard-sync");
}

module.exports = {
  resolveRepoRoot,
  resolveContentRoot,
  resolveReviewRoot,
  resolveDashboardExportDir,
  resolveDashboardSyncDir,
  resolveFromRoot,
};
