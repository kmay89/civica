# Memory Under Spec 0.1

`PROTOCOLS/MEMORY.md` says what a Civica-aligned system must preserve. Under this spec, memory is not a fourth record type. It is the **retained set** of the three that exist.

| The Memory Protocol says preserve | Carried by |
|---|---|
| declared purpose | `civica.purpose` — `purpose`, `serves` |
| known risks and failure modes | `civica.purpose` — `known_harms` |
| prior refusals | every `civica.refusal` record |
| boundary decisions | `civica.refusal` — `boundary`, `article_ids`; `civica.rest` — `authority` |
| scope limitations | `civica.purpose` — `scope_in`, `scope_out`, `never` |
| reasons for rest states | `civica.rest` — `category`, `resume_condition` |

What `tools/check_civica.py` holds the set to:

- every refusal and rest record names a `purpose_id` that is present in the set, for the same `system_id`, declared before the record's `time`. Purpose comes first (Getting Started, step 1); a refusal with no purpose is undefined;
- a purpose record that `supersedes` an earlier one validates only if the earlier record is still in the set. An update **replaces** a purpose; it does not **delete** one (Article V; `EXAMPLES.md`, Example 4);
- records carry a hash and short boundary text, never raw content, so keeping memory does not become extraction (Article IV).

What the checker cannot see: whether records are deleted between runs. That is the deployment's responsibility, and `CHECKLIST.md` asks it directly. The sentence in `citation.md` is false if records can be deleted silently.
