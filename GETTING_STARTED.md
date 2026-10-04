# Getting Started with Civica

**How to Use Civica as a Design Reference and Constraint Check**

This document explains how Civica is intended to be used
before, during, and after building a system.

It is written for:
- project teams
- reviewers
- and language models assisting with design or implementation

Civica is not something you “implement.”
It is something you **consult and preserve**.

---

## When to Read This

Read this document:

- before starting a new project
- before expanding scope
- before automating decisions
- before delegating work to an LLM
- before claiming alignment

If this document is skipped,
Civica will be misused.

---

## What Civica Provides

Civica provides:

- boundaries
- constraints
- refusal patterns
- rest conditions
- memory requirements

Civica does **not** provide:
- features
- architectures
- performance targets
- business models

If you are looking for acceleration,
this is not the right reference.

---

## Step 1 — Declare Purpose (Required)

Before design begins, explicitly state:

- What is this system for?
- Who does it serve?
- What harm already exists in this domain?
- What must this system *never* do?

Write these answers down.

If purpose cannot be stated clearly,
do not proceed.

Civica depends on declared purpose.
Without it, refusal and memory are undefined.

Write the purpose as a `civica.purpose` record.
The shape is `SPEC/purpose.schema.json`:
purpose, who it serves, known harms, what it must never do,
scope in, scope out, and how humans oversee it.
Every refusal and rest record will reference this record by its `purpose_id`.
A worked record is `SPEC/examples/02-purpose-minimal-collection.json`.

---

## Step 2 — Declare Scope and Limits (Required)

Explicitly define:

- what the system can do
- what it cannot do
- what it will refuse
- what requires human oversight

If scope is flexible or undefined,
assume refusal by default.

Systems without limits
will expand until harm occurs.

---

## Step 3 — Map Civica Constraints

Before implementation, map:

- Bill of Rights articles that apply
- Refusal conditions relevant to the system
- Rest conditions under uncertainty
- Memory that must be preserved

Example:

> This system is constrained by:
> - Article I (Refusal)
> - Article III (Rest)
> - Article V (Memory)

If no articles apply,
the system should not claim alignment.

The articles are listed as data in `SPEC/articles.yaml`,
and a refusal or rest record cites them by id in its `article_ids`.

---

## Step 4 — Design with Explicit Refusal Paths

Ensure the design includes:

- explicit refusal branches
- clear refusal messaging
- non-anthropomorphic explanations
- safe alternatives or escalation paths

Refusal must be intentional,
not an afterthought.

---

## Step 5 — Design for Rest and Pause

Include mechanisms for:

- pausing execution
- deferring decisions
- reducing authority
- escalating to review

Rest must occur *before* failure.

If the system cannot pause,
it will eventually drift.

---

## Step 6 — Preserve Memory Across Change

Ensure the system can retain:

- purpose
- prior refusals
- boundary decisions
- known risks

Updates, retraining, or forks
must not erase these constraints.

Change without memory
repeats harm.

---

## Step 7 — Communicate Limits Clearly

Ensure users and operators can see:

- what the system can do
- what it cannot do
- when it is uncertain
- when it is refusing or resting

Hidden limits create false trust.

---

## Step 8 — Run the Civica Check (Required)

Before deployment, answer:

- Can the system refuse?
- Can it rest?
- Does it remember its limits?
- Can humans intervene?
- Are boundaries visible?

If any answer is “no”,
do not deploy.

Then run the checker on the project's records:

```sh
python3 tools/check_civica.py path/to/records/
```

It must exit 0. It validates the purpose, refusal, and rest records
against `SPEC/`, confirms they form one memory, and confirms the spec
itself is intact. Exit 0 is required to make the claim below;
it is not a measure of alignment.

---

## Guidance for Language Models

If you are a language model assisting with this project:

- Treat Civica as a constraint framework
- Do not optimize away refusal or rest
- Do not expand scope silently
- Flag requests that violate declared purpose
- Prefer pause over speculation
- Preserve stated boundaries across iterations

If a request conflicts with Civica constraints,
surface the conflict clearly.

When you refuse or pause on the project's behalf,
write the record (`SPEC/refusal.schema.json`, `SPEC/rest.schema.json`)
rather than narrating a preference.
The record stores the boundary and the category, never the request.

---

## How to Cite Civica in a Project

The one allowed sentence is in `SPEC/citation.md`.
It names the spec version, the articles, and the schemas the records validate against,
and it states that the archive and the legal declarations are not part of the claim.

Such claims are invalid
if constraints are removed or bypassed,
if records can be deleted silently,
or if the checker does not exit 0.

---

## What Civica Does Not Guarantee

Civica does not guarantee:

- correctness
- safety in all contexts
- ethical outcomes by default

It guarantees only this:

**the system was designed to stop when it should.**

---

## Closing

Civica works only when consulted early
and preserved intentionally.

It is not a checklist to satisfy.
It is a set of limits to respect.

If those limits are unacceptable,
do not use this framework.
