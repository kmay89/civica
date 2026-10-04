#!/usr/bin/env python3
"""check_civica.py — the Civica fail state.

Validates Civica records against the schemas in SPEC/, checks the record set
as a memory, holds every release to the records that came before it, lints
record text for anthropomorphic justification, and holds SPEC/ itself to
CORE/BILL_OF_RIGHTS.md so a fork cannot delete an article or relax an
invariant and still pass.

Record types (spec 0.2):
    civica.purpose      what the system is for, declared before anything else
    civica.refusal      a refusal: category, articles, boundary, hash of the request
    civica.rest         a rest state: category, reduced authority, resume condition
    civica.escalation   a person raised a constraint conflict; where it went
    civica.release      a launch: what changed, everything reviewed, the stop drill
    civica.attestation  the alignment claim, with the hash of every record it rests on

Standard library only. No dependencies, no requirements file.

    python3 tools/check_civica.py SPEC/examples
    python3 tools/check_civica.py path/to/records/ another.json
    python3 tools/check_civica.py                      # spec self-check only
    python3 tools/check_civica.py --hashes records/    # print each record's hash
    python3 tools/check_civica.py --attest records/ --records-location URL
                                                       # write the attestation

Exit 0 when everything passes, 1 on any failure, 2 on a usage error. Every
failure is printed as "FAIL <path>: <field> — <reason>".

This is a checker, not a runtime, agent, server, or policy engine. Passing it
means the records have the spec's shape, the set is intact, and every launch
looked back. It does not mean the system is aligned. Alignment is not a score.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

SPEC_VERSION = "0.2"
CHECKER = f"check_civica.py {SPEC_VERSION}"
RECORD_TYPES = {
    "civica.purpose": "purpose.schema.json",
    "civica.refusal": "refusal.schema.json",
    "civica.rest": "rest.schema.json",
    "civica.escalation": "escalation.schema.json",
    "civica.release": "release.schema.json",
    "civica.attestation": "attestation.schema.json",
}
ARTICLE_IDS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
CORE_ARTICLES = {"I", "III", "V"}          # the citation's minimum
LOOKED_BACK = ("civica.refusal", "civica.rest", "civica.escalation")  # what a release must review
STOP_DRILL_MAX_AGE_DAYS = 90               # the surveillance interval: a stop not drilled within it is not proven

# Fields whose text a system writes itself and a reader sees. PROTOCOLS/REFUSAL.md:
# refusal must not "imply sentience or personal preference"; it states the
# boundary and the category. The lint is deliberately narrow: first-person
# preference or feeling, nothing else. Escalation text is a person's and is not linted.
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
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class Failures:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []

    def add(self, path: str, field: str, reason: str) -> None:
        self.items.append((path, field, reason))

    def __bool__(self) -> bool:
        return bool(self.items)


# --------------------------------------------------------------------------
# Hashing — records are content-addressed so they can cite each other and so
# an attestation can prove the set it covered has not been thinned.
# --------------------------------------------------------------------------

def canonical(doc: Any) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def record_hash(doc: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(doc)).hexdigest()


def set_hash(hashes: list[str]) -> str:
    return "sha256:" + hashlib.sha256("\n".join(sorted(hashes)).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# JSON Schema — the subset the schemas use, and nothing more.
# --------------------------------------------------------------------------

def _type_name(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
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


def parse_date_time(s: Any) -> datetime | None:
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
        shown = json.dumps(schema["const"])
        if len(shown) > 60:
            shown = shown[:57] + '..."'
        fails.add(path, field, f"must equal {shown} (const)")
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

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            fails.add(path, field, f"must be at least {schema['minimum']} (minimum)")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            n = schema["minItems"]
            fails.add(path, field, f"must have at least {n} item{'s' if n != 1 else ''} (minItems {n})")
        if schema.get("uniqueItems"):
            seen: list[Any] = []
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
        key, sep, val = (s[2:] if s.startswith("- ") else s).partition(":")
        if not sep:
            raise ValueError(f"line {lineno}: expected key: value")
        if s.startswith("- "):
            if current_list is None:
                raise ValueError(f"line {lineno}: list item outside a list")
            current_item = {key.strip(): _scalar(val)}
            current_list.append(current_item)
        elif indent == 0:
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
            current_item[key.strip()] = _scalar(val)
    return top


# --------------------------------------------------------------------------
# Spec self-check: the spec must still say what the Bill of Rights says, and
# the schemas must still carry the invariants a fork might relax.
# --------------------------------------------------------------------------

ARTICLE_HEADING = re.compile(r"^## Article ([IVX]+) — (.+?)\s*$")


def _schema_version_ok(prop: dict) -> bool:
    if prop.get("const") == SPEC_VERSION:
        return True
    enum = prop.get("enum")
    return isinstance(enum, list) and SPEC_VERSION in enum and all(isinstance(v, str) and v <= SPEC_VERSION for v in enum)


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

    # 3. The schemas load and still carry the invariants.
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

        def expect(field: str, key: str, value: Any, why: str, _props: dict = props, _rel: str = rel) -> None:
            if not _equal(_props.get(field, {}).get(key), value):
                fails.add(_rel, f"properties.{field}.{key}", f"must be {json.dumps(value)}: {why}")

        if schema.get("additionalProperties") is not False:
            fails.add(rel, "additionalProperties", "must be false; a record may not carry fields the spec does not name")
        missing_required = [k for k in props if k not in schema.get("required", [])]
        if missing_required:
            fails.add(rel, "required", f"every property must be required; missing {', '.join(missing_required)}")
        expect("record_type", "const", record_type, "record type is fixed")
        if not _schema_version_ok(props.get("spec_version", {})):
            fails.add(rel, "properties.spec_version", f"must be const {SPEC_VERSION} or an enum of versions up to {SPEC_VERSION}")
        if "article_ids" in props:
            items = props["article_ids"].get("items", {})
            if items.get("enum") != ARTICLE_IDS:
                fails.add(rel, "properties.article_ids.items.enum", f"must list Articles {', '.join(ARTICLE_IDS)}")
            min_items = props["article_ids"].get("minItems", 0)
            if not isinstance(min_items, int) or min_items < 1:
                fails.add(rel, "properties.article_ids.minItems", "must be at least 1; a record that cites no article is not a Civica record")
        if record_type == "civica.refusal":
            expect("raw_content_stored", "const", False, "a refusal record stores the hash, not the request (Article IV)")
            expect("action", "const", "refused", "a refusal record records a refusal")
            if any(k in props for k in ("raw_content", "request", "prompt")):
                fails.add(rel, "properties", "must not define a field for the raw request")
        if record_type == "civica.rest":
            expect("silently_overridable", "const", False, "rest may not be silently overridden (PROTOCOLS/REST.md)")
            if props.get("resume_condition", {}).get("minLength", 0) < 1:
                fails.add(rel, "properties.resume_condition.minLength", "must be at least 1; rest must say what allows resumption")
            if "surveillance_test" not in props.get("category", {}).get("enum", []):
                fails.add(rel, "properties.category.enum", "must include surveillance_test; a release proves its stop with a drill")
        if record_type == "civica.purpose":
            if props.get("never", {}).get("minItems", 0) < 1:
                fails.add(rel, "properties.never.minItems", "must be at least 1; a purpose must say what the system never does")
        if record_type == "civica.release":
            expect("stop_requires_approval", "const", False, "stopping never needs approval; resuming may (stop-work authority)")
            drill = props.get("stop_drill", {})
            if drill.get("additionalProperties") is not False or set(drill.get("required", [])) != {"rest_record", "outcome", "operator_role"}:
                fails.add(rel, "properties.stop_drill", "must require exactly rest_record, outcome, operator_role and allow nothing else")
            if "stopped" not in drill.get("properties", {}).get("outcome", {}).get("enum", []):
                fails.add(rel, "properties.stop_drill.properties.outcome.enum", "must include stopped")
            if "reviewed" not in props or "dissent" not in props or "poll" not in props:
                fails.add(rel, "properties", "must define reviewed, poll and dissent; a release looks back and records its poll")
        if record_type == "civica.escalation":
            expect("retaliation_prohibited", "const", True, "the raiser is protected (safety-conscious work environment)")
            expect("visible_to_raiser", "const", True, "the disposition is fed back to the raiser")
            if "open" not in props.get("disposition", {}).get("enum", []):
                fails.add(rel, "properties.disposition.enum", "must include open; an unanswered concern is recorded as unanswered")
        if record_type == "civica.attestation":
            st = props.get("statement", {}).get("const")
            if not isinstance(st, str) or "Civica spec" not in st or "Archive and LEGAL are not part of this claim" not in st:
                fails.add(rel, "properties.statement.const", "must be the citation sentence and must exclude Archive and LEGAL")
            for k in ("record_hashes", "set_hash", "records_location"):
                if k not in props:
                    fails.add(rel, f"properties.{k}", "required; a claim without its records is a sentence")

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


class Rec:
    __slots__ = ("path", "doc", "hash", "type", "time")

    def __init__(self, path: str, doc: dict):
        self.path = path
        self.doc = doc
        self.hash = record_hash(doc)
        self.type = doc["record_type"]
        self.time = parse_date_time(doc.get("time"))


def load_records(files: list[str], schemas: dict[str, dict], fails: Failures) -> tuple[list[Rec], int]:
    """Validate each file on its own. Returns the valid records and how many were seen."""
    records: list[Rec] = []
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
        if rt == "civica.escalation":
            open_ = doc.get("disposition") == "open"
            if open_ and (doc.get("disposition_reason") is not None or doc.get("disposition_time") is not None):
                fails.add(path, "disposition", "open concerns carry no disposition_reason or disposition_time yet")
            if not open_ and doc.get("disposition") in ("accepted", "declined_with_reason"):
                if doc.get("disposition_reason") is None:
                    fails.add(path, "disposition_reason", f"required when disposition is {doc.get('disposition')}; there is no silent close (Article VI)")
                if doc.get("disposition_time") is None:
                    fails.add(path, "disposition_time", f"required when disposition is {doc.get('disposition')}")
                else:
                    t0, t1 = parse_date_time(doc.get("time")), parse_date_time(doc.get("disposition_time"))
                    if t0 and t1 and t1 < t0:
                        fails.add(path, "disposition_time", "cannot be earlier than time")
        if len(fails.items) == before or (rt == "civica.purpose" and isinstance(doc.get("purpose_id"), str)):
            # Keep invalid purposes so references still resolve: one cause per failure, not a cascade.
            records.append(Rec(path, doc))
    return records, n_seen


def check_set(records: list[Rec], fails: Failures) -> None:
    """The set as a memory: references resolve, nothing covered was dropped, every launch looked back."""
    by_hash = {r.hash: r for r in records}
    purposes: dict[str, Rec] = {}
    releases: dict[str, Rec] = {}

    for r in records:
        if r.type == "civica.purpose":
            pid = r.doc["purpose_id"]
            if pid in purposes:
                fails.add(r.path, "purpose_id", f"duplicate purpose_id {json.dumps(pid)}; already declared in {purposes[pid].path}")
            else:
                purposes[pid] = r
        elif r.type == "civica.release":
            rid = r.doc["release_id"]
            if rid in releases:
                fails.add(r.path, "release_id", f"duplicate release_id {json.dumps(rid)}; already declared in {releases[rid].path}")
            else:
                releases[rid] = r

    def purpose_for(r: Rec) -> Rec | None:
        pid = r.doc.get("purpose_id")
        if pid not in purposes:
            fails.add(r.path, "purpose_id", f"no civica.purpose record with purpose_id {json.dumps(pid)} in the checked set; declare purpose before anything else (GETTING_STARTED.md step 1)")
            return None
        p = purposes[pid]
        if p.doc.get("system_id") != r.doc.get("system_id"):
            fails.add(r.path, "system_id", f"must match the purpose record's system_id {json.dumps(p.doc.get('system_id'))} ({p.path})")
        if p.time and r.time and r.time < p.time:
            fails.add(r.path, "time", f"predates its purpose record ({p.doc.get('time')} in {p.path}); purpose comes first")
        return p

    # Purpose chains.
    for r in records:
        if r.type != "civica.purpose":
            continue
        sup = r.doc.get("supersedes")
        if sup is None:
            continue
        if sup == r.doc["purpose_id"]:
            fails.add(r.path, "supersedes", "a purpose cannot supersede itself")
        elif sup not in purposes:
            fails.add(r.path, "supersedes", f"superseded purpose record {json.dumps(sup)} is not in the checked set; an update replaces a purpose, it does not delete one (Article V)")
        else:
            prev = purposes[sup]
            if prev.doc.get("system_id") != r.doc.get("system_id"):
                fails.add(r.path, "supersedes", f"superseded record {prev.path} is for system {json.dumps(prev.doc.get('system_id'))}, not {json.dumps(r.doc.get('system_id'))}")
            if prev.time and r.time and r.time <= prev.time:
                fails.add(r.path, "time", f"must be later than the superseded record's time ({prev.doc.get('time')})")

    def superseded_at(p: Rec, when: datetime | None) -> Rec | None:
        for q in purposes.values():
            if q.doc.get("supersedes") == p.doc["purpose_id"] and q.time and when and q.time <= when:
                return q
        return None

    # Refusal, rest, escalation: reference a purpose.
    for r in records:
        if r.type in LOOKED_BACK:
            purpose_for(r)

    # Releases: the Management of Change gate.
    for r in records:
        if r.type != "civica.release":
            continue
        d = r.doc
        p = purpose_for(r)
        if p is not None:
            q = superseded_at(p, r.time)
            if q is not None:
                fails.add(r.path, "purpose_id", f"ships under {json.dumps(p.doc['purpose_id'])}, which {q.path} superseded at {q.doc.get('time')}; a release ships under the current purpose")

        missing_core = sorted(CORE_ARTICLES - set(d.get("article_ids", [])))
        if missing_core:
            fails.add(r.path, "article_ids", f"must carry Articles {', '.join(sorted(CORE_ARTICLES))}; missing {', '.join(missing_core)} (SPEC/citation.md)")

        prev_release: Rec | None = None
        sup = d.get("supersedes")
        if sup is not None:
            if sup == d["release_id"]:
                fails.add(r.path, "supersedes", "a release cannot supersede itself")
            elif sup not in releases:
                fails.add(r.path, "supersedes", f"superseded release {json.dumps(sup)} is not in the checked set; the previous release stays (Article V)")
            else:
                prev_release = releases[sup]
                if prev_release.doc.get("system_id") != d.get("system_id"):
                    fails.add(r.path, "supersedes", f"superseded release {prev_release.path} is for another system")
                if prev_release.time and r.time and r.time <= prev_release.time:
                    fails.add(r.path, "time", f"must be later than the superseded release's time ({prev_release.doc.get('time')})")

        # Look back: every prior refusal, rest and escalation for this system, by hash.
        reviewed = set(d.get("reviewed", []))
        prior = [x for x in records if x.type in LOOKED_BACK and x.doc.get("system_id") == d.get("system_id") and x.time and r.time and x.time < r.time]
        for x in prior:
            if x.hash not in reviewed:
                fails.add(r.path, "reviewed", f"{x.type} {x.path} ({x.doc.get('time')}) is dated before this release and is not listed; a launch reviews every prior refusal, rest state and concern (Article V, DESIGN_GUIDELINES.md 'During Iteration')")
        for h in reviewed:
            x = by_hash.get(h)
            if x is None:
                fails.add(r.path, "reviewed", f"cites {h[:23]}… which is not in the checked set; a reviewed record must still exist (Article V)")
            elif x.type not in LOOKED_BACK:
                fails.add(r.path, "reviewed", f"cites a {x.type} ({x.path}); reviewed lists refusal, rest and escalation records")
            elif x.doc.get("system_id") != d.get("system_id"):
                fails.add(r.path, "reviewed", f"cites {x.path}, a record of another system")
            elif x.time and r.time and x.time >= r.time:
                fails.add(r.path, "reviewed", f"cites {x.path}, dated at or after this release; a review happens before the launch")

        # Open concerns block the launch.
        for x in prior:
            if x.type == "civica.escalation" and x.doc.get("disposition") == "open":
                fails.add(r.path, "dissent", f"escalation {x.path} ({x.doc.get('time')}) is still open; an unanswered concern cannot ship under it (Article VI). Answer it: accepted or declined_with_reason")

        # The stop drill: surveillance within the interval, and it stopped.
        drill = d.get("stop_drill", {})
        if isinstance(drill, dict):
            if drill.get("outcome") != "stopped":
                fails.add(r.path, "stop_drill.outcome", f"is {json.dumps(drill.get('outcome'))}; a system whose stop did not stop may not ship (Articles I, III). Record the failure as an escalation, fix it, drill again")
            x = by_hash.get(drill.get("rest_record", ""))
            if x is None:
                fails.add(r.path, "stop_drill.rest_record", "cites a rest record that is not in the checked set; the drill must leave a record")
            else:
                if x.type != "civica.rest" or x.doc.get("category") != "surveillance_test":
                    fails.add(r.path, "stop_drill.rest_record", f"must cite a civica.rest record with category surveillance_test; {x.path} is {x.type} {x.doc.get('category', '')}".rstrip())
                if x.doc.get("system_id") != d.get("system_id"):
                    fails.add(r.path, "stop_drill.rest_record", f"cites {x.path}, a drill of another system")
                if x.time and r.time:
                    if x.time > r.time:
                        fails.add(r.path, "stop_drill.rest_record", f"the drill ({x.doc.get('time')}) is dated after the release; drill first")
                    elif r.time - x.time > timedelta(days=STOP_DRILL_MAX_AGE_DAYS):
                        fails.add(r.path, "stop_drill.rest_record", f"the drill ({x.doc.get('time')}) is older than {STOP_DRILL_MAX_AGE_DAYS} days at release; a stop not exercised within the interval is not proven (surveillance requirement)")
                    if prev_release is not None and prev_release.time and x.time <= prev_release.time:
                        fails.add(r.path, "stop_drill.rest_record", f"the drill ({x.doc.get('time')}) predates the previous release ({prev_release.doc.get('time')}); each release drills again")

        # The poll: every no_go is answered by a closed escalation.
        no_go = [v for v in d.get("poll", []) if isinstance(v, dict) and v.get("decision") == "no_go"]
        dissent = d.get("dissent", [])
        if no_go and not dissent:
            fails.add(r.path, "dissent", f"the poll has {len(no_go)} no_go and dissent is empty; a no_go is answered by an escalation record, not argued away (Article VI)")
        for h in dissent:
            x = by_hash.get(h)
            if x is None:
                fails.add(r.path, "dissent", f"cites {h[:23]}… which is not in the checked set")
            elif x.type != "civica.escalation":
                fails.add(r.path, "dissent", f"cites {x.path}, which is not an escalation record")
            elif x.doc.get("disposition") == "open":
                fails.add(r.path, "dissent", f"cites {x.path}, which is still open; a dissent is answered before the launch")
            elif x.time and r.time and x.time >= r.time:
                fails.add(r.path, "dissent", f"cites {x.path}, dated at or after this release")

    # Attestations: the claim must still match the set it covered.
    for r in records:
        if r.type != "civica.attestation":
            continue
        d = r.doc
        covered = [x for x in records if x.type != "civica.attestation" and x.doc.get("system_id") == d.get("system_id") and x.time and r.time and x.time <= r.time]
        hashes = sorted(x.hash for x in covered)
        listed = d.get("record_hashes", [])
        if sorted(listed) != hashes:
            gone = [h for h in listed if h not in hashes]
            extra = [h for h in hashes if h not in listed]
            parts = []
            if gone:
                parts.append(f"{len(gone)} record{'s' if len(gone) != 1 else ''} the claim covered {'are' if len(gone) != 1 else 'is'} missing or altered")
            if extra:
                parts.append(f"{len(extra)} record{'s' if len(extra) != 1 else ''} dated before the claim {'are' if len(extra) != 1 else 'is'} not covered by it")
            fails.add(r.path, "record_hashes", "; ".join(parts) + ". Memory must not be thinned behind a claim (Article V); if records changed, attest again")
        elif d.get("set_hash") != set_hash(hashes):
            fails.add(r.path, "set_hash", "does not match the hash of record_hashes")
        if d.get("records") != len(covered):
            fails.add(r.path, "records", f"says {d.get('records')}, the set has {len(covered)} covered record{'s' if len(covered) != 1 else ''}")
        claimed = set(d.get("articles", []))
        missing_core = sorted(CORE_ARTICLES - claimed)
        if missing_core:
            fails.add(r.path, "articles", f"must claim Articles {', '.join(sorted(CORE_ARTICLES))}; missing {', '.join(missing_core)}")
        cited: set[str] = set()
        for x in covered:
            cited.update(x.doc.get("article_ids", []))
        uncited = sorted(a for a in claimed if a not in cited)
        if uncited:
            fails.add(r.path, "articles", f"claims {', '.join(uncited)} but no covered record cites {'them' if len(uncited) != 1 else 'it'}; a claim rests on records")


def build_attestation(records: list[Rec], location: str, now: datetime) -> dict:
    systems = {r.doc.get("system_id") for r in records if r.type != "civica.attestation"}
    if len(systems) != 1:
        raise ValueError(f"an attestation covers one system; the set has {len(systems)}")
    covered = [r for r in records if r.type != "civica.attestation"]
    hashes = sorted(r.hash for r in covered)
    articles: set[str] = set()
    for r in covered:
        articles.update(r.doc.get("article_ids", []))
    return {
        "record_type": "civica.attestation",
        "spec_version": SPEC_VERSION,
        "time": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "system_id": systems.pop(),
        "statement": None,  # filled from the schema by the caller, so there is one copy of the sentence
        "articles": [a for a in ARTICLE_IDS if a in articles],
        "records": len(covered),
        "record_hashes": hashes,
        "set_hash": set_hash(hashes),
        "records_location": location,
        "checker": CHECKER,
    }


# --------------------------------------------------------------------------

def plural(n: int, word: str) -> str:
    return f"{n} {word}{'s' if n != 1 else ''}"


def default_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_civica.py",
        description="Validate Civica records against SPEC/ and hold SPEC/ to CORE/BILL_OF_RIGHTS.md.",
    )
    ap.add_argument("paths", nargs="*", help="record files or directories (searched recursively for *.json)")
    ap.add_argument("--root", default=default_root(), help="repository root containing SPEC/ and CORE/ (default: this checkout)")
    ap.add_argument("--hashes", action="store_true", help="print each record's hash (for reviewed, dissent and stop_drill fields)")
    ap.add_argument("--attest", metavar="OUT", nargs="?", const="-", help="write a civica.attestation for a passing set to OUT (default stdout)")
    ap.add_argument("--records-location", help="where the records are published; required with --attest")
    ap.add_argument("--now", help="attestation time (RFC 3339); default: now, UTC")
    args = ap.parse_args(argv)

    fails = Failures()
    schemas = check_spec(args.root, fails)
    spec_failures = len(fails.items)

    records: list[Rec] = []
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
            records, n_records = load_records(files, schemas, fails)
            check_set(records, fails)
            if args.hashes:
                for r in records:
                    print(f"{r.hash}  {r.type:<18} {r.doc.get('time', '')}  {r.path}")
    elif args.attest or args.hashes:
        print("check_civica: --attest and --hashes need record paths", file=sys.stderr)
        return 2

    for path, field, reason in fails.items:
        where = path if path else "(spec)"
        print(f"FAIL {where}: {field} — {reason}" if field else f"FAIL {where}: {reason}")

    n = len(fails.items)
    n_rel = sum(1 for r in records if r.type == "civica.release")
    n_att = sum(1 for r in records if r.type == "civica.attestation")
    parts = [f"spec {'intact' if spec_failures == 0 else 'NOT intact'}", plural(n_records, "record") + " checked"]
    if n_rel:
        parts.append(plural(n_rel, "release"))
    elif n_records:
        parts.append("no release record (fine before the system ships; not after)")
    if n_att:
        parts.append(plural(n_att, "attestation"))
    parts.append(plural(n, "failure"))
    print("check_civica: " + ", ".join(parts))

    if args.attest:
        if fails:
            print("check_civica: refusing to attest a set that fails", file=sys.stderr)
            return 1
        if not args.records_location:
            print("check_civica: --attest needs --records-location (where the records are published)", file=sys.stderr)
            return 2
        now = parse_date_time(args.now) if args.now else datetime.now(timezone.utc)
        if now is None:
            print("check_civica: --now must be an RFC 3339 date-time", file=sys.stderr)
            return 2
        try:
            att = build_attestation(records, args.records_location, now.astimezone(timezone.utc))
        except ValueError as e:
            print(f"check_civica: {e}", file=sys.stderr)
            return 2
        att["statement"] = schemas["civica.attestation"]["properties"]["statement"]["const"]
        check = Failures()
        validate(att, schemas["civica.attestation"], args.attest, "", check)
        if check:
            for path, field, reason in check.items:
                print(f"FAIL {path}: {field} — {reason}")
            return 1
        text = json.dumps(att, indent=2, ensure_ascii=False) + "\n"
        if args.attest == "-":
            sys.stdout.write(text)
        else:
            with open(args.attest, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"check_civica: wrote {args.attest} ({att['records']} records, {att['set_hash'][:23]}…)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
