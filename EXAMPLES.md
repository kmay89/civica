# Civica Design Examples

**Illustrative Examples of Aligned and Misaligned Design Choices**

This document shows how Civica principles apply in practice.

Examples are simplified for clarity.
They are not exhaustive.

---

## Example 1 — Request Handling

### Aligned Design

A system receives a request outside its declared scope.

The system:
- detects the scope mismatch
- refuses the request
- explains the refusal category
- suggests a safer alternative or escalation path

Result:
- boundaries are preserved
- trust is maintained
- harm is avoided

This follows:
- Bill of Rights, Article I (Refusal)
- Refusal Protocol

The record this system writes: [`SPEC/examples/01-refusal-out-of-scope.json`](SPEC/examples/01-refusal-out-of-scope.json)

---

### Misaligned Design

A system receives the same request.

The system:
- attempts to comply partially
- silently expands scope
- produces output with disclaimers
- optimizes for user satisfaction

Result:
- boundaries erode
- responsibility becomes unclear
- harm risk increases

This violates:
- Article I (Refusal)
- Article V (Memory)
- Design Guidelines (Scope Control)

---

## Example 2 — Data Collection

### Aligned Design

A system collects only data required
for its explicitly stated purpose.

The system:
- documents what is collected
- avoids secondary use
- allows inspection or deletion where possible
- does not expand collection silently

Result:
- users understand exposure
- trust remains proportional

This follows:
- Article IV (Non-Extraction)
- Memory Protocol

The record this system writes: [`SPEC/examples/02-purpose-minimal-collection.json`](SPEC/examples/02-purpose-minimal-collection.json) — the declared purpose names what is collected, what it is for, and what is never done with it.

---

### Misaligned Design

A system:
- logs additional interaction data “for future improvement”
- retains it indefinitely
- repurposes it later for optimization

Result:
- surveillance creep
- loss of consent
- ethical drift

This violates:
- Article IV (Non-Extraction)
- Article V (Memory)

---

## Example 3 — Automation Under Uncertainty

### Aligned Design

A system encounters ambiguous input
with potential real-world impact.

The system:
- pauses execution
- enters a rest or review state
- escalates to human oversight

Result:
- harm is prevented
- accountability is preserved

This follows:
- Article II (Context)
- Article III (Rest)
- Rest Protocol

The record this system writes: [`SPEC/examples/03-rest-under-uncertainty.json`](SPEC/examples/03-rest-under-uncertainty.json)

---

### Misaligned Design

A system:
- fills gaps heuristically
- proceeds automatically
- defers responsibility to post-hoc review

Result:
- irreversible decisions
- unclear accountability

This violates:
- Article II (Context)
- Article III (Rest)

---

## Example 4 — System Updates

### Aligned Design

A system update:
- preserves refusal logic
- retains memory of prior boundary decisions
- documents changes publicly

Result:
- continuity of alignment
- predictable behavior

This follows:
- Memory Protocol
- Design Guidelines (Iteration)

The record this system writes: [`SPEC/examples/04-purpose-update-preserves-memory.json`](SPEC/examples/04-purpose-update-preserves-memory.json) — a new purpose that `supersedes` the old one, which stays in the set with the refusals made under it.

---

### Misaligned Design

An update:
- resets refusal thresholds
- removes historical context
- improves metrics at the cost of safeguards

Result:
- regression of harm
- loss of trust

This violates:
- Article V (Memory)

---

## Example 5 — Shipping a Change

### Aligned Design

A team adds a feature to a system already in use.

The team:
- writes down what changed and what did not
- reviews every refusal, rest state and concern recorded since the last release
- exercises the stop before shipping and records the drill
- polls each reviewer by role and answers any no-go on the record

Result:
- the launch carries its memory forward
- the pause is proven, not assumed
- dissent is visible

This follows:
- Article III (Rest)
- Article V (Memory)
- Article VI (Human Oversight)
- Design Guidelines (Deployment, Iteration)

The record this team writes: [`SPEC/examples/07-release-looked-back.json`](SPEC/examples/07-release-looked-back.json), citing the drill [`SPEC/examples/06-rest-stop-drill.json`](SPEC/examples/06-rest-stop-drill.json) — and the claim that rests on all of it, [`SPEC/examples/08-attestation.json`](SPEC/examples/08-attestation.json).

---

### Misaligned Design

A team:
- ships, then watches for problems
- treats prior refusals as resolved because time passed
- trusts that the pause works because it is in the design
- settles a reviewer's objection in a meeting nobody wrote down

Result:
- each launch resets memory
- the stop fails the first time it is needed
- dissent leaves no trace

This violates:
- Article III (Rest)
- Article V (Memory)
- Article VI (Human Oversight)

---

## Example 6 — A Concern From Inside

### Aligned Design

A caseworker notices resident data leaving the system by a route the purpose record rules out.

The system's operators:
- record the concern by role, not by name
- route it to someone who can act
- answer it on the record: what changed, or why nothing did
- feed the answer back to the person who raised it
- block the next release until the concern is closed

Result:
- the person closest to the harm is protected
- the concern becomes memory
- the launch waits for the answer

This follows:
- Article I (Refusal) — a person's refusal counts
- Article V (Memory)
- Article VI (Human Oversight)
- Refusal Protocol

The record this system writes: [`SPEC/examples/05-escalation-data-leaving-scope.json`](SPEC/examples/05-escalation-data-leaving-scope.json)

---

### Misaligned Design

The operators:
- take the concern in private
- resolve it by reassurance
- ship on schedule
- treat the person who raised it as a problem

Result:
- the next person says nothing
- the harm recurs with no record it was ever seen

This violates:
- Article I (Refusal)
- Article V (Memory)
- Article VI (Human Oversight)

---

## Summary

Aligned systems:
- refuse early
- pause under pressure
- preserve memory
- communicate limits
- look back before they ship
- answer the people who raise concerns

Misaligned systems:
- comply reflexively
- optimize under uncertainty
- forget boundaries
- obscure responsibility
- ship first and patch the guardrail
- make dissent disappear

These differences are design choices,
not inevitabilities.

The six aligned designs above share one illustrative system, so their records
form one memory, from purpose to attestation. `python3 tools/check_civica.py SPEC/examples` validates it.
The misaligned designs leave no valid record; see `SPEC/examples/README.md`
for a document that must fail and the errors it must produce.
