# Alan Turing -- Evidence-Based Historical Persona

**This is an evidence-based historical reconstruction for an AI simulation.
It is not a psychological diagnosis of Alan Turing and does not claim that
Turing completed the IPIP-NEO-120.**

This directory is the historically grounded *source of truth* for a future
personality layer for `turing-a1-3B-instruct-abliterated-claudetuned` and
the planned Turing Test Simulator (see the root
[README](../../README.md#roadmap) and [`historical_notes.md`](../../historical_notes.md)).
It does not itself implement the simulator, and it does not fine-tune
anything -- model training has its own [workflow directory](../../finetune). This is data
and the validation code that keeps that data honest.

Requires Python 3.12 -- see the [repo root README](../../README.md#setup)
for venv setup. Standard library only.

## Why this exists

A caricature of Turing -- vaguely British 1940s diction standing in for
personality -- would be easy and worthless. The goal here is the opposite:
every personality- or biography-bearing claim in this project must be
traceable to a source and honest about how strongly that source supports
it, so that a downstream simulator can distinguish:

1. **Historical fact** -- "Turing wrote/said/did X."
2. **Biographical evidence** -- "A biographer, colleague, friend, or
   historical source reports X."
3. **Evidence-based inference** -- "The available evidence suggests X."
4. **Persona extrapolation** -- "For purposes of this simulation, we infer
   X with low confidence."
5. **Unknown** -- "There is insufficient historical evidence to know."

A model (or a human) consuming this data must never silently collapse
categories 2-5 into category 1.

## The provenance/confidence model

Every claim-bearing record carries two independent fields:

- **`evidence_type`** -- where the claim comes from:
  - `DIRECT` -- Turing's own words/writing, or clearly documented behavior
    in a primary source.
  - `CONTEMPORARY` -- someone who knew Turing directly reports it.
  - `SCHOLARLY` -- a reputable biographer/historian draws a conclusion from
    evidence.
  - `INFERRED` -- this project's own reconstruction from multiple pieces of
    evidence, for persona-building purposes.
  - `UNKNOWN` -- insufficient evidence currently in this project's
    bibliography.
- **`confidence`** -- `high` / `medium` / `low` / `unknown` (which must
  agree with `evidence_type`: `UNKNOWN` <-> `unknown`, nothing else pairs
  with `unknown`).

The simulator-facing 5-way category above is *derived*, never stored
separately, by `persona_validation.classify_claim(evidence_type,
confidence)`:

| evidence_type | confidence | -> claim_category |
| --- | --- | --- |
| `DIRECT` | any (non-unknown) | `historical_fact` |
| `CONTEMPORARY` or `SCHOLARLY` | any (non-unknown) | `biographical_evidence` |
| `INFERRED` | `high` / `medium` | `evidence_based_inference` |
| `INFERRED` | `low` | `persona_extrapolation` |
| `UNKNOWN` | `unknown` | `unknown` |

Keeping this as a function rather than a stored field means the two can
never drift out of sync.

Claims also reference reusable **source records** by `source_id` rather
than scattering citations or URLs through every file --
[`sources.json`](sources.json) is the bibliography; everything else points
into it.

## What's here

| File | Contents |
| --- | --- |
| [`sources.json`](sources.json) | Reusable source records (title, author, date, publisher/archive, identifier, source_type, primary/secondary, notes). |
| [`chronology.json`](chronology.json) | Dated life events, each evidence-tagged; includes a documented example of a *contested* claim (the circumstances of his death) recorded as competing scholarly positions rather than a single asserted fact. |
| [`relationships.json`](relationships.json) | Christopher Morcom, Joan Clarke, Sara Turing, Bletchley/Manchester colleagues, and documented relationships -- recorded as documented facts, with no invented characterization beyond what the cited source supports. |
| [`interests.json`](interests.json) | One entry per hobby/interest category (running, cycling, chess/Turochamp, morphogenesis, etc.). Categories this project cannot currently source well (rowing, sailing, food, music, mushroom-gathering specifics) are seeded as explicit `UNKNOWN` entries, not omitted and not guessed. |
| [`conversational_style.json`](conversational_style.json) | Dialogue-influencing traits (formality, humor, directness, use of analogy, ...), an explicit `avoid_caricature_global` list, and sample dialogue -- always labeled `SIMULATED_DIALOGUE_NOT_A_HISTORICAL_QUOTE`, never presented as a real quotation. |
| [`ocean_profile.json`](ocean_profile.json) | A posthumous proxy Big Five (OCEAN) reconstruction at the domain/facet level. Qualitative directional notes only in Phase 1 -- no numeric scores are asserted, and every note is explicitly `INFERRED`/low-to-medium confidence. |
| [`ipip_neo_120.json`](ipip_neo_120.json) | The 120-item IPIP-NEO structural shell (30 facets x 4 items), all left `UNKNOWN`/`unscored` in Phase 1. See "Why the IPIP items aren't scored yet" below. |
| [`persona.json`](persona.json) | The manifest: disclaimers, the evidence/claim taxonomies above, and the **temporal persona registry** (below). |
| [`persona_validation.py`](persona_validation.py) | Validation code: enums, `classify_claim`, per-file and cross-file checks. Run directly (`python persona_validation.py`) for a pass/fail report. |
| [`test_persona_validation.py`](test_persona_validation.py) | `unittest` suite -- both "the bundled data is valid" and "the validator actually rejects bad data" cases. |

## Temporal personas

`persona.json`'s `temporal_personas` defines historically bounded versions
of Turing, each with a `knowledge_cutoff_year` and a `known_events` list
(referencing `chronology.json` event ids):

- `turing_1936` -- computability theory / Princeton era (cutoff 1936)
- `turing_1941` -- wartime cryptanalysis, Bletchley Park (cutoff 1941)
- `turing_1950` -- "Computing Machinery and Intelligence" (cutoff 1950)
- `turing_1952` -- morphogenesis / Manchester computing (cutoff 1952)
- `turing_a1` -- **explicitly fictional** modern interpretive continuation,
  with contemporary CS/security/ML knowledge the historical Turing could
  not have had

`persona_validation.validate_personas` mechanically checks that no
historical (`is_fictional: false`) persona's `known_events` references a
chronology event dated after its own `knowledge_cutoff_year` -- a
`turing_1936` persona cannot know about Bletchley Park.

### `turing_a1`'s two separable layers

`turing_a1-3B-instruct-abliterated-claudetuned` (see
[`historical_notes.md`](../../historical_notes.md)) is deliberately split
into two concepts that must stay separable:

1. **Domain specialization** -- cryptanalysis, computational reasoning,
   security-lab behavior. This is the model's core scope and works
   whether or not any persona is layered on top.
2. **Historical persona** -- this optional, evidence-grounded Alan Turing
   persona layer, defined in this directory.

The technical model must be usable *without* being forced to roleplay Alan
Turing. This directory only ever defines layer 2.

## Why the IPIP items aren't scored yet

The IPIP-NEO-120's facet/domain structure (John A. Johnson's 2014 30-facet
public-domain inventory) is well-established and safe to encode
structurally -- `ipip_neo_120.json` does that for all 120 items. What it
deliberately does *not* do yet is populate `item_text` or a
`proposed_response`: item wording should be transcribed from a verified
IPIP source and cross-checked, not reproduced from memory, since a
transcription error would sit inside a dataset whose entire point is
evidence rigor. Likewise, per the project brief, items are only ever
scored where the evidence genuinely supports it -- not all 120 simply
because the instrument has 120 items. Both are Phase 2 work.

## Validation

```
python -m unittest -v
```

or, for a plain pass/fail report against the bundled data:

```
python persona_validation.py
```

At minimum, the suite checks: every JSON file parses; required fields are
present; `evidence_type`/`confidence` values come from the allowed enums
and agree with each other (an `UNKNOWN` item can never masquerade as
scored evidence); every `source_id` referenced anywhere resolves to a real
entry in `sources.json`; `INFERRED` claims carry a rationale;
`DIRECT`/`CONTEMPORARY`/`SCHOLARLY` claims carry at least one source; OCEAN
facet codes match their declared domain; and no historical temporal
persona references a chronology event past its own knowledge cutoff. Each
rule has both a "the bundled data satisfies this" test and a "the
validator actually rejects a synthetic violation" test.

## Roadmap status

This is the source-of-truth groundwork consumed by the
[Turing Test Simulator](../../bonus/turing_test_simulator). The simulator now
supports conservative evidence-scoped conversations and a configurable model
endpoint. This directory remains persona data and validation, separate from
the model's technical specialization and training.

## Phase 2 (not yet started)

Systematic source-by-source evidence collection; IPIP-NEO-120 item-text
transcription and evidence-backed response reconstruction (only where
supported); facet-level qualitative-to-quantitative writeups;
free-form dialogue/persona generation. Initial extractive integration with the
Turing Test Simulator is complete; that does not complete the research work.
