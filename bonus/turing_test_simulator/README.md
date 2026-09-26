# Turing Test Simulator — the imitation room

A local Flask app for chatting with a configurable model and running a small
blind human-versus-machine comparison. It implements the original roadmap's
chat-based exploration; it does not establish that a model has passed a
scientifically controlled Turing Test or has consciousness.

## Run

Activate the root Python 3.12 environment, then from the repository root:

```text
python -m pip install -r bonus/turing_test_simulator/requirements.txt
python bonus/turing_test_simulator/app.py
```

Open **http://127.0.0.1:5001**, or run root `python app.py` and follow
**Open chat** at http://127.0.0.1:5000. Both entry points use the same local
fine-tuned adapter. The first question loads the weights into GPU memory.
Set `TURING_MODEL_ADAPTER` to select another completed adapter directory.
Missing weights or inference failures produce an explicit error; chat does
not silently substitute canned demonstration answers. See [model setup](../../model/README.md).

`python bonus/turing_test_simulator/demo.py` runs a complete scripted comparison
round without a browser. Its human response is a fixture, explicitly labeled.

## Optional external model endpoint

The transport accepts a chat-completions endpoint, such as a configured
[llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server).
Set the **full endpoint URL**, model identifier, and optional bearer key before
starting the app. PowerShell example:

```powershell
$env:TURING_MODEL_ENDPOINT = 'http://127.0.0.1:8080/v1/chat/completions'
$env:TURING_MODEL_ID = 'your-served-model-id'
# If authentication is enabled, set TURING_MODEL_API_KEY in your environment.
python bonus/turing_test_simulator/app.py
```

The model ID must match the model actually served. Configuration comes from
the server environment, never the browser. Remote endpoints require HTTPS;
loopback HTTP is supported. Requests have a 30-second timeout and responses a
64 KiB limit. Errors do not silently fall back to the demo or expose upstream
error bodies. The key is neither displayed nor included in transcript exports.
Automated transport tests use a local fixture server; local training and measured
model results are recorded separately under `model/`.

## Chat and compare

1. Select a voice and either chat or blind comparison.
2. In comparison mode, give the respondent link to another person in a separate
   browser tab on this computer. The default loopback binding is local-only.
3. Ask up to six questions. Both answers appear together once the human replies.
   A/B assignment is randomized per session. The respondent cannot see the
   machine's answers, and the judge API/export does not reveal the assignment.
4. Record which respondent you think is the machine and your confidence.
   Reveal shows the assignment, correctness, and evidence records.
5. Download the JSON transcript. Human text is participant-supplied, not verified
   historical material. Before reveal, the export preserves the blind view.

Sessions are held in memory, capped at 64, expire after two hours, and disappear
on restart. Invitation/session URLs are separate random bearer tokens; share
only the respondent link. A process-level lock serializes turns in this local
teaching app. It is not a multi-worker hosted service. Style, citations, and
latency can give away the machine; this is a subjective exercise, not a
controlled human-performance benchmark.

## Conversation and historical scope

- **Technical assistant:** receives only the domain-specialist prompt and chat
  history, with no historical persona. Generated answers remain unverified.
- **Historical personas:** speak in first person as an explicit simulation.
  The prompt uses the selected persona description and evidence-rated voice
  guidance in `model/persona/alan_turing/conversational_style.json`. It keeps
  the selected `known_events` and year cutoff. A record spanning beyond the
  cutoff is withheld in full, and undated positive interest claims are withheld.
  Follow-up questions use recent conversation context when retrieving records.
- **Historical evidence:** relevant source records appear separately below each
  answer. If the persona files do not cover a general question, the model can
  still respond conversationally, but that answer is not independently verified
  by this project's evidence library. Unknown preferences remain unknown, and
  generated dialogue is never presented as a historical quotation.
- **Fictional modern continuation:** explicitly fictional; can consult the
  broader historical record without pretending it was Turing's own knowledge.

The simulator retrieves up to three locally matched records and makes one
model call for the conversational reply. It does not ask the model to select
evidence IDs or copy source excerpts into the answer. Persona traits carry their
recorded evidence types, confidence labels and source IDs into the system prompt
as style guidance, not as proof of additional biographical facts.

Claim categories are derived with the existing `persona_validation.classify_claim`.
Factual claims carry resolvable sources, and all persona replies carry
`SIMULATED_DIALOGUE_NOT_A_HISTORICAL_QUOTE`. Citation presence validates provenance
structure, not the historical truth of a source: some bibliography entries still
need page-level verification. Retrieval relevance is fallible, and unsupported
general answers should be checked against reliable sources.

The fine-tuned adapter was trained on synthetic binary increment, unary addition
and Caesar cipher examples. It was not fine-tuned or distilled on Turing dialogue.
The persona layer is an inference-time simulation based on the current persona
files. A learned historical voice requires a separately reviewed source-backed
dialogue dataset and evaluation.

## Verification

From this directory: `python -m unittest -v`. Root discovery includes this suite.
Tests cover HTTP transport, malformed replies, temporal exclusion, unknown
preferences, source references, prompt separation, session bounds, invitation
isolation, and blind/reveal behavior. Flask routes use its
[test client](https://flask.palletsprojects.com/en/stable/testing/).
