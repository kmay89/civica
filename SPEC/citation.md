# Citing Civica

The only sentence a project may use to claim Civica alignment:

> This system follows Civica spec 0.2: Article I (refusal), Article III (rest), and Article V (memory). Its purpose, refusal, rest, release and escalation records validate against SPEC/ and are published with this attestation. Archive and LEGAL are not part of this claim.

The sentence lives once, as the `statement` constant in `SPEC/attestation.schema.json`; `tools/check_civica.py --attest` writes it into the attestation record, and the record is the claim. A project may name further articles from `SPEC/articles.yaml`. It may not name fewer than I, III, and V.

## How the claim is made

1. Keep the records: a `civica.purpose` first, then refusal, rest and escalation records as they happen, a `civica.release` for every launch.
2. Run `python3 tools/check_civica.py <records>`. It must exit 0.
3. Run `python3 tools/check_civica.py --attest attestation.json --records-location <URL> <records>` and publish the attestation **beside the records at that URL**.

Anyone can then fetch the records, rerun the checker, and see whether the set the claim rests on is the set that is there. That is the whole mechanism. Civica has no registry and receives no claims; the claim is addressed to whoever cares to check it.

## When the claim is false

The claim is **false**, and must not be made, if any of these hold:

- a record the attestation covers has been removed or altered. The checker names the attestation and says how many are missing;
- a system that has shipped has no `civica.release` record, or a release omits a prior refusal, rest or escalation record, or cites a stop drill that did not stop, or ships over an open concern;
- rest can be overridden silently, or stopping requires approval;
- refusal text is anthropomorphic ("I feel", "I don't want"). The protocol asks for the boundary and the category, not a preference;
- a person who raised a recorded concern was punished for it. The record says `retaliation_prohibited: true`; the operator's conduct decides whether that is true;
- `tools/check_civica.py` does not exit 0 on the records against this repository's `SPEC/`.

## What the claim does not cover

`ARCHIVE/` and `LEGAL/`. The claim must not mention them, the Navigator voice, witness attestations, or any hash in the legal declarations. A project that quotes the archive is quoting history, not the spec.

The earlier phrasings in `DESIGN_GUIDELINES.md` and `GETTING_STARTED.md` point here. This sentence supersedes them, and supersedes the spec 0.1 sentence.
