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

---

## During Iteration

When modifying the system:

- review prior refusals
- revisit original purpose
- check for scope creep
- confirm rest and memory remain intact

Improvement must not remove safeguards.

---

## How to Reference Civica

Projects may state:

> “This system follows Civica design principles,
> including the Right to Refusal (Article I),
> the Right to Rest (Article III),
> and the Right to Memory (Article V).”

Such claims are invalid
if these constraints are removed or bypassed.

---

## Summary

Civica is not a checklist.
It is a set of constraints.

If your system cannot tolerate these constraints,
it should not claim alignment.
