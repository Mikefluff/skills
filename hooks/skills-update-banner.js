#!/usr/bin/env node
// skills-update-banner.js — Claude Code status-line hook that ambient-checks
// whether a newer Mikefluff/skills release is available.
//
// Behaviour:
//   • Reads ~/.claude/skills/.skills-collection.json to find the local version.
//   • Fetches the latest GitHub release with a 24-hour cache (tag + topline
//     extracted from the release body).
//   • If a newer version exists, appends a quiet single-line banner to the
//     status-line input: " · skills v0.2.0→0.3.0 +3 skills (topline)".
//   • Never prompts, never modifies files, never installs anything. The user
//     follows up by invoking the `/skills-update` skill on demand.
//
// Installation:
//   bash scripts/install-hook.sh    # idempotent
//   — OR hand-edit ~/.claude/settings.json:
//   {
//     "statusLine": {
//       "type": "command",
//       "command": "node /absolute/path/to/hooks/skills-update-banner.js"
//     }
//   }
//
// The hook fails open: any error (network, parse, missing file) is silently
// swallowed and the original status line passes through unchanged.

const fs = require('fs');
const os = require('os');
const path = require('path');
const https = require('https');

const REPO = 'Mikefluff/skills';
const PREFIX = path.join(os.homedir(), '.claude', 'skills');
const MARKER_PATH = path.join(PREFIX, '.skills-collection.json');
const CACHE_PATH = path.join(os.tmpdir(), 'skills-update-banner-cache.json');
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24h
const HTTP_TIMEOUT_MS = 1500;
const MAX_BANNER_LEN = 80;

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
    setTimeout(() => resolve(data), 200).unref();
  });
}

function safeRead(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return null; }
}

function readLocalMarker() {
  const raw = safeRead(MARKER_PATH);
  if (!raw) return null;
  try {
    const obj = JSON.parse(raw);
    return {
      version: typeof obj.version === 'string' ? obj.version : null,
      skills: Array.isArray(obj.skills) ? obj.skills : [],
    };
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
    return obj;
  } catch {
    return null;
  }
}

function writeCache(payload) {
  try {
    fs.writeFileSync(
      CACHE_PATH,
      JSON.stringify({ cachedAt: Date.now(), ...payload }, null, 2),
    );
  } catch {
    // best-effort cache
  }
}

function ghRequest(reqPath) {
  return new Promise((resolve) => {
    const req = https.request(
      {
        host: 'api.github.com',
        path: reqPath,
        method: 'GET',
        headers: {
          'User-Agent': 'skills-update-banner/2.0',
          'Accept': 'application/vnd.github+json',
        },
        timeout: HTTP_TIMEOUT_MS,
      },
      (res) => {
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => {
          try { resolve(JSON.parse(body)); } catch { resolve(null); }
        });
      },
    );
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
    req.end();
  });
}

async function fetchLatestRelease() {
  const obj = await ghRequest(`/repos/${REPO}/releases/latest`);
  if (!obj || typeof obj.tag_name !== 'string') return null;
  return {
    version: obj.tag_name.replace(/^v/, ''),
    body: typeof obj.body === 'string' ? obj.body : '',
  };
}

async function fetchRemoteSkillsList(version) {
  // Pull skills.json from the tag's tree to count delta.
  const tag = `v${version}`;
  const obj = await ghRequest(`/repos/${REPO}/contents/skills.json?ref=${encodeURIComponent(tag)}`);
  if (!obj || typeof obj.content !== 'string') return null;
  try {
    const decoded = Buffer.from(obj.content, 'base64').toString('utf8');
    const parsed = JSON.parse(decoded);
    return Array.isArray(parsed.skills) ? parsed.skills.map((s) => s.name) : null;
  } catch {
    return null;
  }
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

function extractTopline(body) {
  if (!body) return '';
  // First bulleted line. Strip markdown emphasis + leading "**`name`**." prefix.
  const lines = body.split('\n').map((l) => l.trim()).filter(Boolean);
  for (const line of lines) {
    if (!line.startsWith('-') && !line.startsWith('*')) continue;
    let stripped = line.replace(/^[*-]\s+/, '');
    stripped = stripped.replace(/\*\*([^*]+)\*\*/g, '$1');
    stripped = stripped.replace(/`([^`]+)`/g, '$1');
    stripped = stripped.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    if (stripped.length > 0) return stripped;
  }
  return '';
}

function clip(s, n) {
  if (s.length <= n) return s;
  return s.slice(0, n - 1) + '…';
}

(async () => {
  const upstream = await readStdin();

  const marker = readLocalMarker();
  if (!marker || !marker.version) return SILENT_PASSTHROUGH(upstream);

  let cached = readCache();
  let remoteVersion = cached ? cached.version : null;
  let remoteBody = cached ? cached.body : '';
  let remoteSkills = cached && Array.isArray(cached.skills) ? cached.skills : null;

  if (!remoteVersion) {
    const rel = await fetchLatestRelease();
    if (!rel) return SILENT_PASSTHROUGH(upstream);
    remoteVersion = rel.version;
    remoteBody = rel.body;
    remoteSkills = await fetchRemoteSkillsList(remoteVersion);
    writeCache({
      version: remoteVersion,
      body: remoteBody,
      skills: remoteSkills,
    });
  }

  if (!semverGreater(remoteVersion, marker.version)) return SILENT_PASSTHROUGH(upstream);

  // Build the banner.
  const parts = [];
  parts.push(`skills v${marker.version}→${remoteVersion}`);

  // Skill-count delta.
  if (Array.isArray(remoteSkills) && remoteSkills.length > 0) {
    const localSet = new Set(marker.skills);
    let added = 0;
    for (const name of remoteSkills) if (!localSet.has(name)) added += 1;
    let removed = 0;
    for (const name of marker.skills) if (!remoteSkills.includes(name)) removed += 1;
    if (added > 0)   parts.push(`+${added} skill${added > 1 ? 's' : ''}`);
    if (removed > 0) parts.push(`-${removed} skill${removed > 1 ? 's' : ''}`);
  }

  // Topline from release body.
  const topline = extractTopline(remoteBody);
  let banner = ` · ${parts.join(' ')}`;
  if (topline) banner += ` (${clip(topline, MAX_BANNER_LEN - banner.length - 3)})`;
  banner += ` · /skills-update`;

  process.stdout.write((upstream || '').replace(/\s+$/, '') + banner);
  process.exit(0);
})().catch(() => SILENT_PASSTHROUGH(''));
