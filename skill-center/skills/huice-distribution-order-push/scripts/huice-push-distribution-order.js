#!/usr/bin/env node

const fs = require("node:fs");
const https = require("node:https");
const path = require("node:path");

const DEFAULT_BASE_URL = "https://erp.huice.com";
const STATUS_FILTERS = [
  { value: 1, label: "待推单" },
  { value: 2, label: "推单失败" },
  { value: 3, label: "推单中" },
  { value: 4, label: "推单成功" },
];

function usage() {
  return `Usage:
  node huice-push-distribution-order.js --platform-order <number> [options]

Options:
  --execute                  Submit at most one guarded push request
  --watch                    Poll read-only for an automatic state transition
  --failure-remediated       Confirm the diagnosed failure cause was resolved
  --platform-id <id>         Expected platform ID (default: 83)
  --shop-name <name>         Expected shop name (default: 百亿好购店)
  --output <path>            Sanitized JSON evidence path
  --poll-attempts <number>   Post-submit polls, 1-12 (default: 6)
  --auto-push-disabled       Record that Huice automatic push is disabled
  --help                     Show this help

Environment:
  HUICE_MAIN_COOKIE          Ephemeral authenticated cookie; never written to output
  HUICE_APP_VERSION          Current Huice web app version (default: 1.0.640)
  HUICE_BASE_URL             Override API origin for tests
  HUICE_TLS_INSECURE=1       Disable TLS verification only in a controlled environment
`;
}

function parseArgs(argv) {
  const options = {
    execute: false,
    watch: false,
    failureRemediated: false,
    platformId: 83,
    shopName: "百亿好购店",
    pollAttempts: 6,
    autoPushEnabled: true,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--execute") options.execute = true;
    else if (value === "--watch") options.watch = true;
    else if (value === "--failure-remediated") options.failureRemediated = true;
    else if (value === "--platform-order") options.platformOrder = argv[++index];
    else if (value === "--platform-id") options.platformId = Number(argv[++index]);
    else if (value === "--shop-name") options.shopName = argv[++index];
    else if (value === "--output") options.output = argv[++index];
    else if (value === "--poll-attempts") options.pollAttempts = Number(argv[++index]);
    else if (value === "--auto-push-disabled") options.autoPushEnabled = false;
    else if (value === "--help" || value === "-h") options.help = true;
    else throw new Error(`Unknown argument: ${value}`);
  }

  if (options.help) return options;
  if (options.execute && options.watch) {
    throw new Error("--execute and --watch are mutually exclusive");
  }
  if (!/^\d{12,30}$/.test(options.platformOrder || "")) {
    throw new Error("--platform-order must be an exact 12-30 digit platform order number");
  }
  if (!Number.isInteger(options.platformId) || options.platformId <= 0) {
    throw new Error("--platform-id must be a positive integer");
  }
  if (!options.shopName) throw new Error("--shop-name must not be empty");
  if (!Number.isInteger(options.pollAttempts) || options.pollAttempts < 1 || options.pollAttempts > 12) {
    throw new Error("--poll-attempts must be an integer from 1 to 12");
  }
  return options;
}

function shanghaiTimestamp(date = new Date()) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).formatToParts(date).reduce((result, part) => {
    result[part.type] = part.value;
    return result;
  }, {});
  return `${parts.year}${parts.month}${parts.day}-${parts.hour}${parts.minute}${parts.second}`;
}

function baseQuery(pushStatusFast, currentPage = 1) {
  return {
    pushStatusFast,
    providerStatusFast: 0,
    remarkStatusFast: 0,
    deliverTimeOutWaringFast: 0,
    refundStatusFast: 0,
    containSkuSuiteType: 0,
    containSkuSuiteGoodsType: 0,
    excludeSkuSuiteType: 0,
    noSearchField: 0,
    noSearchType: 0,
    containRemarkType: 3,
    containMessageType: 3,
    isIncludeAbnormal: true,
    suiteSearchField: 0,
    suiteSearchType: 0,
    orgPlatformQueryList: [],
    anchorSearchField: 0,
    anchorSearchType: 1,
    excludeAnchorSearchField: 0,
    excludeAnchorSearchType: 1,
    containRemarkFlag: 1,
    remarkFlagList: [],
    pageTab: "WAIT_SEND_CLOUD",
    orderQuerySortParam: "payTimeDesc",
    containSkuIdList: [],
    containSuiteIdList: [],
    manualExcludeSkuIdList: [],
    manualExcludeSuiteIdList: [],
    remarkContainMultiContent: true,
    abnormalIdFastList: [],
    calcTotalCount: false,
    currentPage,
    pageSize: 50,
  };
}

function rowsFromResponse(body) {
  const rows = body?.data?.data ?? body?.data?.rows ?? body?.dataList ?? [];
  return Array.isArray(rows) ? rows : [];
}

function exactOrderNumber(row) {
  return String(row?.srcTids || row?.srcTid || row?.tid || "");
}

function sanitizeOrder(row, statusLabel) {
  const item = row?.orderItemList?.[0] || row?.orderSuiteList?.[0] || {};
  return {
    status: statusLabel,
    platformOrder: exactOrderNumber(row),
    tradeId: String(row?.tradeId || ""),
    tradeNo: row?.tradeNo || null,
    platformId: row?.platformId ?? null,
    shopName: row?.shopName || null,
    supplierName: row?.providerName || item.providerName || null,
    supplierNickNo: row?.providerNickNo || item.providerNickNo || null,
    platformProductId: item.apiSpuId || null,
    platformSkuId: item.apiSkuId || null,
    productName: item.spuName || null,
    specification: item.skuName || null,
    quantity: item.skuNum || item.suiteNum || null,
    paid: row?.paid || item.paid || null,
    distributionGoodsPrice: item.omsPurchaseAmount || null,
    distributionOrderCost: row?.fenxiaoCostPrice || row?.omsPurchaseAmount || null,
    refundStatus: row?.refundStatusText || item.refundStatusName || null,
    pushStatus: row?.tradeStatusFrontText || null,
    pushTime: row?.pushDate || null,
    outsourceOrderNo: row?.outsourceNo || null,
    logisticsCompany: row?.logisticsName || null,
    logisticsNoPresent: Boolean(row?.logisticsNo),
    failureReason: row?.errorMsg || null,
  };
}

function parseErpTime(value) {
  if (!value) return null;
  const text = String(value);
  const hasZone = /(?:Z|[+-]\d{2}:?\d{2})$/i.test(text);
  const millis = Date.parse(hasZone ? text : `${text}+08:00`);
  return Number.isFinite(millis) ? millis : null;
}

function isPresent(value) {
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function verifySuccess(order) {
  const checks = {
    statusSuccessful: order?.status === "推单成功",
    exactTradeId: isPresent(order?.tradeId),
    exactPlatformOrder: isPresent(order?.platformOrder),
    pushTime: isPresent(order?.pushTime),
    outsourceOrderNo: isPresent(order?.outsourceOrderNo),
    supplier: isPresent(order?.supplierName),
    platformProductId: isPresent(order?.platformProductId),
    platformSkuId: isPresent(order?.platformSkuId),
    quantity: isPresent(order?.quantity),
    distributionCost: isPresent(order?.distributionOrderCost),
    noRefundConflict: !order?.refundStatus || order.refundStatus === "无退款",
  };
  const missing = Object.entries(checks)
    .filter(([, passed]) => !passed)
    .map(([name]) => name);
  return {
    verified: missing.length === 0,
    checks,
    missing,
    logisticsFollowUpRequired: !order?.logisticsNoPresent,
  };
}

function extractBalanceAmounts(reason) {
  const text = String(reason || "");
  const availableMatch = text.match(/(?:可用)?(?:账户)?余额(?:仅|为|剩余|还有)?\s*(?:为)?\s*[￥¥]?\s*(-?\d+(?:\.\d+)?)/i);
  const requiredMatch = text.match(/(?:需(?:要)?支付|应付|支付|扣款|货款)(?:金额)?[^\d-]{0,10}[￥¥]?\s*(-?\d+(?:\.\d+)?)/i);
  const allNumbers = [...text.matchAll(/[￥¥]?\s*(-?\d+(?:\.\d+)?)/g)]
    .map((match) => Number(match[1]))
    .filter(Number.isFinite);
  return {
    availableBalance: availableMatch ? Number(availableMatch[1]) : allNumbers[0] ?? null,
    requiredAmount: requiredMatch ? Number(requiredMatch[1]) : allNumbers[1] ?? null,
  };
}

function diagnosePushState(order, { autoPushEnabled = true } = {}) {
  const state = order?.status || "未找到";
  const exactReason = order?.failureReason || null;
  const completionCondition = "精确订单成为推单成功，且成功证据核实完整";

  if (state === "推单成功") {
    const verification = verifySuccess(order);
    return {
      state,
      category: verification.verified ? "success_verified" : "success_requires_verification",
      exactReason: null,
      actionOwner: "codex",
      recommendedAction: verification.verified
        ? "记录成功证据，并继续监控供应商发货及物流回传"
        : `继续回查成功详情，补齐字段：${verification.missing.join(", ")}`,
      allowMutationNow: false,
      shouldPoll: !verification.verified,
      autoRetryExpected: false,
      requiresExternalAction: false,
      completionCondition,
      verification,
    };
  }

  if (state === "推单中") {
    return {
      state,
      category: "processing",
      exactReason: null,
      actionOwner: "huice",
      recommendedAction: "只轮询精确订单，禁止重复推单",
      allowMutationNow: false,
      shouldPoll: true,
      autoRetryExpected: autoPushEnabled,
      requiresExternalAction: false,
      completionCondition,
    };
  }

  if (state === "待推单") {
    return {
      state,
      category: autoPushEnabled ? "waiting_for_auto_push" : "manual_push_candidate",
      exactReason: null,
      actionOwner: autoPushEnabled ? "huice" : "codex",
      recommendedAction: autoPushEnabled
        ? "先观察自动推单；重新核验后仍待推单且已获授权时，仅手动提交一次"
        : "重新核验后仍待推单且已获授权时，仅手动提交一次",
      allowMutationNow: true,
      shouldPoll: autoPushEnabled,
      autoRetryExpected: autoPushEnabled,
      requiresExternalAction: false,
      completionCondition,
    };
  }

  if (state === "推单失败") {
    const reason = String(exactReason || "");
    const base = {
      state,
      exactReason,
      allowMutationNow: false,
      shouldPoll: false,
      autoRetryExpected: false,
      requiresExternalAction: true,
      completionCondition,
    };

    if (/(?:余额|可用金额|账户金额).*(?:不足|不够|小于)|(?:余额不足|金额不足)/i.test(reason)) {
      return {
        ...base,
        category: "supplier_balance_insufficient",
        amounts: extractBalanceAmounts(reason),
        actionOwner: "user",
        recommendedAction: "手动充值对应供销商余额；充值后使用只读 watch 回查慧策自动重试，不要立即重复推单",
        shouldPoll: true,
        autoRetryExpected: autoPushEnabled,
      };
    }
    if (/(?:库存不足|无库存|缺货|库存为0)/i.test(reason)) {
      return {
        ...base,
        category: "supplier_stock_unavailable",
        actionOwner: "supplier_or_operator",
        recommendedAction: "核对精确供应商 SKU 的实时库存与供货状态；恢复库存或更换货源后再回查",
      };
    }
    if (/(?:价格变动|采购价|分销价|金额不一致|价格不一致|成本变动)/i.test(reason)) {
      return {
        ...base,
        category: "supplier_price_changed",
        actionOwner: "operator",
        recommendedAction: "刷新 SKU 实时成本并复算订单利润；确认不亏损后再处理推单",
      };
    }
    if (/(?:SKU|商品|规格).*(?:不存在|下架|失效|未匹配|不匹配)|(?:映射失败|规格不匹配)/i.test(reason)) {
      return {
        ...base,
        category: "supplier_sku_mapping_invalid",
        actionOwner: "operator",
        recommendedAction: "核对供应商商品状态、精确 SKU 与系统货品映射；修复或更换货源后再回查",
      };
    }
    if (/(?:不配送|地区限制|超出配送|物流模板|地址不可达|无法配送)/i.test(reason)) {
      return {
        ...base,
        category: "delivery_restriction",
        actionOwner: "operator_or_supplier",
        recommendedAction: "核对供应商配送范围及物流模板，不输出买家地址；建立可配送路径后再回查",
      };
    }
    if (/(?:未合作|授权失效|店铺停用|供应商停用|合作终止)/i.test(reason)) {
      return {
        ...base,
        category: "supplier_authorization_invalid",
        actionOwner: "operator_or_supplier",
        recommendedAction: "恢复供销合作或授权；无法恢复时更换供应商",
      };
    }
    if (/(?:登录失效|鉴权失败|token.*(?:过期|失效)|未登录|认证失败)/i.test(reason)) {
      return {
        ...base,
        category: "authentication_failure",
        actionOwner: "user_or_codex",
        recommendedAction: "刷新慧策登录态，然后先只读回查精确订单",
      };
    }
    if (isContractRejection(reason)) {
      return {
        ...base,
        category: "request_contract_error",
        actionOwner: "codex",
        recommendedAction: "修正顶层 JSON 请求体；重试前先回查订单，最多再提交一次",
        requiresExternalAction: false,
      };
    }
    return {
      ...base,
      category: "unknown_failure",
      actionOwner: "codex_or_operator",
      recommendedAction: exactReason
        ? "保留原始失败原因，检查订单详情、推单日志和接口响应；未定位原因前禁止盲目重试"
        : "失败原因缺失；继续查询订单详情与推单日志，未取得具体原因前禁止重试",
    };
  }

  return {
    state,
    category: "order_not_found_or_unknown_state",
    exactReason,
    actionOwner: "codex",
    recommendedAction: "重新查询四种状态及后续分页；仍未找到则报告具体阻断",
    allowMutationNow: false,
    shouldPoll: false,
    autoRetryExpected: false,
    requiresExternalAction: false,
    completionCondition,
  };
}

function classifyAttribution(evidence) {
  const pre = evidence.preMutationCheck || evidence.preflight;
  const submission = evidence.submission;
  const finalOrder = evidence.polling.at(-1)?.order || pre;
  const attemptedAt = parseErpTime(submission?.attemptedAt);
  const pushTime = parseErpTime(finalOrder?.pushTime || pre?.pushTime);

  if (evidence.preflight?.status === "推单成功" || evidence.preMutationCheck?.status === "推单成功") {
    return {
      code: evidence.autoPushEnabled
        ? "huice_auto_or_external_before_codex"
        : "external_before_codex",
      codexMutationCausedSuccess: false,
      reason: "The exact order was already successful before any Codex mutation.",
    };
  }

  if (finalOrder?.status === "推单成功" && (!submission || submission.skipped)) {
    return {
      code: evidence.autoPushEnabled
        ? "huice_auto_push_observed_by_codex"
        : "external_success_observed_by_codex",
      codexMutationCausedSuccess: false,
      reason: "Read-only polling observed the exact order become successful without a Codex mutation.",
    };
  }

  if (submission?.skipped && submission.reason === "already_processing") {
    return {
      code: evidence.autoPushEnabled
        ? "huice_auto_or_external_processing"
        : "external_processing",
      codexMutationCausedSuccess: false,
      reason: "Codex skipped because the exact order was already processing.",
    };
  }

  if (!submission || submission.skipped) {
    return {
      code: "no_codex_mutation",
      codexMutationCausedSuccess: false,
      reason: "No HTTP API mutation was submitted by Codex.",
    };
  }

  if (pushTime && attemptedAt && pushTime < attemptedAt) {
    return {
      code: "not_codex_http_api",
      codexMutationCausedSuccess: false,
      reason: "ERP push time predates the Codex mutation attempt.",
    };
  }

  if (submission.contractRejected) {
    return {
      code: "not_codex_http_api",
      codexMutationCausedSuccess: false,
      reason: "The mutation was rejected by request validation and created no business push.",
    };
  }

  if (submission.successTradeIds?.includes(evidence.preflight.tradeId) && finalOrder?.status === "推单成功") {
    return {
      code: "codex_http_api_confirmed",
      codexMutationCausedSuccess: true,
      reason: "The mutation explicitly accepted the exact tradeId and the order later became successful.",
    };
  }

  if (finalOrder?.status === "推单成功") {
    return {
      code: evidence.autoPushEnabled ? "unresolved_auto_or_codex" : "codex_http_api_likely",
      codexMutationCausedSuccess: null,
      reason: "Success followed the attempt, but the response did not directly prove which mechanism caused it.",
    };
  }

  return {
    code: "no_success_to_attribute",
    codexMutationCausedSuccess: false,
    reason: "The exact order has not reached business success.",
  };
}

function isContractRejection(message) {
  return /tradeIdList.*(?:null|empty)|must not be (?:null|empty)/i.test(message || "");
}

function createRequester({ baseUrl, cookie, appVersion }) {
  return async function request(endpoint, payload) {
    const requestBody = JSON.stringify(payload);
    const { statusCode, text } = await new Promise((resolve, reject) => {
      const req = https.request(`${baseUrl}${endpoint}`, {
        method: "POST",
        rejectUnauthorized: process.env.HUICE_TLS_INSECURE !== "1",
        headers: {
          accept: "application/json, text/plain, */*",
          "app-code": "web",
          "app-product-code": "jisu",
          "app-version": appVersion,
          "content-length": Buffer.byteLength(requestBody),
          "content-type": "application/json",
          cookie,
          origin: baseUrl,
          referer: `${baseUrl}/micro-app-new/erpx-web`,
        },
      }, (response) => {
        let responseBody = "";
        response.setEncoding("utf8");
        response.on("data", (chunk) => { responseBody += chunk; });
        response.on("end", () => resolve({ statusCode: response.statusCode || 0, text: responseBody }));
      });
      req.setTimeout(30_000, () => req.destroy(new Error("request timeout")));
      req.on("error", reject);
      req.end(requestBody);
    });

    let body;
    try {
      body = JSON.parse(text);
    } catch {
      throw new Error(`${endpoint} returned non-JSON HTTP ${statusCode}`);
    }
    if (statusCode < 200 || statusCode >= 300) {
      throw new Error(`${endpoint} returned HTTP ${statusCode}: ${body.msg || body.message || body.error || "unknown error"}`);
    }
    return body;
  };
}

async function locateTarget(request, platformOrder) {
  const matches = [];
  for (const status of STATUS_FILTERS) {
    for (let page = 1; page <= 10; page += 1) {
      const body = await request("/api/main/oms/tradeQuery/query", baseQuery(status.value, page));
      const rows = rowsFromResponse(body);
      for (const row of rows) {
        if (exactOrderNumber(row) === platformOrder) matches.push({ row, statusLabel: status.label });
      }
      if (rows.length < 50) break;
    }
  }

  const unique = new Map();
  for (const match of matches) unique.set(String(match.row.tradeId || ""), match);
  if (unique.size > 1) throw new Error(`Ambiguous exact order: found ${unique.size} Huice trade IDs`);
  return unique.values().next().value || null;
}

function validateTarget(order, options) {
  if (!order.tradeId) throw new Error("Exact-order safety check failed: missing tradeId");
  if (Number(order.platformId) !== options.platformId) {
    throw new Error(`Exact-order safety check failed: expected platform ${options.platformId}, got ${order.platformId}`);
  }
  if (order.shopName !== options.shopName) {
    throw new Error(`Exact-order safety check failed: expected shop ${options.shopName}, got ${order.shopName}`);
  }
  if (order.refundStatus && order.refundStatus !== "无退款") {
    throw new Error(`Order has refund state: ${order.refundStatus}`);
  }
}

function summarizeSubmission(response, tradeId, attemptedAt, completedAt) {
  const message = response.msg || response.message || null;
  const successTradeIds = (response.data?.successTradeIdList || response.successTradeIdList || []).map(String);
  const failures = (response.data?.failList || response.failList || []).map((item) => ({
    tradeId: item.tradeId ? String(item.tradeId) : null,
    tradeNo: item.tradeNo || null,
    message: item.message || item.msg || null,
  }));
  const explicitSuccess = successTradeIds.includes(tradeId);
  return {
    skipped: false,
    attemptedAt,
    completedAt,
    success: explicitSuccess || response.success === true || response.errorCode === 200 || response.code === 0,
    message,
    contractRejected: isContractRejection(message),
    successTradeIds,
    failures,
  };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(usage());
    return;
  }

  const cookie = process.env.HUICE_MAIN_COOKIE || "";
  if (!cookie.includes("X-HC-TOKEN=")) throw new Error("HUICE_MAIN_COOKIE is missing or not authenticated");

  const request = createRequester({
    baseUrl: process.env.HUICE_BASE_URL || DEFAULT_BASE_URL,
    cookie,
    appVersion: process.env.HUICE_APP_VERSION || "1.0.640",
  });

  const evidence = {
    schemaVersion: 3,
    recordedAt: new Date().toISOString(),
    platformOrder: options.platformOrder,
    mode: options.execute ? "execute_once" : options.watch ? "watch_read_only" : "read_only",
    autoPushEnabled: options.autoPushEnabled,
    endpoint: "/api/main/oms/omsPushOrder/pushOrder",
    requestRules: {
      source: 0,
      exactTradeIdRequired: true,
      maxMutationCalls: 1,
      skipStates: ["推单中", "推单成功"],
    },
    preflightCheckedAt: null,
    preflight: null,
    preflightDecision: null,
    preMutationCheckedAt: null,
    preMutationCheck: null,
    preMutationDecision: null,
    submission: null,
    polling: [],
    final: null,
    attribution: null,
    decision: null,
  };

  const located = await locateTarget(request, options.platformOrder);
  evidence.preflightCheckedAt = new Date().toISOString();
  if (!located) throw new Error(`Order ${options.platformOrder} was not found in WAIT_SEND_CLOUD push states`);
  evidence.preflight = sanitizeOrder(located.row, located.statusLabel);
  validateTarget(evidence.preflight, options);
  evidence.preflightDecision = diagnosePushState(evidence.preflight, {
    autoPushEnabled: options.autoPushEnabled,
  });

  if (options.execute) {
    const latest = await locateTarget(request, options.platformOrder);
    evidence.preMutationCheckedAt = new Date().toISOString();
    if (!latest) throw new Error("Exact order disappeared before mutation; no request submitted");
    evidence.preMutationCheck = sanitizeOrder(latest.row, latest.statusLabel);
    validateTarget(evidence.preMutationCheck, options);
    evidence.preMutationDecision = diagnosePushState(evidence.preMutationCheck, {
      autoPushEnabled: options.autoPushEnabled,
    });

    if (["推单成功", "推单中"].includes(evidence.preMutationCheck.status)) {
      evidence.submission = {
        skipped: true,
        reason: evidence.preMutationCheck.status === "推单成功" ? "already_success" : "already_processing",
      };
    } else if (evidence.preMutationCheck.status === "推单失败" && !options.failureRemediated) {
      evidence.submission = {
        skipped: true,
        reason: "failure_requires_resolution",
        category: evidence.preMutationDecision.category,
        recommendedAction: evidence.preMutationDecision.recommendedAction,
      };
    } else {
      const attemptedAt = new Date().toISOString();
      const response = await request("/api/main/oms/omsPushOrder/pushOrder", {
        source: 0,
        tradeIdList: [evidence.preMutationCheck.tradeId],
      });
      const completedAt = new Date().toISOString();
      evidence.submission = summarizeSubmission(
        response,
        evidence.preMutationCheck.tradeId,
        attemptedAt,
        completedAt,
      );
    }
  }

  const shouldPoll = options.watch || (options.execute && (
    !evidence.submission?.skipped || evidence.submission?.reason === "already_processing"
  ));
  if (shouldPoll) {
    for (let attempt = 1; attempt <= options.pollAttempts; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, attempt === 1 ? 1200 : 2500));
      const current = await locateTarget(request, options.platformOrder);
      const sanitized = current ? sanitizeOrder(current.row, current.statusLabel) : null;
      evidence.polling.push({ attempt, checkedAt: new Date().toISOString(), order: sanitized });
      if (sanitized?.status === "推单成功") break;
      if (options.execute && !evidence.submission?.skipped && sanitized?.status === "推单失败") break;
    }
  }

  const latest = evidence.polling.at(-1)?.order || evidence.preMutationCheck || evidence.preflight;
  const finalFailureReason = latest?.failureReason || evidence.submission?.failures?.[0]?.message || null;
  const finalOrder = latest ? { ...latest, failureReason: finalFailureReason } : null;
  const finalDecision = diagnosePushState(finalOrder, {
    autoPushEnabled: options.autoPushEnabled,
  });
  evidence.final = {
    status: latest?.status || "未找到",
    success: latest?.status === "推单成功",
    verified: finalDecision.verification?.verified || false,
    verification: finalDecision.verification || null,
    pushTime: latest?.pushTime || null,
    outsourceOrderNo: latest?.outsourceOrderNo || null,
    failureReason: finalFailureReason,
    diagnosis: finalDecision.category,
    nextAction: finalDecision.recommendedAction,
  };
  evidence.attribution = classifyAttribution(evidence);
  evidence.decision = finalDecision;

  const output = path.resolve(options.output || `outputs/huice-order-push-${shanghaiTimestamp()}.json`);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, `${JSON.stringify(evidence, null, 2)}\n`, { mode: 0o600 });
  console.log(JSON.stringify({
    output,
    platformOrder: options.platformOrder,
    tradeId: evidence.preflight.tradeId,
    preflightStatus: evidence.preflight.status,
    mutationSubmitted: Boolean(evidence.submission && !evidence.submission.skipped),
    submission: evidence.submission,
    final: evidence.final,
    attribution: evidence.attribution,
    decision: evidence.decision,
  }, null, 2));
}

module.exports = {
  STATUS_FILTERS,
  baseQuery,
  classifyAttribution,
  diagnosePushState,
  exactOrderNumber,
  extractBalanceAmounts,
  isContractRejection,
  parseArgs,
  parseErpTime,
  rowsFromResponse,
  sanitizeOrder,
  summarizeSubmission,
  usage,
  verifySuccess,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(JSON.stringify({ success: false, error: error.message }));
    process.exit(1);
  });
}
