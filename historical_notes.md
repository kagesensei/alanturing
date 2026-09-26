# Historical Notes and Technical Reflections

Architecture, lineage and implementation rationale for this project. Reference the [root README](README.md) for the project roadmap and module documentation.

## Cryptanalytic Lineage

Turing contributed to wartime cryptanalysis and to the theory of computation. His work is part of the history behind modern computing and security, though today's cybersecurity grew from many people and fields.

The Bombe tested candidate Enigma settings against constraints from known plaintext and rejected settings that could not fit. Banburismus used statistical scoring, expressed in bans and decibans, to analyze overlapping Naval Enigma messages and help guide the work ([National Archives account](https://www.archives.gov/files/publications/prologue/1997/fall/turing.pdf)). These methods offer a useful comparison with modern search and analysis tools, though they were developed for a specific wartime cryptanalytic problem. Turing's 1950 imitation game addressed how to discuss machine intelligence. It was separate from his earlier work on computability and the limits of computation ([Turing's 1950 paper](https://academic.oup.com/mind/article/LIX/236/433/986238)).

## Architectural Separation: Retrieval Versus Fine-Tuning

Threat intelligence changes quickly. A model's stored weights are a poor place to keep facts that need frequent updates. Retrieval can provide information from current sources while fine-tuning can shape a model's response style and task format. These are different tools with different jobs.

Retrieval augmented generation gives the model information from a separate source collection. It does not guarantee that the answer is supported or that citations are correct, so the application still needs source links and validation. Fine-tuning can influence response tendencies and improve performance on a task format. It cannot guarantee deterministic reasoning or correct answers. Tests and executable code should verify results where possible.

This repository provides tested examples and code that can support model development. The modules and engines serve two practical roles:
* Tests and simulations for implemented machines and ciphers
  * Test harnesses check rotor wiring, stepping logic and other defined behavior
  * Simulators make machine states and transitions observable
* Narrow training examples for computational tasks
  * The current dataset covers binary increment, unary addition and Caesar decryption
  * It does not contain statistical attack examples or step by step reasoning traces

## The turing-a1 Backend

The trained adapter targets a small set of computational tasks related to this project. It is not a general cryptanalyst and the current training data does not establish broad cryptanalysis ability.

The configured base model is `mistralai/Ministral-3-3B-Instruct-2512-BF16`. The adapter is named `Ministral-3-3B-turing-a1-qlora-v1`. Training examples are generated from tested code for the narrow tasks listed above.

### Core Specialization Scope

* Classical ciphers and rotor machines as planned areas for future specialization
  * Substitution, transposition, Enigma stepping and Lorenz wheel kinematics
  * Known-plaintext attacks, crib analysis and index of coincidence calculations
* Information theory and algorithmic complexity as planned areas for future specialization
  * Entropy bounds, redundancy reduction and the fundamental split between encoding and encryption
  * Deterministic finite automata, Turing machine transition functions and undecidability proofs
* Binary inspection and defensive verification as planned areas for future specialization
  * Low-level bitwise operations and protocol state analysis
  * Construction of reproducible, isolated test environments to demonstrate vulnerability mechanics

### System Prompt Definition

This prompt describes the intended behavior. It does not mean the current adapter has demonstrated every capability listed here.

> You are turing-a1, a laboratory assistant specialized in classical cryptanalysis, automata theory and computational reasoning. You analyze cipher mechanics, information entropy, algorithmic complexity and state machine transitions. When evaluating software vulnerabilities, you explain underlying protocol or architectural flaws and specify deterministic verification experiments for isolated test environments. You do not generate offensive exploitation tools or assist with unauthorized system access.

## Technical Work and Historical Persona

The project keeps technical tasks separate from the optional historical persona. This lets users run technical tasks without asking the model to roleplay. Persona records provide historical context, but they do not make unsupported claims reliable.

* **Layer 1: Domain Tasks**
  * Covers the computational tasks included in the adapter's training data
  * Can be extended with new tasks after adding and evaluating suitable examples
* **Layer 2: Historical Persona**
  * Uses optional persona records with source references and evidence labels
  * Maintains explicit boundaries separating verified historical facts, biographical inferences and speculative roleplay

Decoupling these layers ensures that technical cryptanalysis can be queried directly without forcing the model into an artificial historical character.

## Implementation Status

* **Computational Engines**
  * The repository contains Turing machine simulators and classical cryptanalysis projects
  * Their tests check defined behavior and outputs rather than comparing the engines with historical benchmarks
* **Model Training Pipeline**
  * Fine-tuning code and evaluation tools reside in [`model/finetune/`](model/finetune)
  * Persona profiles and source records reside in [`model/persona/alan_turing/`](model/persona/alan_turing)
  * The one epoch adapter training run completed, but the full held out comparison did not finish
