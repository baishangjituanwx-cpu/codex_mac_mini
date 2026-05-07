#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

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

function fail(msg) {
  console.error(msg);
  process.exit(1);
}

const FORBIDDEN_PHRASES = [
  "未命名列",
  "当前最高可见",
  "当前最佳样本",
  "页面核验",
  "下一主动作",
  "可见样本",
  "share链接",
  "latest known status=",
  "not_published",
  "share link",
  "receipt",
  "未完成内容级核验",
  "Keep",
  "Retest",
  "Watch",
  "Cut",
  "Browser Bridge",
  "audit-wait-no-republish",
  "live publish",
];

function main() {
  const args = parseArgs(process.argv);
  const rootDir = process.cwd();
  const filePath = args.file;
  if (!filePath) {
    console.error("Missing required arg: --file path/to/export.json");
    process.exit(2);
  }
  const abs = path.isAbsolute(filePath) ? filePath : path.join(rootDir, filePath);
  const raw = fs.readFileSync(abs, "utf-8");
  let obj;
  try {
    obj = JSON.parse(raw);
  } catch (e) {
    fail(`Invalid JSON: ${e.message}`);
  }

  if (!obj || typeof obj !== "object") fail("Export must be a JSON object");
  if (!obj.board || typeof obj.board !== "object") fail("Missing board object");
  if (!Array.isArray(obj.platforms)) fail("platforms must be an array");
  if (obj.platforms.length !== 8) fail(`platforms must have exactly 8 items, got ${obj.platforms.length}`);

  const requiredKeys = ["kuaishou", "wechat", "weibo", "toutiao", "baijiahao", "douyin", "bilibili", "zhihu"];
  const keys = obj.platforms.map((p) => p && p.key);
  for (const k of requiredKeys) {
    if (!keys.includes(k)) fail(`Missing platform key: ${k}`);
  }

  for (const p of obj.platforms) {
    if (!p || typeof p !== "object") fail("platform item must be object");
    if (typeof p.primaryValue !== "number" || Number.isNaN(p.primaryValue)) {
      fail(`primaryValue must be numeric for ${p.key}`);
    }
    if (!Array.isArray(p.metrics) || p.metrics.length !== 4) {
      fail(`metrics must be exactly 4 items for ${p.key}`);
    }
    if (!Array.isArray(p.windows) || p.windows.length !== 3) {
      fail(`windows must be exactly 3 items for ${p.key}`);
    }
    for (const windowItem of p.windows) {
      if (!windowItem || typeof windowItem !== "object") {
        fail(`window item must be object for ${p.key}`);
      }
      if (!Array.isArray(windowItem.metrics) || windowItem.metrics.length !== 4) {
        fail(`window.metrics must be exactly 4 items for ${p.key}/${windowItem.label || "-"}`);
      }
      const labels = windowItem.metrics.map((metric) => metric && metric.label).filter(Boolean);
      if (new Set(labels).size !== labels.length) {
        fail(`window.metrics labels must be unique for ${p.key}/${windowItem.label || "-"}`);
      }
    }
  }

  const summary = obj.board.summary;
  if (!Array.isArray(summary) || summary.length !== 4) fail("board.summary must be exactly 4 items");
  for (const t of summary) {
    if (!t || typeof t !== "object") fail("board.summary tile must be object");
    if (!["cool", "steady", "warning", "hot"].includes(t.tone)) fail(`Invalid summary.tone: ${t.tone}`);
  }
  if (!Array.isArray(obj.board.keep) || obj.board.keep.length !== 3) fail("board.keep must be exactly 3 items");
  if (!Array.isArray(obj.board.cut) || obj.board.cut.length !== 3) fail("board.cut must be exactly 3 items");
  if (!Array.isArray(obj.board.next) || obj.board.next.length !== 3) fail("board.next must be exactly 3 items");

  const serialized = JSON.stringify(obj);
  for (const phrase of FORBIDDEN_PHRASES) {
    if (serialized.includes(phrase)) {
      fail(`Export contains forbidden user-facing phrase: ${phrase}`);
    }
  }
  if (/(?:历史|近作|账号|对照)(?:播放|阅读|展现|推荐量|赞同|评论|互动)\d/.test(serialized)) {
    fail("Export contains numbered sample labels without explicit date context");
  }

  console.log("ok");
}

main();
