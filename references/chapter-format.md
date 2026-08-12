# Chapter format

## Contents

1. Structured manifest
2. Field rules
3. Rendered segment
4. Counting and normalization

## Structured manifest

Use a large story chapter as a navigation container. Put 30–40-unit learning episodes inside `mini_chapters`; do not equate one Word heading with one vocabulary-loading unit.

Each mini chapter must record a scene contract before its paragraphs:

```json
{
  "number": 1,
  "title": "雨棚下的警告",
  "entry_state": "听证会前夜，江穗和陆岑在旧城区公交站；两人刚收到程叙的定位。",
  "goal": "确认发信人是否真是江屿。",
  "conflict": "江穗不能判断陆岑是否参与隐瞒。",
  "choice": "她决定当面赴约，但要求双方共享设备和撤离方案。",
  "consequence": "程叙说出只有兄妹知道的童年细节。",
  "exit_state": "江穗高度怀疑程叙是哥哥，但尚无可公开的身份验证。",
  "required_facts": ["直接承接‘别相信陆岑’"],
  "forbidden_facts": ["不得提前完成DNA确认"],
  "paragraphs": []
}
```

Every paragraph needs one concrete `event`, one `emotional_turn`, a two- or three-sentence `story`, and three or four semantically compatible `terms`. A mini chapter normally contains 30–40 unique units.

Create the chapter as UTF-8 JSON before rendering Markdown or DOCX:

```json
{
  "chapter_title": "第一章：示例",
  "pronunciation": "British",
  "density_mode": "Intensive",
  "segments": [
    {
      "number": 1,
      "story": "她把这次相遇视为 a plausible coincidence（一次看似可信的巧合），却注意到他始终 maintain a cautious distance（保持谨慎距离）。",
      "terms": [
        {
          "term": "a plausible coincidence",
          "ipa": "/ə ˈplɔː.zə.bəl kəʊˈɪn.sɪ.dəns/",
          "pos": "名词短语",
          "meaning": "一次看似可信的巧合",
          "formation": "plausible 与 plausibility 同族；coincidence 与 coincide 同族",
          "collocation": "dismiss something as a coincidence",
          "error_note": "plausible 表示‘貌似合理可信’，不等于已经证实"
        },
        {
          "term": "maintain a cautious distance",
          "ipa": "/meɪnˈteɪn ə ˈkɔː.ʃəs ˈdɪs.təns/",
          "pos": "动词短语",
          "meaning": "保持谨慎距离",
          "formation": "maintain 与 maintenance 同族；cautious 与 caution 同族",
          "collocation": "maintain a safe distance",
          "error_note": ""
        }
      ]
    }
  ]
}
```

The legacy single-level sample below contains only two terms for readability. New long-form work should use the mini-chapter schema above. Validate a small test with explicit limits:

`python scripts/validate_chapter.py sample.json --min-terms-per-segment 2 --max-terms-per-segment 2 --expected-total 2`

## Field rules

- `chapter_title`: required non-empty string.
- `pronunciation`: British or American; keep it consistent.
- `density_mode`: Balanced, Intensive, or Custom.
- `segments`: non-empty list.
- `number`: sequential integer starting at 1.
- `story`: Chinese-led prose containing every assigned English unit and its immediate Chinese gloss.
- `terms`: first-use order from the story.
- `term`: exact preferred display form.
- `ipa`: slash- or bracket-delimited pronunciation.
- `pos`: part of speech or phrase type in Chinese.
- `meaning`: contextual Chinese meaning used in the story.
- `formation`: reliable formation, origin, or family note. Write `整体记忆` when analysis would be speculative.
- `collocation`: one natural reusable collocation or sentence frame.
- `error_note`: optional; use an empty string when no genuine trap exists.

## Rendered segment

Render each segment in this order:

1. 第 N 段
2. one compact story block
3. 词汇精讲 · N 项
4. one three- or four-line card per term

Example card:

```text
plausible /ˈplɔː.zə.bəl/ 形容词·貌似合理可信的
构/源/族：plausible 与 plausibility 同族
搭配：a plausible explanation
易错：表示“听起来可信”，不保证真实
```

Do not combine multiple terms into a single dense explanation line.

## Counting and normalization

Count teaching units after:

- Unicode NFKC normalization;
- case folding;
- trimming and collapsing whitespace;
- converting common dash characters to a standard hyphen;
- removing spaces immediately around a hyphen.

Do not merge genuinely different forms such as `economic` and `economical`. Do merge display-only variants such as `mixed–use` and `mixed-use`.

Use an allocation matrix, not mental arithmetic. Keep coverage accounting separate from prose geometry. Do not use the old 60-segment × 6–7-unit pattern for new work.

For a 385-unit large chapter, one valid navigation split is five 39-unit and five 38-unit learning episodes. Inside each episode, use paragraphs of at most four units and sentences of at most two. The exact paragraph count may vary with the story.

For arithmetic-only audits, a quota still follows:

`total = odd_segment_count × odd_quota + even_segment_count × even_quota`

For 60 segments alternating 7 and 6:

`30 × 7 + 30 × 6 = 390`

