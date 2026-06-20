const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const DEFAULT_BASE_URL = "http://bysl.baiyimiandan.com";
const DEFAULT_LANG = "zh-cn";

function md5(input) {
  return crypto.createHash("md5").update(String(input)).digest("hex");
}

function decodeJwtPayload(token) {
  if (!token || typeof token !== "string") {
    return null;
  }

  const parts = token.split(".");
  if (parts.length < 2) {
    return null;
  }

  try {
    return JSON.parse(Buffer.from(parts[1], "base64url").toString("utf8"));
  } catch {
    return null;
  }
}

function buildSignedHeaders({
  pathname,
  token,
  signConfig,
  time = Math.floor(Date.now() / 1000).toString(),
  custom = Math.random().toString(36).slice(2),
  lang = DEFAULT_LANG,
}) {
  if (!pathname) {
    throw new Error("pathname is required to build signed headers.");
  }
  if (!token) {
    throw new Error("token is required to build signed headers.");
  }
  if (!signConfig?.cloudid || !signConfig?.sign_key) {
    throw new Error("signConfig.cloudid and signConfig.sign_key are required.");
  }

  const signature = md5(
    `${signConfig.cloudid}${signConfig.sign_key}${pathname.toLowerCase()}${time}pc1${token}${custom}`,
  );

  return {
    client: "pc",
    cloudid: signConfig.cloudid,
    version: "1",
    time,
    custom,
    sign: signature,
    token,
    lang,
  };
}

function decryptEnvelope(payload) {
  if (!payload || payload.encrypt !== 1 || typeof payload.data !== "string") {
    return payload;
  }

  const iv = md5(`key_${payload.time}`).slice(0, 16);
  const key = md5(payload.sign).slice(0, 16);
  const decipher = crypto.createDecipheriv(
    "aes-128-cbc",
    Buffer.from(key, "utf8"),
    Buffer.from(iv, "utf8"),
  );

  let plaintext = decipher.update(payload.data, "base64", "utf8");
  plaintext += decipher.final("utf8");

  return {
    ...payload,
    data: JSON.parse(plaintext),
  };
}

async function parseJsonResponse(response) {
  const text = await response.text();
  let parsed;

  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error(`Expected JSON response, got: ${text.slice(0, 400)}`);
  }

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${text.slice(0, 400)}`);
  }

  return decryptEnvelope(parsed);
}

function readPromptFile(filePath) {
  if (!filePath) {
    throw new Error("--prompt-file is required.");
  }

  return fs.readFileSync(filePath, "utf8").replace(/^\uFEFF/, "");
}

function countQuestionMarks(text) {
  return (String(text).match(/\?/g) || []).length;
}

function normalizeImageRefs(images) {
  if (!images) {
    return "";
  }

  const items = Array.isArray(images) ? images : String(images).split(",");
  return items.map((item) => String(item).trim()).filter(Boolean).join(",");
}

function requirePrompt(prompt) {
  if (!prompt || !String(prompt).trim()) {
    throw new Error("Prompt is required. Prefer --prompt-file for Chinese text.");
  }

  return String(prompt);
}

function buildImageCreatePayload({
  modelId,
  prompt,
  ratio = "1:1",
  images = "",
}) {
  const parsedModelId = Number(modelId);
  if (!Number.isInteger(parsedModelId) || parsedModelId <= 0) {
    throw new Error("modelId must be a positive integer.");
  }

  return {
    model_id: parsedModelId,
    prompt: requirePrompt(prompt),
    image: normalizeImageRefs(images),
    ratio,
  };
}

function buildNanoPayload({
  prompt,
  ratio = "1:1",
  images = "",
  isPro = false,
  resolution = "1K",
}) {
  const payload = {
    content: requirePrompt(prompt),
    is_pro: Boolean(isPro),
    ratio,
    images: normalizeImageRefs(images),
  };

  if (payload.is_pro) {
    payload.resolution_s = resolution || "1K";
  }

  return payload;
}

function guessMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "application/octet-stream";
}

function createClient({
  baseUrl = process.env.NANO_BASE_URL || DEFAULT_BASE_URL,
  token = process.env.NANO_TOKEN || "",
  cookie = process.env.NANO_COOKIE || "",
  lang = process.env.NANO_LANG || DEFAULT_LANG,
  fetchImpl = globalThis.fetch,
} = {}) {
  if (!fetchImpl) {
    throw new Error("fetch is not available. Use Node.js 20 or newer.");
  }

  let signConfigCache = null;

  async function getSignConfig() {
    if (signConfigCache) {
      return signConfigCache;
    }

    const response = await fetchImpl(`${baseUrl}/api/common/base`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=UTF-8",
      },
      body: "{}",
    });
    const envelope = await parseJsonResponse(response);

    if (envelope.code !== 0) {
      throw new Error(`Failed to load sign config: ${JSON.stringify(envelope)}`);
    }

    signConfigCache = envelope.data;
    return signConfigCache;
  }

  async function request(pathname, options = {}) {
    const {
      method = "POST",
      body,
      extraHeaders = {},
      useJson = true,
      needsAuth = true,
    } = options;
    const headers = { ...extraHeaders };

    if (useJson) {
      headers["Content-Type"] = "application/json;charset=UTF-8";
    }
    if (cookie) {
      headers.Cookie = cookie;
    }
    if (needsAuth) {
      if (!token) {
        throw new Error("NANO_TOKEN is required for authenticated requests.");
      }
      const signConfig = await getSignConfig();
      Object.assign(headers, buildSignedHeaders({ pathname, token, signConfig, lang }));
    }

    const response = await fetchImpl(`${baseUrl}${pathname}`, {
      method,
      headers,
      body,
    });

    return parseJsonResponse(response);
  }

  async function callApi(pathname, payload = {}) {
    const envelope = await request(pathname, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (envelope.code !== 0) {
      throw new Error(`${pathname} failed: ${JSON.stringify(envelope)}`);
    }

    return envelope.data;
  }

  async function uploadFile(filePath) {
    const fileBuffer = fs.readFileSync(filePath);
    const formData = new FormData();
    const blob = new Blob([fileBuffer], { type: guessMimeType(filePath) });
    formData.append("file", blob, path.basename(filePath));

    const envelope = await request("/api/common/upload", {
      method: "POST",
      body: formData,
      useJson: false,
    });

    if (envelope.code !== 0) {
      throw new Error(`Upload failed for ${filePath}: ${JSON.stringify(envelope)}`);
    }

    return envelope.data;
  }

  async function downloadUrl(url, outPath) {
    const response = await fetchImpl(url);
    if (!response.ok) {
      throw new Error(`Download failed with HTTP ${response.status}: ${url}`);
    }

    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, Buffer.from(await response.arrayBuffer()));
    return outPath;
  }

  return {
    baseUrl,
    token,
    getSignConfig,
    request,
    callApi,
    uploadFile,
    downloadUrl,
    userInfo: () => callApi("/api/user/info", {}),
    listTasks: (payload = {}) => callApi("/api/ai_image/list", payload),
    imageModelGroups: () => callApi("/api/ai_image/image_model_type", {}),
    imageModels: (payload) => callApi("/api/ai_video/video_model", payload),
    imageCreate: (payload) => callApi("/api/ai_image/image_create", payload),
    nanoCreate: (payload) => callApi("/api/ai_image/nano_banana", payload),
  };
}

module.exports = {
  DEFAULT_BASE_URL,
  buildImageCreatePayload,
  buildNanoPayload,
  buildSignedHeaders,
  countQuestionMarks,
  createClient,
  decodeJwtPayload,
  decryptEnvelope,
  normalizeImageRefs,
  parseJsonResponse,
  readPromptFile,
};
