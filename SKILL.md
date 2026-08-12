---
name: ielts-romance-vocabulary-skill
description: Create or revise high-density IELTS vocabulary stories for Chinese learners, especially romance or mystery narratives in which nearly every Chinese sentence embeds target English words or phrases followed by Chinese glosses, and every short segment is followed by multi-line vocabulary notes covering IPA, contextual meaning, word formation or family, collocation, and optional error warnings. Use when a learner asks to turn an IELTS word list or wordbook into a Chinese-context novel, compress thousands of vocabulary items into dozens of chapters, generate a sample chapter, increase English density, add segment-level explanations, export the result to DOCX, or audit coverage and layout.
---

# IELTS Romance Vocabulary Story

## Goal

Turn a target IELTS lexicon into a coherent Chinese-led story that maximizes useful English exposure without becoming an unreadable word dump. Preserve exact vocabulary coverage, attach the Chinese gloss at first use, and explain each teaching unit immediately after the short segment where it appears.

## Load the relevant guidance

- Read [references/chapter-format.md](references/chapter-format.md) before drafting or validating a chapter.
- Read [references/linguistic-quality.md](references/linguistic-quality.md) before finalizing vocabulary, IPA, formation notes, collocations, or error warnings.
- Read [references/docx-layout.md](references/docx-layout.md) only when creating or revising a Word document.

## 1. Establish scope

Identify or reasonably assume the vocabulary source, genre, relationship arc, learner level, chapter quota, pronunciation convention, and output format.

Do not imply that there is one official, complete “IELTS word list.” If no list is supplied, curate transferable B1–C1 words and phrases and state that choice. Do not reproduce a proprietary wordbook’s selection, order, definitions, or examples for public release unless its licence permits it.

Use one of these density modes:

- Balanced: 180–240 unique teaching units per chapter.
- Intensive: 300–400 unique teaching units per chapter.
- Custom: obey the user’s explicit quota.

Choose Intensive when the user asks to finish quickly, reduce Chinese-only narration, put English in nearly every sentence, or compress the course into dozens of chapters. Estimate chapter count as `ceiling(unique teaching units / target units per chapter)`.

Treat a useful phrase or collocation as one teaching unit. Report units rather than loosely calling every item a single word.

## 2. Normalize and allocate the lexicon

Normalize Unicode, case, whitespace, apostrophes, and hyphens before deduplication. Preserve the preferred display spelling separately.

Prioritize high-transfer academic and everyday vocabulary, productive word families, natural collocations, and words that can carry plot, emotion, evidence, institutions, or decisions. Remove duplicates, proper names, low-value filler, and forced phrases.

Build the allocation table before prose. A proven intensive pattern is 50–60 short segments with 6–7 units per segment. For exactly 390 units, use 60 segments and alternate 7 units in odd-numbered segments with 6 in even-numbered segments. Do not hard-code these sample parameters; derive every quota from the current contract.

Keep every unit globally unique unless repetition is explicitly used for review and excluded from the unique count.

## 3. Design a plot that can carry the vocabulary

Use one primary relationship and one external conflict. The relationship supplies emotional continuity; the external conflict supplies academic, civic, technical, and institutional vocabulary.

A reliable five-beat arc is:

1. encounter and attraction;
2. mistrust or separation;
3. forced cooperation;
4. revelation and consequential choice;
5. qualified resolution or open ending.

Outline all segments before writing. Give each segment one event, one emotional turn, and its assigned vocabulary. Do not add a plot-only paragraph with no teaching value.

## 4. Write high-density bilingual story segments

Write natural Chinese syntax and embed each assigned English unit immediately followed by a full-width Chinese gloss: `English unit（中文语境义）`.

Aim for at least one target unit in every sentence. In Intensive mode, require at least 80% of story sentences to contain a target unit and aim for 100%. Keep bridge sentences short and rare.

Within each segment:

- use all assigned units;
- introduce them in the same order as the explanation cards;
- keep the Chinese gloss specific to the scene;
- make the English function grammatically inside the Chinese sentence;
- avoid translating the whole sentence twice;
- allow later natural repetition, but count only the allocated first use;
- prefer a different plot construction over an unnatural English collocation.

## 5. Explain vocabulary immediately after each segment

Do not collect hundreds of explanations at the end of the chapter. Place `词汇精讲 · N 项` directly after every short story segment.

Give every unit its own three- or four-line card:

1. English unit + IPA + part of speech or phrase type + contextual Chinese meaning
2. 构/源/族：transparent formation, cautious origin, or useful family
3. 搭配：one natural, reusable collocation
4. 易错：only when a real pronunciation, spelling, countability, preposition, register, or meaning trap exists

Use a manual line break between fields. Keep a whole card together on one page. Match explanation order and spelling to the story exactly.

## 6. Validate before formatting

Draft or export a structured chapter manifest that follows [references/chapter-format.md](references/chapter-format.md), then run:

`python scripts/validate_chapter.py path/to/chapter.json --expected-total 390`

Fix every error before DOCX generation. The validator checks quotas, uniqueness, inline glosses, story coverage, explanation fields, and first-use order. It cannot certify linguistic naturalness; perform the linguistic review separately.

Required gates:

- allocated count equals explained count;
- normalized unique count equals the intended unique total;
- every allocated unit appears in its segment with an inline gloss;
- every explanation maps one-to-one and in order;
- every story sentence contains a target unit, unless an accepted bridge sentence is reported;
- IPA convention is consistent;
- collocations and grammar survive a separate review;
- plot names, timeline, evidence, and relationship state remain consistent.

## 7. Create and inspect DOCX when requested

Use the available document-creation workflow rather than treating a saved file as finished. Apply [references/docx-layout.md](references/docx-layout.md), render the DOCX to page images, and inspect every page.

Reject the document if any card is split across pages, a line is clipped, a story box overlaps another element, the final card is missing, or the rendered count differs from the structured manifest.

## 8. Report the result precisely

State chapters or segments produced, unique teaching units, quotas, density mode, pronunciation convention, validation results, page-render results, licensing limitations, and any unresolved linguistic uncertainty.

Never claim that the material is an official IELTS list, an official band predictor, or a substitute for active recall and spaced review.
