import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

function cleanText(value) {
  return String(value || '')
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function countVisibleChars(value) {
  return cleanText(value).replace(/\s+/g, '').length;
}

function stripTopics(value) {
  const text = cleanText(value);
  const markerIndex = text.search(/[#@]/);
  return markerIndex >= 0 ? text.slice(0, markerIndex).trim() : text;
}

export function extractCaptionLead(caption) {
  const withoutTopics = stripTopics(caption);
  const sentence = withoutTopics.match(/^[^。！？!?；;]+/);
  return cleanText(sentence ? sentence[0] : withoutTopics);
}

function normalizeForCompare(value) {
  return cleanText(value)
    .toLowerCase()
    .replace(/[#@][^\s#@]+/g, '')
    .replace(/[0-9a-z]/g, '')
    .replace(/[\s,，。.!！?？:：;；、'"“”‘’()（）【】\[\]<>《》\-—_~`·]/g, '');
}

function longestCommonSubstring(left, right) {
  if (!left || !right) return { length: 0, text: '' };
  const dp = new Array(right.length + 1).fill(0);
  let maxLength = 0;
  let endIndex = 0;
  for (let i = 1; i <= left.length; i += 1) {
    let prev = 0;
    for (let j = 1; j <= right.length; j += 1) {
      const nextPrev = dp[j];
      if (left[i - 1] === right[j - 1]) {
        dp[j] = prev + 1;
        if (dp[j] > maxLength) {
          maxLength = dp[j];
          endIndex = i;
        }
      } else {
        dp[j] = 0;
      }
      prev = nextPrev;
    }
  }
  return { length: maxLength, text: left.slice(endIndex - maxLength, endIndex) };
}

function collectSharedChunks(left, right, minLength = 3, maxLength = 6) {
  const result = new Set();
  const upper = Math.min(maxLength, left.length, right.length);
  for (let size = upper; size >= minLength; size -= 1) {
    for (let index = 0; index <= left.length - size; index += 1) {
      const fragment = left.slice(index, index + size);
      if (!fragment || result.has(fragment)) continue;
      if (right.includes(fragment)) {
        result.add(fragment);
      }
    }
  }
  return Array.from(result);
}

export function analyzeDouyinPackaging({
  title,
  caption,
  maxTitleChars = 20,
  maxCaptionLeadChars = 18,
} = {}) {
  const safeTitle = cleanText(title);
  const captionLead = extractCaptionLead(caption);
  const titleNormalized = normalizeForCompare(safeTitle);
  const captionLeadNormalized = normalizeForCompare(captionLead);
  const overlap = longestCommonSubstring(titleNormalized, captionLeadNormalized);
  const sharedChunks = collectSharedChunks(titleNormalized, captionLeadNormalized);
  const titleChars = countVisibleChars(safeTitle);
  const captionLeadChars = countVisibleChars(captionLead);
  const mergedPreview = cleanText(`${safeTitle} ${captionLead}`);
  const problems = [];

  if (!safeTitle) problems.push('missing-title');
  if (!captionLead) problems.push('missing-caption-lead');
  if (titleChars > maxTitleChars) problems.push(`title-too-long:${titleChars}`);
  if (captionLeadChars > maxCaptionLeadChars) {
    problems.push(`caption-lead-too-long:${captionLeadChars}`);
  }
  if (titleNormalized && captionLeadNormalized.includes(titleNormalized)) {
    problems.push('caption-lead-repeats-title');
  }
  if (overlap.length >= 3) {
    problems.push(`title-caption-overlap:${overlap.text}`);
  }

  return {
    ok: problems.length === 0,
    title: safeTitle,
    captionLead,
    mergedPreview,
    titleChars,
    captionLeadChars,
    titleNormalized,
    captionLeadNormalized,
    overlap,
    sharedChunks,
    limits: { maxTitleChars, maxCaptionLeadChars },
    problems,
  };
}

export function assertDouyinPackaging(input) {
  const report = analyzeDouyinPackaging(input);
  if (!report.ok) {
    throw new Error(
      `douyin packaging guard failed: ${report.problems.join(', ')} | merged preview: ${report.mergedPreview}`
    );
  }
  return report;
}

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) continue;
    const next = argv[index + 1];
    if (!next || next.startsWith('--')) {
      options[token] = true;
      continue;
    }
    options[token] = next;
    index += 1;
  }
  return options;
}

function loadFromBrief(filePath) {
  const resolved = path.resolve(filePath);
  const data = JSON.parse(fs.readFileSync(resolved, 'utf8'));
  return {
    source: resolved,
    title: data.douyin_title || data.title || data.video_title || '',
    caption: data.douyin_desc || data.caption || data.description || '',
  };
}

function usage() {
  console.error(
    'usage: node scripts/douyin-packaging-guard.mjs --brief /path/to/brief.json\n' +
      '   or: node scripts/douyin-packaging-guard.mjs --title "..." --caption "..."'
  );
}

const entryPath = process.argv[1] ? path.resolve(process.argv[1]) : '';
const thisPath = fileURLToPath(import.meta.url);

if (entryPath === thisPath) {
  const args = parseArgs(process.argv.slice(2));
  const source = args['--brief']
    ? loadFromBrief(String(args['--brief']))
    : {
        source: 'cli',
        title: String(args['--title'] || ''),
        caption: String(args['--caption'] || ''),
      };
  if (!source.title || !source.caption) {
    usage();
    process.exit(1);
  }
  const report = analyzeDouyinPackaging(source);
  console.log(JSON.stringify({ source: source.source, ...report }, null, 2));
  process.exit(report.ok ? 0 : 2);
}
