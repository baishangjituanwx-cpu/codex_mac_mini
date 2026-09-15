#!/usr/bin/env node

const assert = require("node:assert/strict");
const {
  baseQuery,
  classifyAttribution,
  diagnosePushState,
  exactOrderNumber,
  extractBalanceAmounts,
  isContractRejection,
  parseArgs,
  sanitizeOrder,
  summarizeSubmission,
  verifySuccess,
} = require("./huice-push-distribution-order.js");

function test(name, callback) {
  try {
    callback();
    process.stdout.write(`ok - ${name}\n`);
  } catch (error) {
    process.stderr.write(`not ok - ${name}: ${error.message}\n`);
    process.exitCode = 1;
  }
}

test("defaults to read-only target shop", () => {
  const options = parseArgs(["--platform-order", "1234567890123456789"]);
  assert.equal(options.execute, false);
  assert.equal(options.platformId, 83);
  assert.equal(options.shopName, "百亿好购店");
  assert.equal(options.autoPushEnabled, true);
});

test("builds WAIT_SEND_CLOUD query", () => {
  const query = baseQuery(2, 3);
  assert.equal(query.pushStatusFast, 2);
  assert.equal(query.pageTab, "WAIT_SEND_CLOUD");
  assert.equal(query.currentPage, 3);
});

test("supports read-only watch and rejects watch plus execute", () => {
  const options = parseArgs([
    "--platform-order", "1234567890123456789",
    "--watch",
    "--poll-attempts", "12",
  ]);
  assert.equal(options.watch, true);
  assert.equal(options.pollAttempts, 12);
  assert.throws(() => parseArgs([
    "--platform-order", "1234567890123456789",
    "--watch",
    "--execute",
  ]), /mutually exclusive/);
});

test("matches exact platform order and sanitizes buyer data", () => {
  const row = {
    srcTid: "1234567890123456789",
    tradeId: "8888",
    shopName: "百亿好购店",
    platformId: 83,
    receiverName: "must-not-appear",
    receiverMobile: "SENSITIVE-MOBILE",
    receiverAddress: "must-not-appear",
    orderItemList: [{ spuName: "测试商品", skuName: "默认规格", skuNum: 1 }],
  };
  assert.equal(exactOrderNumber(row), "1234567890123456789");
  const sanitized = sanitizeOrder(row, "待推单");
  assert.equal(sanitized.productName, "测试商品");
  assert.equal(Object.prototype.hasOwnProperty.call(sanitized, "receiverName"), false);
  assert.equal(JSON.stringify(sanitized).includes("SENSITIVE-MOBILE"), false);
});

test("attributes a pre-existing success away from Codex", () => {
  const attribution = classifyAttribution({
    autoPushEnabled: true,
    preflight: { status: "推单成功", tradeId: "8888", pushTime: "2026-08-02T15:18:03" },
    submission: { attemptedAt: "2026-08-02T15:24:02+08:00", success: false },
    polling: [],
  });
  assert.equal(attribution.code, "huice_auto_or_external_before_codex");
  assert.equal(attribution.codexMutationCausedSuccess, false);
});

test("diagnoses supplier balance failure and extracts amounts", () => {
  const reason = "供应商余额仅 1.36 元，不足支付 5.33 元";
  assert.deepEqual(extractBalanceAmounts(reason), {
    availableBalance: 1.36,
    requiredAmount: 5.33,
  });
  const decision = diagnosePushState({
    status: "推单失败",
    failureReason: reason,
  }, { autoPushEnabled: true });
  assert.equal(decision.category, "supplier_balance_insufficient");
  assert.equal(decision.allowMutationNow, false);
  assert.equal(decision.actionOwner, "user");
  assert.equal(decision.autoRetryExpected, true);
  assert.equal(decision.shouldPoll, true);
});

test("requires strong evidence before marking success verified", () => {
  const incomplete = verifySuccess({
    status: "推单成功",
    tradeId: "8888",
    platformOrder: "1234567890123456789",
  });
  assert.equal(incomplete.verified, false);
  assert.ok(incomplete.missing.includes("outsourceOrderNo"));

  const complete = verifySuccess({
    status: "推单成功",
    tradeId: "8888",
    platformOrder: "1234567890123456789",
    pushTime: "2026-08-02T15:18:03",
    outsourceOrderNo: "SAFE-OUTSOURCE-ID",
    supplierName: "测试供应商",
    platformProductId: "PRODUCT-ID",
    platformSkuId: "SKU-ID",
    quantity: 1,
    distributionOrderCost: "5.33",
    refundStatus: "无退款",
  });
  assert.equal(complete.verified, true);
  assert.deepEqual(complete.missing, []);
});

test("attributes a watched failure-to-success transition to Huice automatic push", () => {
  const attribution = classifyAttribution({
    autoPushEnabled: true,
    preflight: { status: "推单失败", tradeId: "8888" },
    submission: null,
    polling: [{
      checkedAt: "2026-08-02T15:18:05+08:00",
      order: { status: "推单成功", pushTime: "2026-08-02T15:18:03" },
    }],
  });
  assert.equal(attribution.code, "huice_auto_push_observed_by_codex");
  assert.equal(attribution.codexMutationCausedSuccess, false);
});

test("treats validation rejection as no business push", () => {
  const message = "[tradeIdList: must not be null][tradeIdList: must not be empty]";
  assert.equal(isContractRejection(message), true);
  const submission = summarizeSubmission(
    { success: false, message },
    "8888",
    "2026-08-02T15:24:02+08:00",
    "2026-08-02T15:24:03+08:00",
  );
  assert.equal(submission.contractRejected, true);
  assert.deepEqual(submission.successTradeIds, []);
});

test("confirms Codex only with exact success tradeId", () => {
  const attribution = classifyAttribution({
    autoPushEnabled: true,
    preflight: { status: "推单失败", tradeId: "8888" },
    preMutationCheck: { status: "推单失败", tradeId: "8888" },
    submission: {
      skipped: false,
      attemptedAt: "2026-08-02T15:24:02+08:00",
      successTradeIds: ["8888"],
    },
    polling: [{
      checkedAt: "2026-08-02T15:24:06+08:00",
      order: { status: "推单成功", pushTime: "2026-08-02T15:24:04" },
    }],
  });
  assert.equal(attribution.code, "codex_http_api_confirmed");
  assert.equal(attribution.codexMutationCausedSuccess, true);
});

if (!process.exitCode) process.stdout.write("all tests passed\n");
