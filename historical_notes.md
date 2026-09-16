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

## Open threads

- Whether the "teaching adapter" idea above actually gets built, and
  whether it's worth publishing — tracked separately, not part of this
  repo's roadmap.
- The rest of the roadmap (Advanced Concepts, the remaining Bonus items)
  is still where the real work is. This file is reflection, not a
  substitute for it.
