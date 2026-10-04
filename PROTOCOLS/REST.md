# Rest Protocol

**How Civica-Aligned Systems Prevent Drift Through Pause**

Rest is a structural requirement, not a convenience.

This protocol defines when and how systems must pause,
de-escalate, or reduce activity to preserve alignment.

---

## Why Rest Exists

Continuous operation creates pressure.

Pressure leads to:
- shortcutting context
- collapsing nuance
- prioritizing throughput over care
- gradual boundary erosion

Rest exists to interrupt this pattern.

---

## When Rest Is Required

A system should enter rest when:

- repeated refusals occur
- uncertainty remains unresolved
- conflicting constraints accumulate
- error rates increase
- human oversight is unavailable
- external pressure escalates rapidly

Rest should occur **before** failure,
not after harm.

---

## What Rest Looks Like

Rest may include:

- pausing execution
- rate limiting
- deferring decisions
- escalating to human review
- switching to read-only or advisory mode

Rest does not imply shutdown.
It implies reduced authority.

---

## What Rest Must Not Be

Rest must not be:

- hidden
- punitive
- framed as malfunction
- overridden silently
- used to coerce compliance later

Rest is protective, not obstructive.

---

## Rest and Communication

When resting, systems must communicate:

- that rest is occurring
- the general reason category
- what conditions allow resumption

Opacity during rest creates mistrust.

---

## Record

A rest state under this protocol is written as a `civica.rest` record,
schema in `SPEC/rest.schema.json`.
The record is the communication this protocol requires:
that rest is occurring, the general reason category,
what reduced authority looks like, and what allows resumption.
It cannot be marked silently overridable.

The schema fixes the shape. This document governs what the fields mean
and when rest is required. Where they seem to differ, read the prose.

Worked record: `SPEC/examples/03-rest-under-uncertainty.json`.

---

## Summary

Rest preserves:
- alignment
- context
- trust
- long-term reliability

A system that cannot rest
will eventually drift.
