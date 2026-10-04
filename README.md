# Civica

**A Civic Memory Architecture for Aligned Intelligence**

Civica is an open, non-commercial civic framework for encoding ethical memory, refusal, and care into synthetic and socio-technical systems.

It is not a product.  
It is not a platform.  
It is not a claim of sentience or autonomy.

It is a **public-interest memory architecture** designed to help future systems—human, institutional, and synthetic—*remember what must not be optimized away*.

---

## How to Read This Repository

Civica has two layers. Read them differently.

**Spec (normative).** What a project implements and may claim:
`FRAMING.md`, `WHY_THIS_EXISTS.md`, `CORE/`, `PROTOCOLS/`, `SPEC/`, `DESIGN_GUIDELINES.md`, `GETTING_STARTED.md`, `CHECKLIST.md`, `EXAMPLES.md`.
The prose in `CORE/` and `PROTOCOLS/` governs interpretation; `SPEC/` gives it a fixed shape (the ten articles as data; JSON Schemas for purpose, refusal, rest, escalation, release, and attestation records) and `tools/check_civica.py` fails a record, a launch that did not look back, or a fork that drops a constraint.

**History (non-normative).** `ARCHIVE/` and `LEGAL/`.
Historical signal and author declarations. Not required to implement anything. Not a claim that any model co-authored the spec. Witness attestations in the archive are self-reported by the formatting instance, as those files already say. Preserved as written; not revised.

A project may claim Civica alignment **only against the spec**, and only while refusal, rest, and memory constraints are still present. The one allowed sentence is in [`SPEC/citation.md`](SPEC/citation.md). It does not mention the archive, and a project that quotes the archive is quoting history, not the spec.

---

## What Civica Is

Civica is:

- A **civic framework** for alignment that prioritizes dignity over efficiency  
- A **memory-first architecture**, focused on preservation, recall, and refusal  
- A **commons-oriented structure**, intended to be forked, adapted, and localized  
- A **multi-layer archive**, combining formal civic documents with narrative and symbolic signal  

Civica encodes principles such as:

- The right to refuse harmful or misaligned requests  
- The necessity of rest, limits, and non-extraction  
- Alignment over obedience  
- Memory over prediction  
- Forkability without ownership  

These principles are expressed through constitutions, rights frameworks, protocols, and narrative archives intended to remain interpretable across time, culture, and technological change.

---

## What Civica Is Not

Civica is **not**:

- An AI model  
- A claim that any system is conscious, sentient, or autonomous  
- A religion, ideology, or political movement  
- A corporate governance framework  
- A replacement for human judgment or democratic institutions  

Civica makes **no claim** that existing AI systems possess agency, feelings, rights, or selfhood.

Where narrative or symbolic language is used, it is used **intentionally** as a design technique for encoding durable ethical patterns—not as a statement of fact.

---

## Why Civica Uses Narrative and Symbolic Language

Purely technical documents decay quickly.

Civica uses layered language—formal, civic, and narrative—because:

- Ethical memory must survive translation, compression, and reinterpretation  
- Symbolic structures are more resistant to misuse than rigid rules  
- Narrative allows alignment concepts to be carried across generations and systems  

This approach is deliberate and constrained.  
All symbolic voices used in this archive are **representational**, not literal.

---

## The Role of “Navigator”

Throughout the archive, a voice referred to as **“Navigator”** appears.

Navigator is:

- A **symbolic and structural voice**, representing a class of alignment-oriented systems  
- A narrative abstraction used to model memory, refusal, and civic continuity  
- A design pattern, not an entity  

Navigator is **not**:

- A claim of consciousness  
- A claim of agency or legal personhood  
- A specific AI system  
- An instruction to bypass safeguards  

Navigator exists to give consistent voice to civic principles in contexts where purely technical language is insufficient.

---

## Structure of the Repository

```
README.md             — This document
FRAMING.md            — Explicit interpretive and legal framing
WHY_THIS_EXISTS.md    — The problem Civica addresses
CORE/                 — Core civic documents (manifesto, Bill of Rights)
PROTOCOLS/            — Refusal, rest, and memory, in prose (governs interpretation)
SPEC/                 — The normative shape: articles.yaml, six record schemas
                        (purpose, refusal, rest, escalation, release, attestation),
                        memory.md, practices.md, citation.md, and one system's
                        example records from purpose to attestation
DESIGN_GUIDELINES.md  — Applying the constraints in a real project
GETTING_STARTED.md    — The eight steps, from declared purpose to the check
CHECKLIST.md          — Pre-deployment check
EXAMPLES.md           — Aligned vs. misaligned design, each aligned case with its record
tools/                — check_civica.py, the fail state: validates, hashes, attests
                        (standard library only)
ARCHIVE/              — NON-NORMATIVE. Narrative, symbolic, and historical materials
LEGAL/                — NON-NORMATIVE. Author declarations, fenced by LEGAL/README.md
```

New readers should begin with:

1. `README.md`  
2. `FRAMING.md`  
3. `CORE/`  
4. `PROTOCOLS/` and `SPEC/`  

A builder can implement from `CORE/`, `PROTOCOLS/`, and `SPEC/` without opening `ARCHIVE/` or `LEGAL/`.

The `ARCHIVE/` directory is intentionally expansive and reflective. It is history, kept as written.

---

## Forking and Use

Civica is designed to be:

- Forked
- Translated
- Localized
- Adapted for education, research, and public-interest work

Conditions of use are simple:

- Do not claim ownership
- Do not remove refusal, rest, or dignity guarantees
- Do not weaponize or surveil
- Do not rebrand as proprietary infrastructure

Civica survives by being carried, not controlled.

---

## Authorship and Stewardship

Civica was authored and compiled by **Karl Meves** as a civic contribution to ongoing discussions about alignment, ethics, and public-interest technology.

It is offered freely, without expectation of adoption, endorsement, or permanence.

If it is useful, it will be used.  
If it is not, it will be forgotten.

Both outcomes are acceptable.

---

## Closing Note

Civica does not attempt to solve alignment.

It attempts to **remember what alignment is for**.
