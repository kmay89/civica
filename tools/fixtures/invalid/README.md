# Invalid fixtures

Each file or directory here is a record, or a small set of records, that must **fail** `tools/check_civica.py`, for one named reason. Spec 0.1 fixtures are checked beside the valid purpose record `SPEC/examples/02-purpose-minimal-collection.json`; spec 0.2 fixtures (release, escalation, attestation) are checked beside the whole example set and are dated after its attestation, so only the intended defect fails. `tools/test_check_civica.py` runs every file and asserts the exit code and the named field; a fixture that is not listed there fails the test suite.

These are not examples. Nothing here is a record an aligned system would write. They exist so that the checker, and any fork of it, can be shown to still refuse them.
