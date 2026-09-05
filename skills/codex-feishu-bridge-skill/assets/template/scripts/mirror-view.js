const fs = require("fs");
const path = require("path");

const rootDir = path.resolve(__dirname, "..");
const statePath = path.join(rootDir, ".codex-feishu-bridge", "state.json");
const target = process.argv[2] || "latest";
const count = Math.max(1, Math.min(200, Number(process.argv[3]) || 60));

if (!fs.existsSync(statePath)) {
  console.error(`Mirror state not found: ${statePath}`);
  process.exit(1);
}

const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
const conversations = Object.entries(state.conversations || {});

function fmt(value) {
  if (!value) {
    return "unknown";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

let match = null;
if (target === "latest") {
  match =
    conversations
      .map(([key, value]) => ({ key, value }))
      .sort((a, b) =>
        String(b.value.updatedAt || "").localeCompare(String(a.value.updatedAt || ""))
      )[0] || null;
} else {
  match =
    conversations
      .map(([key, value]) => ({ key, value }))
      .find(
        ({ key, value }) =>
          value.threadId === target ||
          value.chatId === target ||
          value.senderOpenId === target ||
          key === target
      ) || null;
}

if (!match) {
  console.error(`No mirrored conversation matched: ${target}`);
  process.exit(1);
}

const { key, value } = match;
const history = Array.isArray(value.history) ? value.history.slice(-count) : [];

console.log("== Mirror View ==");
console.log(`conversationKey: ${key}`);
console.log(`chatId: ${value.chatId || ""}`);
console.log(`senderOpenId: ${value.senderOpenId || ""}`);
console.log(`threadId: ${value.threadId || ""}`);
console.log(`updatedAt: ${fmt(value.updatedAt)}`);
if (value.mirror && value.mirror.markdown) {
  console.log(`markdown: ${value.mirror.markdown}`);
}
if (value.mirror && value.mirror.jsonl) {
  console.log(`jsonl: ${value.mirror.jsonl}`);
}
console.log("");
console.log(`== Recent ${history.length} item(s) ==`);
for (const item of history) {
  const role =
    item.role === "user" ? "User" : item.role === "assistant" ? "Assistant" : "System";
  console.log(`[${role}] ${fmt(item.at)} | ${item.source || "bridge"}`);
  console.log(String(item.text || "").trim());
  console.log("");
}
