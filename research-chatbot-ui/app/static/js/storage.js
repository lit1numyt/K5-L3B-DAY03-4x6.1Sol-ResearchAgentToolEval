// localStorage persistence. All access is wrapped: storage can be full or disabled.
const Storage = (() => {
  const KEY = "rc.conversations.v1";
  const ACTIVE = "rc.active.v1";

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; }
  }
  function save(convs) {
    try { localStorage.setItem(KEY, JSON.stringify(convs)); } catch (e) { console.warn("Could not save", e); }
  }
  function getActive() { try { return localStorage.getItem(ACTIVE); } catch { return null; } }
  function setActive(id) { try { id ? localStorage.setItem(ACTIVE, id) : localStorage.removeItem(ACTIVE); } catch {} }

  function uuid() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0; return (c === "x" ? r : (r & 3 | 8)).toString(16);
    });
  }
  function newConversation() {
    const now = new Date().toISOString();
    return { id: uuid(), title: "New chat", created_at: now, updated_at: now, messages: [] };
  }
  return { load, save, getActive, setActive, newConversation };
})();
