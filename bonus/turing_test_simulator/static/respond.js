"use strict";
const invite = document.getElementById("human-room").dataset.invite;
const byId = id => document.getElementById(id);
let timer = null;
let remaining = 3600;
let rendered = "";
async function refresh() {
  clearTimeout(timer);
  try {
    const response = await fetch(`/api/respond/${invite}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    byId("mode").textContent = `Persona: ${data.persona}`;
    const content = JSON.stringify(data.rounds);
    if (content !== rendered) {
      byId("transcript").replaceChildren();
      data.rounds.forEach(round => {
        const entry = document.createElement("p"); entry.className = "reply";
        entry.textContent = `Judge: ${round.question}\n\nYou: ${round.answer ?? "Awaiting your answer"}`;
        byId("transcript").append(entry);
      });
      rendered = content;
    }
    byId("send").disabled = data.complete || !data.rounds.length || data.rounds.at(-1).answer !== null;
    byId("status").textContent = data.complete ? "The judge has revealed the result." : "";
    if (!data.complete && remaining-- > 0) timer = setTimeout(refresh, 2000);
  } catch (error) { byId("status").textContent = error.message; }
}
byId("answer").addEventListener("submit", async event => {
  event.preventDefault(); byId("send").disabled = true;
  try {
    const response = await fetch(`/api/respond/${invite}`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({answer:byId("response").value})});
    const data = await response.json(); if (!response.ok) throw new Error(data.error);
    byId("response").value = ""; await refresh();
  } catch (error) { byId("status").textContent = error.message; byId("send").disabled = false; }
});
byId("refresh").addEventListener("click", refresh);
refresh();
