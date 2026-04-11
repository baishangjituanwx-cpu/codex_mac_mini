const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CONTENT_ROOT = path.join(ROOT, "workflow", "content-library");
const TEMPLATE_ROOT = path.join(CONTENT_ROOT, "templates");

function parseArgs(argv) {
  const result = {};
  for (let i = 2; i < argv.length; i += 1) {
    const part = argv[i];
    if (!part.startsWith("--")) {
      continue;
    }
    const key = part.slice(2);
    const value = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
    result[key] = value;
  }
  return result;
}

function must(value, message) {
  if (!value) {
    console.error(message);
    process.exit(1);
  }
  return value;
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function readTemplate(name) {
  return fs.readFileSync(path.join(TEMPLATE_ROOT, name), "utf8");
}

function writeIfMissing(filePath, content) {
  ensureDir(path.dirname(filePath));
  if (fs.existsSync(filePath)) {
    console.log(`skip existing: ${path.relative(ROOT, filePath)}`);
    return;
  }
  fs.writeFileSync(filePath, content, "utf8");
  console.log(`created: ${path.relative(ROOT, filePath)}`);
}

function replaceAll(template, vars) {
  return Object.entries(vars).reduce((acc, [key, value]) => {
    return acc.replaceAll(`{{${key}}}`, value);
  }, template);
}

function main() {
  const args = parseArgs(process.argv);
  const campaignId = must(args.id, "Missing --id, for example --id 2026-04-11-ai-workflow");
  const theme = must(args.theme, "Missing --theme, for example --theme \"AI先替劳动，不是先替人\"");
  const assetRoot = `{{WORKSPACE_ROOT}}/workflow/content-library/assets/generated/${campaignId}`;

  const vars = {
    CAMPAIGN_ID: campaignId,
    THEME: theme,
    ASSET_ROOT: assetRoot,
  };

  [
    "assets/generated",
    "assets/shared",
    "posts/shared",
    "posts/video",
    "posts/weibo",
    "posts/xiaohongshu",
    "posts/baijiahao",
    "posts/toutiao",
    "posts/zhihu",
    "logs/weibo",
    "logs/douyin",
    "logs/wechat_channels",
    "logs/kuaishou",
    "logs/baijiahao",
    "logs/toutiao",
    "logs/zhihu",
    "logs/xiaohongshu",
    `assets/generated/${campaignId}/covers`,
  ].forEach((relativeDir) => ensureDir(path.join(CONTENT_ROOT, relativeDir)));

  const files = [
    {
      output: `posts/shared/${campaignId}-campaign-brief.md`,
      template: "campaign-brief.md",
    },
    {
      output: `posts/shared/${campaignId}-production-pack.md`,
      template: "production-pack.md",
    },
    {
      output: `posts/shared/${campaignId}-all-platform-publish-package.md`,
      template: "all-platform-publish-package.md",
    },
    {
      output: `posts/video/${campaignId}-video-publish-package.md`,
      template: "video-publish-package.md",
    },
    {
      output: `posts/weibo/${campaignId}-video-post-001.md`,
      template: "weibo-video-post.md",
    },
    {
      output: `posts/xiaohongshu/${campaignId}-note-001.md`,
      template: "xiaohongshu-note.md",
    },
    {
      output: `posts/baijiahao/${campaignId}-article-001.md`,
      template: "baijiahao-article.md",
    },
    {
      output: `posts/toutiao/${campaignId}-article-001.md`,
      template: "toutiao-article.md",
    },
    {
      output: `posts/zhihu/${campaignId}-answer-001.md`,
      template: "zhihu-answer.md",
    },
  ];

  files.forEach(({ output, template }) => {
    writeIfMissing(path.join(CONTENT_ROOT, output), replaceAll(readTemplate(template), vars));
  });

  const logTemplate = readTemplate("publish-log.md");
  const logTargets = [
    { file: `logs/weibo/${campaignId}-video-post-001-log.md`, platform: "微博" },
    { file: `logs/douyin/${campaignId}-video-post-001-log.md`, platform: "抖音" },
    { file: `logs/wechat_channels/${campaignId}-video-post-001-log.md`, platform: "微信视频号" },
    { file: `logs/kuaishou/${campaignId}-video-post-001-log.md`, platform: "快手" },
    { file: `logs/baijiahao/${campaignId}-article-001-log.md`, platform: "百家号" },
    { file: `logs/toutiao/${campaignId}-article-001-log.md`, platform: "今日头条 / 头条号" },
    { file: `logs/zhihu/${campaignId}-answer-001-log.md`, platform: "知乎" },
    { file: `logs/xiaohongshu/${campaignId}-note-001-log.md`, platform: "小红书" },
  ];

  logTargets.forEach(({ file, platform }) => {
    const content = replaceAll(logTemplate, {
      ...vars,
      PLATFORM: platform,
    });
    writeIfMissing(path.join(CONTENT_ROOT, file), content);
  });

  console.log("");
  console.log("Next:");
  console.log(`1. Fill posts/shared/${campaignId}-campaign-brief.md`);
  console.log(`2. Fill posts/shared/${campaignId}-production-pack.md`);
  console.log(`3. Fill posts/shared/${campaignId}-all-platform-publish-package.md`);
  console.log("4. Follow docs/browser-operation-sop.md to publish");
  console.log("5. Backfill platform logs immediately after each publish");
}

main();
