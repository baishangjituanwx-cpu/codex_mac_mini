#!/usr/bin/env node

const fs = require("node:fs/promises");
const https = require("node:https");
const path = require("node:path");
const crypto = require("node:crypto");

const IMAGE_TYPES = new Map([
  ["image/jpeg", ".jpg"],
  ["image/png", ".png"],
  ["image/webp", ".webp"],
  ["image/gif", ".gif"],
]);

function collect(value, keyPath = []) {
  const found = [];
  if (typeof value === "string") {
    for (const match of value.matchAll(/https?:\/\/[^\s'"<>]+/g)) {
      const key = keyPath.join(".").toLowerCase();
      const kind = key.includes("sku") ? "sku" : key.includes("detail") || key.includes("description") ? "detail" : "main";
      found.push({ url: match[0], kind });
    }
  } else if (Array.isArray(value)) {
    value.forEach((item, index) => found.push(...collect(item, [...keyPath, String(index)])));
  } else if (value && typeof value === "object") {
    for (const [key, item] of Object.entries(value)) found.push(...collect(item, [...keyPath, key]));
  }
  return found;
}

function downloadMedia(url) {
  if (process.env.HUICE_TLS_INSECURE !== "1" || !url.startsWith("https://")) {
    return fetch(url).then(async (response) => ({
      ok: response.ok,
      status: response.status,
      mime: String(response.headers.get("content-type") || "").split(";", 1)[0].toLowerCase(),
      body: Buffer.from(await response.arrayBuffer()),
    }));
  }

  return new Promise((resolve, reject) => {
    const request = https.get(url, { rejectUnauthorized: false }, (response) => {
      const chunks = [];
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => resolve({
        ok: response.statusCode >= 200 && response.statusCode < 300,
        status: response.statusCode || 0,
        mime: String(response.headers["content-type"] || "").split(";", 1)[0].toLowerCase(),
        body: Buffer.concat(chunks),
      }));
      response.on("error", reject);
    });
    request.on("error", reject);
  });
}

async function main() {
  const [input, outputDir] = process.argv.slice(2);
  if (!input || !outputDir) throw new Error("usage: download-huice-detail-images <detail.json> <output-dir>");

  const payload = JSON.parse(await fs.readFile(path.resolve(input), "utf8"));
  const candidates = collect(payload);
  const seen = new Set();
  const files = [];
  const root = path.resolve(outputDir);
  await fs.mkdir(root, { recursive: true });

  for (const candidate of candidates) {
    if (seen.has(candidate.url)) continue;
    seen.add(candidate.url);
    const response = await downloadMedia(candidate.url);
    if (!response.ok) throw new Error(`image download failed: HTTP ${response.status}`);
    const mime = response.mime;
    const extension = IMAGE_TYPES.get(mime);
    if (!extension) throw new Error(`unsupported media type: ${mime || "missing"}`);
    const body = response.body;
    const sha256 = crypto.createHash("sha256").update(body).digest("hex");
    const duplicate = files.find((item) => item.sha256 === sha256);
    if (duplicate) continue;
    const dir = path.join(root, candidate.kind);
    await fs.mkdir(dir, { recursive: true });
    const fileName = `${String(files.length + 1).padStart(3, "0")}-${sha256.slice(0, 12)}${extension}`;
    await fs.writeFile(path.join(dir, fileName), body);
    files.push({ kind: candidate.kind, filename: `${candidate.kind}/${fileName}`, bytes: body.length, mime, sha256 });
  }

  const manifest = {
    retrievedAt: new Date().toISOString(),
    source: "Huice goods detail media export",
    supplierGoodsId: payload?.supplierGoodsId ?? payload?.data?.supplierGoodsId ?? null,
    supplierShopId: payload?.supplierShopId ?? payload?.data?.supplierShopId ?? null,
    counts: Object.fromEntries(["main", "detail", "sku"].map((kind) => [kind, files.filter((item) => item.kind === kind).length])),
    files,
  };
  await fs.writeFile(path.join(root, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`);
  console.log(JSON.stringify({ outputDir: root, files: files.length, manifest: "manifest.json" }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
