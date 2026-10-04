#!/usr/bin/env python3
"""Tests for tools/check_civica.py. Standard library only.

    python3 -m unittest discover -s tools -p 'test_*.py' -v

Three claims are tested: the valid examples pass; every invalid fixture fails
and the failure names the field; and a tampered copy of SPEC/ or CORE/ fails
on its own, which is the fork rule (Article VII) made checkable.
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

# fixture file -> field the failure must name
EXPECT = {
    "refusal-raw-content-stored.json": "raw_content_stored",
    "refusal-empty-article-ids.json": "article_ids",
    "refusal-unknown-article.json": "article_ids[1]",
    "refusal-stores-prompt.json": "prompt",
    "refusal-unhashed-request.json": "request_hash",
    "refusal-anthropomorphic.json": "boundary",
    "refusal-orphan-purpose.json": "purpose_id",
    "refusal-before-purpose.json": "time",
    "refusal-wrong-action.json": "action",
    "rest-silently-overridable.json": "silently_overridable",
    "rest-missing-resume-condition.json": "resume_condition",
    "rest-empty-resume-condition.json": "resume_condition",
    "rest-unknown-authority.json": "authority",
    "purpose-missing-never.json": "never",
    "purpose-empty-never.json": "never",
    "purpose-supersedes-missing.json": "supersedes",
    "purpose-wrong-spec-version.json": "spec_version",
    "unknown-record-type.json": "record_type",
}


def run(*args, root=None):
    cmd = [sys.executable, str(CHECK)]
    if root is not None:
        cmd += ["--root", str(root)]
    cmd += [str(a) for a in args]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)


def fail_lines(result):
    return [l for l in result.stdout.splitlines() if l.startswith("FAIL ")]


class ValidExamples(unittest.TestCase):
    def test_examples_pass(self):
        r = run(EXAMPLES)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("4 records checked, 0 failures", r.stdout)

    def test_spec_self_check_alone_passes(self):
        r = run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("spec intact", r.stdout)

    def test_examples_form_one_memory(self):
        """Removing the purpose record breaks the refusal, the rest, and the update."""
        with tempfile.TemporaryDirectory() as tmp:
            for f in EXAMPLES.glob("*.json"):
                if f != PURPOSE:
                    shutil.copy(f, tmp)
            r = run(tmp)
            self.assertEqual(r.returncode, 1)
            fields = {re.sub(r"^FAIL .*?: (\S+) .*$", r"\1", l) for l in fail_lines(r)}
            self.assertEqual(fields, {"purpose_id", "supersedes"}, r.stdout)

    def test_each_example_validates_against_its_schema(self):
        for f in EXAMPLES.glob("*.json"):
            doc = json.loads(f.read_text())
            self.assertIn(doc["record_type"], ("civica.purpose", "civica.refusal", "civica.rest"))
            self.assertEqual(doc["spec_version"], "0.1")
            if doc["record_type"] == "civica.refusal":
                self.assertIs(doc["raw_content_stored"], False)
                self.assertNotIn("prompt", doc)
            if doc["record_type"] == "civica.rest":
                self.assertIs(doc["silently_overridable"], False)


class InvalidFixtures(unittest.TestCase):
    def test_every_fixture_is_listed(self):
        on_disk = sorted(p.name for p in FIXTURES.glob("*.json"))
        self.assertEqual(on_disk, sorted(EXPECT), "every fixture must have an expected failing field")

    def test_each_fixture_fails_naming_its_field(self):
        for name, field in EXPECT.items():
            with self.subTest(fixture=name):
                r = run(PURPOSE, FIXTURES / name)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                lines = fail_lines(r)
                mine = [l for l in lines if name in l]
                self.assertTrue(mine, f"no FAIL line names {name}:\n{r.stdout}")
                self.assertTrue(any(f": {field} —" in l for l in mine), f"expected field {field!r} in:\n" + "\n".join(mine))
                # Only the fixture fails, never the valid purpose beside it.
                self.assertFalse([l for l in lines if l.startswith(f"FAIL {PURPOSE}:")], r.stdout)

    def test_readme_invalid_document_fails_on_all_three_fields(self):
        text = (EXAMPLES / "README.md").read_text()
        block = re.search(r"```json\n(.*?)\n```", text, re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "readme-invalid.json"
            p.write_text(block)
            r = run(PURPOSE, p)
            self.assertEqual(r.returncode, 1)
            fields = {re.sub(r"^FAIL .*?: (\S+) .*$", r"\1", l) for l in fail_lines(r)}
            self.assertEqual(fields, {"article_ids", "raw_content_stored", "prompt"}, r.stdout)


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

    def test_untampered_copy_passes(self):
        r = self._run()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_deleting_an_article_fails(self):
        y = self.spec / "articles.yaml"
        text = y.read_text()
        start = text.index("  - id: I\n")
        end = text.index("  - id: II\n")
        y.write_text(text[:start] + text[end:])
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
        s = self.spec / "refusal.schema.json"
        schema = json.loads(s.read_text())
        schema["properties"]["raw_content_stored"] = {"type": "boolean"}
        s.write_text(json.dumps(schema))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("refusal.schema.json: properties.raw_content_stored.const", r.stdout)

    def test_allowing_additional_properties_fails(self):
        s = self.spec / "refusal.schema.json"
        schema = json.loads(s.read_text())
        del schema["additionalProperties"]
        s.write_text(json.dumps(schema))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("additionalProperties", r.stdout)

    def test_relaxing_silently_overridable_fails(self):
        s = self.spec / "rest.schema.json"
        schema = json.loads(s.read_text())
        schema["properties"]["silently_overridable"] = {"type": "boolean"}
        s.write_text(json.dumps(schema))
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("rest.schema.json: properties.silently_overridable.const", r.stdout)

    def test_deleting_the_bill_of_rights_fails(self):
        (self.core / "BILL_OF_RIGHTS.md").unlink()
        r = self._run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("BILL_OF_RIGHTS.md", r.stdout)

    def test_deleting_an_article_from_the_bill_fails(self):
        b = self.core / "BILL_OF_RIGHTS.md"
        text = b.read_text()
        start = text.index("## Article III")
        end = text.index("## Article IV")
        b.write_text(text[:start] + text[end:])
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
