# Content quality audit — 2026-08-12

## Decision

Withdraw the previously published Chapters 2–50 Word files. They passed vocabulary-accounting, package, and render checks, but they do not meet the standard for coherent fiction or natural contextual vocabulary teaching.

## Direct findings

- Chapter 2 contains 385 teaching units, but only 57 were matched to the chapter theme; 328 were filled from a general pool.
- All 120 story sentences in Chapter 2 arrange three or four target units as enumeration-style strings.
- All 60 Chapter 2 sections reproduce an outline-style event label instead of dramatizing that event.
- All 60 `emotional_turn` values and continuity records in Chapter 2 are empty.
- Across the old Chapters 2–50 plan, 2,303 of 2,940 beat summaries (78.3%) come from 47 generic summaries repeated across all 49 chapters.
- The old prose generator split every six- or seven-unit bundle into two lists and inserted those lists into one of 24 fixed sentence templates. Template choice did not use plot, meaning, grammar, or character state.

## Root cause

The workflow assigned and rotated vocabulary before writing scenes. Coverage quotas were treated as prose geometry, and validators checked counts, order, inline glosses, Word structure, and visual layout without checking causal plot, semantic fit, character motivation, or repeated sentence skeletons.

## Replacement standard

- Write the Chinese scene and its causal contract first.
- Use learning episodes of 30–40 unique units inside the larger story chapters.
- Introduce at most two new units per sentence and four per short paragraph.
- Allocate vocabulary by semantic and grammatical compatibility; return forced units to the unassigned pool.
- Require non-empty entry state, goal, conflict, choice, consequence, exit state, required facts, and forbidden facts.
- Reject outline language, three-unit enumeration dumps, repeated fill-in templates, and evidence/list containers used only to hide unrelated words.
- Remove English and glosses during review; the remaining Chinese must still tell a coherent story.
- Do not publish a rewritten batch until narrative, language, vocabulary-card, structural, and rendered-page checks all pass.

The first chapter remains public as a quality reference. New Chapters 2–50 will be published only after replacement content passes the new gates.

