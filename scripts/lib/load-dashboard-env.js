"use strict";

const fs = require("fs");
const path = require("path");

function stripQuotes(value) {
  const trimmed = String(value || "").trim();
  if (
    (trimmed.startsWith("\"") && trimmed.endsWith("\"")) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"))
  ) {
    return trimmed.slice(1, -1);
  }
  return trimmed;
}

function applyEnvFile(absPath, targetEnv) {
  if (!fs.existsSync(absPath)) {
    return false;
  }

  const lines = fs.readFileSync(absPath, "utf-8").split(/\r?\n/);
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    const match = line.match(/^([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (!match) continue;
    const key = match[1];
    if (Object.prototype.hasOwnProperty.call(targetEnv, key) && String(targetEnv[key]).length > 0) {
      continue;
    }
    targetEnv[key] = stripQuotes(match[2]);
  }
  return true;
}

function loadDashboardEnv(rootDir, targetEnv = process.env) {
  const candidates = [
    path.join(rootDir, ".env.dashboard.local"),
    path.join(rootDir, ".env.dashboard"),
  ];
  const loaded = [];
  for (const candidate of candidates) {
    if (applyEnvFile(candidate, targetEnv)) {
      loaded.push(candidate);
    }
  }
  return loaded;
}

module.exports = {
  loadDashboardEnv,
};
