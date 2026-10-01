# Hypertension RAG

Python 3.12 and uv. Current stage: local PDF ingestion and extraction inspection.

This project is building a retrieval-augmented question-answering service over
the WHO hypertension guideline and web annexes A and B. Currently it extracts
source text and records provenance; it does not yet answer questions or run an API.

## Quick start (Windows PowerShell)

Install Python 3.12 and uv, then run these commands from the repository root.
Use the committed lockfile to reproduce the dependency versions:

```powershell
uv sync --locked
uv run python ingestion/ingest.py --dir knowledge_base --ext pdf
uv run python ingestion/ingest.py --dir knowledge_base --ext pdf --output output/ingestion/baseline
uv run python -m unittest discover -s tests -p test_ingestion.py
```

Discovery is nonrecursive. Extraction requires a new output directory on each run
to avoid overwriting previous results or retaining stale pages.
If `baseline` already exists, choose another name such as `output/ingestion/run-02`.
Generated outputs and the virtual environment are ignored by Git.

## Repository map

| Path | Purpose |
| --- | --- |
| `ingestion/ingest.py` | Working discovery and extraction CLI |
| `knowledge_base/` | Three source PDFs and corpus inventory |
| `tests/test_ingestion.py` | Four ingestion regression tests |
| `app/` | Empty placeholders for the future API and configuration |
| `src/clinical_rag/` | Package scaffold |
| `tests/test_api.py`, `tests/test_retrieval.py` | Empty test placeholders |
| `docs/architecture.md` | Data flow, design choices, and limitations |
| `docs/roadmap.md` | Planned stages and completion criteria |
| `CONTRIBUTING.md` | Local checks and commit conventions |

See [the corpus inventory](knowledge_base/README.md),
[architecture](docs/architecture.md), and [roadmap](docs/roadmap.md).

## Output

- `documents.jsonl`: SHA-256 identity of exact file bytes, filename, local path,
  file size, page count, UTC extraction time, and extractor version/mode.
- `pages.jsonl`: original extracted text, document/page IDs, one-based physical
  PDF page numbers, PDF page labels, quality metrics, and any extraction errors.
- `quality_report.json`: document failures and empty, sparse (under 100 trimmed
  characters), replacement-character, or failed pages.
- `inspection.md`: bounded text previews of first pages and flagged pages.

Renaming a PDF preserves its content ID. Any byte change changes the ID, including
metadata-only changes. Page labels come from PDF metadata and may not match printed
page numbers. Join pages to documents through `document_id` for full provenance.
Local source paths are not public source URLs.

## Review before chunking

Open the source PDFs beside extracted text. Inspect representative prose pages,
recommendations, tables, and flagged pages. Check reading order, headings, numbers,
footnotes, and table cell associations. Empty pages can be intentional; unflagged
pages can still contain extraction errors. This baseline does not perform OCR or
reconstruct tables. Do not interpret successful extraction as clinical validation.

Document-level failures and page extraction errors produce exit code 1 while
preserving successful records and the report. Sparse or empty text alone does not.

Chunking, retrieval evaluation, generation, API serving, deployment, and
observability remain subsequent stages.
