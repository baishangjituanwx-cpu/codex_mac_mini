#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { loadDashboardEnv } = require("./lib/load-dashboard-env");
const {
  resolveRepoRoot,
  resolveContentRoot,
  resolveDashboardExportDir,
} = require("./lib/workspace-paths");

const PLATFORM_CONFIG = [
  { key: "kuaishou", name: "快手", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读", "未命名列1"] },
  { key: "wechat", name: "视频号", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读", "未命名列1"] },
  { key: "weibo", name: "微博", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读", "未命名列1"] },
  { key: "toutiao", name: "头条号", contentType: "图文", defaultPrimaryLabel: "阅读", preferredLabels: ["阅读", "展现", "推荐量", "未命名列1"] },
  { key: "baijiahao", name: "百家号", contentType: "图文", defaultPrimaryLabel: "阅读", preferredLabels: ["阅读", "推荐量", "未命名列1"] },
  { key: "douyin", name: "抖音", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读", "未命名列1"] },
  { key: "bilibili", name: "B站", contentType: "视频", defaultPrimaryLabel: "播放", preferredLabels: ["播放", "阅读", "未命名列1"] },
  { key: "zhihu", name: "知乎", contentType: "图文", defaultPrimaryLabel: "阅读", preferredLabels: ["阅读", "赞同", "评论", "未命名列1"] },
];

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

function findLatestReviewReport(reviewRoot, reviewDate) {
  if (!fs.existsSync(reviewRoot)) return null;
  const dir = reviewRoot;
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

function disambiguatePackedSeries(text) {
  const input = String(text || "").replace(
    /(\d{2}-\d{2})(?:\s*\/\s*(\d{2}-\d{2}))+/g,
    (match) => match.split("/").map((item) => cleanInline(item)).join("、")
  );
  return input.replace(/(\d[\d,]*(?:\s*\/\s*\d[\d,]*)+)/g, (match) => {
    const parts = match.split("/").map((item) => cleanInline(item)).filter(Boolean);
    if (parts.length < 2) return match;
    return parts.map((value, index) => `未命名列${index + 1} ${value}`).join("，");
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

function collectPackedSeries(text) {
  const input = cleanInline(text);
  if (!input) return [];
  const packed = input.match(/\d[\d,]*(?:\s*\/\s*\d[\d,]*)+/);
  if (!packed) return [];
  return packed[0]
    .split("/")
    .map((item) => parseNumber(item.trim()))
    .map((value, index) => ({ label: `未命名列${index + 1}`, value }));
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
      { label: "今日", headline: reason, metrics: [] },
      { label: "近7日账号", headline: "未提供近几条对照。", metrics: [] },
      { label: "近30日账号", headline: "未提供账号盘面。", metrics: [] },
    ],
    metrics: [
      { label: "核验等级", value: "缺失平台段落" },
      { label: "发布状态", value: "待补" },
      { label: config.defaultPrimaryLabel, value: 0 },
      { label: "决策", value: "Retest" },
    ],
    diagnosis: reason,
    action: "补齐该平台的复盘段落后重新导出并上传数据面板。",
  };
}

function buildPlatformCard({ reviewDate, config, fields, titleFallback }) {
  const verification = fieldText(fields, "核验等级") || "未完成内容级核验";
  const currentWorkItems = fieldList(fields, "当前作品（后台可见）");
  const currentWorkText = fieldText(fields, "当前作品（后台可见）", "当前作品");
  const currentWorkRaw = rawFieldText(fields, "当前作品（后台可见）", "当前作品");
  const visibleText = fieldText(fields, "当前可见数据");
  const visibleRaw = rawFieldText(fields, "当前可见数据");
  const accountText = fieldText(fields, "账号盘面");
  const accountRaw = rawFieldText(fields, "账号盘面");
  const compareText = fieldText(fields, "近几条对照");
  const compareRaw = rawFieldText(fields, "近几条对照");
  const statusText = fieldText(fields, "发布状态") || "-";
  const diagnosis = fieldText(fields, "诊断") || "复盘正文未给出诊断。";
  const action = fieldList(fields, "明日动作").join("；") || fieldText(fields, "明日动作") || "待补下一步动作。";
  const decision = fieldText(fields, "决策") || "-";

  const explicitTitle =
    extractTitleCandidate(currentWorkText) ||
    extractTitleCandidate(fieldText(fields, "计划内容")) ||
    titleFallback ||
    "-";

  const currentMetricSource = currentWorkItems[0] || currentWorkRaw || visibleRaw;
  let currentMetrics = collectLabeledMetrics(currentMetricSource);
  if (currentMetrics.length === 0) currentMetrics = collectLabeledMetrics(visibleRaw);
  if (currentMetrics.length === 0) currentMetrics = collectPackedSeries(visibleRaw);
  if (currentMetrics.length === 0) currentMetrics = collectPackedSeries(currentMetricSource);
  const primaryMetric = choosePrimaryMetric(config, currentMetrics);

  let compareMetrics = collectLabeledMetrics(compareRaw);
  if (compareMetrics.length === 0) compareMetrics = collectPackedSeries(compareRaw);
  const baselineMetric = choosePrimaryMetric(config, compareMetrics);

  let accountMetrics = collectLabeledMetrics(accountRaw);
  if (accountMetrics.length === 0) accountMetrics = collectPackedSeries(accountRaw);

  const hasNoContent = /无发布项|未计划发布|本批次未发现/.test(currentWorkText) || /无发布项|未计划发布/.test(fieldText(fields, "计划内容"));
  const publishTimeBase = parseDateTime(currentWorkText || statusText, reviewDate) || reviewDate;
  const publishTime = `${publishTimeBase} · ${statusText}`;

  let status = "watch";
  if (hasNoContent || config.name === "B站") {
    status = "watch";
  } else if (verification.includes("未完成内容级核验")) {
    status = "warning";
  } else if (decision.includes("Keep")) {
    status = "steady";
  } else if (decision.includes("Retest")) {
    status = "warning";
  } else if (decision.includes("Watch")) {
    status = "watch";
  }

  const statusLabel = hasNoContent ? "本批次未发现发布项" : verification;
  const baselineNote = compareText || "近几条对照未展开。";

  const todayMetrics = currentMetrics.length
    ? currentMetrics.slice(0, 4)
    : [
        { label: "状态", value: statusText },
        { label: primaryMetric.label, value: primaryMetric.value },
      ];

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
    compareLabel: "近几条对照",
    baselineValue: baselineMetric.value,
    baselineNote,
    windows: [
      {
        label: "今日",
        headline: currentWorkText || visibleText || "本轮未抓到今日正文。",
        metrics: todayMetrics,
      },
      {
        label: "近7日账号",
        headline: compareText || "本轮未展开近几条对照。",
        metrics: compareMetrics.slice(0, 4),
      },
      {
        label: "近30日账号",
        headline: accountText || "本轮未展开账号盘面。",
        metrics: accountMetrics.slice(0, 4),
      },
    ],
    metrics: [
      { label: "核验等级", value: statusLabel },
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

function buildBoard({ reviewDate, themeLine, platformCards, reviewMd }) {
  const crossSection = parseSectionBullets(reviewMd, "## 4. 跨平台结论");
  const graphicSection = parseSectionBullets(reviewMd, "## 5. 下一批图文内容高占比倾向");
  const videoSection = parseSectionBullets(reviewMd, "## 6. 下一批小云雀视频高占比倾向");
  const pendingSection = parseSectionBullets(reviewMd, "## 7. 未完成核验项");
  const memorySection = parseSectionBullets(reviewMd, "## 8. 写回规则");

  const verifiedCards = platformCards.filter(
    (card) => !card.statusLabel.includes("未完成内容级核验") && !card.statusLabel.includes("未发现发布项")
  );
  const pendingCards = platformCards.filter((card) => card.statusLabel.includes("未完成内容级核验"));
  const noContentCards = platformCards.filter((card) => card.statusLabel.includes("未发现发布项"));

  const highestCard = platformCards
    .filter((card) => card.primaryValue > 0)
    .sort((a, b) => {
      const aUnknown = a.primaryLabel.startsWith("未命名列") ? 1 : 0;
      const bUnknown = b.primaryLabel.startsWith("未命名列") ? 1 : 0;
      if (b.primaryValue !== a.primaryValue) return b.primaryValue - a.primaryValue;
      return aUnknown - bUnknown;
    })[0];

  const riskValue = reviewMd.includes("标题漂移") || reviewMd.includes("重复")
    ? "重复与标题漂移"
    : "早窗误判";
  const riskNote =
    fieldText(crossSection, "标题 / 封面结论") ||
    fieldText(crossSection, "本轮最不该误判的点") ||
    "早窗与运营问题必须先分开，不要把 0 直接写成内容失败。";

  const nextValue = pendingCards.length > 0 ? `补${pendingCards[0].name}核验` : "补24h 对照";
  const nextNote =
    fieldText(pendingSection, "下一步补什么") ||
    fieldText(memorySection, "明天必须复查的点") ||
    "先补未完成平台的页面证据，再滚动看 24 小时数据。";

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
  ];

  const cut = [
    reviewMd.includes("重复")
      ? "切掉重复发布或删改后不回填字段的操作，先修运营问题再看内容效果。"
      : "切掉会污染对照样本的重复发布与重复归因。",
    reviewMd.includes("标题漂移")
      ? "切掉“发布包标题”和“后台真实标题”不一致但不写回字段的做法。"
      : "切掉标题与实际后台落地不一致却不回填的做法。",
    "切掉把早窗 0、审核中或未入账直接写成内容失败的复盘口径。",
  ];

  const pendingItems = fieldList(pendingSection, "下一步补什么");
  const mustReviewItems = fieldList(memorySection, "明天必须复查的点");
  const next = [
    firstAvailable(
      [pendingItems[0], mustReviewItems[0], nextNote],
      "先补未完成平台的页面核验。"
    ),
    firstAvailable(
      [pendingItems[1], mustReviewItems[1], "24 小时后补抓播放、阅读、展现与互动。"],
      "24 小时后补抓播放、阅读、展现与互动。"
    ),
    firstAvailable(
      [mustReviewItems[2], fieldText(memorySection, "账号趋势要继续观察的平台"), "把实际后台标题、链接和状态词写回复盘字段。"],
      "把实际后台标题、链接和状态词写回复盘字段。"
    ),
  ];

  const verifiedNames = verifiedCards.map((card) => card.name).join("、") || "暂无";
  const pendingNames = pendingCards.map((card) => card.name).join("、");
  const noContentNames = noContentCards.map((card) => card.name).join("、");
  const subtitleParts = [
    verifiedCards.length > 0 ? `已从复盘正文抽取真实平台核验：${verifiedNames}` : "本轮暂无可确认的平台核验结果",
    pendingCards.length > 0 ? `${pendingNames} 仍待补内容级核验` : "",
    noContentCards.length > 0 ? `${noContentNames} 本批次无发布项` : "",
  ].filter(Boolean);

  return {
    title: "8 平台最新数据看板",
    dateLabel: `${reviewDate} 晚间复盘已同步（${verifiedCards.length} / 8 已核验）`,
    subtitle: `${subtitleParts.join("；")}。`,
    northStar: "AI 先替平台执行，人回到判断",
    summary: [
      {
        label: "页面核验",
        value: `${verifiedCards.length} / 8`,
        note: pendingCards.length > 0 || noContentCards.length > 0
          ? `待补：${[pendingNames, noContentNames].filter(Boolean).join("；") || "无"}。`
          : "8 张固定平台卡片都已有页面级证据。",
        tone: pendingCards.length > 0 ? "warning" : "steady",
      },
      {
        label: "当前最高可见",
        value: highestCard ? `${highestCard.name} ${highestCard.primaryValue}` : "-",
        note: highestCard
          ? `${highestCard.name} 当前可见主值为 ${highestCard.primaryValue}（${highestCard.primaryLabel}）。`
          : "当前没有已明确标注字段的可见主值。",
        tone: highestCard ? "cool" : "warning",
      },
      {
        label: "最大风险",
        value: riskValue,
        note: riskNote,
        tone: "warning",
      },
      {
        label: "下一主动作",
        value: nextValue,
        note: nextNote,
        tone: "hot",
      },
    ],
    keep,
    cut,
    next,
  };
}

function main() {
  const args = parseArgs(process.argv);
  const rootDir = resolveRepoRoot(__dirname);
  loadDashboardEnv(rootDir);
  const contentRoot = resolveContentRoot(rootDir);
  const reviewRoot = path.join(contentRoot, "logs", "review");
  const reviewDate = String(args["review-date"] || "").trim();
  if (!reviewDate) {
    fail("Missing required arg: --review-date YYYY-MM-DD");
  }

  const reviewAbs = findLatestReviewReport(reviewRoot, reviewDate);
  if (!reviewAbs) {
    fail(`No review report found for ${reviewDate} under ${reviewRoot}`);
  }

  const reviewMd = readText(reviewAbs);
  const batch = args.batch || inferBatchFromReviewFilename(reviewDate, reviewAbs);

  const sharedPackageAbs = path.join(contentRoot, "posts", "shared", `${batch}-all-platform-publish-package.md`);
  const videoPackageAbs = path.join(contentRoot, "posts", "video", `${batch}-video-publish-package.md`);
  const weiboAbs = path.join(contentRoot, "posts", "weibo", `${batch}-video-post-001.md`);
  const zhihuAbs = path.join(contentRoot, "posts", "zhihu", `${batch}-answer-001.md`);
  const baijiahaoAbs = path.join(contentRoot, "posts", "baijiahao", `${batch}-article-001.md`);
  const toutiaoAbs = path.join(contentRoot, "posts", "toutiao", `${batch}-article-001.md`);

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
    (platform) => !platform.statusLabel.includes("未完成内容级核验") && !platform.statusLabel.includes("未发现发布项")
  ).length;
  if (verifiedSections > 0 && exportedVerified === 0) {
    fail("Review contains verified platform evidence, but dashboard export resolved to 0 verified platform cards.");
  }

  const exportObj = {
    meta: {
      sourceBatch: batch,
      sourceReviewDate: reviewDate,
      mode: "review-section-export",
      verifiedAt: reviewDate,
    },
    board: buildBoard({
      reviewDate,
      themeLine: titleFallbacks._theme,
      platformCards: platforms,
      reviewMd,
    }),
    platforms,
    footerLinks: [],
  };

  const outDir = resolveDashboardExportDir(rootDir);
  fs.mkdirSync(outDir, { recursive: true });
  const outAbs = path.join(outDir, `${batch}-dashboard-export.json`);
  fs.writeFileSync(outAbs, `${JSON.stringify(exportObj, null, 2)}\n`, "utf-8");
  console.log(outAbs);
}

main();
