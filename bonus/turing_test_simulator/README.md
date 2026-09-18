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

Open **http://127.0.0.1:5001**. The default is explicitly labeled **local
demonstration (no trained model)**. Historical modes retrieve bundled evidence
lexically; technical mode explains that a model endpoint must be connected.
There is no pretend turing-a1 model behind this demonstration.

`python bonus/turing_test_simulator/demo.py` runs a complete scripted comparison
round without a browser. Its human response is a fixture, explicitly labeled.

## Connect turing-a1

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
An actual turing-a1 endpoint has not yet been trained or tested here; automated
tests exercise the HTTP contract against a local fixture server.

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

## Evidence and historical scope

- **Technical assistant:** receives only the domain-specialist prompt and chat
  history, with no historical persona. Generated answers remain unverified.
- **Historical personas:** use the existing registry, `known_events`, and year
  cutoffs. A record spanning beyond the cutoff is withheld in full. Undated
  positive interest claims are also withheld. Precision is by year, matching
  the source registry, not by day within a year.
- **Fictional modern continuation:** explicitly fictional; can consult the
  broader historical record without pretending it was Turing's own knowledge.

In persona modes the endpoint only selects up to three permitted evidence IDs
as `{"claim_ids": ["E005"]}`. The application renders the stored record text;
it never accepts model-written biographical prose or quotations. Unknown IDs,
future IDs, extra JSON fields, and malformed replies fail closed. Empty
selections abstain. `UNKNOWN` entries retain their category, confidence, and
absence of supporting sources. This conservative first version is an evidence
conversation, not free-form historical impersonation.

Claim categories are derived with the existing `persona_validation.classify_claim`.
Factual claims carry resolvable sources, and all persona replies carry
`SIMULATED_DIALOGUE_NOT_A_HISTORICAL_QUOTE`. Citation presence validates provenance
structure, not the historical truth of a source: some bibliography entries still
need page-level verification. The app adds no biographical claims to the dataset.
Retrieval relevance is also fallible; a related excerpt may not answer a question.

## Verification

From this directory: `python -m unittest -v`. Root discovery includes this suite.
Tests cover HTTP transport, malformed replies, temporal exclusion, unknown
preferences, source references, prompt separation, session bounds, invitation
isolation, and blind/reveal behavior. Flask routes use its
[test client](https://flask.palletsprojects.com/en/stable/testing/).
