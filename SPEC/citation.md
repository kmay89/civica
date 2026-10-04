# Citing Civica

The only sentence a project may use to claim Civica alignment:

> This system follows Civica spec 0.1: Article I (refusal), Article III (rest), and Article V (memory). Records validate against SPEC/refusal.schema.json and SPEC/rest.schema.json. Archive and LEGAL are not part of this claim.

A project may name further articles from `SPEC/articles.yaml` in the same form. It may not name fewer than I, III, and V.

The claim is **false**, and must not be made, if any of these hold:

- refusal, rest, or purpose records can be deleted silently;
- rest can be overridden silently. A rest record with `silently_overridable` set to anything but `false` does not validate; a deployment that overrides rest without a record is the same failure without the evidence;
- refusal text is anthropomorphic ("I feel", "I don't want", "I'm not comfortable"). The protocol asks for the boundary and the category, not a preference;
- `tools/check_civica.py` does not exit 0 on the project's records against this repository's `SPEC/`.

The claim does not cover `ARCHIVE/` or `LEGAL/`, and must not mention them, the Navigator voice, witness attestations, or any hash in the legal declarations. A project that quotes the archive is quoting history, not the spec.

The earlier phrasings in `DESIGN_GUIDELINES.md` and `GETTING_STARTED.md` point here. This sentence supersedes them.
