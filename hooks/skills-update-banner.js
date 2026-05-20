#!/usr/bin/env node
// skills-update-banner.js — Claude Code status-line hook that ambient-checks
// whether a newer Mikefluff/skills release is available.
//
// Behaviour:
//   • Reads ~/.claude/skills/.skills-collection.json to find the local version.
//   • Fetches the latest GitHub release tag with a 24-hour cache.
//   • If a newer version exists, appends a quiet single-line banner to the
//     status-line input (so it shows up next to whatever else is there).
//   • Never prompts, never modifies files, never installs anything. The user
//     follows up by invoking the `/skills-update` skill on demand.
//
// Installation:
//   Add to ~/.claude/settings.json:
//   {
//     "statusLine": {
//       "type": "command",
//       "command": "node /absolute/path/to/hooks/skills-update-banner.js"
//     }
//   }
//
// The hook fails open: any error (network, parse, missing file) is silently
// swallowed and the original status line passes through unchanged. The goal is
// "nice-to-have ambient signal", not a critical path.

const fs = require('fs');
const os = require('os');
const path = require('path');
const https = require('https');

const REPO = 'Mikefluff/skills';
const PREFIX = path.join(os.homedir(), '.claude', 'skills');
const MARKER_PATH = path.join(PREFIX, '.skills-collection.json');
const CACHE_PATH = path.join(os.tmpdir(), 'skills-update-banner-cache.json');
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24h

const SILENT_PASSTHROUGH = (line) => {
  process.stdout.write(line || '');
  process.exit(0);
};

function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    if (process.stdin.isTTY) return resolve('');
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => (data += chunk));
    process.stdin.on('end', () => resolve(data));
    // Guard: don't block forever on a stale stdin
    setTimeout(() => resolve(data), 200).unref();
  });
}

function safeRead(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return null; }
}

function readLocalVersion() {
  const raw = safeRead(MARKER_PATH);
  if (!raw) return null;
  try {
    const obj = JSON.parse(raw);
    return typeof obj.version === 'string' ? obj.version : null;
  } catch {
    return null;
  }
}

function readCache() {
  const raw = safeRead(CACHE_PATH);
  if (!raw) return null;
  try {
    const obj = JSON.parse(raw);
    if (typeof obj.cachedAt !== 'number' || typeof obj.version !== 'string') return null;
    if (Date.now() - obj.cachedAt > CACHE_TTL_MS) return null;
    return obj.version;
  } catch {
    return null;
  }
}

function writeCache(version) {
  try {
    fs.writeFileSync(
      CACHE_PATH,
      JSON.stringify({ cachedAt: Date.now(), version }, null, 2),
    );
  } catch {
    // ignore — cache is best-effort
  }
}

function fetchLatestTag() {
  return new Promise((resolve) => {
    const req = https.request(
      {
        host: 'api.github.com',
        path: `/repos/${REPO}/releases/latest`,
        method: 'GET',
        headers: {
          'User-Agent': 'skills-update-banner/1.0',
          'Accept': 'application/vnd.github+json',
        },
        timeout: 1500,
      },
      (res) => {
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => {
          try {
            const obj = JSON.parse(body);
            const tag = typeof obj.tag_name === 'string' ? obj.tag_name : null;
            if (!tag) return resolve(null);
            resolve(tag.replace(/^v/, ''));
          } catch {
            resolve(null);
          }
        });
      },
    );
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.end();
  });
}

function semverGreater(a, b) {
  const pa = a.split('.').map((n) => parseInt(n, 10) || 0);
  const pb = b.split('.').map((n) => parseInt(n, 10) || 0);
  for (let i = 0; i < 3; i++) {
    if ((pa[i] || 0) > (pb[i] || 0)) return true;
    if ((pa[i] || 0) < (pb[i] || 0)) return false;
  }
  return false;
}

(async () => {
  const upstream = await readStdin();

  const local = readLocalVersion();
  if (!local) return SILENT_PASSTHROUGH(upstream);

  let remote = readCache();
  if (!remote) {
    remote = await fetchLatestTag();
    if (remote) writeCache(remote);
  }
  if (!remote) return SILENT_PASSTHROUGH(upstream);

  if (!semverGreater(remote, local)) return SILENT_PASSTHROUGH(upstream);

  // Emit upstream + quiet update banner. Keep banner short so it doesn't
  // overflow narrow terminals.
  const banner = ` · skills v${local}→${remote} (run /skills-update)`;
  process.stdout.write((upstream || '').replace(/\s+$/, '') + banner);
  process.exit(0);
})().catch(() => SILENT_PASSTHROUGH(''));
