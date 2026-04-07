#!/usr/bin/env node
// ─────────────────────────────────────────────────────────────────────────────
// speKset — Magic Invite Link Generator
// Usage:
//   node generate-invite.js [name] [days]
//
// Examples:
//   node generate-invite.js "Nike AV"        → 7-day link (default)
//   node generate-invite.js "Marcus"  14     → 14-day link
//   node generate-invite.js "Festival"  1    → expires end of today
//   node generate-invite.js                  → prompts interactively
// ─────────────────────────────────────────────────────────────────────────────

const crypto = require('crypto');
const readline = require('readline');

// ── Shared secret — keep this private, never commit to public repos ───────────
const SECRET = 'sk_inv_7f3a9c2e1b4d8f6a0e5c3b7d2a9f1e4c';

// ── Base URL ──────────────────────────────────────────────────────────────────
const BASE_URL = 'https://spekset.com';

// ─────────────────────────────────────────────────────────────────────────────

function generateToken(expiryTimestamp) {
  const payload = String(expiryTimestamp);
  const hmac = crypto.createHmac('sha256', SECRET).update(payload).digest('hex');
  // Token = base64url(payload + ':' + first 16 chars of hmac)
  const raw = payload + ':' + hmac.slice(0, 32);
  return Buffer.from(raw).toString('base64url');
}

function buildLink(name, days) {
  const now = Date.now();
  const expiry = now + days * 24 * 60 * 60 * 1000;
  const token = generateToken(expiry);
  const url = `${BASE_URL}/?i=${token}`;
  const expiryDate = new Date(expiry).toLocaleDateString('en-US', {
    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
  });

  console.log('');
  console.log('─'.repeat(60));
  console.log(`  speKset Invite Link`);
  if (name) console.log(`  Recipient : ${name}`);
  console.log(`  Expires   : ${expiryDate} (${days} day${days !== 1 ? 's' : ''})`);
  console.log('─'.repeat(60));
  console.log('');
  console.log(url);
  console.log('');
}

async function promptAndGenerate() {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const ask = (q) => new Promise(res => rl.question(q, res));

  const name = await ask('Recipient name (optional): ');
  const daysStr = await ask('Expires in how many days? [7]: ');
  const days = parseInt(daysStr) || 7;
  rl.close();
  buildLink(name.trim(), days);
}

// ── Main ──────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);

if (args.length === 0) {
  promptAndGenerate();
} else {
  const name = args[0] || '';
  const days = parseInt(args[1]) || 7;
  buildLink(name, days);
}
