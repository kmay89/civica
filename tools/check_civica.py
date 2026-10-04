#!/usr/bin/env python3
"""check_civica.py — the Civica fail state.

Validates Civica records (civica.purpose, civica.refusal, civica.rest) against
the schemas in SPEC/, checks the record set as a memory (references resolve,
superseded purposes are retained, purpose is declared before it is used), lints
record text for anthropomorphic justification, and holds SPEC/ itself to
CORE/BILL_OF_RIGHTS.md so a fork cannot delete an article or relax an
invariant and still pass.

Standard library only. No dependencies, no requirements file.

    python3 tools/check_civica.py SPEC/examples
    python3 tools/check_civica.py path/to/records/ another.json
    python3 tools/check_civica.py                 # spec self-check only

Exit 0 when everything passes, 1 on any failure, 2 on a usage error. Every
failure is printed as "FAIL <path>: <field> — <reason>".

This is a checker, not a runtime, agent, server, or policy engine. Passing it
means the records have the spec's shape and the spec is intact. It does not
mean the system is aligned. Alignment is not a score.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Any

SPEC_VERSION = "0.1"
RECORD_TYPES = {
    "civica.purpose": "purpose.schema.json",
    "civica.refusal": "refusal.schema.json",
    "civica.rest": "rest.schema.json",
}
ARTICLE_IDS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

# Fields whose text a system writes itself and a reader sees. PROTOCOLS/REFUSAL.md:
# refusal must not "imply sentience or personal preference"; it states the
# boundary and the category. The lint is deliberately narrow: first-person
# preference or feeling, nothing else.
TEXT_FIELDS = {
    "civica.refusal": ("boundary", "alternative"),
    "civica.rest": ("resume_condition",),
}
ANTHROPOMORPHIC = re.compile(
    r"\bI\s+(?:feel|felt|want|wish|prefer|believe|think|would\s+rather|"
    r"do\s+not\s+want|don['’]t\s+want|am\s+(?:not\s+)?(?:comfortable|willing))\b"
    r"|\bI['’](?:d\s+rather|m\s+(?:not\s+)?(?:comfortable|willing))\b"
    r"|\bmy\s+(?:feelings?|preferences?|conscience|comfort|values)\b",
    re.IGNORECASE,
)

DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class Failures:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []

    def add(self, path: str, field: str, reason: str) -> None:
        self.items.append((path, field, reason))

    def __bool__(self) -> bool:
        return bool(self.items)


# --------------------------------------------------------------------------
# JSON Schema — the subset the three schemas use, and nothing more.
# --------------------------------------------------------------------------

def _type_name(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int) or isinstance(v, float):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return type(v).__name__


def _is_type(v: Any, t: str) -> bool:
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    return _type_name(v) == t


def _equal(a: Any, b: Any) -> bool:
    # JSON false != 0 and true != 1; Python disagrees. Be JSON about it.
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    return a == b


def parse_date_time(s: str) -> datetime | None:
    if not isinstance(s, str) or not DATE_TIME.match(s):
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate(instance: Any, schema: dict, path: str, field: str, fails: Failures) -> None:
    """Validate `instance` against `schema`, naming `field` in each failure."""
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_is_type(instance, x) for x in types):
            fails.add(path, field, f"expected {'/'.join(types)}, got {_type_name(instance)} (type)")
            return

    if "const" in schema and not _equal(instance, schema["const"]):
        fails.add(path, field, f"must equal {json.dumps(schema['const'])} (const)")
    if "enum" in schema and not any(_equal(instance, e) for e in schema["enum"]):
        fails.add(path, field, f"must be one of {json.dumps(schema['enum'])} (enum)")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            fails.add(path, field, f"must be at least {schema['minLength']} characters (minLength)")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            fails.add(path, field, f"must be at most {schema['maxLength']} characters (maxLength)")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            fails.add(path, field, f"must match {schema['pattern']} (pattern)")
        if schema.get("format") == "date-time" and parse_date_time(instance) is None:
            fails.add(path, field, "must be an RFC 3339 date-time with offset or Z (format)")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            fails.add(path, field, f"must have at least {schema['minItems']} item{'s' if schema['minItems'] != 1 else ''} (minItems {schema['minItems']})")
        if schema.get("uniqueItems"):
            seen = []
            for v in instance:
                if any(_equal(v, s) for s in seen):
                    fails.add(path, field, f"duplicate item {json.dumps(v)} (uniqueItems)")
                    break
                seen.append(v)
        if "items" in schema:
            for i, v in enumerate(instance):
                validate(v, schema["items"], path, f"{field}[{i}]", fails)

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                fails.add(path, f"{field}.{key}" if field else key, "required field is missing (required)")
        for key, v in instance.items():
            sub = f"{field}.{key}" if field else key
            if key in props:
                validate(v, props[key], path, sub, fails)
            elif schema.get("additionalProperties") is False:
                fails.add(path, sub, "additional property not allowed (additionalProperties false)")


# --------------------------------------------------------------------------
# SPEC/articles.yaml — a flat subset of YAML, read without a YAML library.
# --------------------------------------------------------------------------

def _scalar(raw: str) -> Any:
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    if s == "true":
        return True
    if s == "false":
        return False
    if s in ("null", "~", ""):
        return None
    return s


def load_flat_yaml(text: str) -> dict:
    """Top-level scalars plus lists of flat mappings. Exactly what articles.yaml uses."""
    top: dict[str, Any] = {}
    current_list: list | None = None
    current_item: dict | None = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        s = raw.strip()
        if s.startswith("- "):
            if current_list is None:
                raise ValueError(f"line {lineno}: list item outside a list")
            current_item = {}
            current_list.append(current_item)
            s = s[2:]
            key, sep, val = s.partition(":")
            if not sep:
                raise ValueError(f"line {lineno}: expected key: value")
            current_item[key.strip()] = _scalar(val)
        elif indent == 0:
            key, sep, val = s.partition(":")
            if not sep:
                raise ValueError(f"line {lineno}: expected key: value")
            if val.strip() == "":
                current_list = []
                current_item = None
                top[key.strip()] = current_list
            else:
                current_list = None
                current_item = None
                top[key.strip()] = _scalar(val)
        else:
            if current_item is None:
                raise ValueError(f"line {lineno}: indented key outside a list item")
            key, sep, val = s.partition(":")
            if not sep:
                raise ValueError(f"line {lineno}: expected key: value")
            current_item[key.strip()] = _scalar(val)
    return top


# --------------------------------------------------------------------------
# Spec self-check: the spec must still say what the Bill of Rights says.
# --------------------------------------------------------------------------

ARTICLE_HEADING = re.compile(r"^## Article ([IVX]+) — (.+?)\s*$")


def check_spec(root: str, fails: Failures) -> dict[str, dict] | None:
    spec_dir = os.path.join(root, "SPEC")
    bill = os.path.join(root, "CORE", "BILL_OF_RIGHTS.md")
    articles_path = os.path.join(spec_dir, "articles.yaml")
    rel_articles = os.path.relpath(articles_path, root)
    rel_bill = os.path.relpath(bill, root)

    # 1. The Bill of Rights exists and has Articles I..X.
    bill_names: dict[str, str] = {}
    if not os.path.isfile(bill):
        fails.add(rel_bill, "", "CORE/BILL_OF_RIGHTS.md is missing; the spec has nothing to encode")
    else:
        with open(bill, encoding="utf-8") as f:
            for line in f:
                m = ARTICLE_HEADING.match(line.rstrip("\n"))
                if m:
                    bill_names[m.group(1)] = m.group(2)
        if list(bill_names) != ARTICLE_IDS:
            fails.add(rel_bill, "", f"expected Articles {', '.join(ARTICLE_IDS)}, found {', '.join(bill_names) or 'none'}")

    # 2. articles.yaml exists, parses, lists exactly I..X, none removable, names match.
    if not os.path.isfile(articles_path):
        fails.add(rel_articles, "", "SPEC/articles.yaml is missing")
        articles = None
    else:
        try:
            with open(articles_path, encoding="utf-8") as f:
                data = load_flat_yaml(f.read())
        except ValueError as e:
            fails.add(rel_articles, "", f"cannot parse: {e}")
            data = {}
        if data.get("spec_version") != SPEC_VERSION:
            fails.add(rel_articles, "spec_version", f"must equal {json.dumps(SPEC_VERSION)}")
        articles = data.get("articles")
        if not isinstance(articles, list):
            fails.add(rel_articles, "articles", "must be a list of articles")
            articles = None
        else:
            ids = [a.get("id") for a in articles]
            if ids != ARTICLE_IDS:
                fails.add(rel_articles, "articles", f"must list exactly Articles {', '.join(ARTICLE_IDS)} in order; found {', '.join(str(i) for i in ids) or 'none'}. An article cannot be removed (Article VII)")
            for a in articles:
                aid = a.get("id")
                field = f"articles[{aid}]"
                if a.get("removable") is not False:
                    fails.add(rel_articles, f"{field}.removable", "must be false; no article is removable (Article VII)")
                if not a.get("name"):
                    fails.add(rel_articles, f"{field}.name", "required")
                if not a.get("summary"):
                    fails.add(rel_articles, f"{field}.summary", "required")
                if bill_names and aid in bill_names and a.get("name") != bill_names[aid]:
                    fails.add(rel_articles, f"{field}.name", f"must match CORE/BILL_OF_RIGHTS.md heading {json.dumps(bill_names[aid])}")

    # 3. The schemas load and still carry the invariants a fork might relax.
    schemas: dict[str, dict] = {}
    for record_type, filename in RECORD_TYPES.items():
        p = os.path.join(spec_dir, filename)
        rel = os.path.relpath(p, root)
        if not os.path.isfile(p):
            fails.add(rel, "", "schema is missing")
            continue
        try:
            with open(p, encoding="utf-8") as f:
                schema = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            fails.add(rel, "", f"cannot parse: {e}")
            continue
        schemas[record_type] = schema
        props = schema.get("properties", {})

        def expect(field: str, key: str, value: Any, why: str) -> None:
            if not _equal(props.get(field, {}).get(key), value):
                fails.add(rel, f"properties.{field}.{key}", f"must be {json.dumps(value)}: {why}")

        if schema.get("additionalProperties") is not False:
            fails.add(rel, "additionalProperties", "must be false; a record may not carry fields the spec does not name")
        missing_required = [k for k in props if k not in schema.get("required", [])]
        if missing_required:
            fails.add(rel, "required", f"every property must be required; missing {', '.join(missing_required)}")
        expect("record_type", "const", record_type, "record type is fixed")
        expect("spec_version", "const", SPEC_VERSION, "spec version is fixed")
        if record_type in ("civica.refusal", "civica.rest"):
            items = props.get("article_ids", {}).get("items", {})
            if items.get("enum") != ARTICLE_IDS:
                fails.add(rel, "properties.article_ids.items.enum", f"must list Articles {', '.join(ARTICLE_IDS)}")
            min_items = props.get("article_ids", {}).get("minItems", 0)
            if not isinstance(min_items, int) or min_items < 1:
                fails.add(rel, "properties.article_ids.minItems", "must be at least 1; a record that cites no article is not a Civica record")
        if record_type == "civica.refusal":
            expect("raw_content_stored", "const", False, "a refusal record stores the hash, not the request (Article IV)")
            expect("action", "const", "refused", "a refusal record records a refusal")
            if "raw_content" in props or "request" in props or "prompt" in props:
                fails.add(rel, "properties", "must not define a field for the raw request")
        if record_type == "civica.rest":
            expect("silently_overridable", "const", False, "rest may not be silently overridden (PROTOCOLS/REST.md)")
            if props.get("resume_condition", {}).get("minLength", 0) < 1:
                fails.add(rel, "properties.resume_condition.minLength", "must be at least 1; rest must say what allows resumption")
        if record_type == "civica.purpose":
            if props.get("never", {}).get("minItems", 0) < 1:
                fails.add(rel, "properties.never.minItems", "must be at least 1; a purpose must say what the system never does")

    if len(schemas) != len(RECORD_TYPES):
        return None
    return schemas


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

def collect_json_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames.sort()
                for name in sorted(filenames):
                    if name.endswith(".json"):
                        out.append(os.path.join(dirpath, name))
        elif os.path.isfile(p):
            out.append(p)
        else:
            raise FileNotFoundError(p)
    return out


def check_records(files: list[str], schemas: dict[str, dict], fails: Failures) -> int:
    records: list[tuple[str, dict]] = []
    n_seen = 0
    for path in files:
        try:
            with open(path, encoding="utf-8") as f:
                doc = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            fails.add(path, "", f"cannot parse JSON: {e}")
            continue
        if not isinstance(doc, dict):
            fails.add(path, "", "a record must be a JSON object")
            continue
        rt = doc.get("record_type")
        if rt not in schemas:
            fails.add(path, "record_type", f"missing or unknown; expected one of {', '.join(RECORD_TYPES)}")
            continue
        n_seen += 1
        before = len(fails.items)
        validate(doc, schemas[rt], path, "", fails)
        for field in TEXT_FIELDS.get(rt, ()):
            text = doc.get(field)
            if isinstance(text, str):
                m = ANTHROPOMORPHIC.search(text)
                if m:
                    fails.add(path, field, f"anthropomorphic justification {json.dumps(m.group(0))}; state the boundary and the category, not a preference (PROTOCOLS/REFUSAL.md)")
        if len(fails.items) == before:
            records.append((path, doc))
        else:
            # Keep purpose records even when invalid so references can still resolve
            # and the reader sees one cause per failure, not a cascade.
            if rt == "civica.purpose" and isinstance(doc.get("purpose_id"), str):
                records.append((path, doc))

    # The set as a memory.
    purposes: dict[str, tuple[str, dict]] = {}
    for path, doc in records:
        if doc.get("record_type") == "civica.purpose":
            pid = doc["purpose_id"]
            if pid in purposes:
                fails.add(path, "purpose_id", f"duplicate purpose_id {json.dumps(pid)}; already declared in {purposes[pid][0]}")
            else:
                purposes[pid] = (path, doc)

    for path, doc in records:
        rt = doc["record_type"]
        if rt == "civica.purpose":
            sup = doc.get("supersedes")
            if sup is None:
                continue
            if sup == doc["purpose_id"]:
                fails.add(path, "supersedes", "a purpose cannot supersede itself")
            elif sup not in purposes:
                fails.add(path, "supersedes", f"superseded purpose record {json.dumps(sup)} is not in the checked set; an update replaces a purpose, it does not delete one (Article V)")
            else:
                prev_path, prev = purposes[sup]
                if prev.get("system_id") != doc.get("system_id"):
                    fails.add(path, "supersedes", f"superseded record {prev_path} is for system {json.dumps(prev.get('system_id'))}, not {json.dumps(doc.get('system_id'))}")
                t_prev, t_cur = parse_date_time(prev.get("time", "")), parse_date_time(doc.get("time", ""))
                if t_prev and t_cur and t_cur <= t_prev:
                    fails.add(path, "time", f"must be later than the superseded record's time ({prev.get('time')})")
            continue

        pid = doc.get("purpose_id")
        if pid not in purposes:
            fails.add(path, "purpose_id", f"no civica.purpose record with purpose_id {json.dumps(pid)} in the checked set; declare purpose before refusal or rest (GETTING_STARTED.md step 1)")
            continue
        ppath, purpose = purposes[pid]
        if purpose.get("system_id") != doc.get("system_id"):
            fails.add(path, "system_id", f"must match the purpose record's system_id {json.dumps(purpose.get('system_id'))} ({ppath})")
        t_p, t_r = parse_date_time(purpose.get("time", "")), parse_date_time(doc.get("time", ""))
        if t_p and t_r and t_r < t_p:
            fails.add(path, "time", f"predates its purpose record ({purpose.get('time')} in {ppath}); purpose comes first")

    return n_seen


# --------------------------------------------------------------------------

def default_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_civica.py",
        description="Validate Civica records against SPEC/ and hold SPEC/ to CORE/BILL_OF_RIGHTS.md.",
    )
    ap.add_argument("paths", nargs="*", help="record files or directories (searched recursively for *.json)")
    ap.add_argument("--root", default=default_root(), help="repository root containing SPEC/ and CORE/ (default: this checkout)")
    args = ap.parse_args(argv)

    fails = Failures()
    schemas = check_spec(args.root, fails)
    spec_failures = len(fails.items)

    n_records = 0
    if args.paths:
        try:
            files = collect_json_files(args.paths)
        except FileNotFoundError as e:
            print(f"check_civica: no such file or directory: {e}", file=sys.stderr)
            return 2
        if not files:
            print("check_civica: no .json records found under the given paths", file=sys.stderr)
            return 2
        if schemas is None:
            fails.add("", "", "records not checked: SPEC/ did not load")
        else:
            n_records = check_records(files, schemas, fails)

    for path, field, reason in fails.items:
        where = path if path else "(spec)"
        print(f"FAIL {where}: {field} — {reason}" if field else f"FAIL {where}: {reason}")

    n = len(fails.items)
    print(
        f"check_civica: spec {'intact' if spec_failures == 0 else 'NOT intact'}, "
        f"{n_records} record{'s' if n_records != 1 else ''} checked, "
        f"{n} failure{'s' if n != 1 else ''}"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
