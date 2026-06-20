#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const {
  buildImageCreatePayload,
  buildNanoPayload,
  countQuestionMarks,
  createClient,
  decodeJwtPayload,
  readPromptFile,
} = require("../src/bysl-client");

function printHelp() {
  console.log([
    "Usage:",
    "  bysl-api doctor",
    "  bysl-api sign-config",
    "  bysl-api user",
    "  bysl-api list [--type nano|image] [--page 1 --pagesize 10]",
    "  bysl-api upload <file1> [file2 ...]",
    "  bysl-api image-model-groups",
    "  bysl-api image-models [--type 15 --source 2]",
    "  bysl-api image-create --model-id 63 --ratio 9:16 --prompt-file prompt.md [--images url1,url2] [--out out.png]",
    "  bysl-api nano-create --ratio 1:1 --prompt-file prompt.md [--images url1,url2] [--is-pro true --resolution 1K] [--out out.png]",
    "  bysl-api download --url https://... --out out.png",
    "",
    "Environment:",
    "  NANO_TOKEN     Required for authenticated API calls. Use localStorage.user.token.",
    "  NANO_BASE_URL  Optional. Default: http://bysl.baiyimiandan.com",
    "  NANO_COOKIE    Optional. Usually not needed.",
  ].join("\n"));
}

function parseFlags(argv) {
  const flags = {};
  const positionals = [];

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (!arg.startsWith("--")) {
      positionals.push(arg);
      continue;
    }

    const key = arg.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) {
      flags[key] = "true";
      continue;
    }

    flags[key] = next;
    index += 1;
  }

  return { flags, positionals };
}

function parseBoolean(value, defaultValue = false) {
  if (value === undefined) return defaultValue;
  return ["1", "true", "yes", "y", "on"].includes(String(value).toLowerCase());
}

function parseInteger(value, fallback) {
  if (value === undefined) return fallback;
  const parsed = Number(value);
  if (!Number.isInteger(parsed)) {
    throw new Error(`Expected integer, got: ${value}`);
  }
  return parsed;
}

function printJson(value) {
  console.log(JSON.stringify(value, null, 2));
}

function promptFromFlags(flags) {
  if (flags["prompt-file"]) {
    return readPromptFile(flags["prompt-file"]);
  }
  if (flags.prompt) {
    return flags.prompt;
  }
  throw new Error("Use --prompt-file for prompt text. --prompt is only suitable for ASCII smoke tests.");
}

function promptDiagnostics(prompt) {
  return {
    promptLength: prompt.length,
    questionMarkCount: countQuestionMarks(prompt),
  };
}

function firstResultUrl(task) {
  if (!task || typeof task !== "object") return "";
  if (typeof task.url === "string" && task.url) return task.url;
  if (Array.isArray(task.url) && task.url[0]) return task.url[0];
  if (typeof task.result === "string" && task.result.startsWith("http")) return task.result;
  if (Array.isArray(task.result) && task.result[0]) return task.result[0];
  return "";
}

async function pollTask({
  client,
  taskId,
  listPayload,
  intervalMs,
  maxPolls,
}) {
  for (let attempt = 1; attempt <= maxPolls; attempt += 1) {
    const list = await client.listTasks(listPayload);
    const items = Array.isArray(list?.data) ? list.data : Array.isArray(list?.list) ? list.list : [];
    const task = items.find((item) => String(item.id ?? item.task_id) === String(taskId));

    if (task) {
      const status = Number(task.task_status ?? task.status);
      const url = firstResultUrl(task);
      console.error(`poll ${attempt}/${maxPolls}: status=${status || "unknown"} url=${url ? "yes" : "no"}`);

      if (status === 5 && url) {
        return { task, url };
      }
      if (status === 6) {
        throw new Error(`Task failed: ${JSON.stringify(task)}`);
      }
    } else {
      console.error(`poll ${attempt}/${maxPolls}: task not visible yet`);
    }

    if (attempt < maxPolls) {
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
  }

  throw new Error(`Timed out waiting for task ${taskId}.`);
}

async function createAndMaybeDownload({
  client,
  create,
  listPayload,
  flags,
  result,
}) {
  const shouldPoll = parseBoolean(flags.poll, true);
  const output = {
    create: result,
  };

  if (!shouldPoll) {
    printJson(output);
    return;
  }

  const taskId = result.task_id ?? result.id;
  if (!taskId) {
    throw new Error(`Create response did not include task_id: ${JSON.stringify(result)}`);
  }

  const polled = await pollTask({
    client,
    taskId,
    listPayload,
    intervalMs: parseInteger(flags["interval-ms"], 8000),
    maxPolls: parseInteger(flags["max-polls"], 60),
  });

  output.task = polled.task;
  output.url = polled.url;

  if (flags.out) {
    const outPath = path.resolve(flags.out);
    await client.downloadUrl(polled.url, outPath);
    output.out = outPath;
    output.bytes = fs.statSync(outPath).size;
  }

  printJson(output);
}

async function main() {
  const [, , command, ...rest] = process.argv;

  if (!command || command === "help" || command === "--help" || command === "-h") {
    printHelp();
    return;
  }

  const { flags, positionals } = parseFlags(rest);
  const client = createClient();

  if (command === "doctor") {
    const token = process.env.NANO_TOKEN || "";
    const payload = decodeJwtPayload(token);
    const result = {
      node: process.version,
      baseUrl: client.baseUrl,
      hasToken: Boolean(token),
      tokenLength: token.length,
      tokenUserId: payload?.id ?? null,
      tokenExpiresAt: payload?.exp ? new Date(payload.exp * 1000).toISOString() : null,
    };

    if (token) {
      await client.userInfo();
      const list = await client.listTasks({ page: 1, pagesize: 1 });
      result.api = "ok";
      result.latestTaskVisible = Boolean(
        (Array.isArray(list?.data) && list.data.length) ||
        (Array.isArray(list?.list) && list.list.length),
      );
    } else {
      result.api = "skipped: NANO_TOKEN is not set";
    }

    printJson(result);
    return;
  }

  if (command === "sign-config") {
    printJson(await client.getSignConfig());
    return;
  }

  if (command === "user") {
    printJson(await client.userInfo());
    return;
  }

  if (command === "list") {
    const payload = {
      page: parseInteger(flags.page, 1),
      pagesize: parseInteger(flags.pagesize, 10),
    };
    if (flags.type === "image") {
      payload.type = 2;
    } else if (flags.type && flags.type !== "nano") {
      payload.type = parseInteger(flags.type);
    }
    printJson(await client.listTasks(payload));
    return;
  }

  if (command === "upload") {
    if (!positionals.length) {
      throw new Error("upload requires at least one file path.");
    }
    const uploads = [];
    for (const filePath of positionals) {
      uploads.push({ file: filePath, response: await client.uploadFile(filePath) });
    }
    printJson(uploads);
    return;
  }

  if (command === "image-model-groups") {
    printJson(await client.imageModelGroups());
    return;
  }

  if (command === "image-models") {
    const payload = {};
    if (flags.type !== undefined) payload.type = parseInteger(flags.type);
    if (flags.source !== undefined) payload.source = parseInteger(flags.source);
    printJson(await client.imageModels(payload));
    return;
  }

  if (command === "image-create") {
    const prompt = promptFromFlags(flags);
    const payload = buildImageCreatePayload({
      modelId: flags["model-id"],
      prompt,
      ratio: flags.ratio || "1:1",
      images: flags.images || "",
    });
    const result = await client.imageCreate(payload);
    await createAndMaybeDownload({
      client,
      create: "image-create",
      listPayload: { page: 1, pagesize: parseInteger(flags.pagesize, 20), type: 2 },
      flags,
      result: {
        ...result,
        diagnostics: promptDiagnostics(prompt),
      },
    });
    return;
  }

  if (command === "nano-create") {
    const prompt = promptFromFlags(flags);
    const payload = buildNanoPayload({
      prompt,
      ratio: flags.ratio || "1:1",
      images: flags.images || "",
      isPro: parseBoolean(flags["is-pro"], false),
      resolution: flags.resolution || "1K",
    });
    const result = await client.nanoCreate(payload);
    await createAndMaybeDownload({
      client,
      create: "nano-create",
      listPayload: { page: 1, pagesize: parseInteger(flags.pagesize, 20) },
      flags,
      result: {
        ...result,
        diagnostics: promptDiagnostics(prompt),
      },
    });
    return;
  }

  if (command === "download") {
    if (!flags.url || !flags.out) {
      throw new Error("download requires --url and --out.");
    }
    const outPath = path.resolve(flags.out);
    await client.downloadUrl(flags.url, outPath);
    printJson({
      out: outPath,
      bytes: fs.statSync(outPath).size,
    });
    return;
  }

  throw new Error(`Unknown command: ${command}`);
}

main().catch((error) => {
  console.error(error?.stack || String(error));
  process.exitCode = 1;
});
