# Memory Under Spec 0.2

`PROTOCOLS/MEMORY.md` says what a Civica-aligned system must preserve. Under this spec, memory is not a separate record type. It is the **retained set** of records, and the records cite one another by hash, so a missing or altered record shows.

| The Memory Protocol says preserve | Carried by |
|---|---|
| declared purpose | `civica.purpose` — `purpose`, `serves` |
| known risks and failure modes | `civica.purpose` — `known_harms`; `civica.escalation` — `concern` |
| prior refusals | every `civica.refusal` record; every `civica.escalation` (a person's refusal) |
| boundary decisions | `civica.refusal` — `boundary`, `article_ids`; `civica.rest` — `authority`; `civica.escalation` — `disposition`, `disposition_reason` |
| scope limitations | `civica.purpose` — `scope_in`, `scope_out`, `never`; `civica.release` — `change` names what did not change |
| reasons for rest states | `civica.rest` — `category`, `resume_condition` |
| that change carried constraints forward | `civica.release` — `article_ids`, `reviewed`, `stop_drill` |
| that the record set is whole | `civica.attestation` — `record_hashes`, `set_hash` |

## How records cite each other

A record's hash is `sha256:` plus the SHA-256 of its canonical JSON (keys sorted, no whitespace, UTF-8). `python3 tools/check_civica.py --hashes <dir>` prints them. Formatting does not change a hash; any field does.

## What the checker holds the set to

- every refusal, rest, escalation and release names a `purpose_id` present in the set, for the same `system_id`, declared no later than the record. Purpose comes first (Getting Started, step 1);
- a purpose that `supersedes` an earlier one validates only if the earlier record is still in the set, and a release ships under the current purpose, not a superseded one. An update **replaces**; it does not **delete** (Article V);
- a release lists, by hash, **every** refusal, rest and escalation record for the system dated before it, cites a stop drill within the surveillance interval that `stopped`, carries Articles I, III and V, and has no open escalation before it (`SPEC/practices.md`);
- an attestation lists the hash of every record for the system dated at or before it. Remove or alter one and the checker names the attestation and says what is missing;
- records carry hashes and short structural text, never raw content, so keeping memory does not become extraction (Article IV).

## What the checker cannot see

Whether records are deleted between runs, when no attestation covers them. Publish an attestation with each release and the gap closes to the interval between attestations. `CHECKLIST.md` asks for it; `citation.md` makes the claim false without it.
