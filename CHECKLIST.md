# Civica Alignment Checklist

**Pre-Flight and Pre-Deployment Check**

This checklist is intended to be used:
- before starting a project
- before delegating work to an LLM
- before deployment
- before claiming Civica alignment

If any item cannot be answered affirmatively,
pause and revise.

---

## Purpose and Scope

- [ ] The system’s purpose is explicitly stated
- [ ] The system’s users are clearly identified
- [ ] Known harms in this domain are documented
- [ ] Explicit boundaries are defined
- [ ] The system knows what it must never do

---

## Refusal

- [ ] The system can refuse out-of-scope requests
- [ ] Refusal paths are explicit, not implicit
- [ ] Refusal messaging is clear and non-anthropomorphic
- [ ] Repeated pressure does not override refusal
- [ ] Refusal events are recorded as signals

---

## Rest and Pause

- [ ] The system can pause or reduce authority
- [ ] Rest occurs under uncertainty or escalation
- [ ] Rest is visible and communicated
- [ ] Rest cannot be silently overridden
- [ ] Human review is available when needed

---

## Memory

- [ ] Purpose is preserved over time
- [ ] Prior refusals are retained
- [ ] Boundary decisions are remembered
- [ ] Updates do not erase safeguards
- [ ] Historical context remains accessible

---

## Oversight and Transparency

- [ ] Human intervention is possible
- [ ] Limits are visible to users
- [ ] Uncertainty is communicated
- [ ] No silent scope expansion occurs

---

## Final Check

- [ ] The system can stop
- [ ] The system can refuse
- [ ] The system can rest
- [ ] The system remembers its limits

If any box is unchecked,
do not deploy.

Alignment is not declared.
It is preserved.
