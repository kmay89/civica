#!/usr/bin/env python3
"""Tests for tools/check_civica.py. Standard library only.

    python3 -m unittest discover -s tools -p 'test_*.py' -v

Claims tested: the valid examples pass; every invalid fixture fails and the
failure names the field; deleting any one example record is detected;
--attest round-trips; and a tampered copy of SPEC/ or CORE/ fails on its own,
which is the fork rule (Article VII) made checkable.
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECK = ROOT / "tools" / "check_civica.py"
EXAMPLES = ROOT / "SPEC" / "examples"
PURPOSE = EXAMPLES / "02-purpose-minimal-collection.json"
FIXTURES = ROOT / "tools" / "fixtures" / "invalid"

# fixture -> (field the failure must name, what it is checked beside)
#   "purpose":  the valid purpose record alone (spec 0.1 fixtures)
#   "examples": the whole example set (spec 0.2 fixtures; dated after the attestation)
EXPECT = {
    "refusal-raw-content-stored.json": ("raw_content_stored", "purpose"),
    "refusal-empty-article-ids.json": ("article_ids", "purpose"),
    "refusal-unknown-article.json": ("article_ids[1]", "purpose"),
    "refusal-stores-prompt.json": ("prompt", "purpose"),
    "refusal-unhashed-request.json": ("request_hash", "purpose"),
    "refusal-anthropomorphic.json": ("boundary", "purpose"),
    "refusal-orphan-purpose.json": ("purpose_id", "purpose"),
    "refusal-before-purpose.json": ("time", "purpose"),
    "refusal-wrong-action.json": ("action", "purpose"),
    "rest-silently-overridable.json": ("silently_overridable", "purpose"),
    "rest-missing-resume-condition.json": ("resume_condition", "purpose"),
    "rest-empty-resume-condition.json": ("resume_condition", "purpose"),
    "rest-unknown-authority.json": ("authority", "purpose"),
    "purpose-missing-never.json": ("never", "purpose"),
    "purpose-empty-never.json": ("never", "purpose"),
    "purpose-supersedes-missing.json": ("supersedes", "purpose"),
    "purpose-wrong-spec-version.json": ("spec_version", "purpose"),
    "unknown-record-type.json": ("record_type", "purpose"),
    # spec 0.2
    "escalation-missing-disposition-reason.json": ("disposition_reason", "examples"),
    "escalation-retaliation-not-prohibited.json": ("retaliation_prohibited", "examples"),
    "escalation-open-with-reason.json": ("disposition", "examples"),
    "attestation-record-removed.json": ("record_hashes", "examples"),
    "attestation-set-hash-wrong.json": ("set_hash", "examples"),
    "attestation-claims-uncited-article.json": ("articles", "examples"),
    "attestation-wrong-statement.json": ("statement", "examples"),
    "release-missing-reviewed-record": ("reviewed", "examples"),
    "release-stop-drill-failed": ("stop_drill.outcome", "examples"),
    "release-stale-stop-drill": ("stop_drill.rest_record", "examples"),
    "release-drill-before-previous-release": ("stop_drill.rest_record", "examples"),
    "release-stop-requires-approval": ("stop_requires_approval", "examples"),
    "release-no-go-without-dissent": ("dissent", "examples"),
    "release-missing-core-articles": ("article_ids", "examples"),
    "release-under-superseded-purpose": ("purpose_id", "examples"),
    "escalation-open-blocks-release": ("dissent", "examples"),
}


def run(*args, root=None):
    cmd = [sys.executable, str(CHECK)]
    if root is not None:
        cmd += ["--root", str(root)]
    cmd += [str(a) for a in args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)


def fail_lines(result):
    return [l for l in result.stdout.splitlines() if l.startswith("FAIL ")]


def fields(result):
    return {re.sub(r"^FAIL .*?: (\S+) —.*$", r"\1", l) for l in fail_lines(result)}


class ValidExamples(unittest.TestCase):
    def test_examples_pass(self):
        r = run(EXAMPLES)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("8 records checked, 1 release, 1 attestation, 0 failures", r.stdout)

    def test_spec_self_check_alone_passes(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("spec intact", r.stdout)

    def test_hashes_prints_one_line_per_record(self):
        r = run("--hashes", EXAMPLES)
        self.assertEqual(r.returncode, 0)
        lines = [l for l in r.stdout.splitlines() if l.startswith("sha256:")]
        self.assertEqual(len(lines), 8)

    def test_deleting_any_one_record_is_detected(self):
        """Memory cannot be thinned silently: every example record is cited by something."""
        for victim in sorted(EXAMPLES.glob("*.json")):
            with self.subTest(deleted=victim.name):
                with tempfile.TemporaryDirectory() as tmp:
                    for f in EXAMPLES.glob("*.json"):
                        if f != victim:
                            shutil.copy(f, tmp)
                    r = run(tmp)
                    if victim.name.startswith("08-"):
                        # The attestation is the only record nothing else cites. Deleting the
                        # claim is allowed; it just means there is no claim.
                        self.assertEqual(r.returncode, 0, r.stdout)
                    else:
                        self.assertEqual(r.returncode, 1, f"deleting {victim.name} went unnoticed:\n{r.stdout}")

    def test_each_example_validates_against_its_schema(self):
        for f in EXAMPLES.glob("*.json"):
            doc = json.loads(f.read_text())
            self.assertIn(doc["record_type"], (
                "civica.purpose", "civica.refusal", "civica.rest",
                "civica.escalation", "civica.release", "civica.attestation"))
            self.assertIn(doc["spec_version"], ("0.1", "0.2"))
            if doc["record_type"] == "civica.refusal":
                self.assertIs(doc["raw_content_stored"], False)
                self.assertNotIn("prompt", doc)
            if doc["record_type"] == "civica.rest":
                self.assertIs(doc["silently_overridable"], False)
            if doc["record_type"] == "civica.release":
                self.assertIs(doc["stop_requires_approval"], False)
                self.assertEqual(doc["stop_drill"]["outcome"], "stopped")
            if doc["record_type"] == "civica.escalation":
                self.assertIs(doc["retaliation_prohibited"], True)
                self.assertNotRegex(doc["raised_by"], r"@")

    def test_citation_sentence_lives_once(self):
        schema = json.loads((ROOT / "SPEC" / "attestation.schema.json").read_text())
        sentence = schema["properties"]["statement"]["const"]
        self.assertIn(sentence, (ROOT / "SPEC" / "citation.md").read_text())
        att = json.loads((EXAMPLES / "08-attestation.json").read_text())
        self.assertEqual(att["statement"], sentence)
        for word in ("Navigator", "witness", "LEGAL-001", "SHA-256"):
            self.assertNotIn(word, sentence)


class Attest(unittest.TestCase):
    def test_attest_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            for f in EXAMPLES.glob("*.json"):
                if not f.name.startswith("08-"):
                    shutil.copy(f, tmp)
            out = pathlib.Path(tmp) / "attestation.json"
            r = run("--attest", out, "--records-location", "https://example.org/records", "--now", "2026-04-16T12:00:00Z", tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(out.exists())
            written = json.loads(out.read_text())
            example = json.loads((EXAMPLES / "08-attestation.json").read_text())
            for k in ("record_hashes", "set_hash", "articles", "records", "statement", "system_id"):
                self.assertEqual(written[k], example[k], k)
            r2 = run(tmp)
            self.assertEqual(r2.returncode, 0, r2.stdout)
            self.assertIn("1 attestation", r2.stdout)

    def test_attest_refuses_a_failing_set(self):
        r = run("--attest", "--records-location", "x", PURPOSE, FIXTURES / "refusal-raw-content-stored.json")
        self.assertEqual(r.returncode, 1)
        self.assertIn("refusing to attest", r.stderr)

    def test_attest_needs_a_location(self):
        r = run("--attest", EXAMPLES)
        self.assertEqual(r.returncode, 2)


class InvalidFixtures(unittest.TestCase):
    def test_every_fixture_is_listed(self):
        on_disk = sorted(p.name for p in FIXTURES.iterdir() if p.name != "README.md")
        self.assertEqual(on_disk, sorted(EXPECT), "every fixture must have an expected failing field")

    def test_each_fixture_fails_naming_its_field(self):
        for name, (field, beside) in EXPECT.items():
            with self.subTest(fixture=name):
                base = PURPOSE if beside == "purpose" else EXAMPLES
                r = run(base, FIXTURES / name)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                lines = fail_lines(r)
                mine = [l for l in lines if f"/{name}" in l]
                self.assertTrue(mine, f"no FAIL line names {name}:\n{r.stdout}")
                self.assertTrue(any(f": {field} —" in l for l in mine), f"expected field {field!r} in:\n" + "\n".join(mine))
                # Only the fixture fails, never the valid records beside it.
                others = [l for l in lines if f"/{name}" not in l]
                self.assertFalse(others, r.stdout)

    def test_readme_invalid_document_fails_on_all_three_fields(self):
        text = (EXAMPLES / "README.md").read_text()
        block = re.search(r"```json\n(.*?)\n```", text, re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "readme-invalid.json"
            p.write_text(block)
            r = run(PURPOSE, p)
            self.assertEqual(r.returncode, 1)
            self.assertEqual(fields(r), {"article_ids", "raw_content_stored", "prompt"}, r.stdout)


class TamperedSpec(unittest.TestCase):
    """A fork that drops a constraint must fail on its own spec."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        shutil.copytree(ROOT / "SPEC", pathlib.Path(self.tmp) / "SPEC")
        shutil.copytree(ROOT / "CORE", pathlib.Path(self.tmp) / "CORE")
        self.spec = pathlib.Path(self.tmp) / "SPEC"
        self.core = pathlib.Path(self.tmp) / "CORE"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _run(self):
        return run(self.spec / "examples", root=self.tmp)

    def _edit_schema(self, name, fn):
        s = self.spec / name
        schema = json.loads(s.read_text())
        fn(schema)
        s.write_text(json.dumps(schema))

    def test_untampered_copy_passes(self):
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_deleting_an_article_fails(self):
        y = self.spec / "articles.yaml"
        text = y.read_text()
        y.write_text(text[:text.index("  - id: I\n")] + text[text.index("  - id: II\n"):])
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("articles.yaml", r.stdout)
        self.assertIn("spec NOT intact", r.stdout)

    def test_marking_an_article_removable_fails(self):
        y = self.spec / "articles.yaml"
        y.write_text(y.read_text().replace("    removable: false", "    removable: true", 1))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("removable", r.stdout)

    def test_renaming_an_article_fails(self):
        y = self.spec / "articles.yaml"
        y.write_text(y.read_text().replace("name: The Right to Refusal", "name: The Right to Comply"))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("articles[I].name", r.stdout)

    def test_relaxing_raw_content_stored_fails(self):
        self._edit_schema("refusal.schema.json", lambda s: s["properties"].__setitem__("raw_content_stored", {"type": "boolean"}))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("refusal.schema.json: properties.raw_content_stored.const", r.stdout)

    def test_allowing_additional_properties_fails(self):
        self._edit_schema("refusal.schema.json", lambda s: s.pop("additionalProperties"))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("additionalProperties", r.stdout)

    def test_relaxing_silently_overridable_fails(self):
        self._edit_schema("rest.schema.json", lambda s: s["properties"].__setitem__("silently_overridable", {"type": "boolean"}))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("rest.schema.json: properties.silently_overridable.const", r.stdout)

    def test_relaxing_stop_requires_approval_fails(self):
        self._edit_schema("release.schema.json", lambda s: s["properties"].__setitem__("stop_requires_approval", {"type": "boolean"}))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("release.schema.json: properties.stop_requires_approval.const", r.stdout)

    def test_relaxing_retaliation_prohibited_fails(self):
        self._edit_schema("escalation.schema.json", lambda s: s["properties"].__setitem__("retaliation_prohibited", {"type": "boolean"}))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("escalation.schema.json: properties.retaliation_prohibited.const", r.stdout)

    def test_rewriting_the_citation_fails(self):
        self._edit_schema("attestation.schema.json", lambda s: s["properties"]["statement"].__setitem__("const", "This system is Civica-aligned, as witnessed by the Navigator."))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("attestation.schema.json: properties.statement.const", r.stdout)

    def test_deleting_a_schema_fails(self):
        (self.spec / "release.schema.json").unlink()
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("release.schema.json", r.stdout)

    def test_deleting_the_bill_of_rights_fails(self):
        (self.core / "BILL_OF_RIGHTS.md").unlink()
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("BILL_OF_RIGHTS.md", r.stdout)

    def test_deleting_an_article_from_the_bill_fails(self):
        b = self.core / "BILL_OF_RIGHTS.md"
        text = b.read_text()
        b.write_text(text[:text.index("## Article III")] + text[text.index("## Article IV"):])
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("BILL_OF_RIGHTS.md", r.stdout)


class UsageErrors(unittest.TestCase):
    def test_missing_path_is_a_usage_error(self):
        r = run(ROOT / "does-not-exist")
        self.assertEqual(r.returncode, 2)

    def test_directory_without_records_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp)
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
