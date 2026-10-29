# Initial text inspection

This is a review of extracted text and chunk boundaries, not a visual comparison
against rendered PDFs or acceptance of extraction quality.

Baseline input: `output/ingestion/verified/pages.jsonl`. Chunking configuration:
`page-words-v1`, 300 words, 50-word overlap. Result: 565 chunks, five empty pages
skipped, four chunks carrying sparse-text flags.

## Observations

- Main guideline, physical PDF page 14: prose is present, but the 300-word window
  cuts a list item mid-sentence. The following overlapping chunk retains the
  continuation. Line-break hyphenation and bracket-like bullet markers remain.
- Annex A, physical PDF page 8: the table column headings and values appear in
  linear text. Row/column relationships cannot be assumed from this representation.
- Empty pages are recorded rather than silently removed from provenance. Sparse
  pages remain as chunks; they may include covers or page-number-only text.

## Outstanding acceptance work

Compare these pages and representative recommendations against rendered PDFs.
Inspect annex B tables and all flagged pages. Decide how to represent tables and
whether sentence-aware boundaries improve evidence completeness. Build retrieval
evaluation cases that test qualifications spanning chunk and page boundaries.
