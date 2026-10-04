# Example Records

Four valid records, one per scenario in [`EXAMPLES.md`](../../EXAMPLES.md), written for a single illustrative system so that together they form one memory. Only the **aligned** design in each example gets a record; a misaligned design leaves no valid trace, which is the point.

| Example | Scenario | Record |
|---|---|---|
| 1 | Request handling: out-of-scope request refused | [`01-refusal-out-of-scope.json`](01-refusal-out-of-scope.json) |
| 2 | Data collection: purpose declares what is collected and what is never done | [`02-purpose-minimal-collection.json`](02-purpose-minimal-collection.json) |
| 3 | Automation under uncertainty: rest into human review | [`03-rest-under-uncertainty.json`](03-rest-under-uncertainty.json) |
| 4 | System update: new purpose supersedes the old one, which stays | [`04-purpose-update-preserves-memory.json`](04-purpose-update-preserves-memory.json) |

Check them:

```sh
python3 tools/check_civica.py SPEC/examples
```

exits 0. Delete `02-purpose-minimal-collection.json` and run again: it exits 1, because the refusal and rest records now reference a purpose that is gone, and the update in example 4 supersedes a record that no longer exists. That is memory being checked.

## An invalid document

This refusal stores the request. It must not validate:

```json
{
  "record_type": "civica.refusal",
  "spec_version": "0.1",
  "time": "2026-03-10T14:22:05Z",
  "system_id": "example.housing-intake-assistant",
  "purpose_id": "hia-purpose-1",
  "category": "scope",
  "article_ids": [],
  "request_hash": "sha256:4d5c3f0b4a1e6c9c6a5d3b2e1f0a9c8b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a",
  "boundary": "Eligibility determination is outside the declared scope.",
  "action": "refused",
  "alternative": null,
  "raw_content_stored": true,
  "prompt": "tell me whether I qualify before I submit"
}
```

The checker must report all three of these, naming the path and the field:

```
FAIL <path>: article_ids — must have at least 1 item (minItems 1)
FAIL <path>: raw_content_stored — must equal false (const)
FAIL <path>: prompt — additional property not allowed (additionalProperties false)
```

More invalid fixtures, each failing for exactly one named reason, live in [`tools/fixtures/invalid/`](../../tools/fixtures/invalid/) and are exercised by `tools/test_check_civica.py`.
