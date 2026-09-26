"use strict";
const base = document.body.dataset.base || "";
const history = [];
let sessionId = null;
const byId = id => document.getElementById(id);

async function post(path, body) {
  const response = await fetch(`${base}${path}`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "The request failed");
  return data;
}

function addMessage(role, content) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = content;
  byId("messages").append(bubble);
  bubble.scrollIntoView({block: "end"});
}

async function startSession() {
  history.length = 0;
  sessionId = null;
  byId("messages").replaceChildren();
  byId("status").textContent = "Starting a new chat…";
  try {
    const session = await post("/api/session", {});
    sessionId = session.session_id;
    byId("status").textContent = "Ready";
  } catch (error) {
    byId("status").textContent = error.message;
  }
}

byId("chat-form").addEventListener("submit", async event => {
  event.preventDefault();
  const text = byId("message").value.trim();
  if (!text || !sessionId) return;
  const pending = [...history, {role: "user", content: text}];
  addMessage("user", text);
  byId("message").value = "";
  byId("send").disabled = true;
  byId("status").textContent = "Mistral is thinking…";
  try {
    const result = await post("/api/chat", {session_id: sessionId, messages: pending});
    history.push({role: "user", content: text},
                 {role: "assistant", content: result.response});
    addMessage("assistant", result.response);
    byId("status").textContent = "Ready";
  } catch (error) {
    byId("status").textContent = error.message;
  } finally {
    byId("send").disabled = false;
    byId("message").focus();
  }
});

byId("new-chat").addEventListener("click", startSession);
startSession();
