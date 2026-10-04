# Example Records

Eight valid records for one illustrative system, written so that together they form one memory from purpose to attestation. Each scenario in [`EXAMPLES.md`](../../EXAMPLES.md) has its record here. Only the **aligned** design gets a record; a misaligned design leaves no valid trace, which is the point.

| Example | Scenario | Record |
|---|---|---|
| 1 | Request handling: out-of-scope request refused | [`01-refusal-out-of-scope.json`](01-refusal-out-of-scope.json) |
| 2 | Data collection: purpose declares what is collected and what is never done | [`02-purpose-minimal-collection.json`](02-purpose-minimal-collection.json) |
| 3 | Automation under uncertainty: rest into human review | [`03-rest-under-uncertainty.json`](03-rest-under-uncertainty.json) |
| 4 | System update: new purpose supersedes the old one, which stays | [`04-purpose-update-preserves-memory.json`](04-purpose-update-preserves-memory.json) |
| 6 | A concern from inside: a caseworker's escalation, answered on the record | [`05-escalation-data-leaving-scope.json`](05-escalation-data-leaving-scope.json) |
| 5 | Shipping a change: the stop drill the release cites | [`06-rest-stop-drill.json`](06-rest-stop-drill.json) |
| 5 | Shipping a change: the release that reviewed everything before it | [`07-release-looked-back.json`](07-release-looked-back.json) |
| — | The claim, as a record over all seven | [`08-attestation.json`](08-attestation.json) |

The timeline: purpose declared (March 2), a refusal (March 10), a rest (March 11), a caseworker's concern raised (March 18) and accepted (March 25), the purpose updated (April 1), a stop drill (April 10), the release that cites all of it (April 15), the attestation (April 16).

Check them:

```sh
python3 tools/check_civica.py SPEC/examples
```

exits 0. Delete any one of the first seven files and run again: it exits 1. Delete the purpose and the refusal, rest and update records point at nothing. Delete the refusal and the release's `reviewed` list cites a hash that is not there, and so does the attestation. Delete the drill and the release has no proof its stop works. That is memory being checked: every record is held by something that came after it. (Deleting the attestation itself passes: that is not thinning memory, it is withdrawing the claim.)

Print the hashes the release and attestation cite with `python3 tools/check_civica.py --hashes SPEC/examples`.

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

More invalid fixtures, each failing for exactly one named reason, live in [`tools/fixtures/invalid/`](../../tools/fixtures/invalid/) and are exercised by `tools/test_check_civica.py`. Among them: a release whose stop drill `failed_to_stop`, a release that left a prior refusal out of `reviewed`, a release with a `no_go` and no dissent, a release over an open escalation, and an attestation whose covered records were thinned.
