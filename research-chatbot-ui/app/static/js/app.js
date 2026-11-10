// Application state and event wiring.
(() => {
  const { $ } = UI;
  let convs = Storage.load();
  let activeId = Storage.getActive();
  let loading = false;       // true while a request is in flight (blocks duplicate submits)
  let pendingRetry = false;  // true when the last user message has no answer due to an error

  const active = () => convs.find(c => c.id === activeId) || null;
  const persist = () => Storage.save(convs);

  function render() {
    UI.renderSidebar(convs, activeId, { select, remove });
    UI.renderMessages(active(), loading);
    updateSend();
  }

  function updateSend() {
    $("sendBtn").disabled = loading || $("input").value.trim() === "";
    $("retryBtn").disabled = loading;
  }

  function select(id) {
    if (loading) return;
    activeId = id; Storage.setActive(id); pendingRetry = false; UI.hideError();
    closeSidebar(); render();
  }

  function newChat() {
    if (loading) return;
    const cur = active();
    if (cur && cur.messages.length === 0) { closeSidebar(); $("input").focus(); return; } // reuse empty chat
    const c = Storage.newConversation();
    convs.push(c); activeId = c.id; Storage.setActive(c.id);
    persist(); pendingRetry = false; UI.hideError(); closeSidebar(); render(); $("input").focus();
  }

  function remove(id) {
    if (loading) return;
    if (!confirm("Delete this chat?")) return;
    convs = convs.filter(c => c.id !== id);
    if (activeId === id) { activeId = convs.length ? convs[convs.length - 1].id : null; Storage.setActive(activeId); }
    persist(); pendingRetry = false; UI.hideError(); render();
  }

  async function requestReply(conv) {
    loading = true; UI.hideError(); render();
    try {
      const data = await Api.chat(conv.id, conv.messages);
      const toolCount = Array.isArray(data.tool_events) ? data.tool_events.length : 0;
      conv.messages.push({
        role: "assistant",
        content: data.assistant_text || "(The assistant returned an empty response.)",
        timestamp: new Date().toISOString(),
        ...(toolCount ? { tools_used: toolCount } : {}),
      });
      conv.updated_at = new Date().toISOString();
      pendingRetry = false;
      persist();
    } catch (e) {
      pendingRetry = true;
      UI.showError(e.message);
    } finally {
      loading = false; render(); $("input").focus();
    }
  }

  async function send() {
    const text = $("input").value.trim();
    if (!text || loading) return;
    let conv = active();
    if (!conv) { conv = Storage.newConversation(); convs.push(conv); activeId = conv.id; Storage.setActive(conv.id); }

    const now = new Date().toISOString();
    conv.messages.push({ role: "user", content: text, timestamp: now });
    if (conv.messages.length === 1) conv.title = text.length > 40 ? text.slice(0, 40).trimEnd() + "..." : text;
    conv.updated_at = now;
    persist();
    $("input").value = ""; autosize();
    await requestReply(conv);
  }

  // Retry re-sends the existing history; the user message is not appended again.
  async function retry() {
    const conv = active();
    if (!conv || loading || !pendingRetry) return;
    await requestReply(conv);
  }

  function autosize() {
    const t = $("input"); t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight, 200) + "px"; updateSend();
  }

  const sidebar = $("sidebar");
  function closeSidebar() { sidebar.classList.remove("open"); }

  $("newChat").onclick = newChat;
  $("sendBtn").onclick = send;
  $("retryBtn").onclick = retry;
  $("menuBtn").onclick = () => sidebar.classList.toggle("open");
  $("scrim").onclick = closeSidebar;
  $("input").addEventListener("input", autosize);
  $("input").addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); }
  });

  // Initial state
  if (!active()) { activeId = convs.length ? convs[convs.length - 1].id : null; }
  if (!activeId) { const c = Storage.newConversation(); convs.push(c); activeId = c.id; persist(); }
  Storage.setActive(activeId);

  // If the last stored message is an unanswered user message (e.g. page reloaded after an error), offer retry.
  const cur = active();
  if (cur && cur.messages.length && cur.messages[cur.messages.length - 1].role === "user") {
    pendingRetry = true; UI.showError("The last message has no reply yet.");
  }
  render();
})();
