# Ingestion architecture

## Current flow

```text
Local directory -> nonrecursive discovery -> SHA-256 file identity
                -> pypdf extraction per page -> quality heuristics
                -> JSONL records + JSON report + Markdown previews
```

Discovery accepts extensions with or without a leading dot, ignores case, and
sorts by case-folded filename. Supplying `--output` enables PDF-only extraction.

## Identity and provenance

`document_id` is the SHA-256 digest of the PDF bytes. Hashing and extraction use
the same open file stream. This identifies a file version, not a logical title:
metadata-only edits also produce a new identity. Identical copies share an ID;
the current pipeline does not deduplicate repeated input files.

`page_id` is `<document_id>:<page_number>`. Physical page numbers start at 1 and
include covers and blank pages. `page_label` comes from PDF metadata and is not
verified against printed numbering. Page records join to document records by
`document_id`; document metadata records the local path, filename, byte size,
page count, extraction time, and pypdf version and mode.

## Artifact contract

Every output is UTF-8. JSONL files contain one JSON object per line.

| Artifact | Main fields |
| --- | --- |
| `documents.jsonl` | `schema_version`, `document_id`, `filename`, `source_path`, `size_bytes`, `page_count`, `extracted_at`, `extractor` |
| `pages.jsonl` | `document_id`, `page_id`, `filename`, `page_number`, `page_label`, `text`, `quality`, `error` |
| `quality_report.json` | `document_count`, `page_count`, `failed_documents`, `flagged_pages`, `limitations` |
| `inspection.md` | First-page and flagged-page previews, capped at 1,500 characters per page |

Quality includes character count, whitespace-delimited word count, and flags:
empty text, fewer than 100 trimmed characters, Unicode replacement characters,
or an extraction exception. These heuristics are review aids, not quality scores.

## Failure behavior and tradeoffs

- Missing or invalid input directories fail discovery.
- Extraction rejects an empty selection or non-PDF input.
- An existing output directory is rejected to protect earlier runs.
- Encrypted and unreadable PDFs are recorded as failed documents.
- Page extraction exceptions preserve a page record with empty text and an error.
- Document or page failures yield exit code 1 after writing available results.
- Empty or sparse text alone does not change the exit code.

All extracted records are held in memory before writing. Outputs are not published
atomically, so a process or disk failure can leave an incomplete directory.
Consumers must check successful completion and the report. This is a small-corpus
baseline, not a concurrent or resumable ingestion service.

pypdf extracts plain text; fonttools supports embedded font decoding. The lockfile
captures dependency versions. No OCR, table reconstruction, layout-aware chunking,
source URL registry, or automated clinical validation is implemented.
