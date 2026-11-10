// Backend calls. Only role + content are sent; the server owns the system prompt and tools.
const Api = (() => {
  const TIMEOUT_MS = 120000;

  async function chat(conversationId, messages) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
        }),
        signal: ctrl.signal,
      });
      if (!res.ok) {
        let detail = "";
        try { const body = await res.json(); detail = typeof body.detail === "string" ? body.detail : ""; } catch {}
        if (res.status === 422) detail = "The message could not be processed (it may be too long).";
        if (res.status === 429) detail = "Too many requests. Wait a moment and retry.";
        throw new Error(detail || `The server returned an error (${res.status}).`);
      }
      return await res.json();
    } catch (e) {
      if (e.name === "AbortError") throw new Error("The request took too long. Retry, or try a simpler question.");
      if (e instanceof TypeError) throw new Error("Could not reach the server. Check your connection and retry.");
      throw e;
    } finally {
      clearTimeout(timer);
    }
  }
  return { chat };
})();
