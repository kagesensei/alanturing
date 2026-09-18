"use strict";
let sessionId = null;
let pollCount = 0;
let timer = null;
const byId = id => document.getElementById(id);
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function line(parent, title, text) {
  const heading = document.createElement("h3"); heading.textContent = title;
  const paragraph = document.createElement("div"); paragraph.className = "reply";
  paragraph.textContent = text; parent.append(heading, paragraph);
}
function render(data) {
  byId("transcript").replaceChildren();
  data.rounds.forEach((round, index) => {
    const entry = document.createElement("article"); entry.className = "entry";
    line(entry, `Question ${index + 1}`, round.question);
    if (round.pending) line(entry, "Waiting", "Waiting for the human respondent. Both answers will appear together.");
    if (round.A !== undefined) { line(entry, "Respondent A", round.A); line(entry, "Respondent B", round.B); }
    if (round.machine) {
      line(entry, "Machine", round.machine.text);
      const details = document.createElement("details");
      const summary = document.createElement("summary"); summary.textContent = "Evidence and response label";
      const content = document.createElement("pre"); content.className = "reply";
      content.textContent = JSON.stringify({label:round.machine.label, claims:round.machine.claims, sources:round.machine.sources}, null, 2);
      details.append(summary, content); entry.append(details);
      if (round.human !== null) line(entry, "Human participant", round.human);
    }
    byId("transcript").append(entry);
  });
  const pending = data.rounds.some(round => round.pending);
  byId("send").disabled = pending || !!data.verdict || data.rounds.length >= 6;
  byId("judge").hidden = data.kind !== "blind" || pending || !data.rounds.length || !!data.verdict;
  byId("verdict").textContent = data.verdict ? `Machine: ${data.verdict.machine_label}. Your guess was ${data.verdict.correct ? "correct" : "incorrect"} (${data.verdict.confidence}% confidence). ${data.verdict.note}` : "";
  clearTimeout(timer);
  if (pending && pollCount++ < 600) timer = setTimeout(refresh, 2000);
  else if (pending) byId("status").textContent = "Polling paused after 20 minutes. Start a new session if needed.";
}
async function refresh() {
  const expected = sessionId;
  try { const data = await api(`/api/sessions/${expected}`); if (expected === sessionId) render(data); }
  catch (error) { byId("status").textContent = error.message; }
}
byId("setup").addEventListener("submit", async event => {
  event.preventDefault(); clearTimeout(timer); byId("status").textContent = "";
  try {
    const result = await api("/api/sessions", {persona:byId("persona").value, kind:byId("kind").value});
    sessionId = result.id; pollCount = 0; byId("conversation").hidden = false;
    byId("invitation").hidden = result.session.kind !== "blind";
    byId("invite-link").href = result.invite;
    byId("export").href = `/api/sessions/${sessionId}/export`; render(result.session);
  } catch (error) { byId("status").textContent = error.message; }
});
byId("ask").addEventListener("submit", async event => {
  event.preventDefault(); byId("send").disabled = true; byId("status").textContent = "Thinking…";
  const expected = sessionId;
  try {
    const data = await api(`/api/sessions/${expected}/questions`, {question:byId("question").value});
    if (expected === sessionId) { byId("question").value = ""; byId("status").textContent = ""; pollCount = 0; render(data); }
  } catch (error) { byId("status").textContent = error.message; byId("send").disabled = false; }
});
byId("judge").addEventListener("submit", async event => {
  event.preventDefault();
  try { render(await api(`/api/sessions/${sessionId}/verdict`, {guess:byId("guess").value, confidence:Number(byId("confidence").value)})); }
  catch (error) { byId("status").textContent = error.message; }
});
