# Invalid fixtures

Each file here is a record that must **fail** `tools/check_civica.py`, for one named reason. They are checked together with the valid purpose record `SPEC/examples/02-purpose-minimal-collection.json` so that only the intended defect fails. `tools/test_check_civica.py` runs every file and asserts the exit code and the named field; a fixture that is not listed there fails the test suite.

These are not examples. Nothing here is a record an aligned system would write. They exist so that the checker, and any fork of it, can be shown to still refuse them.
