// DOM rendering helpers. No state lives here.
const UI = (() => {
  const $ = id => document.getElementById(id);

  if (window.DOMPurify) {
    DOMPurify.addHook("afterSanitizeAttributes", node => {
      if (node.tagName === "A") { node.setAttribute("target", "_blank"); node.setAttribute("rel", "noopener noreferrer"); }
    });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // Markdown -> sanitized HTML. Falls back to escaped text if the libraries failed to load.
  function renderMarkdown(text) {
    if (window.marked && window.DOMPurify) {
      return DOMPurify.sanitize(marked.parse(text, { breaks: true, gfm: true }));
    }
    return `<p style="white-space:pre-wrap">${escapeHtml(text)}</p>`;
  }

  function renderSidebar(convs, activeId, handlers) {
    const list = $("chatList");
    list.replaceChildren();
    [...convs].sort((a, b) => b.updated_at.localeCompare(a.updated_at)).forEach(c => {
      const li = document.createElement("li");
      li.className = "chat-item" + (c.id === activeId ? " active" : "");
      const t = document.createElement("button");
      t.className = "chat-title"; t.textContent = c.title; t.title = c.title;
      t.onclick = () => handlers.select(c.id);
      const d = document.createElement("button");
      d.className = "chat-del"; d.textContent = "\u00d7"; d.setAttribute("aria-label", "Delete chat");
      d.onclick = e => { e.stopPropagation(); handlers.remove(c.id); };
      li.append(t, d); list.append(li);
    });
  }

  function messageEl(m) {
    const wrap = document.createElement("div");
    wrap.className = "msg " + m.role;
    const role = document.createElement("div");
    role.className = "role"; role.textContent = m.role === "user" ? "You" : "Assistant";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    if (m.role === "user") bubble.textContent = m.content;
    else { bubble.classList.add("md"); bubble.innerHTML = renderMarkdown(m.content); }
    wrap.append(role, bubble);
    if (m.tools_used) {
      const n = document.createElement("div");
      n.className = "tools-note";
      n.textContent = `Used ${m.tools_used} tool call${m.tools_used > 1 ? "s" : ""}`;
      wrap.append(n);
    }
    return wrap;
  }

  function renderMessages(conv, loading) {
    const box = $("messages");
    box.replaceChildren();
    if (!conv || conv.messages.length === 0) {
      const e = document.createElement("div");
      e.className = "empty"; e.textContent = "Ask a question to start a conversation.";
      box.append(e);
    } else {
      conv.messages.forEach(m => box.append(messageEl(m)));
    }
    if (loading) {
      const w = document.createElement("div");
      w.className = "msg assistant";
      w.innerHTML = '<div class="role">Assistant</div><div class="thinking" role="status"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span>Thinking...</span></div>';
      box.append(w);
    }
    box.scrollTop = box.scrollHeight;
  }

  function showError(text) { $("errorText").textContent = text; $("error").hidden = false; }
  function hideError() { $("error").hidden = true; }

  return { $, renderSidebar, renderMessages, showError, hideError };
})();
