/**
 * Telegram webhook receiver for llm-wiki cloud pipeline.
 *
 * Flow:
 *   1. Telegram POSTs an Update to /tg with header X-Telegram-Bot-Api-Secret-Token.
 *   2. Verify secret + chat_id allowlist.
 *   3. Extract URL from message text.
 *   4. Send ack via sendMessage ("đang xử lý...").
 *   5. Trigger GitHub repository_dispatch with {url, chat_id, msg_id}.
 *   6. GitHub Actions workflow ingest-url.yml does the rest and replies to user.
 *
 * Secrets (set via `wrangler secret put <NAME>`):
 *   WEBHOOK_SECRET          shared with Telegram setWebhook secret_token
 *   ALLOWED_CHAT_ID         single allowed chat id
 *   GITHUB_DISPATCH_TOKEN   PAT with repo scope (or fine-grained: contents+actions)
 *   GITHUB_REPO             "owner/name" e.g. "liangdabiao/llm-wiki"
 *   TELEGRAM_BOT_TOKEN      bot token for ack reply
 */

const URL_RE = /https?:\/\/[^\s<>"']+/i;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/") {
      return new Response("llm-wiki webhook OK\n", { status: 200 });
    }

    if (request.method !== "POST" || url.pathname !== "/tg") {
      return new Response("not found", { status: 404 });
    }

    // Verify Telegram secret header.
    const secret = request.headers.get("x-telegram-bot-api-secret-token") || "";
    if (!env.WEBHOOK_SECRET || secret !== env.WEBHOOK_SECRET) {
      return new Response("forbidden", { status: 403 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("bad json", { status: 400 });
    }

    const msg = update.message || update.edited_message;
    if (!msg || !msg.text) {
      return new Response("ignored: no text", { status: 200 });
    }

    const chatId = String(msg.chat?.id ?? "");
    const msgId = String(msg.message_id ?? "");
    const allowed = String(env.ALLOWED_CHAT_ID || "");

    if (!allowed || chatId !== allowed) {
      console.log(`reject chat_id=${chatId} (allowed=${allowed})`);
      return new Response("ok", { status: 200 });
    }

    const m = URL_RE.exec(msg.text);
    if (!m) {
      await sendMessage(env, chatId, msgId, "❌ Không tìm thấy URL hợp lệ. Gửi 1 link http(s) nhé.");
      return new Response("ok", { status: 200 });
    }
    const targetUrl = m[0];

    // Ack immediately so user knows we got it.
    await sendMessage(
      env,
      chatId,
      msgId,
      `🔄 Đã nhận URL — đang đẩy vào pipeline GitHub Actions:\n${targetUrl}\n\nSẽ reply link wiki khi pipeline xong (thường 2–6 phút).`,
    );

    // Trigger repository_dispatch.
    const dispatchResp = await dispatchToGitHub(env, {
      url: targetUrl,
      chat_id: chatId,
      msg_id: msgId,
    });

    if (!dispatchResp.ok) {
      const body = await dispatchResp.text();
      console.log(`dispatch failed: ${dispatchResp.status} ${body}`);
      await sendMessage(
        env,
        chatId,
        msgId,
        `❌ Không trigger được GitHub Actions (HTTP ${dispatchResp.status}). Check worker logs.`,
      );
      return new Response("dispatch failed", { status: 500 });
    }

    return new Response("ok", { status: 200 });
  },
};

async function sendMessage(env, chatId, replyTo, text) {
  if (!env.TELEGRAM_BOT_TOKEN) return;
  const body = {
    chat_id: chatId,
    text,
    disable_web_page_preview: true,
  };
  if (replyTo) body.reply_to_message_id = Number(replyTo);
  try {
    await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (e) {
    console.log("sendMessage error:", e);
  }
}

async function dispatchToGitHub(env, clientPayload) {
  const repo = env.GITHUB_REPO;
  const token = env.GITHUB_DISPATCH_TOKEN;
  if (!repo || !token) {
    return new Response("missing GITHUB_REPO or GITHUB_DISPATCH_TOKEN", { status: 500 });
  }
  return fetch(`https://api.github.com/repos/${repo}/dispatches`, {
    method: "POST",
    headers: {
      accept: "application/vnd.github+json",
      authorization: `Bearer ${token}`,
      "content-type": "application/json",
      "user-agent": "llm-wiki-cf-worker",
      "x-github-api-version": "2022-11-28",
    },
    body: JSON.stringify({
      event_type: "ingest-url",
      client_payload: clientPayload,
    }),
  });
}
