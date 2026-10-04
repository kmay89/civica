# SPEC — The Normative Shape of Civica

**Spec version 0.1.**

This directory is normative. `ARCHIVE/` and `LEGAL/` are not. If anything in the archive or the legal declarations conflicts with this directory, this directory and `FRAMING.md` win.

The prose in `CORE/` and `PROTOCOLS/` still governs interpretation. This directory gives that prose a shape two implementers cannot read differently:

- `articles.yaml` — the ten articles of `CORE/BILL_OF_RIGHTS.md` as data. None is removable.
- `purpose.schema.json` — the declared purpose that Getting Started step 1 requires you to write down.
- `refusal.schema.json` — a refusal record. It has no field for the request and allows no extra fields, so storing the raw request is invalid.
- `rest.schema.json` — a rest record. It cannot be marked silently overridable.
- `memory.md` — what memory is under this spec: the retained set of these records.
- `citation.md` — the one sentence a project may use to claim alignment.
- `examples/` — one valid record per scenario in `EXAMPLES.md`, forming one system's memory.

`tools/check_civica.py` is the fail state. It exits 0 on `examples/` and exits 1 on a record, or on a fork of this directory, that drops a constraint. Passing is necessary to claim alignment. It is not sufficient: alignment is not a score.

Related shapes, for orientation only and implying no endorsement in either direction: a purpose record covers the same ground as a model card's intended-use and out-of-scope-use sections; refusal and rest records are event records in the ordinary structured-logging sense, with the content hashed out.
