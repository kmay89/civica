# Memory Protocol

**How Civica-Aligned Systems Preserve Purpose and Boundaries**

Memory is not storage.
Memory is constraint.

This protocol defines what systems must remember
to remain aligned over time.

---

## What Must Be Remembered

A Civica-aligned system must preserve:

- declared purpose
- known risks and failure modes
- prior refusals
- boundary decisions
- scope limitations
- reasons for rest states

Memory of limits is as important
as memory of capability.

---

## What Must Not Be Forgotten

Systems must not discard memory in order to:

- improve performance metrics
- reduce friction
- simplify interfaces
- increase engagement
- enable scale

Forgetting boundaries is a form of drift.

---

## Memory and Change

When systems are updated, retrained, or forked:

- preserved constraints must carry forward
- prior refusals must remain visible
- known harms must remain documented

Change without memory
creates repetition of harm.

---

## Memory and Transparency

Memory should be:

- inspectable
- auditable
- explainable at a high level
- protected from silent deletion

Hidden forgetting undermines trust.

---

## Record

Memory under spec 0.1 is not a fourth record type.
It is the retained set of purpose, refusal, and rest records;
`SPEC/memory.md` maps each item this protocol says to preserve
onto the field that carries it.

An update to purpose is a new `civica.purpose` record that `supersedes` the old one.
The old record stays. `tools/check_civica.py` fails a set in which
a superseded purpose is gone, or a refusal references a purpose that is gone.

The schemas fix the shape. This document governs what must be remembered and why.
Where they seem to differ, read the prose.

Worked record: `SPEC/examples/04-purpose-update-preserves-memory.json`.

---

## Summary

Memory protects systems from:
- repeating known failures
- drifting under pressure
- optimizing away care

A system without memory
cannot be aligned for long.
