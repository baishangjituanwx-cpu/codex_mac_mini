#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const { spawn, spawnSync } = require("child_process");

const scriptName = process.argv[2];
const extraArgs = process.argv.slice(3);
const scriptsDir = __dirname;

if (!scriptName) {
  console.error("Usage: node scripts/run-platform-script.js <script-name> [args...]");
  process.exit(1);
}

function pickPowerShell() {
  const candidates = ["pwsh.exe", "pwsh", "powershell.exe", "powershell"];
  for (const candidate of candidates) {
    const result = spawnSync(candidate, ["-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"], {
      stdio: "ignore",
    });
    if (!result.error && result.status === 0) {
      return candidate;
    }
  }
  return null;
}

let command = "";
let args = [];

if (process.platform === "win32") {
  const target = path.join(scriptsDir, `${scriptName}.ps1`);
  if (!fs.existsSync(target)) {
    console.error(`Missing PowerShell script: ${target}`);
    process.exit(1);
  }
  const shell = pickPowerShell();
  if (!shell) {
    console.error("PowerShell was not found on PATH.");
    process.exit(1);
  }
  command = shell;
  args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", target, ...extraArgs];
} else {
  const target = path.join(scriptsDir, `${scriptName}.sh`);
  if (!fs.existsSync(target)) {
    console.error(`Missing shell script: ${target}`);
    process.exit(1);
  }
  command = "zsh";
  args = [target, ...extraArgs];
}

const child = spawn(command, args, { stdio: "inherit" });
child.on("error", (error) => {
  console.error(error.message);
  process.exit(1);
});
child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
