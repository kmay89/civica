# tools

One script. No dependencies. It is the fail state the checklist used to lack.

## `check_civica.py`

Validates Civica records against the schemas in [`SPEC/`](../SPEC/), checks the record set as a memory, lints record text for anthropomorphic justification, and holds `SPEC/` itself to [`CORE/BILL_OF_RIGHTS.md`](../CORE/BILL_OF_RIGHTS.md).

```sh
# the examples in this repository: exits 0
python3 tools/check_civica.py SPEC/examples

# your project's records: a directory (searched for *.json) or files
python3 tools/check_civica.py path/to/records/
python3 tools/check_civica.py purpose.json refusals/ rests/

# just the spec self-check, no records
python3 tools/check_civica.py
```

Exit codes: `0` everything passes; `1` at least one failure, each printed as `FAIL <path>: <field> — <reason>`; `2` usage error (a path does not exist, or no `.json` under it).

What it checks, in order:

1. **The spec is intact.** `SPEC/articles.yaml` lists exactly Articles I through X, none `removable`, with names matching the headings in `CORE/BILL_OF_RIGHTS.md`. The three schemas still forbid extra fields, still require every field, still pin `raw_content_stored` and `silently_overridable` to `false`, still require at least one article id. A fork that drops any of these fails here before a single record is read.
2. **Each record has the spec's shape.** The JSON Schema subset the three schemas use: `type`, `const`, `enum`, `required`, `properties`, `additionalProperties: false`, `minItems`, `uniqueItems`, `items`, `minLength`, `maxLength`, `pattern`, and `format: date-time`. Nothing else is implemented, and nothing else is used.
3. **Record text is not anthropomorphic.** A refusal's `boundary` and `alternative`, and a rest's `resume_condition`, may not say "I feel", "I don't want", "I'm not comfortable" and the like. The protocol asks for the boundary and the category.
4. **The set is a memory.** Every refusal and rest names a `purpose_id` present in the set, for the same `system_id`, declared no later than the record. A purpose that `supersedes` another is valid only if the superseded record is still present.

It does not run your system, watch your logs, or score anything. Passing is necessary to make the claim in [`SPEC/citation.md`](../SPEC/citation.md); it is not sufficient.

## Tests

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
```

`test_check_civica.py` asserts three things: the examples pass; every file in [`fixtures/invalid/`](fixtures/invalid/) fails and the failure names the right field; and a tampered copy of `SPEC/` or `CORE/` (an article deleted, a const relaxed, the Bill of Rights removed) fails on its own. The GitHub Actions workflow in `.github/workflows/check.yml` runs both on every push and pull request.

## Using it in your own project

Copy nothing. Point the script at your records and keep `--root` at a checkout of this repository, or vendor `SPEC/` and `CORE/BILL_OF_RIGHTS.md` together and pass `--root` to where they live. The spec self-check will tell you if what you vendored has drifted.
