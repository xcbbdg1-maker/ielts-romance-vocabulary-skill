# DOCX layout and visual QA

## Page design

Use a restrained study-book layout:

- clear chapter title and short usage note;
- blue segment headings;
- a pale-blue story block;
- English teaching units in bold dark blue;
- inline Chinese glosses in red;
- a gold or dark-yellow `词汇精讲 · N 项` label;
- dark body text on white;
- page number in the footer.

Keep the main text around 10–11 pt with comfortable margins. Use approximately 1.15 line spacing and visible space between vocabulary cards.

## Vocabulary cards

Put one unit in one paragraph with manual line breaks:

1. unit + IPA + phrase type + contextual meaning;
2. 构/源/族;
3. 搭配;
4. optional 易错.

Use keep-together formatting so a card does not split between pages. Keep the story block with its segment heading when possible. Do not shrink the whole document merely to reduce page count.

## Structural checks

Verify from the DOCX package or document model:

- segment heading count equals manifest segment count;
- story block count equals segment count;
- vocabulary-label count equals segment count;
- definition-card count equals the unique teaching-unit count;
- each definition card contains at least two manual line breaks;
- first and final teaching units are present.

## Render checks

Render the final DOCX to PDF or page images and inspect every page at readable resolution.

Reject and rebuild if:

- any text is clipped or overlaps;
- a vocabulary card is split across pages;
- a story block loses its left border or background;
- a heading is orphaned at the bottom of a page;
- fonts substitute into unreadable IPA or Chinese;
- a blank page appears unexpectedly;
- the last segment or last card is truncated.

Report the rendered page count and the fact that every page was inspected. Saving the DOCX is not completion.
