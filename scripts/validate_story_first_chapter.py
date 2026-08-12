#!/usr/bin/env python3
"""Validate story-first IELTS vocabulary macro chapters.

The validator intentionally checks *delivery structure*, not literary merit.  It
prevents the mechanical failure modes that made the old continuation unusable:
term dumps, outline prose, repeated paragraph moulds, over-dense sentences and
untraceable vocabulary coverage.  Plot facts and state transitions are exposed
in the report for a human semantic review instead of being guessed by code.

Expected JSON shape (``story`` may also be named ``body`` or ``text``).  One
macro chapter can contain any number of causally linked mini chapters::

    {
      "expected_total_terms": 385,
      "mini_chapters": [
        {
          "mini_chapter_number": 1,
          "entry_state": "...", "goal": "...", "conflict": "...",
          "choice": "...", "consequence": "...", "exit_state": "...",
          "required_facts": ["..."], "forbidden_facts": ["..."],
          "paragraphs": [
            {
              "event": "...", "emotional_turn": "...",
              "story": "... **evidence**（证据） ...。...。",
              "terms": [
                {"unit_id": "u000001", "term": "evidence", "meaning": "证据"}
              ]
            }
          ]
        }
      ]
    }

Defaults implement the agreed production envelope: 30--40 terms per mini
chapter, 3--4 terms per paragraph, roughly eleven paragraphs (8--14 accepted),
and no more than two first-use annotations in one sentence.  Every limit can be
overridden on the command line for small fixtures or a deliberately different
edition.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


CJK_RE = re.compile(r"[\u3400-\u9fff]")
ANNOTATION_RE = re.compile(
    r"(?P<mark>\*\*|__)(?P<term>[^\r\n]+?)(?P=mark)[ \t]*"
    r"(?:（(?P<gloss_fw>[^（）\r\n]*)）|\((?P<gloss_ascii>[^()\r\n]*)\))"
)
EMPHASIS_RE = re.compile(r"(?:\*\*([^\r\n]+?)\*\*|__([^\r\n]+?)__)")
LEADING_LABEL_RE = re.compile(
    r"^\s*(?:(?:第\s*)?\d+(?:\s*[段节])?\s*[|｜:：.、\-—]\s*)"
)

# These phrases describe an outline or a generation operation rather than an
# event experienced by a character.  Run the check after teaching annotations
# are removed so a legitimate English entry cannot trigger it.
META_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "Chinese outline/generation language",
        re.compile(
            r"(?:本段|这一段|该段|本小节|这一小节|本节|本章|下一段|上一段)"
            r".{0,10}(?:用于|负责|需要|将会|主要|重点|推进|呈现|描写|包含|嵌入|插入|使用)"
        ),
    ),
    (
        "labelled plot metadata",
        re.compile(
            r"(?:剧情推进|情感转折|故事目标|冲突点|词汇清单|单词清单|"
            r"触发事件发生|中点揭示|主题自然换轨|让读者知道|推进主线|"
            r"为(?:下一段|下一节|后文).{0,8}铺垫|"
            r"事件\s*[：:]|目标\s*[：:]|冲突\s*[：:]|选择\s*[：:]|后果\s*[：:]|"
            r"入场状态\s*[：:]|离场状态\s*[：:])"
        ),
    ),
    (
        "term insertion language",
        re.compile(r"(?:以下|上述).{0,8}(?:单词|词汇|词条)|(?:单词|词汇|词条).{0,8}(?:依次|如下|塞入|插入|嵌入)"),
    ),
    (
        "English outline/generation language",
        re.compile(
            r"\b(?:this (?:paragraph|section|chapter)|plot point|story beat|"
            r"vocabulary list|insert (?:the )?(?:terms|words)|outline:)\b",
            flags=re.IGNORECASE,
        ),
    ),
)

REQUIRED_STATE_FIELDS = (
    "entry_state",
    "goal",
    "conflict",
    "choice",
    "consequence",
    "exit_state",
)
REQUIRED_FACT_FIELDS = ("required_facts", "forbidden_facts")
FULL_SENTENCE_TYPES = {
    "full_sentence",
    "full-sentence",
    "sentence",
    "complete_sentence",
    "complete-sentence",
    "完整句",
    "完整句型",
}


@dataclass(frozen=True)
class ValidationConfig:
    min_mini_terms: int = 30
    max_mini_terms: int = 40
    min_paragraphs: int = 8
    max_paragraphs: int = 14
    min_paragraph_terms: int = 3
    max_paragraph_terms: int = 4
    min_sentences: int = 2
    max_terms_per_sentence: int = 2
    max_gloss_chars: int = 24
    expected_total: int | None = None

    def check(self) -> None:
        pairs = (
            ("mini terms", self.min_mini_terms, self.max_mini_terms),
            ("paragraphs", self.min_paragraphs, self.max_paragraphs),
            ("paragraph terms", self.min_paragraph_terms, self.max_paragraph_terms),
        )
        for label, minimum, maximum in pairs:
            if minimum < 0 or maximum < minimum:
                raise ValueError(f"invalid {label} range: {minimum}..{maximum}")
        if self.min_sentences < 1:
            raise ValueError("min_sentences must be at least 1")
        if self.max_terms_per_sentence < 1:
            raise ValueError("max_terms_per_sentence must be at least 1")
        if self.max_gloss_chars < 1:
            raise ValueError("max_gloss_chars must be at least 1")
        if self.expected_total is not None and self.expected_total < 0:
            raise ValueError("expected_total cannot be negative")


@dataclass(frozen=True)
class Annotation:
    start: int
    end: int
    term: str
    gloss: str
    raw: str


@dataclass(frozen=True)
class Sentence:
    start: int
    end: int
    text: str
    terminated: bool


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _compact_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def _canonical_term(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[‐‑‒–—−]", "-", text)
    return re.sub(r"\s+", " ", text).strip().casefold()


def _story_value(paragraph: dict[str, Any]) -> str:
    for field in ("story", "body", "text"):
        value = paragraph.get(field)
        if isinstance(value, str):
            return value
    return ""


def _term_value(term: dict[str, Any]) -> str:
    for field in ("term", "preferred_display", "source_unit"):
        value = term.get(field)
        if _nonempty(value):
            return str(value).strip()
    return ""


def _term_meaning(term: dict[str, Any]) -> str:
    value = term.get("meaning")
    if isinstance(value, list):
        return next((str(item).strip() for item in value if _nonempty(item)), "")
    return str(value).strip() if value is not None else ""


def _is_full_sentence(term: dict[str, Any]) -> bool:
    for field in ("unit_type", "entry_type", "kind"):
        value = _canonical_term(term.get(field))
        if value in FULL_SENTENCE_TYPES:
            return True
    return False


def _annotations(story: str) -> list[Annotation]:
    result: list[Annotation] = []
    for match in ANNOTATION_RE.finditer(story):
        gloss = match.group("gloss_fw")
        if gloss is None:
            gloss = match.group("gloss_ascii") or ""
        result.append(
            Annotation(
                start=match.start(),
                end=match.end(),
                term=match.group("term").strip(),
                gloss=gloss.strip(),
                raw=match.group(0),
            )
        )
    return result


def _sentences(story: str) -> list[Sentence]:
    """Split at sentence punctuation outside emphasis and gloss parentheses."""

    result: list[Sentence] = []
    start = 0
    ascii_depth = 0
    fullwidth_depth = 0
    emphasis_marker: str | None = None
    index = 0
    while index < len(story):
        marker = story[index : index + 2]
        if marker in {"**", "__"}:
            emphasis_marker = None if emphasis_marker == marker else marker
            index += 2
            continue
        character = story[index]
        if emphasis_marker is None:
            if character == "(":
                ascii_depth += 1
            elif character == ")" and ascii_depth:
                ascii_depth -= 1
            elif character == "（":
                fullwidth_depth += 1
            elif character == "）" and fullwidth_depth:
                fullwidth_depth -= 1
            elif character in "。！？!?" and not ascii_depth and not fullwidth_depth:
                end = index + 1
                text = story[start:end]
                if text.strip():
                    result.append(Sentence(start, end, text, True))
                start = end
        index += 1
    if story[start:].strip():
        result.append(Sentence(start, len(story), story[start:], False))
    return result


def _strip_annotations(story: str, replacement: str = "") -> str:
    return ANNOTATION_RE.sub(replacement, story)


def _skeleton(story: str) -> str:
    value = _strip_annotations(story, "<TERM>")
    value = LEADING_LABEL_RE.sub("", value)
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"\d+", "<N>", value)
    return re.sub(r"\s+", "", value).strip()


def _issue(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _sequence_sample(values: Iterable[str], limit: int = 6) -> str:
    items = list(values)
    shown = items[:limit]
    suffix = " …" if len(items) > limit else ""
    return " -> ".join(shown) + suffix


def validate_document(
    document: Any, config: ValidationConfig | None = None
) -> dict[str, Any]:
    """Return a JSON-serialisable validation report without mutating input."""

    config = config or ValidationConfig()
    config.check()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    continuity_review: list[dict[str, Any]] = []
    fact_review: list[dict[str, Any]] = []
    mini_counts: list[dict[str, int]] = []

    if not isinstance(document, dict):
        return {
            "valid": False,
            "config": asdict(config),
            "counts": {"mini_chapters": 0, "paragraphs": 0, "terms": 0},
            "errors": [_issue("schema.root", "$", "root value must be an object")],
            "warnings": [],
            "manual_review": {"continuity": [], "fact_constraints": []},
        }

    mini_chapters = document.get("mini_chapters")
    if not isinstance(mini_chapters, list) or not mini_chapters:
        errors.append(
            _issue(
                "schema.mini_chapters",
                "$.mini_chapters",
                "mini_chapters must be a non-empty list",
            )
        )
        mini_chapters = []

    seen_unit_ids: dict[str, str] = {}
    seen_mini_numbers: dict[str, str] = {}
    seen_skeletons: dict[str, str] = {}
    total_terms = 0
    total_paragraphs = 0

    for mini_index, mini in enumerate(mini_chapters):
        mini_path = f"$.mini_chapters[{mini_index}]"
        if not isinstance(mini, dict):
            errors.append(_issue("schema.mini_chapter", mini_path, "mini chapter must be an object"))
            continue

        mini_number = mini.get("mini_chapter_number", mini.get("number"))
        if mini_number is None or isinstance(mini_number, (dict, list, bool)):
            errors.append(
                _issue(
                    "schema.mini_chapter_number",
                    f"{mini_path}.mini_chapter_number",
                    "mini_chapter_number (or number) is required",
                )
            )
            mini_key = f"index:{mini_index}"
        else:
            mini_key = str(mini_number).strip()
            if not mini_key:
                errors.append(
                    _issue(
                        "schema.mini_chapter_number",
                        f"{mini_path}.mini_chapter_number",
                        "mini chapter number cannot be blank",
                    )
                )
            elif mini_key in seen_mini_numbers:
                errors.append(
                    _issue(
                        "schema.duplicate_mini_chapter_number",
                        f"{mini_path}.mini_chapter_number",
                        f"duplicate mini chapter number; first seen at {seen_mini_numbers[mini_key]}",
                    )
                )
            else:
                seen_mini_numbers[mini_key] = mini_path

        for field in REQUIRED_STATE_FIELDS:
            if not _nonempty(mini.get(field)):
                errors.append(
                    _issue(
                        "plot.required_state",
                        f"{mini_path}.{field}",
                        f"{field} must be a non-empty string",
                    )
                )

        for field in REQUIRED_FACT_FIELDS:
            facts = mini.get(field)
            if not isinstance(facts, list) or not facts or not all(_nonempty(item) for item in facts):
                errors.append(
                    _issue(
                        "plot.required_fact_list",
                        f"{mini_path}.{field}",
                        f"{field} must be a non-empty list of non-empty strings",
                    )
                )

        fact_review.append(
            {
                "mini_chapter_number": mini_number,
                "required_facts": mini.get("required_facts", []),
                "forbidden_facts": mini.get("forbidden_facts", []),
                "status": "manual semantic review required",
            }
        )

        paragraphs = mini.get("paragraphs")
        if not isinstance(paragraphs, list):
            errors.append(
                _issue(
                    "schema.paragraphs",
                    f"{mini_path}.paragraphs",
                    "paragraphs must be a list",
                )
            )
            paragraphs = []
        elif not (config.min_paragraphs <= len(paragraphs) <= config.max_paragraphs):
            errors.append(
                _issue(
                    "density.paragraph_count",
                    f"{mini_path}.paragraphs",
                    f"expected {config.min_paragraphs}..{config.max_paragraphs} paragraphs; got {len(paragraphs)}",
                )
            )

        mini_term_count = 0
        total_paragraphs += len(paragraphs)
        for paragraph_index, paragraph in enumerate(paragraphs):
            paragraph_path = f"{mini_path}.paragraphs[{paragraph_index}]"
            if not isinstance(paragraph, dict):
                errors.append(_issue("schema.paragraph", paragraph_path, "paragraph must be an object"))
                continue

            for field in ("event", "emotional_turn"):
                if not _nonempty(paragraph.get(field)):
                    errors.append(
                        _issue(
                            "plot.required_paragraph_field",
                            f"{paragraph_path}.{field}",
                            f"{field} must be a non-empty string",
                        )
                    )

            story = _story_value(paragraph)
            if not story.strip():
                errors.append(
                    _issue(
                        "schema.story",
                        f"{paragraph_path}.story",
                        "story (or body/text) must be a non-empty string",
                    )
                )

            terms = paragraph.get("terms")
            if not isinstance(terms, list):
                errors.append(
                    _issue("schema.terms", f"{paragraph_path}.terms", "terms must be a list")
                )
                terms = []
            elif not (config.min_paragraph_terms <= len(terms) <= config.max_paragraph_terms):
                errors.append(
                    _issue(
                        "density.paragraph_terms",
                        f"{paragraph_path}.terms",
                        f"expected {config.min_paragraph_terms}..{config.max_paragraph_terms} terms; got {len(terms)}",
                    )
                )

            mini_term_count += len(terms)
            total_terms += len(terms)
            annotations = _annotations(story)

            annotation_starts = {item.start for item in annotations}
            for match in EMPHASIS_RE.finditer(story):
                if match.start() not in annotation_starts:
                    emphasized = (match.group(1) or match.group(2) or "").strip()
                    errors.append(
                        _issue(
                            "gloss.missing_or_malformed",
                            f"{paragraph_path}.story",
                            f"emphasised entry {emphasized!r} needs an immediate parenthesised Chinese gloss",
                        )
                    )

            listed_terms: list[str] = []
            full_sentence_positions: list[int] = []
            for term_index, term in enumerate(terms):
                term_path = f"{paragraph_path}.terms[{term_index}]"
                if not isinstance(term, dict):
                    errors.append(_issue("schema.term", term_path, "term must be an object"))
                    listed_terms.append("")
                    continue
                unit_id = term.get("unit_id")
                if not _nonempty(unit_id):
                    errors.append(
                        _issue("coverage.unit_id_missing", f"{term_path}.unit_id", "unit_id is required")
                    )
                else:
                    unit_key = str(unit_id).strip()
                    if unit_key in seen_unit_ids:
                        errors.append(
                            _issue(
                                "coverage.duplicate_unit_id",
                                f"{term_path}.unit_id",
                                f"unit_id {unit_key!r} already used at {seen_unit_ids[unit_key]}",
                            )
                        )
                    else:
                        seen_unit_ids[unit_key] = term_path

                display = _term_value(term)
                if not display:
                    errors.append(
                        _issue("schema.term_display", term_path, "term/preferred_display/source_unit is required")
                    )
                listed_terms.append(_canonical_term(display))
                if not _term_meaning(term):
                    errors.append(
                        _issue("schema.meaning", f"{term_path}.meaning", "meaning must be non-empty")
                    )
                if _is_full_sentence(term):
                    full_sentence_positions.append(term_index)

            annotated_terms = [_canonical_term(item.term) for item in annotations]
            if annotated_terms != listed_terms:
                errors.append(
                    _issue(
                        "coverage.story_terms_order",
                        f"{paragraph_path}.story",
                        "annotated first uses must match terms one-to-one and in order; "
                        f"story=[{_sequence_sample(annotated_terms)}], "
                        f"terms=[{_sequence_sample(listed_terms)}]",
                    )
                )

            for annotation_index, annotation in enumerate(annotations):
                annotation_path = f"{paragraph_path}.story.annotation[{annotation_index}]"
                if not annotation.gloss:
                    errors.append(_issue("gloss.empty", annotation_path, "inline gloss cannot be empty"))
                else:
                    if not CJK_RE.search(annotation.gloss):
                        errors.append(
                            _issue("gloss.no_chinese", annotation_path, "inline gloss must contain Chinese")
                        )
                    if _compact_length(annotation.gloss) > config.max_gloss_chars:
                        errors.append(
                            _issue(
                                "gloss.too_long",
                                annotation_path,
                                f"inline gloss exceeds {config.max_gloss_chars} non-space characters",
                            )
                        )

            sentence_items = _sentences(story)
            completed_sentences = sum(item.terminated for item in sentence_items)
            if completed_sentences < config.min_sentences:
                errors.append(
                    _issue(
                        "prose.too_few_sentences",
                        f"{paragraph_path}.story",
                        f"paragraph needs at least {config.min_sentences} complete natural sentences; got {completed_sentences}",
                    )
                )
            for sentence_index, sentence in enumerate(sentence_items):
                sentence_annotations = [
                    item for item in annotations if sentence.start <= item.start < sentence.end
                ]
                if len(sentence_annotations) > config.max_terms_per_sentence:
                    errors.append(
                        _issue(
                            "density.sentence_terms",
                            f"{paragraph_path}.story.sentence[{sentence_index}]",
                            f"sentence introduces {len(sentence_annotations)} terms; maximum is {config.max_terms_per_sentence}",
                        )
                    )

            # Explicitly reject the old `term、term、term` dump even when a
            # caller relaxes the per-sentence density limit.
            for first, second, third in zip(annotations, annotations[1:], annotations[2:]):
                separator_one = story[first.end : second.start].strip()
                separator_two = story[second.end : third.start].strip()
                if re.fullmatch(r"[、，,]+", separator_one) and re.fullmatch(
                    r"[、，,]+", separator_two
                ):
                    errors.append(
                        _issue(
                            "prose.term_dump",
                            f"{paragraph_path}.story",
                            "three teaching entries cannot be presented as a punctuation-separated list",
                        )
                    )
                    break

            plain_story = _strip_annotations(story)
            for label, pattern in META_PATTERNS:
                match = pattern.search(plain_story)
                if match:
                    errors.append(
                        _issue(
                            "prose.meta_outline",
                            f"{paragraph_path}.story",
                            f"outline/generation language is not story prose ({label}): {match.group(0)!r}",
                        )
                    )
                    break

            skeleton = _skeleton(story)
            if skeleton:
                if skeleton in seen_skeletons:
                    errors.append(
                        _issue(
                            "prose.duplicate_skeleton",
                            f"{paragraph_path}.story",
                            f"de-term paragraph duplicates the narrative skeleton at {seen_skeletons[skeleton]}",
                        )
                    )
                else:
                    seen_skeletons[skeleton] = f"{paragraph_path}.story"

            # A complete-sentence teaching item is itself the whole sentence;
            # it must not be made a grammatical object inside Chinese prose.
            if annotated_terms == listed_terms:
                for term_index in full_sentence_positions:
                    annotation = annotations[term_index]
                    containing = next(
                        (
                            item
                            for item in sentence_items
                            if item.start <= annotation.start < item.end
                        ),
                        None,
                    )
                    if containing is None:
                        continue
                    peers = [
                        item
                        for item in annotations
                        if containing.start <= item.start < containing.end
                    ]
                    local_start = annotation.start - containing.start
                    local_end = annotation.end - containing.start
                    outside = containing.text[:local_start] + containing.text[local_end:]
                    outside = re.sub(r"[\s。！？!?…“”\"'‘’：:—-]+", "", outside)
                    if len(peers) != 1 or outside:
                        errors.append(
                            _issue(
                                "prose.full_sentence_not_standalone",
                                f"{paragraph_path}.terms[{term_index}]",
                                "a full_sentence entry must occupy a sentence by itself",
                            )
                        )

        if not (config.min_mini_terms <= mini_term_count <= config.max_mini_terms):
            errors.append(
                _issue(
                    "density.mini_terms",
                    mini_path,
                    f"expected {config.min_mini_terms}..{config.max_mini_terms} terms; got {mini_term_count}",
                )
            )
        declared_mini_total = mini.get("expected_terms")
        if declared_mini_total is not None and declared_mini_total != mini_term_count:
            errors.append(
                _issue(
                    "coverage.mini_expected_total",
                    f"{mini_path}.expected_terms",
                    f"declared {declared_mini_total!r}; counted {mini_term_count}",
                )
            )
        mini_counts.append(
            {
                "mini_chapter_number": mini_number,
                "paragraphs": len(paragraphs),
                "terms": mini_term_count,
            }
        )

    for index in range(max(0, len(mini_chapters) - 1)):
        left = mini_chapters[index]
        right = mini_chapters[index + 1]
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        left_exit = left.get("exit_state")
        right_entry = right.get("entry_state")
        pair_path = f"$.mini_chapters[{index}] -> $.mini_chapters[{index + 1}]"
        if not _nonempty(left_exit) or not _nonempty(right_entry):
            errors.append(
                _issue(
                    "continuity.missing_boundary_state",
                    pair_path,
                    "adjacent mini chapters require a non-empty previous exit_state and next entry_state",
                )
            )
        continuity_review.append(
            {
                "from_mini_chapter_number": left.get("mini_chapter_number", left.get("number")),
                "to_mini_chapter_number": right.get("mini_chapter_number", right.get("number")),
                "from_exit_state": left_exit,
                "to_entry_state": right_entry,
                "status": "manual semantic review required",
            }
        )

    declared_expected = document.get("expected_total_terms")
    expected_total = config.expected_total
    if expected_total is None:
        if isinstance(declared_expected, int) and not isinstance(declared_expected, bool):
            expected_total = declared_expected
        else:
            errors.append(
                _issue(
                    "coverage.expected_total_missing",
                    "$.expected_total_terms",
                    "expected_total_terms must be an integer, or pass --expected-total",
                )
            )
    elif declared_expected is not None and declared_expected != expected_total:
        warnings.append(
            _issue(
                "coverage.expected_total_overridden",
                "$.expected_total_terms",
                f"document declares {declared_expected!r}; CLI/config override is {expected_total}",
            )
        )

    if expected_total is not None and total_terms != expected_total:
        errors.append(
            _issue(
                "coverage.total_terms",
                "$.expected_total_terms",
                f"expected {expected_total} terms; counted {total_terms}",
            )
        )

    return {
        "valid": not errors,
        "config": asdict(config),
        "counts": {
            "mini_chapters": len(mini_chapters),
            "paragraphs": total_paragraphs,
            "terms": total_terms,
            "expected_terms": expected_total,
            "per_mini_chapter": mini_counts,
        },
        "errors": errors,
        "warnings": warnings,
        "manual_review": {
            "continuity": continuity_review,
            "fact_constraints": fact_review,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="macro-chapter JSON file")
    parser.add_argument("--report", type=Path, help="optional JSON report output")
    parser.add_argument("--expected-total", type=int)
    parser.add_argument("--min-mini-terms", type=int, default=30)
    parser.add_argument("--max-mini-terms", type=int, default=40)
    parser.add_argument("--min-paragraphs", type=int, default=8)
    parser.add_argument("--max-paragraphs", type=int, default=14)
    parser.add_argument("--min-paragraph-terms", type=int, default=3)
    parser.add_argument("--max-paragraph-terms", type=int, default=4)
    parser.add_argument("--min-sentences", type=int, default=2)
    parser.add_argument("--max-terms-per-sentence", type=int, default=2)
    parser.add_argument("--max-gloss-chars", type=int, default=24)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    config = ValidationConfig(
        min_mini_terms=args.min_mini_terms,
        max_mini_terms=args.max_mini_terms,
        min_paragraphs=args.min_paragraphs,
        max_paragraphs=args.max_paragraphs,
        min_paragraph_terms=args.min_paragraph_terms,
        max_paragraph_terms=args.max_paragraph_terms,
        min_sentences=args.min_sentences,
        max_terms_per_sentence=args.max_terms_per_sentence,
        max_gloss_chars=args.max_gloss_chars,
        expected_total=args.expected_total,
    )
    try:
        config.check()
    except ValueError as exc:
        parser.error(str(exc))

    try:
        document = json.loads(args.input.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        parser.error(f"cannot read {args.input}: {exc}")
    except json.JSONDecodeError as exc:
        parser.error(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )

    report = validate_document(document, config)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    sys.stdout.write(payload)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

