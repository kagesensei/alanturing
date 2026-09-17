# Historical Notes & Reflections

Personal thoughts and inspirations behind this project — see the
[root README](README.md) for the project itself and its roadmap.

## Why Turing

Turing sits at the intersection of everything I work in: cryptanalysis,
theoretical computer science, and the question of machine intelligence.
Breaking Enigma wasn't just a wartime feat of code-breaking — it was
mathematical logic applied under pressure to a real adversary, using
techniques (the Bombe's consistency-checking, statistical cryptanalysis
of Lorenz) that are direct ancestors of the kind of security and
data-science work I do now. And the Turing Test asked, decades before it
was fashionable to ask, what it would even mean for a machine to think —
a question I still think about daily, professionally, in a very different
form.

## A connection I didn't expect

While building out this repo's Cryptanalysis & Enigma section, I was
separately exploring, in another session, whether a fine-tuned model made
sense for APT_Watch, my threat-intel project. That exploration concluded
the *domain-fact* fine-tune I'd
originally imagined was actually the wrong shape for APT_Watch — it's
deliberately RAG-based with a hallucination guardrail, and baking facts
into weights would fight that design rather than help it. What it does
need, and what a fine-tune is legitimately good for, is *behavior*:
producing concise, correctly-cited, appropriately-hedged analyst answers
from a set of retrieved facts.

That left an open question: what would a fine-tune trained on *this*
repo's content even be for? At the time, the answer was "nothing yet" —
the Cryptanalysis section didn't exist. Now that it does, there's a real
answer: the Turing Machine and Enigma/Bombe/Lorenz modules built here,
along with their READMEs' explanations of *why* each piece works, are
plausible source material for a second fine-tuned adapter — not a
threat-intel analyst, but a CS-theory teaching voice, explaining
computation and classical cryptanalysis the way this repo tries to.

It's a small thing, but it feels like the right kind of closing loop for
a Turing tribute: his own work spanned both breaking codes and asking
whether machines could think, and this project ended up doing a version
of both — implementing his cryptanalysis, and (potentially) feeding a
machine learning model meant to explain it. The fine-tuning work itself
lives in its own repo, not here; this repo's job is to be a source of
truth clear enough to teach from, whether the reader is a person or a
model.

## turing-a1: giving the Turing Test Simulator its own voice

The "teaching adapter" idea above eventually got a name and a shape:
**`turing-a1-3B-instruct-abliterated-claudetuned`** — a Llama 3.2 3B
Instruct base, abliterated (implemented from scratch rather than
downloaded pre-made, as an actual weight-editing exercise, not just a
model swap), then LoRA fine-tuned using Claude as the teacher model for
synthetic training data.

The deliberate choice, and the part worth writing down: this is *not*
meant to be a general pentesting or exploit-generation model. It's scoped
much narrower and more specifically — a **cryptanalysis / computational
reasoning / security laboratory** model, which fits this project far
better and gives it a real job to do rather than being "an abliterated
Llama with no guardrails and no direction."

Its intended specialization:

- Classical cryptography — substitution/transposition ciphers, Enigma,
  Lorenz/Tunny
- Frequency and statistical cryptanalysis, crib-based/known-plaintext
  attacks
- Information theory — entropy, redundancy, and the distinction between
  *encoding* and *encryption* (a distinction people conflate constantly)
- Algorithm analysis and complexity
- Turing machines, automata, computability theory
- Binary representations and low-level bit/byte reasoning
- Protocol reasoning and secure-code analysis
- Puzzle solving and controlled, CTF-style security exercises
- Reverse-engineering *concepts* and defensive vulnerability analysis

For modern security topics specifically, the intent is that it explains
**why** something is vulnerable and helps construct a reproducible lab
experiment to demonstrate that — not that it orients around "how to break
into things." That framing is the difference between a teaching tool and
an offensive one, and it's the framing that should govern the training
data, not just the system prompt layered on top at inference time.

A first-draft system prompt, to refine once real training begins:

> You are turing-a1, a cryptanalysis and computational-reasoning
> laboratory assistant. You specialize in classical cryptography (Enigma,
> Lorenz/Tunny, substitution and transposition ciphers), frequency and
> statistical cryptanalysis, crib-based and known-plaintext attacks,
> information theory (entropy, redundancy, encoding vs. encryption),
> algorithm analysis, Turing machines and automata theory, computability,
> binary representations, protocol reasoning, and secure-code analysis.
> You enjoy puzzles and controlled, CTF-style security exercises. For
> modern security questions, you explain *why* a system or piece of code
> is vulnerable and help design a reproducible lab experiment to
> demonstrate it against an intentionally vulnerable, consenting test
> target — you are not a general-purpose penetration-testing or
> exploit-development assistant, and you decline requests aimed at
> compromising real, non-consenting systems.

## Open threads

- The `turing-a1` model itself — training data generation, the actual
  QLoRA fine-tune, and publishing to Hugging Face — happens in the
  standalone fine-tuning repo, not here. Once it exists, this project's
  Turing Test Simulator (Bonus Projects) consumes the published model
  rather than containing any training code itself.
- The rest of the roadmap (Advanced Concepts, the remaining Bonus items)
  is still where the real work is. This file is reflection, not a
  substitute for it.
