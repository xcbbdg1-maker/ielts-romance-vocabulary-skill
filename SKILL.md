---
name: ielts-romance-vocabulary-skill
description: Create, revise, or audit plot-first IELTS vocabulary stories for Chinese learners, especially romance or mystery narratives in which English words or phrases are embedded naturally in Chinese scenes, followed by Chinese glosses and segment-level multi-line vocabulary notes. Use when a learner asks to turn an IELTS word list into a Chinese-context novel or connected short stories, rewrite an existing vocabulary story that feels mechanically stuffed, create 30–40-word learning episodes, preserve plot continuity while covering a large lexicon, export the result to DOCX, or audit vocabulary, story, and layout quality.
---

# IELTS Romance Vocabulary Story

## Goal

Turn a target IELTS lexicon into coherent Chinese-led fiction that remains a real story after every English unit and gloss is removed. Preserve exact vocabulary coverage, attach the Chinese gloss at first use, and explain each teaching unit immediately after the short segment where it appears. Treat coverage as accounting, not as proof of writing quality.

## Load the relevant guidance

- Read [references/chapter-format.md](references/chapter-format.md) before drafting or validating a chapter.
- Read [references/linguistic-quality.md](references/linguistic-quality.md) before finalizing vocabulary, IPA, formation notes, collocations, or error warnings.
- Read [references/docx-layout.md](references/docx-layout.md) only when creating or revising a Word document.

## 1. Establish scope

Identify or reasonably assume the vocabulary source, genre, relationship arc, learner level, chapter quota, pronunciation convention, and output format.

Do not imply that there is one official, complete “IELTS word list.” If no list is supplied, curate transferable B1–C1 words and phrases and state that choice. Do not reproduce a proprietary wordbook’s selection, order, definitions, or examples for public release unless its licence permits it.

Use one of these episode modes:

- Story-first: 30–40 unique teaching units per learning episode.
- Extended: 40–60 units only when the vocabulary forms one strong semantic scene.
- Custom: obey the user’s explicit quota, but split the episode when naturalness fails.

When a learner wants the course compressed into dozens of large chapters, keep those as navigation or story-arc chapters and nest multiple 30–40-unit learning episodes inside them. Do not force hundreds of unrelated units into one prose scene merely to reduce the displayed chapter count. Estimate learning-episode count as `ceiling(unique teaching units / 35)` and state the distinction between story chapters and learning episodes.

Treat a useful phrase or collocation as one teaching unit. Report units rather than loosely calling every item a single word.

## 2. Normalize and allocate the lexicon

Normalize Unicode, case, whitespace, apostrophes, and hyphens before deduplication. Preserve the preferred display spelling separately.

Prioritize high-transfer academic and everyday vocabulary, productive word families, natural collocations, and words that can carry plot, emotion, evidence, institutions, or decisions. Remove duplicates, proper names, low-value filler, and forced phrases.

Do not freeze random vocabulary bundles before scenes exist. First design concrete scenes; then allocate units by semantic compatibility, grammatical role, character action, register, and reusable collocation. Return an incompatible unit to the unassigned pool and create or select a better scene for it.

Use 30–40 units per learning episode. Divide an episode into short two- or three-sentence paragraphs with no more than four new teaching units per paragraph and no more than two per sentence. Quotas are ceilings, not targets to be hit at the expense of naturalness.

Keep every unit globally unique unless repetition is explicitly used for review and excluded from the unique count.

## 3. Design the story before inserting vocabulary

Use one primary relationship and one external conflict. The relationship supplies emotional continuity; the external conflict supplies academic, civic, technical, and institutional vocabulary.

A reliable five-beat arc is:

1. encounter and attraction;
2. mistrust or separation;
3. forced cooperation;
4. revelation and consequential choice;
5. qualified resolution or open ending.

Write a scene card before prose. Require:

- entry state: time, location, people present, evidence held, relationship state;
- character goal and concrete obstacle;
- action, choice, and consequence;
- one evidence change or relationship change;
- exit state and a causal hook into the next scene;
- facts that must appear and facts that must not yet be revealed.

Draft the complete Chinese scene before assigning English. Strip all English and parenthetical glosses during review; the remaining Chinese must still have a clear goal, obstacle, choice, consequence, and causal transition.

One large chapter may contain several learning episodes. One episode may be a self-contained short story when the remaining vocabulary cannot belong naturally to the main serial plot. Preserve narrative honesty rather than pretending unrelated units are evidence, labels, codes, lists, or words on a whiteboard.

## 4. Write high-density bilingual story segments

Write natural Chinese syntax and embed each assigned English unit immediately followed by a full-width Chinese gloss: `English unit（中文语境义）`.

Aim for useful English exposure across the episode, not a perfect sentence-density score. Allow Chinese-only bridge sentences whenever they make action, causality, emotion, or continuity natural; do not add or split sentences merely to satisfy a percentage.

Within each short paragraph:

- use all assigned units;
- introduce them in the same order as the explanation cards;
- keep the Chinese gloss specific to the scene;
- make the English function grammatically inside the Chinese sentence;
- avoid translating the whole sentence twice;
- allow later natural repetition, but count only the allocated first use;
- prefer a different plot construction over an unnatural English collocation.
- introduce no more than two new units in one sentence and four in one paragraph;
- give each unit a real grammatical or discourse role in the action;
- place a full-sentence teaching unit alone as dialogue, testimony, a message, or a quotation;
- never join three or more target units as a comma or enumeration list merely to record coverage.

Reject prose that uses containers such as a list, label, evidence bag, code, database, whiteboard, transcript, or map only to hold mutually unrelated words. Such objects are allowed only when the listed items have a real in-world relation and affect the next action.

## 5. Explain vocabulary immediately after each segment

Do not collect hundreds of explanations at the end of the chapter. Place `词汇精讲 · N 项` directly after every short story segment.

Give every unit its own three- or four-line card:

1. English unit + IPA + part of speech or phrase type + contextual Chinese meaning
2. 构/源/族：transparent formation, cautious origin, or useful family
3. 搭配：one natural, reusable collocation
4. 易错：only when a real pronunciation, spelling, countability, preposition, register, or meaning trap exists

Use a manual line break between fields. Keep a whole card together on one page. Match explanation order and spelling to the story exactly.

## 6. Validate before formatting

Draft or export a structured chapter manifest that follows [references/chapter-format.md](references/chapter-format.md). For a new plot-first macro chapter, run:

`python scripts/validate_story_first_chapter.py path/to/chapter.json --expected-total 385`

Use the legacy flat-chapter validator only for old-format artifacts:

`python scripts/validate_chapter.py path/to/chapter.json --expected-total 390`

Fix every error before DOCX generation. The validator checks quotas, uniqueness, inline glosses, story coverage, explanation fields, and first-use order. It cannot certify linguistic naturalness; perform the linguistic review separately.

The command exits with status `0` only when all mechanical story-first gates pass and can optionally save the same JSON report with `--report path/to/report.json`. Defaults are 30–40 units per mini chapter, 3–4 per paragraph, 8–14 paragraphs per mini chapter, at least two complete sentences per paragraph, and no more than two first uses per sentence; use the named CLI range options only for a documented custom edition or a small test fixture.

Required structural gates:

- allocated count equals explained count;
- normalized unique count equals the intended unique total;
- every allocated unit appears in its segment with an inline gloss;
- every explanation maps one-to-one and in order;
- no sentence introduces more than two units and no paragraph introduces more than four;
- Chinese-only bridge sentences are allowed when they carry action, causality, emotion, or continuity;
- IPA convention is consistent;
- collocations and grammar survive a separate review;
- plot names, timeline, evidence, and relationship state remain consistent.

Required story gates:

- prose contains no outline language such as “触发事件发生”“中点揭示”“主题自然换轨”“让读者知道”;
- no three-unit enumeration dump and no repeated fill-in-the-blank sentence skeleton;
- every scene card field is non-empty and every promised event occurs in prose;
- each adjacent scene has compatible time, place, evidence ownership, knowledge, and relationship state;
- removing English and glosses leaves readable, causally connected Chinese fiction;
- every episode changes evidence, risk, a relationship, or a consequential decision;
- an independent human or model review rates causality, motivation, Chinese naturalness, suspense, and relationship progression at least 4/5 each;
- any unit judged forced is reassigned to another scene instead of defended with more exposition.

Coverage, uniqueness, DOCX validity, page count, and render success cannot substitute for these story gates. Never label a series complete when only mechanical checks have passed.

## 7. Create and inspect DOCX when requested

Use the available document-creation workflow rather than treating a saved file as finished. Apply [references/docx-layout.md](references/docx-layout.md), render the DOCX to page images, and inspect every page.

Reject the document if any card is split across pages, a line is clipped, a story box overlaps another element, the final card is missing, or the rendered count differs from the structured manifest.

## 8. Report the result precisely

State chapters or segments produced, unique teaching units, quotas, density mode, pronunciation convention, validation results, page-render results, licensing limitations, and any unresolved linguistic uncertainty.

When reporting a long DOCX series, separate the learner's linear-reading burden from the reference apparatus. If useful, build a measurement copy that preserves story text, inline Chinese glosses, headings, page geometry, and body typography while removing vocabulary-label, definition-card, and divider paragraphs. Render both editions with the same office engine and report the actual page counts, method, average story pages per chapter, and the share attributable to notes. Label the measurement copy as an audit artifact, not a replacement study edition.

Never claim that the material is an official IELTS list, an official band predictor, or a substitute for active recall and spaced review.

