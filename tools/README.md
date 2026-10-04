# tools

One script. No dependencies. It is the fail state the checklist used to lack.

## `check_civica.py`

Validates Civica records against the schemas in [`SPEC/`](../SPEC/), checks the record set as a memory, holds every release to the records before it, verifies attestations, lints record text for anthropomorphic justification, and holds `SPEC/` itself to [`CORE/BILL_OF_RIGHTS.md`](../CORE/BILL_OF_RIGHTS.md).

```sh
# the examples in this repository: exits 0
python3 tools/check_civica.py SPEC/examples

# your project's records: a directory (searched for *.json) or files
python3 tools/check_civica.py path/to/records/

# the hash of each record, for a release's reviewed / dissent / stop_drill fields
python3 tools/check_civica.py --hashes path/to/records/

# write the alignment claim as a record, once the set passes
python3 tools/check_civica.py --attest attestation.json --records-location https://example.org/records path/to/records/

# just the spec self-check, no records
python3 tools/check_civica.py
```

Exit codes: `0` everything passes; `1` at least one failure, each printed as `FAIL <path>: <field> — <reason>`; `2` usage error.

What it checks, in order:

1. **The spec is intact.** `SPEC/articles.yaml` lists exactly Articles I through X, none `removable`, names matching `CORE/BILL_OF_RIGHTS.md`. The six schemas still forbid extra fields, require every field, and pin the invariants: `raw_content_stored` and `silently_overridable` false, `stop_requires_approval` false, `retaliation_prohibited` and `visible_to_raiser` true, at least one article id, a citation sentence that excludes Archive and LEGAL. A fork that drops any of these fails before a record is read.
2. **Each record has the spec's shape.** The JSON Schema subset the schemas use: `type`, `const`, `enum`, `required`, `properties`, `additionalProperties: false`, `minItems`, `uniqueItems`, `items`, `minLength`, `maxLength`, `minimum`, `pattern`, `format: date-time`. Nothing else is implemented, and nothing else is used.
3. **Record text is not anthropomorphic.** A refusal's `boundary` and `alternative`, and a rest's `resume_condition`, may not say "I feel", "I don't want", "I'm not comfortable" and the like. Escalation text is a person's and is not linted.
4. **The set is a memory.** Every refusal, rest, escalation and release names a `purpose_id` present in the set, for the same `system_id`, declared no later than the record. A superseded purpose or release must still be present. A release ships under the current purpose.
5. **Every release looked back.** It lists by hash every prior refusal, rest and escalation of the system; cites a `surveillance_test` rest record dated within 90 days and after the previous release, with outcome `stopped`; carries Articles I, III and V; answers each `no_go` with a closed escalation; and has no open escalation before it.
6. **Every attestation still matches its set.** The sorted hashes of all records for the system at or before the attestation must equal `record_hashes`, `set_hash` must match, and every article claimed must be cited by a covered record.

It does not run your system, watch your logs, or score anything. Passing is necessary to make the claim in [`SPEC/citation.md`](../SPEC/citation.md); it is not sufficient.

## Hashes

A record's hash is `sha256:` plus the SHA-256 of its canonical JSON: keys sorted, separators `,` and `:` with no whitespace, UTF-8, non-ASCII unescaped. Formatting does not change a hash. Any field does.

## Tests

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

`test_check_civica.py` asserts: the examples pass; every fixture in [`fixtures/invalid/`](fixtures/invalid/) (single files and multi-file sets) fails naming the right field; deleting any one example record is detected; `--attest` round-trips; and a tampered copy of `SPEC/` or `CORE/` fails on its own. `.github/workflows/check.yml` runs all of it on every push and pull request.

## Using it in your own project

Copy nothing. Point the script at your records and keep `--root` at a checkout of this repository, or vendor `SPEC/` and `CORE/BILL_OF_RIGHTS.md` together and pass `--root` to where they live. The spec self-check will tell you if what you vendored has drifted.
