#!/usr/bin/env node

const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");

const IMAGE_TYPES = new Map([["image/jpeg", ".jpg"], ["image/png", ".png"], ["image/webp", ".webp"], ["image/gif", ".gif"]]);

function collect(value, keyPath = []) {
  const found = [];
  if (typeof value === "string") {
    const kindPath = keyPath.join(".").toLowerCase();
    const kind = kindPath.includes("sku") ? "sku" : kindPath.includes("detail") || kindPath.includes("description") ? "detail" : "main";
    for (const match of value.matchAll(/https?:\/\/[^\s'"<>]+/g)) found.push({ url: match[0], kind });
  } else if (Array.isArray(value)) value.forEach((item, index) => found.push(...collect(item, [...keyPath, String(index)])));
  else if (value && typeof value === "object") for (const [key, item] of Object.entries(value)) found.push(...collect(item, [...keyPath, key]));
  return found;
}

async function main() {
  const [input, outputDir] = process.argv.slice(2);
  if (!input || !outputDir) throw new Error("usage: download-huice-detail-images <detail.json> <output-dir>");
  const payload = JSON.parse(await fs.readFile(path.resolve(input), "utf8"));
  const root = path.resolve(outputDir);
  const seenUrls = new Set();
  const seenHashes = new Set();
  const files = [];
  await fs.mkdir(root, { recursive: true });

  for (const candidate of collect(payload)) {
    if (seenUrls.has(candidate.url)) continue;
    seenUrls.add(candidate.url);
    const response = await fetch(candidate.url);
    if (!response.ok) throw new Error(`image download failed: HTTP ${response.status}`);
    const mime = String(response.headers.get("content-type") || "").split(";", 1)[0].toLowerCase();
    const extension = IMAGE_TYPES.get(mime);
    if (!extension) throw new Error(`unsupported media type: ${mime || "missing"}`);
    const body = Buffer.from(await response.arrayBuffer());
    const sha256 = crypto.createHash("sha256").update(body).digest("hex");
    if (seenHashes.has(sha256)) continue;
    seenHashes.add(sha256);
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

main().catch((error) => { console.error(error.message); process.exitCode = 1; });
