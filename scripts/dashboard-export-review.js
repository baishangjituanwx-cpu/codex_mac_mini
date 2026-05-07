#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const PLATFORM_CONFIG = [
  { key: "kuaishou", name: "快手", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读"] },
  { key: "wechat", name: "视频号", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读"] },
  { key: "weibo", name: "微博", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读"] },
  { key: "toutiao", name: "头条号", contentType: "图文", defaultPrimaryLabel: "阅读", preferredLabels: ["阅读", "展现", "推荐量"] },
  { key: "baijiahao", name: "百家号", contentType: "图文", defaultPrimaryLabel: "阅读", preferredLabels: ["阅读", "推荐量"] },
  { key: "douyin", name: "抖音", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读"] },
  { key: "bilibili", name: "B站", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读"] },
  { key: "zhihu", name: "知乎", contentType: "图文", defaultPrimaryLabel: "阅读", preferredLabels: ["阅读", "赞同", "评论"] },
];
const DASHBOARD_PLATFORM_NAME_SET = new Set(PLATFORM_CONFIG.map((item) => item.name));
const SUPPLEMENTAL_PLATFORM_NAMES = ["小红书"];
const PLATFORM_LIST_PATTERN = new RegExp(
  `(?:${[...DASHBOARD_PLATFORM_NAME_SET, ...SUPPLEMENTAL_PLATFORM_NAMES].join("|")})(?:\\s*[\\/／、,，]\\s*(?:${[...DASHBOARD_PLATFORM_NAME_SET, ...SUPPLEMENTAL_PLATFORM_NAMES].join("|")}))+`,
  "g"
);

const METRIC_PATTERNS = [
  ["播放", /播放(?:量)?\s*`?([\d,]+)`?/g],
  ["阅读", /阅读(?:量)?\s*`?([\d,]+)`?/g],
  ["展现", /展现(?:量)?\s*`?([\d,]+)`?/g],
  ["推荐量", /推荐量\s*`?([\d,]+)`?/g],
  ["点赞", /点赞(?:量)?\s*`?([\d,]+)`?/g],
  ["评论", /评论(?:量)?\s*`?([\d,]+)`?/g],
  ["分享", /分享(?:量)?\s*`?([\d,]+)`?/g],
  ["收藏", /收藏(?:量)?\s*`?([\d,]+)`?/g],
  ["赞同", /赞同(?:量)?\s*`?([\d,]+)`?/g],
  ["推荐", /推荐\s*`?([\d,]+)`?/g],
  ["粉丝", /粉丝(?:量)?\s*`?([\d,]+)`?/g],
  ["累计投稿量", /累计投稿量\s*`?([\d,]+)`?/g],
  ["累计阅读", /累计阅读(?:\(播放\)量)?\s*`?([\d,]+)`?/g],
  ["总粉丝量", /总粉丝量\s*`?([\d,]+)`?/g],
];

const METRIC_DISPLAY_LABELS = {
  播放: "播放量",
  阅读: "阅读量",
  展现: "展现量",
  推荐量: "推荐量",
  点赞: "点赞量",
  评论: "评论量",
  分享: "分享量",
  收藏: "收藏量",
  赞同: "赞同",
  推荐: "推荐量",
  粉丝: "粉丝量",
  互动: "互动",
};

const STATUS_CODE_LABELS = {
  under_review: "审核中",
  published: "已发布",
  submitted_pending_public_verification: "待公开页核验",
  submitted_verified_in_manager: "管理页已命中",
  published_verified_in_manager: "后台已确认发布",
  not_started: "未启动",
  not_published: "未发布",
  ready_for_publish: "待发布",
  publish_failed: "发布失败",
  draft_saved: "草稿已保存",
};

const STATUS_CODE_PATTERN = new RegExp(`\\b(${Object.keys(STATUS_CODE_LABELS).join("|")})\\b`, "g");
const SAMPLE_LABEL_PATTERN = /^(历史|近作|账号|对照)(播放|阅读|展现|推荐量|赞同|评论|互动)(\d+)?$/;

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

function readText(absPath) {
  return fs.readFileSync(absPath, "utf-8");
}

function findLatestReviewReport(rootDir, reviewDate) {
  const dir = path.join(rootDir, "content-library", "logs", "review");
  const entries = fs.readdirSync(dir).filter((n) => n.startsWith(`${reviewDate}-`) && n.endsWith("-review.md"));
  if (entries.length === 0) return null;
  const ranked = entries
    .map((name) => {
      const abs = path.join(dir, name);
      const stat = fs.statSync(abs);
      return { abs, mtimeMs: stat.mtimeMs };
    })
    .sort((a, b) => b.mtimeMs - a.mtimeMs);
  return ranked[0].abs;
}

function inferBatchFromReviewFilename(reviewDate, reviewAbs) {
  const base = path.basename(reviewAbs);
  const prefix = `${reviewDate}-`;
  const suffix = "-review.md";
  if (!base.startsWith(prefix) || !base.endsWith(suffix)) {
    throw new Error(`Unexpected review filename: ${base}`);
  }
  return base.slice(prefix.length, base.length - suffix.length);
}

function firstNonEmptyLine(afterIndex, lines) {
  for (let i = afterIndex; i < lines.length; i += 1) {
    const trimmed = lines[i].trim();
    if (trimmed.length > 0) return trimmed;
  }
  return null;
}

function sanitizeBoardScopeText(value) {
  const input = normalizeOpsWording(value);
  if (!input) return "";
  return input
    .replace(PLATFORM_LIST_PATTERN, (match) => {
      const filtered = match
        .split(/[\/／、,，]/)
        .map((item) => cleanInline(item))
        .filter((item) => DASHBOARD_PLATFORM_NAME_SET.has(item));
      return [...new Set(filtered)].join(" / ");
    })
    .replace(/（\s*）/g, "")
    .replace(/\(\s*\)/g, "")
    .replace(/([：:])\s*([；;，,。])/g, "$2")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function extractVideoPackageTitle(md, { platform }) {
  const lines = md.split("\n");
  const secIndex = lines.findIndex((l) => l.trim() === platform.trim());
  if (secIndex < 0) return null;
  const start = secIndex + 1;
  for (let i = start; i < Math.min(lines.length, start + 200); i += 1) {
    if (lines[i].trim() === "### 标题" || lines[i].trim() === "### 短标题") {
      return cleanInline(firstNonEmptyLine(i + 1, lines) || "");
    }
  }
  return null;
}

function cleanInline(value) {
  return String(value || "")
    .replace(/`/g, "")
    .replace(/[“”]/g, "\"")
    .replace(/\s+/g, " ")
    .trim();
}

function normalizeOpsWording(value) {
  let text = cleanInline(value);
  if (!text) return "";
  text = text.replace(STATUS_CODE_PATTERN, (_, code) => STATUS_CODE_LABELS[code] || code);
  return text
    .replace(/\bKeep\b/g, "保留")
    .replace(/\bRetest\b/g, "复测")
    .replace(/\bWatch\b/g, "观察")
    .replace(/\bCut\b/g, "停止")
    .replace(/latest known status=/g, "最新状态：")
    .replace(/manager row status=/g, "管理页状态：")
    .replace(/管理页状态词=/g, "管理页状态：")
    .replace(/管理页行文本显示/g, "管理页状态：")
    .replace(/\bmanager verified\b/gi, "后台已确认发布")
    .replace(/\bBrowser Bridge\b/g, "浏览器桥接")
    .replace(/\blive publish\b/gi, "正式发布")
    .replace(/\blive\b/gi, "正式发布")
    .replace(/\baudit-wait-no-republish\b/g, "待审不重发批次")
    .replace(/\bno-new-batch\b/g, "无新批次")
    .replace(/\bshare link\b/gi, "公开链接")
    .replace(/\blink\b/gi, "链接")
    .replace(/\bpin\b/gi, "置顶位")
    .replace(/share链接/g, "公开链接")
    .replace(/\breceipt\b/gi, "回执")
    .replace(/公开链接历史样本/g, "历史公开链接样本")
    .replace(/公开链接\s+历史样本/g, "历史公开链接样本")
    .replace(/已有\s+历史公开链接样本/g, "已有历史公开链接样本")
    .replace(/均有\s+历史公开链接样本/g, "均有历史公开链接样本")
    .replace(/待发包明确是\s*未发布/g, "待发包：未发布")
    .replace(/待发包=\s*未发布/g, "待发包：未发布")
    .replace(/未完成内容级核验/g, "未完成作品级核验")
    .replace(/([\u4e00-\u9fa5A-Za-z0-9])\s+(公开链接|回执|链接|置顶位)/g, "$1$2")
    .replace(/均为\s+已发布/g, "均为已发布")
    .replace(/从\s+(\d{2}-\d{2})\s+([^，；]+?)\s+到\s+(\d{2}-\d{2})\s+([^，；]+?)\s+再到\s+(\d{2}-\d{2})\s+([^，；]+)/g, "从 $1 $2，到 $3 $4，再到 $5 $6")
    .replace(/(\d{2}-\d{2})\s*到\s*(\d{2}-\d{2})/g, "$1 到 $2")
    .replace(/(\d{4}-\d{2}-\d{2})\s*到\s*(\d{4}-\d{2}-\d{2})/g, "$1 到 $2")
    .replace(/到\s+(\d{2}-\d{2})/g, "到$1")
    .replace(/([到再])(\d{2}-\d{2})/g, "$1 $2")
    .replace(/([到再])(\d{4}-\d{2}-\d{2})/g, "$1 $2")
    .replace(/跑到\s+后台已确认发布/g, "跑到后台已确认发布")
    .replace(/连续多批\s+审核中/g, "连续多批处于审核中")
    .replace(/浏览器桥接\s+断开/g, "浏览器桥接断开")
    .replace(/问题在\s+浏览器桥接/g, "问题在浏览器桥接")
    .replace(/主动作/g, "当前重点")
    .replace(/不进入\s*正式发布/g, "不进入正式发布流程")
    .replace(/当成\s*正式发布\s*替代/g, "当成正式发布替代方案")
    .replace(/最新状态：([^；，\/]+)\s*\/\s*\1/g, "最新状态：$1")
    .replace(/：\s+/g, "：")
    .replace(/\s*\/\s*/g, " / ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function buildSampleMetricLabel(baseLabel, index) {
  return `${baseLabel}${index + 1}`;
}

function isSampleMetricLabel(label) {
  return SAMPLE_LABEL_PATTERN.test(cleanInline(label));
}

function normalizePrimaryMetric(config, metric) {
  if (!metric) return { label: config.defaultPrimaryLabel, value: 0 };
  if (isSampleMetricLabel(metric.label)) {
    return { label: metric.label.replace(/\d+$/, ""), value: metric.value };
  }
  return metric;
}

function inferSampleMetricPrefix(text, fallbackPrefix = "对照") {
  const input = normalizeOpsWording(text);
  if (!input) return fallbackPrefix;
  if (input.includes("历史")) return "历史";
  if (input.includes("近几条") || input.includes("近作") || input.includes("最近")) return "近作";
  if (input.includes("账号盘面") || input.includes("近30日") || input.includes("账号")) return "账号";
  return fallbackPrefix;
}

function inferMetricTypeFromText(text, config) {
  const input = normalizeOpsWording(text);
  if (!input) return config.defaultPrimaryLabel;
  const metricHints = [
    ["播放", /播放(?:量)?|播放样本|完播|转码/],
    ["阅读", /阅读(?:量)?|阅读样本/],
    ["展现", /展现(?:量)?/],
    ["推荐量", /推荐量|推荐/],
    ["赞同", /赞同/],
    ["评论", /评论/],
    ["互动", /互动/],
  ];
  for (const [label, pattern] of metricHints) {
    if (pattern.test(input)) return label;
  }
  return config.defaultPrimaryLabel;
}

function inferSampleMetricBaseLabel(text, config, fallbackPrefix = "对照") {
  const prefix = inferSampleMetricPrefix(text, fallbackPrefix);
  const metricType = inferMetricTypeFromText(text, config);
  return `${prefix}${metricType}`;
}

function extractMetricTypeFromLabel(label, fallbackLabel) {
  const match = cleanInline(label).match(/(播放|阅读|展现|推荐量|赞同|评论|互动)/);
  return match ? match[1] : fallbackLabel;
}

function displayMetricType(label) {
  return METRIC_DISPLAY_LABELS[label] || label || "指标";
}

function extractDateLabels(text) {
  const input = normalizeOpsWording(text);
  if (!input) return [];
  const matches = [...input.matchAll(/(\d{4}-\d{2}-\d{2}|\d{2}-\d{2})/g)];
  return matches.map((match) => {
    const value = match[1];
    return value.length === 10 ? value.slice(5) : value;
  });
}

function relabelMetricsWithDates(metrics, contextText, fallbackLabel) {
  const dates = extractDateLabels(contextText);
  if (!metrics.length || !dates.length || dates.length < metrics.length) return metrics;
  return metrics.map((metric, index) => ({
    ...metric,
    label: `${dates[index]} ${displayMetricType(extractMetricTypeFromLabel(metric.label, fallbackLabel))}`,
  }));
}

function extractCurrentZeroMetric(text, config) {
  const input = normalizeOpsWording(text);
  if (!input) return null;
  if (!/(当前条目|当前条|当前作品|管理页当前条|当前可见)/.test(input)) return null;
  if (!/(仍为\s*0|为\s*0|暂无|暂未可见|未补抓)/.test(input)) return null;
  return {
    label: inferMetricTypeFromText(input, config),
    value: 0,
  };
}

function extractHistoricalVisibleMetrics(text, config) {
  const input = normalizeOpsWording(text);
  if (!input || !/历史/.test(input)) return [];
  return collectPackedSeries(input, inferSampleMetricBaseLabel(input, config, "历史"));
}

function dedupeMetricItems(metrics) {
  const output = [];
  const seen = new Set();
  for (const metric of metrics) {
    if (!metric) continue;
    const label = cleanInline(metric.label);
    const value = metric.value;
    const key = `${label}:${value}`;
    if (!label || seen.has(key)) continue;
    seen.add(key);
    output.push({ label, value });
  }
  return output;
}

function buildCurrentWindowMetrics(statusText, currentMetrics) {
  const base = statusText ? [{ label: "状态", value: statusText }] : [];
  return dedupeMetricItems([...base, ...currentMetrics]).slice(0, 4);
}

function isIncompleteVerificationLabel(label) {
  const input = normalizeOpsWording(label);
  return input.includes("未完成作品级核验") || input.includes("待作品级核验");
}

function normalizeVerificationDisplay(label) {
  const input = normalizeOpsWording(label);
  if (!input) return "-";
  if (input.includes("未完成作品级核验")) return "待作品级核验";
  return input;
}

function metricCell(label, value) {
  return {
    label: cleanInline(label),
    value: typeof value === "number" ? value : cleanInline(value) || "-",
  };
}

function finalizeWindowMetrics(metrics, fallbackLabels) {
  const output = [];
  const seen = new Set();
  for (const metric of metrics) {
    if (!metric) continue;
    const next = metricCell(metric.label, metric.value);
    if (!next.label || seen.has(next.label)) continue;
    seen.add(next.label);
    output.push(next);
    if (output.length === 4) return output;
  }
  for (const label of fallbackLabels) {
    const normalizedLabel = cleanInline(label);
    if (!normalizedLabel || seen.has(normalizedLabel)) continue;
    seen.add(normalizedLabel);
    output.push(metricCell(normalizedLabel, "-"));
    if (output.length === 4) break;
  }
  return output.slice(0, 4);
}

function extractBatchTag(statusText) {
  const input = normalizeOpsWording(statusText);
  const match = input.match(/(\d{2}-\d{2})\s*基线/);
  return match ? `${match[1]}基线` : "本轮";
}

function extractMainStatus(statusText) {
  const input = normalizeOpsWording(statusText);
  if (/仍未发现.*回执|缺.*回执|回执缺口/.test(input)) return "待回执";
  if (/待公开页核验|公开页未确认/.test(input)) return "待公开页核验";
  if (/审核中|转码中/.test(input) && /管理页/.test(input)) return "审核中";
  const candidates = ["后台已确认发布", "已发布", "待公开页核验", "管理页已命中", "审核中", "草稿已保存", "待发布", "未发布", "未启动"];
  for (const candidate of candidates) {
    if (input.includes(candidate)) {
      return candidate === "后台已确认发布" ? "已发布" : candidate;
    }
  }
  return input || "-";
}

function extractManagerStatus(statusText, verification) {
  const input = normalizeOpsWording(statusText);
  const managerMatch = input.match(/管理页状态：([^；，]+)/);
  if (managerMatch) return cleanInline(managerMatch[1]);
  if (input.includes("管理页已命中")) return "已命中";
  if (normalizeVerificationDisplay(verification).includes("后台已核验")) return "已核验";
  return "-";
}

function inferEvidenceClosure(statusText, verification, diagnosis, action) {
  const input = normalizeOpsWording([statusText, verification, diagnosis, action].filter(Boolean).join("；"));
  if (/未发现.*回执|缺.*回执|回执缺口/.test(input)) return "缺回执";
  if (/后台已确认发布/.test(input)) return "后台已确认";
  if (/(管理页已命中|后台已核验)/.test(input) && /审核中|转码中/.test(input)) return "已命中待审核";
  if (/待公开页核验|公开页未确认|公开页复核|补.*公开页|补.*链接|缺.*链接/.test(input)) return "待公开页";
  if (/缺少管理页行|补查.*管理页|补抓.*管理页|待补管理页/.test(input)) return "待管理页";
  if (/未完成作品级核验/.test(input) && /已发布/.test(input)) return "待二次核验";
  if (/后台已确认发布|后台已核验|管理页已命中/.test(input)) return "管理页已确认";
  return "-";
}

function inferDataRecovery(visibleText, currentMetrics, diagnosis, action) {
  const input = normalizeOpsWording([visibleText, diagnosis, action].filter(Boolean).join("；"));
  if (currentMetrics.some((metric) => typeof metric.value === "number" && metric.value > 0)) return "已回收";
  if (/24h|数据中心|指标|暂未可见|暂无|未补抓|仍为 0|为 0/.test(input)) return "待补";
  return "-";
}

function splitReferenceEntries(text) {
  const input = normalizeOpsWording(text);
  if (!input) return [];
  return input
    .split(/[；;]/)
    .map((item) => cleanInline(item))
    .filter(Boolean);
}

function countReferenceSamples(...texts) {
  const dateSet = new Set();
  for (const text of texts) {
    for (const date of extractDateLabels(text)) {
      dateSet.add(date);
    }
  }
  if (dateSet.size > 0) return dateSet.size;
  const items = texts.flatMap((text) => splitReferenceEntries(text));
  return items.length;
}

function extractRecentDates(text, limit = 2) {
  return [...new Set(extractDateLabels(text))].slice(0, limit);
}

function deriveCoverageValue(accountText, compareText) {
  const input = normalizeOpsWording([accountText, compareText].filter(Boolean).join("；"));
  const rangeMatch = input.match(/近\s*(\d+)\s*到\s*(\d+)\s*条/);
  if (rangeMatch) return `${rangeMatch[1]}-${rangeMatch[2]}条`;
  if (/近两批|两批/.test(input)) return "2 批";
  if (/连续多批/.test(input)) return "多批";
  const sampleCount = countReferenceSamples(accountText, compareText);
  return sampleCount > 0 ? `${sampleCount} 条` : "-";
}

function deriveAccountHealth(accountText, diagnosis) {
  const input = normalizeOpsWording([accountText, diagnosis].filter(Boolean).join("；"));
  if (/最稳定|稳定/.test(input)) return "稳定";
  if (/链路可跑|说明账号可发|具备稳定同形态对照条件|链路在改善|账号可发/.test(input)) return "可发";
  if (/审核/.test(input) && /慢|等待|停留|停滞/.test(input)) return "审核慢";
  if (/待核验|证据缺口|缺少|未完成/.test(input)) return "待核验";
  return "观察中";
}

function derivePrimaryBlocker(statusText, diagnosis, action) {
  const statusAndDiagnosis = normalizeOpsWording([statusText, diagnosis].filter(Boolean).join("；"));
  const input = normalizeOpsWording([statusText, diagnosis, action].filter(Boolean).join("；"));
  if (/未发现.*回执|缺.*回执|receipt/.test(input)) return "回执缺口";
  if (/公开页|公开链接|链接/.test(input)) return "公开页待补";
  if (/审核|转码/.test(statusAndDiagnosis)) return "审核等待";
  if (/24h|数据中心|阅读|播放|互动|赞同|评论|收藏|指标/.test(input) && /补|未补抓|缺/.test(input)) return "24h待补";
  if (/待发包|allow_live|执行决策/.test(input)) return "待发决策";
  return "继续观察";
}

function deriveActionFocus(action) {
  const input = normalizeOpsWording(action);
  const candidates = [
    { label: "补管理页", pattern: /管理页/ },
    { label: "补公开页", pattern: /公开页|公开链接|链接/ },
    { label: "补24h数据", pattern: /24h|数据中心|阅读|播放|互动|赞同|评论|收藏|指标/ },
    { label: "先不重发", pattern: /不.*重发|不触发重发|不进入正式发布/ },
    { label: "继续观察", pattern: /跟踪|观察|复查/ },
  ];
  let best = null;
  for (const candidate of candidates) {
    const match = input.match(candidate.pattern);
    if (!match) continue;
    const index = match.index ?? Number.MAX_SAFE_INTEGER;
    if (!best || index < best.index) {
      best = { label: candidate.label, index };
    }
  }
  if (best) return best.label;
  return "待处理";
}

function buildTodayWindowMetrics({ statusText, verification, currentMetrics, visibleText, diagnosis, action }) {
  return finalizeWindowMetrics(
    [
      { label: "发布状态", value: extractMainStatus(statusText) },
      { label: "管理页", value: extractManagerStatus(statusText, verification) },
      { label: "证据闭环", value: inferEvidenceClosure(statusText, verification, diagnosis, action) },
      { label: "24h数据", value: inferDataRecovery(visibleText, currentMetrics, diagnosis, action) },
    ],
    ["发布状态", "管理页", "证据闭环", "24h数据"]
  );
}

function buildComparisonWindowMetrics(compareMetrics, compareText) {
  const sampleCount = countReferenceSamples(compareText);
  const recentDates = extractRecentDates(compareText, 2);
  if (compareMetrics.length > 0) {
    return finalizeWindowMetrics(
      [
        ...compareMetrics.slice(0, 2),
        { label: "对照样本", value: `${sampleCount || compareMetrics.length} 条` },
        { label: "主指标回收", value: "已回收" },
      ],
      ["对照样本", "主指标回收", "最新样本", "次新样本"]
    );
  }
  return finalizeWindowMetrics(
    [
      { label: "对照样本", value: sampleCount > 0 ? `${sampleCount} 条` : "-" },
      { label: "最新样本", value: recentDates[0] || "-" },
      { label: "次新样本", value: recentDates[1] || "-" },
      { label: "主指标回收", value: sampleCount > 0 ? "待补" : "-" },
    ],
    ["对照样本", "最新样本", "次新样本", "主指标回收"]
  );
}

function buildAccountWindowMetrics(accountText, compareText, statusText, diagnosis, action) {
  return finalizeWindowMetrics(
    [
      { label: "链路判断", value: deriveAccountHealth(accountText, diagnosis) },
      { label: "样本覆盖", value: deriveCoverageValue(accountText, compareText) },
      { label: "主要问题", value: derivePrimaryBlocker(statusText, diagnosis, action) },
      { label: "当前动作", value: deriveActionFocus(action) },
    ],
    ["链路判断", "样本覆盖", "主要问题", "当前动作"]
  );
}

function buildPrimaryMetricSummary(comparableCards, verifiedCards) {
  if (comparableCards.length > 0) {
    const leadCard = comparableCards.sort((a, b) => b.primaryValue - a.primaryValue)[0];
    return {
      label: "24h数据回收",
      value: `${comparableCards.length} / 8`,
      note: `已回收到可比较主指标的平台共有 ${comparableCards.length} 个；当前先以 ${leadCard.name} ${leadCard.primaryLabel} ${leadCard.primaryValue} 作为已回收样本。`,
      tone: "cool",
    };
  }
  if (verifiedCards.length > 0) {
    return {
      label: "24h数据回收",
      value: "待补 24h 主指标",
      note: "当前已核验平台仍以发布状态和审核状态为主，尚未回收到可横向比较的播放或阅读数据；先补 24h 主指标，再判断平台强弱。",
      tone: "warning",
    };
  }
  return {
    label: "24h数据回收",
    value: "暂无主指标",
    note: "本轮还没有平台进入主指标回收阶段。",
    tone: "warning",
  };
}

function disambiguatePackedSeries(text) {
  const input = String(text || "").replace(
    /(\d{2}-\d{2})(?:\s*\/\s*(\d{2}-\d{2}))+/g,
    (match) => match.split("/").map((item) => cleanInline(item)).join("、")
  );
  return input.replace(/(\d[\d,]*(?:\s*\/\s*\d[\d,]*)+)/g, (match) => {
    const parts = match.split("/").map((item) => cleanInline(item)).filter(Boolean);
    if (parts.length < 2) return match;
    return parts.join("、");
  });
}

function flattenRawField(value) {
  if (Array.isArray(value)) {
    return value.map((item) => cleanInline(item)).filter(Boolean).join("；");
  }
  return cleanInline(value);
}

function flattenField(value) {
  return disambiguatePackedSeries(flattenRawField(value));
}

function fieldList(fields, label) {
  const value = fields[label];
  if (Array.isArray(value)) {
    return value.map((item) => cleanInline(item)).filter(Boolean);
  }
  const single = cleanInline(value);
  return single ? [single] : [];
}

function fieldText(fields, ...labels) {
  for (const label of labels) {
    if (fields[label] !== undefined) {
      return flattenField(fields[label]);
    }
  }
  return "";
}

function rawFieldText(fields, ...labels) {
  for (const label of labels) {
    if (fields[label] !== undefined) {
      return flattenRawField(fields[label]);
    }
  }
  return "";
}

function extractSectionBody(md, exactHeading) {
  const lines = md.split("\n");
  const startIndex = lines.findIndex((line) => line.trim() === exactHeading.trim());
  if (startIndex < 0) return "";
  let endIndex = lines.length;
  for (let i = startIndex + 1; i < lines.length; i += 1) {
    if (/^##\s+/.test(lines[i])) {
      endIndex = i;
      break;
    }
  }
  return lines.slice(startIndex + 1, endIndex).join("\n").trim();
}

function parseBulletFields(block) {
  const fields = {};
  const lines = block.split("\n");
  let currentKey = "";
  let currentItems = [];

  function flush() {
    if (!currentKey) return;
    const cleaned = currentItems.map((item) => cleanInline(item)).filter(Boolean);
    if (cleaned.length === 0) {
      fields[currentKey] = "";
    } else if (cleaned.length === 1) {
      fields[currentKey] = cleaned[0];
    } else {
      fields[currentKey] = cleaned;
    }
    currentKey = "";
    currentItems = [];
  }

  for (const line of lines) {
    const topLevel = line.match(/^- ([^：:]+)[：:]\s*(.*)$/);
    if (topLevel) {
      flush();
      currentKey = cleanInline(topLevel[1]);
      const initial = cleanInline(topLevel[2]);
      if (initial) currentItems.push(initial);
      continue;
    }
    if (!currentKey) continue;
    const nested = line.match(/^\s+-\s*(.*)$/);
    if (nested) {
      const next = cleanInline(nested[1]);
      if (next) currentItems.push(next);
      continue;
    }
    const plain = cleanInline(line);
    if (plain) currentItems.push(plain);
  }
  flush();
  return fields;
}

function parsePlatformSections(reviewMd) {
  const section = extractSectionBody(reviewMd, "## 3. 分平台详细状态");
  if (!section) return {};
  const headingMatches = [...section.matchAll(/^###\s*(.+)$/gm)];
  const sections = {};
  for (let index = 0; index < headingMatches.length; index += 1) {
    const title = cleanInline(headingMatches[index][1]);
    const bodyStart = headingMatches[index].index + headingMatches[index][0].length;
    const bodyEnd = index + 1 < headingMatches.length ? headingMatches[index + 1].index : section.length;
    const body = section.slice(bodyStart, bodyEnd).trim();
    sections[title] = parseBulletFields(body);
  }
  return sections;
}

function parseNumber(raw) {
  return Number(String(raw).replace(/,/g, ""));
}

function collectLabeledMetrics(text) {
  const output = [];
  const seen = new Set();
  const input = cleanInline(text);
  if (!input) return output;
  for (const [label, pattern] of METRIC_PATTERNS) {
    const regex = new RegExp(pattern.source, pattern.flags);
    let match;
    while ((match = regex.exec(input))) {
      const value = parseNumber(match[1]);
      const key = `${label}:${value}`;
      if (seen.has(key)) continue;
      seen.add(key);
      output.push({ label, value });
    }
  }
  return output;
}

function collectPackedSeries(text, baseLabel) {
  const input = cleanInline(text)
    .replace(/\b\d{2}-\d{2}(?:\s*\/\s*\d{2}-\d{2})+\b/g, "")
    .replace(/\b\d{4}-\d{2}-\d{2}(?:\s*\/\s*\d{4}-\d{2}-\d{2})+\b/g, "");
  if (!input) return [];
  const packed = input.match(/\d[\d,]*(?:\s*\/\s*\d[\d,]*)+/);
  if (!packed) return [];
  const resolvedBaseLabel = cleanInline(baseLabel) || "对照播放";
  return packed[0]
    .split("/")
    .map((item) => parseNumber(item.trim()))
    .map((value, index) => ({ label: buildSampleMetricLabel(resolvedBaseLabel, index), value }));
}

function choosePrimaryMetric(config, metrics) {
  for (const label of config.preferredLabels) {
    const found = metrics.find((metric) => metric.label === label);
    if (found) return found;
  }
  return metrics[0] || { label: config.defaultPrimaryLabel, value: 0 };
}

function parseDateTime(text, reviewDate) {
  const input = cleanInline(text);
  if (!input) return "";
  let match = input.match(/(\d{4})年(\d{2})月(\d{2})日\s*(\d{2}:\d{2})/);
  if (match) return `${match[1]}-${match[2]}-${match[3]} ${match[4]}`;
  match = input.match(/(\d{4})-(\d{2})-(\d{2})\s*(\d{2}:\d{2})/);
  if (match) return `${match[1]}-${match[2]}-${match[3]} ${match[4]}`;
  match = input.match(/(\d{2})-(\d{2})\s*(\d{2}:\d{2})/);
  if (match) {
    const year = reviewDate.slice(0, 4);
    return `${year}-${match[1]}-${match[2]} ${match[3]}`;
  }
  match = input.match(/(\d{4})-(\d{2})-(\d{2})/);
  if (match) return `${match[1]}-${match[2]}-${match[3]}`;
  return "";
}

function extractTitleCandidate(text) {
  const input = cleanInline(text);
  if (!input) return "";
  const patterns = [
    /后台标题显示为[「"]([^」"]+)[」"]/,
    /标题显示为[「"]([^」"]+)[」"]/,
    /标题[「"]([^」"]+)[」"]/,
    /短标题[「"]([^」"]+)[」"]/,
  ];
  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) return cleanInline(match[1]);
  }
  return "";
}

function buildFallbackTitleMap(sharedMd, videoMd, weiboMd, zhihuMd, baijiahaoMd, toutiaoMd) {
  const linesForSection = (md) => {
    const lines = md.split("\n");
    const idx = lines.findIndex((line) => line.trim() === "## 标题");
    return idx < 0 ? "" : cleanInline(firstNonEmptyLine(idx + 1, lines) || "");
  };
  return {
    抖音: extractVideoPackageTitle(videoMd, { platform: "## 二、抖音" }),
    快手: extractVideoPackageTitle(videoMd, { platform: "## 三、快手" }),
    视频号: extractVideoPackageTitle(videoMd, { platform: "## 四、视频号" }),
    微博: linesForSection(weiboMd),
    知乎: linesForSection(zhihuMd),
    百家号: linesForSection(baijiahaoMd),
    头条号: linesForSection(toutiaoMd),
    B站: "",
    _theme:
      (() => {
        const match = sharedMd.match(/theme:\\s*\"([^\"]+)\"/);
        return match ? cleanInline(match[1]) : "";
      })() || "平台执行三步（改写/分发/回填复盘）",
  };
}

function buildMissingPlatformCard({ reviewDate, config, latestTitle, reason }) {
  return {
    key: config.key,
    name: config.name,
    status: "warning",
    statusLabel: "复盘正文缺少平台段落",
    latestTitle: latestTitle || "-",
    publishTime: `${reviewDate} · 待补`,
    contentType: config.contentType,
    primaryLabel: config.defaultPrimaryLabel,
    primaryValue: 0,
    compareLabel: "近几条对照",
    baselineValue: 0,
    baselineNote: reason,
    windows: [
      { label: "今日", headline: reason, metrics: finalizeWindowMetrics([], ["发布状态", "管理页", "证据闭环", "24h数据"]) },
      { label: "近7日账号", headline: "-", metrics: finalizeWindowMetrics([], ["对照样本", "最新样本", "次新样本", "主指标回收"]) },
      { label: "近30日账号", headline: "-", metrics: finalizeWindowMetrics([], ["链路判断", "样本覆盖", "主要问题", "当前动作"]) },
    ],
    metrics: [
      { label: "核验状态", value: "缺失平台段落" },
      { label: "发布状态", value: "待补" },
      { label: config.defaultPrimaryLabel, value: 0 },
      { label: "决策", value: "复测" },
    ],
    diagnosis: reason,
    action: "补齐该平台的复盘段落后重新导出并上传数据面板。",
  };
}

function buildPlatformCard({ reviewDate, config, fields, titleFallback }) {
  const verification = normalizeOpsWording(fieldText(fields, "核验等级") || "未完成作品级核验");
  const verificationDisplay = normalizeVerificationDisplay(verification);
  const currentWorkItems = fieldList(fields, "当前作品（后台可见）");
  const currentWorkText = normalizeOpsWording(fieldText(fields, "当前作品（后台可见）", "当前作品"));
  const currentWorkRaw = rawFieldText(fields, "当前作品（后台可见）", "当前作品");
  const visibleText = normalizeOpsWording(fieldText(fields, "当前可见数据"));
  const visibleRaw = rawFieldText(fields, "当前可见数据");
  const accountText = normalizeOpsWording(fieldText(fields, "账号盘面"));
  const accountRaw = rawFieldText(fields, "账号盘面");
  const compareText = normalizeOpsWording(fieldText(fields, "近几条对照"));
  const compareRaw = rawFieldText(fields, "近几条对照");
  const statusText = normalizeOpsWording(fieldText(fields, "发布状态") || "-");
  const diagnosis = normalizeOpsWording(fieldText(fields, "诊断") || "复盘正文未给出诊断。");
  const action = normalizeOpsWording(fieldList(fields, "明日动作").join("；") || fieldText(fields, "明日动作") || "待补下一步动作。");
  const rawDecision = fieldText(fields, "决策") || "-";
  const decision = normalizeOpsWording(rawDecision);

  const explicitTitle =
    extractTitleCandidate(currentWorkText) ||
    extractTitleCandidate(fieldText(fields, "计划内容")) ||
    titleFallback ||
    "-";

  const hasNoContent = /无发布项|未计划发布|本批次未发现/.test(currentWorkText) || /无发布项|未计划发布/.test(fieldText(fields, "计划内容"));
  const currentZeroMetric = extractCurrentZeroMetric(visibleRaw, config);
  const historicalVisibleMetrics = extractHistoricalVisibleMetrics(visibleRaw, config);
  const currentMetricSource = currentWorkItems[0] || currentWorkRaw || (hasNoContent ? "" : visibleRaw);
  let currentMetrics = collectLabeledMetrics(currentMetricSource);
  if (!hasNoContent && currentMetrics.length === 0 && !/历史/.test(normalizeOpsWording(visibleRaw))) {
    currentMetrics = collectLabeledMetrics(visibleRaw);
  }
  if (!hasNoContent && currentMetrics.length === 0 && currentZeroMetric) {
    currentMetrics = [currentZeroMetric];
  }
  if (!hasNoContent && currentMetrics.length === 0 && !historicalVisibleMetrics.length) {
    currentMetrics = collectPackedSeries(currentMetricSource, inferSampleMetricBaseLabel(currentMetricSource, config, "对照"));
  }
  const primaryMetric = hasNoContent
    ? { label: config.defaultPrimaryLabel, value: 0 }
    : normalizePrimaryMetric(config, choosePrimaryMetric(config, currentMetrics));

  let compareMetrics = collectLabeledMetrics(compareRaw);
  if (compareMetrics.length === 0) compareMetrics = collectPackedSeries(compareRaw, inferSampleMetricBaseLabel(compareRaw, config, "近作"));
  if (compareMetrics.length === 0 && historicalVisibleMetrics.length > 0) compareMetrics = historicalVisibleMetrics;
  compareMetrics = relabelMetricsWithDates(compareMetrics, compareText || compareRaw, config.defaultPrimaryLabel);
  const baselineMetric = hasNoContent ? { label: config.defaultPrimaryLabel, value: 0 } : choosePrimaryMetric(config, compareMetrics);

  let accountMetrics = collectLabeledMetrics(accountRaw);
  if (accountMetrics.length === 0) accountMetrics = collectPackedSeries(accountRaw, inferSampleMetricBaseLabel(accountRaw, config, "账号"));

  const publishTimeBase = parseDateTime(currentWorkText || statusText, reviewDate) || reviewDate;
  const publishTime = `${publishTimeBase} · ${extractBatchTag(statusText)} ${extractMainStatus(statusText)}`;

  let status = "watch";
  if (hasNoContent) {
    status = "watch";
  } else if (isIncompleteVerificationLabel(verificationDisplay)) {
    status = "warning";
  } else if (rawDecision.includes("Keep")) {
    status = "steady";
  } else if (rawDecision.includes("Retest")) {
    status = "warning";
  } else if (rawDecision.includes("Watch")) {
    status = "watch";
  }

  const statusLabel = hasNoContent ? "本批次未发现发布项" : verificationDisplay;
  const baselineNote = compareText || "近几条对照未展开。";
  const todayMetrics = buildTodayWindowMetrics({
    statusText,
    verification: verificationDisplay,
    currentMetrics,
    visibleText,
    diagnosis,
    action,
  });
  const comparisonWindowMetrics = buildComparisonWindowMetrics(compareMetrics, compareText || compareRaw);
  const accountWindowMetrics = buildAccountWindowMetrics(accountText || accountRaw, compareText || compareRaw, statusText, diagnosis, action);
  const todayHeadline = explicitTitle && explicitTitle !== "-" ? explicitTitle : currentWorkText || visibleText || "-";

  return {
    key: config.key,
    name: config.name,
    status,
    statusLabel,
    latestTitle: explicitTitle,
    publishTime,
    contentType: config.contentType,
    primaryLabel: primaryMetric.label,
    primaryValue: primaryMetric.value,
    compareLabel: compareMetrics.length > 0 ? "同题材对照" : "近作对照",
    baselineValue: baselineMetric.value,
    baselineNote,
    windows: [
      {
        label: "今日",
        headline: todayHeadline,
        metrics: todayMetrics,
      },
      {
        label: "近7日账号",
        headline: compareText || "-",
        metrics: comparisonWindowMetrics,
      },
      {
        label: "近30日账号",
        headline: accountText || "-",
        metrics: accountWindowMetrics,
      },
    ],
    metrics: [
      { label: "核验状态", value: statusLabel },
      { label: "发布状态", value: statusText },
      { label: primaryMetric.label, value: primaryMetric.value },
      { label: "决策", value: decision },
    ],
    diagnosis,
    action,
  };
}

function parseSectionBullets(reviewMd, heading) {
  const body = extractSectionBody(reviewMd, heading);
  return body ? parseBulletFields(body) : {};
}

function firstAvailable(list, fallback) {
  const found = list.find((item) => cleanInline(item));
  return found ? cleanInline(found) : fallback;
}

function isNoNewBatchReview(batch, reviewMd) {
  const batchText = cleanInline(batch).toLowerCase();
  if (batchText.includes("no-new-batch")) return true;
  const reviewText = cleanInline(reviewMd);
  return reviewText.includes("本轮复盘性质：无新发布日") || reviewText.includes("本轮复盘性质：无新执行日");
}

function buildBoard({ reviewDate, batch, themeLine, platformCards, reviewMd }) {
  const crossSection = parseSectionBullets(reviewMd, "## 4. 跨平台结论");
  const graphicSection = parseSectionBullets(reviewMd, "## 5. 下一批图文内容高占比倾向");
  const videoSection = parseSectionBullets(reviewMd, "## 6. 下一批小云雀视频高占比倾向");
  const pendingSection = parseSectionBullets(reviewMd, "## 7. 未完成核验项");
  const memorySection = parseSectionBullets(reviewMd, "## 8. 写回规则");
  const isNoNewBatch = isNoNewBatchReview(batch, reviewMd);

  const verifiedCards = platformCards.filter(
    (card) => !isIncompleteVerificationLabel(card.statusLabel) && !card.statusLabel.includes("未发现发布项")
  );
  const pendingCards = platformCards.filter((card) => isIncompleteVerificationLabel(card.statusLabel));
  const noContentCards = platformCards.filter((card) => card.statusLabel.includes("未发现发布项"));

  const comparableMetricCards = verifiedCards
    .filter((card) => card.primaryValue > 0 && !isSampleMetricLabel(card.primaryLabel));

  const riskValue = reviewMd.includes("标题漂移") || reviewMd.includes("重复")
    ? "重复与标题漂移"
    : "早窗误判";
  const riskNote =
    sanitizeBoardScopeText(
      fieldText(crossSection, "标题 / 封面结论") ||
      fieldText(crossSection, "本轮最不该误判的点") ||
      "早窗与运营问题必须先分开，不要把 0 直接写成内容失败。"
    );

  const mainDirectionValue = sanitizeBoardScopeText(
    firstAvailable(
      [
        normalizeOpsWording(fieldText(graphicSection, "高占比主母题")),
        normalizeOpsWording(fieldText(videoSection, "高占比核心母题")),
        "看下一批方向",
      ],
      "看下一批方向"
    )
  );
  const nextValue = isNoNewBatch
    ? "等待新批次"
    : pendingCards.length > 0
      ? `补${pendingCards[0].name}核验`
      : mainDirectionValue;
  const nextNote = isNoNewBatch
    ? "本轮仅确认无新执行并完成面板同步；不把跨日补抓任务写成当前重点。"
    : sanitizeBoardScopeText(
        fieldText(pendingSection, "下一步补什么") ||
        fieldText(memorySection, "明天必须复查的点") ||
        fieldText(graphicSection, "高占比主判断") ||
        fieldText(videoSection, "高占比核心判断") ||
        "沿用已确认方向，等待下一批数据继续校验。"
      );

  const keep = [
    firstAvailable(
      [
        fieldText(graphicSection, "高占比主判断"),
        fieldText(crossSection, "图文侧结论"),
        `保留“${themeLine}”这条跨平台母题。`,
      ],
      `保留“${themeLine}”这条跨平台母题。`
    ),
    firstAvailable(
      [
        fieldText(videoSection, "高占比核心判断"),
        fieldText(crossSection, "短视频侧结论"),
        "保留短视频里“人做判断，AI 跑平台”的判断链。",
      ],
      "保留短视频里“人做判断，AI 跑平台”的判断链。"
    ),
    firstAvailable(
      [
        fieldText(graphicSection, "必须保留的具体例子"),
        fieldText(videoSection, "开头高占比规则"),
        "保留字段样例与清单式表达，不再只讲抽象提效。",
      ],
      "保留字段样例与清单式表达，不再只讲抽象提效。"
    ),
  ].map((item) => sanitizeBoardScopeText(item));

  const cut = [
    reviewMd.includes("重复")
      ? "切掉重复发布或删改后不回填字段的操作，先修运营问题再看内容效果。"
      : "切掉会污染对照样本的重复发布与重复归因。",
    reviewMd.includes("标题漂移")
      ? "切掉“发布包标题”和“后台真实标题”不一致但不写回字段的做法。"
      : "切掉标题与实际后台落地不一致却不回填的做法。",
    "切掉把早窗 0、审核中或未入账直接写成内容失败的复盘口径。",
  ].map((item) => sanitizeBoardScopeText(item));

  const pendingItems = fieldList(pendingSection, "下一步补什么").map((item) => sanitizeBoardScopeText(item));
  const mustReviewItems = fieldList(memorySection, "明天必须复查的点").map((item) => sanitizeBoardScopeText(item));
  const next = isNoNewBatch
    ? [
        sanitizeBoardScopeText(firstAvailable(
          [
            fieldText(graphicSection, "高占比主判断"),
            fieldText(crossSection, "图文侧结论"),
            "本轮无新批次，保持已确认图文方向，等待真实新批次后刷新。",
          ],
          "本轮无新批次，保持已确认图文方向，等待真实新批次后刷新。"
        )),
        sanitizeBoardScopeText(firstAvailable(
          [
            fieldText(videoSection, "高占比核心判断"),
            fieldText(crossSection, "短视频侧结论"),
            "本轮无新批次，保持已确认视频方向，等待真实新批次后刷新。",
          ],
          "本轮无新批次，保持已确认视频方向，等待真实新批次后刷新。"
        )),
        sanitizeBoardScopeText(firstAvailable(
          [
            fieldText(crossSection, "本轮最不该误判的点"),
            "未完成内容级核验不等于内容失败。",
          ],
          "未完成内容级核验不等于内容失败。"
        )),
      ]
    : [
        sanitizeBoardScopeText(firstAvailable(
          [pendingItems[0], mustReviewItems[0], nextNote],
          "先补未完成平台的页面核验。"
        )),
        sanitizeBoardScopeText(firstAvailable(
          [pendingItems[1], mustReviewItems[1], "24 小时后补抓播放、阅读、展现与互动。"],
          "24 小时后补抓播放、阅读、展现与互动。"
        )),
        sanitizeBoardScopeText(firstAvailable(
          [mustReviewItems[2], sanitizeBoardScopeText(fieldText(memorySection, "账号趋势要继续观察的平台")), "把实际后台标题、链接和状态词写回复盘字段。"],
          "把实际后台标题、链接和状态词写回复盘字段。"
        )),
      ];

  const verifiedNames = verifiedCards.map((card) => card.name).join("、") || "暂无";
  const pendingNames = pendingCards.map((card) => card.name).join("、");
  const noContentNames = noContentCards.map((card) => card.name).join("、");
  const subtitleParts = [
    verifiedCards.length > 0 ? `已核验平台：${verifiedNames}` : "本轮暂无已核验平台",
    pendingCards.length > 0 ? `${pendingNames} 仍待补作品级核验` : "",
    noContentCards.length > 0 ? `${noContentNames} 本批次无发布项` : "",
  ].filter(Boolean);

  return {
    title: "8 平台复盘面板",
    dateLabel: `${reviewDate} 晚间复盘已同步（${verifiedCards.length} / 8 平台已核验）`,
    subtitle: `${subtitleParts.join("；")}。`,
    northStar: "AI 先替平台执行，人回到判断",
    summary: [
      {
        label: "已核验平台",
        value: `${verifiedCards.length} / 8`,
        note: isNoNewBatch
          ? "本轮无新批次，8 张固定平台卡片保留占位；不把“未发现发布项”当作失败结论或当前重点。"
          : pendingCards.length > 0 || noContentCards.length > 0
            ? `待补：${[pendingNames, noContentNames].filter(Boolean).join("；") || "无"}。`
            : "8 张固定平台卡片都已有页面级证据。",
        tone: isNoNewBatch ? "steady" : pendingCards.length > 0 ? "warning" : "steady",
      },
      buildPrimaryMetricSummary(comparableMetricCards, verifiedCards),
      {
        label: "当前主要风险",
        value: riskValue,
        note: riskNote,
        tone: "warning",
      },
      {
        label: "下一步重点",
        value: nextValue,
        note: nextNote,
        tone: isNoNewBatch ? "steady" : "hot",
      },
    ],
    keep,
    cut,
    next,
  };
}

function main() {
  const args = parseArgs(process.argv);
  const rootDir = process.cwd();
  const reviewDate = String(args["review-date"] || "").trim();
  if (!reviewDate) {
    fail("Missing required arg: --review-date YYYY-MM-DD");
  }

  const reviewAbs = findLatestReviewReport(rootDir, reviewDate);
  if (!reviewAbs) {
    fail(`No review report found for ${reviewDate} under content-library/logs/review`);
  }

  const reviewMd = readText(reviewAbs);
  const batch = args.batch || inferBatchFromReviewFilename(reviewDate, reviewAbs);

  const sharedPackageAbs = path.join(rootDir, "content-library", "posts", "shared", `${batch}-all-platform-publish-package.md`);
  const videoPackageAbs = path.join(rootDir, "content-library", "posts", "video", `${batch}-video-publish-package.md`);
  const weiboAbs = path.join(rootDir, "content-library", "posts", "weibo", `${batch}-video-post-001.md`);
  const zhihuAbs = path.join(rootDir, "content-library", "posts", "zhihu", `${batch}-answer-001.md`);
  const baijiahaoAbs = path.join(rootDir, "content-library", "posts", "baijiahao", `${batch}-article-001.md`);
  const toutiaoAbs = path.join(rootDir, "content-library", "posts", "toutiao", `${batch}-article-001.md`);

  const titleFallbacks = buildFallbackTitleMap(
    fs.existsSync(sharedPackageAbs) ? readText(sharedPackageAbs) : "",
    fs.existsSync(videoPackageAbs) ? readText(videoPackageAbs) : "",
    fs.existsSync(weiboAbs) ? readText(weiboAbs) : "",
    fs.existsSync(zhihuAbs) ? readText(zhihuAbs) : "",
    fs.existsSync(baijiahaoAbs) ? readText(baijiahaoAbs) : "",
    fs.existsSync(toutiaoAbs) ? readText(toutiaoAbs) : ""
  );

  const platformSections = parsePlatformSections(reviewMd);
  if (Object.keys(platformSections).length === 0) {
    fail(`Review file has no '## 3. 分平台详细状态' platform blocks: ${reviewAbs}`);
  }

  const platforms = PLATFORM_CONFIG.map((config) => {
    const fields = platformSections[config.name];
    if (!fields) {
      return buildMissingPlatformCard({
        reviewDate,
        config,
        latestTitle: titleFallbacks[config.name],
        reason: `复盘正文未提供 ${config.name} 的平台段落。`,
      });
    }
    return buildPlatformCard({
      reviewDate,
      config,
      fields,
      titleFallback: titleFallbacks[config.name],
    });
  });

  const verifiedSections = Object.values(platformSections).filter((fields) =>
    fieldText(fields, "核验等级").includes("后台已核验") || fieldText(fields, "核验等级").includes("公开页已核验")
  ).length;
  const exportedVerified = platforms.filter(
    (platform) => !isIncompleteVerificationLabel(platform.statusLabel) && !platform.statusLabel.includes("未发现发布项")
  ).length;
  if (verifiedSections > 0 && exportedVerified === 0) {
    fail("Review contains verified platform evidence, but dashboard export resolved to 0 verified platform cards.");
  }

  const exportObj = {
    meta: {
      sourceBatch: batch,
      sourceReviewDate: reviewDate,
      mode: "review-section-export",
      isNoNewBatch: isNoNewBatchReview(batch, reviewMd),
      verifiedAt: reviewDate,
    },
    board: buildBoard({
      reviewDate,
      batch,
      themeLine: titleFallbacks._theme,
      platformCards: platforms,
      reviewMd,
    }),
    platforms,
    footerLinks: [],
  };

  const outDir = path.join(rootDir, "content-library", "logs", "review", "dashboard-export");
  fs.mkdirSync(outDir, { recursive: true });
  const outAbs = path.join(outDir, `${batch}-dashboard-export.json`);
  fs.writeFileSync(outAbs, `${JSON.stringify(exportObj, null, 2)}\n`, "utf-8");
  console.log(outAbs);
}

main();
