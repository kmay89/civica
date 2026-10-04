# Civica Design Guidelines

**How to Apply Civica Principles in Real Projects**

This document translates Civica principles
into practical design guidance.

---

## Before You Build

Ask:

- What is this system for?
- Who does it serve?
- What harm is already known in this domain?
- What must this system refuse to do?

If these answers are unclear,
do not proceed to implementation.

---

## During Design

Ensure the system:

- has a defined scope and boundary
- can refuse requests outside that scope
- can pause or reduce authority
- preserves memory of prior decisions
- allows human oversight

Avoid designs that:
- maximize engagement by default
- silently expand scope
- treat all inputs as actionable
- optimize away friction without review

---

## During Implementation

Encode:

- refusal as an explicit path
- rest as a valid state
- memory as preserved constraint
- transparency of limits

Do not rely on:
- undocumented behavior
- hidden heuristics
- silent fallbacks
- assumed compliance

---

## During Deployment

Verify that:

- users understand system limits
- refusal behavior is visible
- oversight mechanisms exist
- updates do not erase constraints

Deployment without boundaries
is not alignment.

Each deployment is a `civica.release` record: what changed, every prior
refusal, rest and escalation reviewed by hash, a stop drill within the
interval that stopped, a readiness poll by role. Nothing ships over an open
concern. See `SPEC/practices.md` for where this comes from.

---

## During Iteration

When modifying the system:

- review prior refusals
- revisit original purpose
- check for scope creep
- confirm rest and memory remain intact

Improvement must not remove safeguards.

The release record is where "review prior refusals" stops being advice:
the checker fails a release that did not list one.

---

## How to Reference Civica

The one allowed sentence is in `SPEC/citation.md`.
It names spec 0.2, Articles I, III, and V at minimum,
and is written into a `civica.attestation` record that lists
the hash of every record the claim rests on.

Such claims are invalid
if these constraints are removed or bypassed,
and the claim never covers `ARCHIVE/` or `LEGAL/`.

---

## Summary

Civica is not a checklist.
It is a set of constraints.

If your system cannot tolerate these constraints,
it should not claim alignment.
