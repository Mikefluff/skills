#!/usr/bin/env node
// skills — npm-distributed CLI wrapper around install.sh.
// Delegates every subcommand to install.sh from the package's own directory
// so global installs work the same as the curl-pipe install.

"use strict";

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const PKG_ROOT = path.resolve(__dirname, "..");
const INSTALL_SH = path.join(PKG_ROOT, "install.sh");

function die(msg) {
  process.stderr.write(`skills: ${msg}\n`);
  process.exit(1);
}

if (!fs.existsSync(INSTALL_SH)) {
  die(`install.sh not found in package root (${PKG_ROOT})`);
}

const args = process.argv.slice(2);

// Subcommands map directly onto install.sh flags so users don't need to learn
// two surfaces. Default = install from the bundled checkout.
let cmd;
const passthrough = [];
switch (args[0]) {
  case undefined:
  case "install":
    cmd = ["--copy-from", PKG_ROOT];
    passthrough.push(...args.slice(1));
    break;
  case "update":
    cmd = ["--copy-from", PKG_ROOT, "--update"];
    passthrough.push(...args.slice(1));
    break;
  case "uninstall":
    cmd = ["--uninstall"];
    passthrough.push(...args.slice(1));
    break;
  case "check":
    cmd = ["--check"];
    passthrough.push(...args.slice(1));
    break;
  case "list":
    cmd = ["--list"];
    passthrough.push(...args.slice(1));
    break;
  case "-h":
  case "--help":
  case "help":
    printHelp();
    process.exit(0);
  case "-v":
  case "--version":
  case "version":
    printVersion();
    process.exit(0);
  default:
    // Unknown subcommand — assume it's a direct install.sh flag set
    cmd = args;
    break;
}

const child = spawn("bash", [INSTALL_SH, ...cmd, ...passthrough], {
  stdio: "inherit",
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.exit(128 + signalToNumber(signal));
  }
  process.exit(code ?? 0);
});

function printVersion() {
  const versionFile = path.join(PKG_ROOT, "VERSION");
  if (fs.existsSync(versionFile)) {
    process.stdout.write(fs.readFileSync(versionFile, "utf8"));
  } else {
    const pkg = JSON.parse(
      fs.readFileSync(path.join(PKG_ROOT, "package.json"), "utf8")
    );
    process.stdout.write(`${pkg.version}\n`);
  }
}

function printHelp() {
  process.stdout.write(`skills — Mikefluff/skills collection CLI

Usage:
  skills [install]               Install all skills into ~/.claude/skills
  skills update                  Reinstall (overwrite existing skills)
  skills uninstall               Remove all installed skills + marker
  skills check                   Compare installed version to latest release
  skills list                    List installed skills
  skills version                 Show version
  skills help                    Show this message

Advanced flags are passed through to install.sh. See install.sh --help.

Repo: https://github.com/Mikefluff/skills
`);
}

function signalToNumber(signal) {
  const map = { SIGINT: 2, SIGTERM: 15, SIGHUP: 1, SIGKILL: 9 };
  return map[signal] ?? 0;
}
