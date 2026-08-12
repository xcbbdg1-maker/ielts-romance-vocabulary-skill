#!/usr/bin/env python3
"""Validate a structured IELTS bilingual-story chapter manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REQUIRED_TERM_FIELDS = (
    "term",
    "ipa",
    "pos",
    "meaning",
    "formation",
    "collocation",
)
HYPHEN_TRANSLATION = str.maketrans(
    {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
    }
)


def canonical(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).translate(HYPHEN_TRANSLATION)
    value = re.sub(r"\s*-\s*", "-", value)
    return re.sub(r"\s+", " ", value).strip().casefold()


def story_for_matching(value: str) -> str:
    return canonical(value.replace("**", "").replace("__", ""))


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


@dataclass
class Audit:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    segment_count: int = 0
    term_count: int = 0
    unique_count: int = 0

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError("the manifest root must be a JSON object")
    return data


def validate_manifest(
    data: dict[str, Any],
    *,
    min_terms: int,
    max_terms: int,
    expected_total: int | None,
    allow_bridge_sentences: bool,
) -> Audit:
    audit = Audit()

    if not nonempty_string(data.get("chapter_title")):
        audit.error("chapter_title must be a non-empty string")

    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        audit.error("segments must be a non-empty list")
        return audit

    audit.segment_count = len(segments)
    global_terms: dict[str, str] = {}

    for expected_number, segment in enumerate(segments, start=1):
        prefix = f"segment {expected_number}"
        if not isinstance(segment, dict):
            audit.error(f"{prefix}: must be an object")
            continue

        if segment.get("number") != expected_number:
            audit.error(
                f"{prefix}: number must be {expected_number}, "
                f"found {segment.get('number')!r}"
            )

        story = segment.get("story")
        if not nonempty_string(story):
            audit.error(f"{prefix}: story must be a non-empty string")
            continue

        terms = segment.get("terms")
        if not isinstance(terms, list):
            audit.error(f"{prefix}: terms must be a list")
            continue

        term_total = len(terms)
        audit.term_count += term_total
        if not min_terms <= term_total <= max_terms:
            audit.error(
                f"{prefix}: expected {min_terms}-{max_terms} terms, "
                f"found {term_total}"
            )

        matchable_story = story_for_matching(story)
        positions: list[int] = []
        segment_keys: list[str] = []

        for term_index, item in enumerate(terms, start=1):
            item_prefix = f"{prefix}, term {term_index}"
            if not isinstance(item, dict):
                audit.error(f"{item_prefix}: must be an object")
                continue

            for field_name in REQUIRED_TERM_FIELDS:
                if not nonempty_string(item.get(field_name)):
                    audit.error(f"{item_prefix}: {field_name} must be non-empty")

            term = item.get("term")
            if not nonempty_string(term):
                continue

            term_key = canonical(term)
            segment_keys.append(term_key)
            if term_key in global_terms:
                audit.error(
                    f"{item_prefix}: duplicate teaching unit {term!r}; "
                    f"first seen as {global_terms[term_key]!r}"
                )
            else:
                global_terms[term_key] = term

            position = matchable_story.find(term_key)
            if position < 0:
                audit.error(f"{item_prefix}: {term!r} is missing from the story")
                continue
            positions.append(position)

            tail = matchable_story[
                position + len(term_key) : position + len(term_key) + 64
            ]
            if not re.match(r"^\s*\([^)\n]{1,50}\)", tail):
                audit.error(
                    f"{item_prefix}: {term!r} is not immediately followed "
                    "by a Chinese gloss"
                )

            ipa = item.get("ipa")
            if nonempty_string(ipa):
                stripped = ipa.strip()
                if not (
                    (stripped.startswith("/") and stripped.endswith("/"))
                    or (stripped.startswith("[") and stripped.endswith("]"))
                ):
                    audit.warn(
                        f"{item_prefix}: IPA is not slash- or bracket-delimited"
                    )

        if positions != sorted(positions):
            audit.error(
                f"{prefix}: explanation terms are not in first-use story order"
            )

        sentences = [
            part.strip()
            for part in re.split(r"[。！？!?；;]+", story)
            if part.strip()
        ]
        uncovered = []
        for sentence_index, sentence in enumerate(sentences, start=1):
            sentence_key = story_for_matching(sentence)
            if not any(term_key in sentence_key for term_key in segment_keys):
                uncovered.append(sentence_index)
        if uncovered:
            message = (
                f"{prefix}: sentences without an assigned teaching unit: "
                + ", ".join(map(str, uncovered))
            )
            if allow_bridge_sentences:
                audit.warn(message)
            else:
                audit.error(message)

    audit.unique_count = len(global_terms)
    if expected_total is not None and audit.term_count != expected_total:
        audit.error(
            f"expected {expected_total} total terms, found {audit.term_count}"
        )
    if audit.unique_count != audit.term_count:
        audit.error(
            f"unique total {audit.unique_count} does not equal allocated total "
            f"{audit.term_count}"
        )
    return audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate quotas, uniqueness, inline glosses, explanation fields, "
            "sentence density, and first-use order in a chapter JSON manifest."
        )
    )
    parser.add_argument("manifest", type=Path, help="UTF-8 chapter JSON file")
    parser.add_argument("--min-terms-per-segment", type=int, default=6)
    parser.add_argument("--max-terms-per-segment", type=int, default=7)
    parser.add_argument("--expected-total", type=int)
    parser.add_argument(
        "--allow-bridge-sentences",
        action="store_true",
        help="report Chinese-only bridge sentences as warnings instead of errors",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable audit result",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.min_terms_per_segment < 1:
        print("error: --min-terms-per-segment must be positive", file=sys.stderr)
        return 2
    if args.max_terms_per_segment < args.min_terms_per_segment:
        print(
            "error: --max-terms-per-segment must be >= --min-terms-per-segment",
            file=sys.stderr,
        )
        return 2

    try:
        data = load_manifest(args.manifest)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    audit = validate_manifest(
        data,
        min_terms=args.min_terms_per_segment,
        max_terms=args.max_terms_per_segment,
        expected_total=args.expected_total,
        allow_bridge_sentences=args.allow_bridge_sentences,
    )

    result = {
        "manifest": str(args.manifest),
        "segments": audit.segment_count,
        "terms": audit.term_count,
        "unique_terms": audit.unique_count,
        "errors": audit.errors,
        "warnings": audit.warnings,
        "status": "pass" if not audit.errors else "fail",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"segments={audit.segment_count} "
            f"terms={audit.term_count} "
            f"unique_terms={audit.unique_count}"
        )
        for warning in audit.warnings:
            print(f"WARNING: {warning}")
        for error in audit.errors:
            print(f"ERROR: {error}")
        print(f"VALIDATION={result['status'].upper()}")
    return 0 if not audit.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
