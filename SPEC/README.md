# SPEC — The Normative Shape of Civica

**Spec version 0.2.** Records written under 0.1 remain valid.

This directory is normative. `ARCHIVE/` and `LEGAL/` are not. If anything in the archive or the legal declarations conflicts with this directory, this directory and `FRAMING.md` win.

The prose in `CORE/` and `PROTOCOLS/` still governs interpretation. This directory gives that prose a shape two implementers cannot read differently:

- `articles.yaml` — the ten articles of `CORE/BILL_OF_RIGHTS.md` as data. None is removable.
- `purpose.schema.json` — the declared purpose that Getting Started step 1 requires you to write down.
- `refusal.schema.json` — a refusal record. No field for the request, no extra fields: storing the raw request is invalid.
- `rest.schema.json` — a rest record. It cannot be marked silently overridable. Category `surveillance_test` is a stop drill.
- `escalation.schema.json` — a person raised a constraint conflict. By role, never by name; answered on the record or recorded as open; an open one blocks any later release.
- `release.schema.json` — a launch. What changed, every prior refusal, rest and escalation cited by hash, the stop drill that proves the pause works, the readiness poll, and the dissent that answers each no-go.
- `attestation.schema.json` — the alignment claim as a record: the hash of every record it rests on, published with the records' location, so deletion shows.
- `memory.md` — what memory is under this spec: the retained, hash-linked set of these records.
- `practices.md` — where the release, drill, poll, escalation and attestation shapes come from: process safety, nuclear technical specifications, aviation safety reporting.
- `citation.md` — the one sentence a project may use, and when it is false.
- `examples/` — one valid record per scenario in `EXAMPLES.md`, forming one system's memory from purpose to attestation.

`tools/check_civica.py` is the fail state. It exits 0 on `examples/`, exits 1 on a record or a fork of this directory that drops a constraint, prints hashes, and writes attestations. Passing is necessary to claim alignment. It is not sufficient: alignment is not a score.
