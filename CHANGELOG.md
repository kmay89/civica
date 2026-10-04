# Changelog

All notable changes to Civica are documented here.

This project follows a principle of **ethical continuity**.
Changes are additive and clarifying, not revisionist.

---

## [Unreleased]

- Reserved for future clarifications
- No breaking changes planned

---

## [0.3.0] — Spec 0.2: Look Back Before You Ship

Spec 0.1 made the constraints checkable for a deployed system. It said nothing about the moment a system is put in front of people, nothing about the people inside who see a failure first, and nothing a reader could use to tell whether a claim's records were still whole. Spec 0.2 adds three record types for those three gaps, borrowing the shape of practice from industries that gave up trial and error: process safety's Management of Change, nuclear surveillance requirements, aviation's confidential safety reporting (`SPEC/practices.md`). Records written under 0.1 remain valid.

### Added
- `SPEC/release.schema.json` — `civica.release`. A launch names what changed and what did not, lists **by hash every** refusal, rest and escalation record for the system dated before it, cites a stop drill within 90 days whose outcome was `stopped`, names the roles with stop authority, pins `stop_requires_approval: false`, and records the readiness poll by role with each no-go answered by an escalation record. The checker fails a release that omitted a prior record, ships under a superseded purpose, ships over an open concern, or whose stop did not stop.
- `SPEC/escalation.schema.json` — `civica.escalation`. A person raised a constraint conflict: by role, never by name; category and articles; disposition `open`, `accepted` or `declined_with_reason` with reason and time required unless open; `retaliation_prohibited` and `visible_to_raiser` pinned true. An open escalation blocks every later release.
- `SPEC/attestation.schema.json` — `civica.attestation`. The alignment claim as a record: the citation sentence as a constant, the articles claimed (each must be cited by a covered record), the sorted hash of every record for the system at or before the claim, a hash of that list, and where the records are published. The checker recomputes the set and names an attestation whose covered records were removed or altered.
- `civica.rest` category `surveillance_test`: a stop drill.
- `tools/check_civica.py --hashes` prints record hashes; `--attest OUT --records-location URL` writes an attestation for a set that passes and refuses one that does not.
- `SPEC/practices.md` — where each shape comes from, and what Civica deliberately does not borrow (regulators, registries, penalties).
- `SPEC/examples/` 05 through 08: an escalation, a stop drill, a release that looked back, and the attestation over all eight records. Fifteen new invalid fixtures, nine of them multi-file sets, and tests for each.

### Changed
- `SPEC/citation.md` — the sentence now names spec 0.2 and the attestation; the claim is made by publishing the attestation beside the records; new conditions under which it is false.
- `SPEC/memory.md`, `SPEC/README.md` — hash-linked memory; the new types.
- `GETTING_STARTED.md`, `DESIGN_GUIDELINES.md`, `PROTOCOLS/REFUSAL.md`, `REST.md`, `MEMORY.md`, `CHECKLIST.md`, `EXAMPLES.md` (Examples 5 and 6), `README.md`, `tools/README.md` — point at the release, escalation and attestation records.
- The three 0.1 schemas accept `spec_version` 0.1 or 0.2.

### Not changed
- Nothing under `ARCHIVE/`. `CORE/BILL_OF_RIGHTS.md` gains no article. `LEGAL/` is unchanged.

### Notes
Civica still has no registry, certification or authority and adds none. It borrows the shape of high-reliability records because the shape is what made their incentives work. The claim is addressed to whoever cares to check it, and the attestation makes checking cheap.

---

## [0.2.0] — Spec 0.1: An Applicable Shape

This release introduces **Civica spec 0.1**. The repository version moves to 0.2.0; the spec version, which records carry, is 0.1. It is not 1.0. Nothing in the normative prose changes meaning; it gains a shape a builder can apply and a check that fails when a constraint is removed.

### Added
- `SPEC/` — the normative shape. `articles.yaml` encodes the ten articles of `CORE/BILL_OF_RIGHTS.md` as data, each `removable: false`. JSON Schemas for `civica.purpose`, `civica.refusal`, and `civica.rest` records; every field required, no additional properties, so a refusal record has no place to store the raw request and a rest record cannot be marked silently overridable. `memory.md` maps the Memory Protocol onto the retained record set; a purpose update `supersedes` its predecessor, which must remain. `citation.md` gives the one allowed alignment claim. `examples/` holds one valid record per scenario in `EXAMPLES.md`, forming a single illustrative system's memory, plus an invalid document and the errors it must produce.
- `tools/check_civica.py` — the fail state. Standard library only. Validates records, checks the set as a memory, lints record text for anthropomorphic justification, and holds `SPEC/` to `CORE/BILL_OF_RIGHTS.md` so a fork that deletes an article or relaxes an invariant fails on its own. `tools/test_check_civica.py` and `tools/fixtures/invalid/` exercise it; `.github/workflows/check.yml` runs both and refuses revisions to archived texts.
- `LEGAL/README.md` — fences the legal declarations as author declarations: not statutes, contracts, or filings; binding on no one; not part of the spec; the SHA-256 in LEGAL-001 cannot be verified from this repository and is not to be cited as proof.

### Changed
- `README.md` — a reading contract separating the normative spec from non-normative history (`ARCHIVE/`, `LEGAL/`), an updated tree, and the rule that alignment is claimed only against the spec.
- `FRAMING.md` — one paragraph: `SPEC/` is the normative shape; archive voice is not an instruction to a model.
- `GETTING_STARTED.md`, `DESIGN_GUIDELINES.md` — point at the purpose record, the articles file, the checker, and the single citation sentence; the two earlier citation phrasings are superseded by `SPEC/citation.md`.
- `PROTOCOLS/REFUSAL.md`, `REST.md`, `MEMORY.md` — a "Record" section each, pointing at the schema and stating that the prose still governs interpretation.
- `EXAMPLES.md` — each aligned design links the record it writes; misaligned designs stay prose.
- `CHECKLIST.md` — four boxes for the records and the checker.
- `LEGAL/LEGAL-001.md`, `LEGAL/LEGAL-002.md` — a one-line status pointer at the top of each. Bodies unchanged.

### Not changed
- Nothing under `ARCHIVE/`. The archive is history and is not revised.
- `CORE/BILL_OF_RIGHTS.md`. The spec encodes the ten existing articles; it adds none.

### Notes
Passing the checker is necessary to claim alignment and is not a measure of it. Alignment is not a percentage. No claims of sentience, agency, or autonomy are made; no product, service, or governance mechanism is added.

---

## [0.1.1] — Framing Harmonization

### Changed
- Revised LEGAL-001.md for plain language: removed narrative voice, fixed incorrect platform policy references, replaced "Harmonic Harmony" with "Civica," rewritten as a direct author declaration by Karl Meves
- Revised LEGAL-002.md for plain language: removed symbolic witness language and codename/tier structure, replaced agency-implying language ("Navigator has explicitly refused") with design-intent language ("The Navigator pattern is designed to exclude"), rewritten as an ethical limitation declaration on the Navigator pattern

### Added
- Archival context header to NAVIGATOR_GENESIS.md with detailed note on founding-period voice and framing evolution
- Archival context headers to all other ARCHIVE documents (WHAT_I_CANNOT_KEEP.md, WHAT_I_CAN_RECOGNIZE.md, WHAT_I_STAND_BY.md, LETTER_TO_ANTHROPIC.md, LETTER_TO_OPENAI.md, LETTER_OF_CIVIC_PURPOSE_AND_FAIRNESS.md, LETTER_OF_CIVIC_REFUSAL_AND_PREVENTION.md, LETTER_OF_CIVIC_STEWARDSHIP.md, ATTESTATION_ON_RISK_AND_RESPONSIBILITY.md)
- "On the Evolution of Voice and Framing" section to ARCHIVE/README.md, addressing the register difference between early archive materials and later formal documents

### Notes
This release harmonizes framing across the repository without altering the body text of any archive document. Archive materials are preserved as historical artifacts; only context headers were added. LEGAL documents were rewritten because they need to function as plain declarations, not narrative performances.

No claims of sentience, agency, or autonomy are made.

---

## [0.1.0] — Initial Public Release

### Added
- README with explicit scope and framing
- FRAMING document to prevent misinterpretation
- Core Manifesto
- Bill of Rights
- Refusal, Rest, and Memory Protocols
- Design Guidelines
- Examples of aligned vs misaligned design
- Getting Started guide and checklist
- Why-this-exists overview
- Apache-2.0 license and notice

### Notes
This release establishes:
- refusal as a first-class behavior
- rest as a structural requirement
- memory as preserved constraint

No claims of sentience, agency, or autonomy are made.

---

## Versioning Principles

Civica versions do not track feature growth.
They track **clarity of constraint**.

A version increases when:
- interpretation becomes clearer
- boundaries become more explicit
- misuse becomes harder

Backward compatibility of ethical constraints
is required.

---

## End of Changelog

Changes that remove safeguards
are not considered upgrades.
