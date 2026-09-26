#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

function valueAfter(flag) {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const positional = process.argv
  .slice(2)
  .filter((arg, index, args) => !arg.startsWith("--") && args[index - 1] !== "--target");
const input = valueAfter("--raw") ?? positional[0];
if (!input) {
  throw new Error("usage: validate-weixin-selling-scan.js <live-raw.json> [--target <platformGoodsId>]");
}

const raw = JSON.parse(fs.readFileSync(path.resolve(input), "utf8"));
const rows = raw.products ?? raw.rows ?? raw.data?.products ?? [];
const displayedTotal = Number(raw.displayedTotal ?? raw.totalNum ?? raw.total ?? raw.data?.total);
const returned = Number(raw.returned ?? rows.length);
const rawPageCounts = raw.pageCounts ?? raw.pages?.map((page) => page.rowCount ?? page.count ?? page.rows?.length ?? 0);
const pageCounts = Array.isArray(rawPageCounts) ? rawPageCounts.map(Number) : Object.values(rawPageCounts ?? {}).map(Number);
const ids = rows.map((row) => String(row.platformGoodsId ?? row.productId ?? row.goodsId ?? row.id ?? "")).filter(Boolean);
const uniqueCount = new Set(ids).size;
const pageSum = pageCounts.reduce((sum, count) => sum + count, 0);
const target = valueAfter("--target");

const checks = {
  responseOk: raw.ok !== false,
  displayedTotalIsInteger: Number.isInteger(displayedTotal) && displayedTotal >= 0,
  pageCountsPresent: pageCounts.length > 0,
  pageSumMatchesDisplayed: pageSum === displayedTotal,
  returnedMatchesDisplayed: returned === displayedTotal,
  uniqueMatchesDisplayed: uniqueCount === displayedTotal,
  allRowsHaveExactId: ids.length === rows.length,
};

if (!Object.values(checks).every(Boolean)) {
  throw new Error(`invalid live selling scan: displayed=${displayedTotal}, pages=${pageSum}, returned=${returned}, unique=${uniqueCount}`);
}

console.log(JSON.stringify({
  ok: true,
  displayedTotal,
  pageCounts,
  pageSum,
  returned,
  uniqueCount,
  target: target ?? null,
  targetPresent: target ? ids.includes(String(target)) : null,
}));
