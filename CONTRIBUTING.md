# Contributing

## Local workflow

Use Windows PowerShell, Python 3.12, and uv. Run commands at the repository root:

```powershell
uv sync --locked
uv run python -m unittest discover -s tests
uv run python ingestion/ingest.py --dir knowledge_base --ext pdf
git diff --check
```

The corrupt-PDF test intentionally emits parser warnings. A passing run ends
with `Ran 8 tests` and `OK`. API and retrieval test files are placeholders.

When extraction changes, also run it against the three source PDFs into a new
output directory and inspect the report and representative source pages.
There is no automated assertion that extracted tables are semantically correct.

Use `uv add PACKAGE` to change dependencies and commit both `pyproject.toml` and
`uv.lock`. Keep outputs, credentials, and virtual environments out of commits.

## Explainable commits

Keep each commit focused on one purpose. Use a short imperative subject, with a
prefix such as `feat:`, `fix:`, `test:`, `docs:`, or `chore:`. Add a body describing
why the change exists, any relevant tradeoff, and what validation was performed.

Example:

```text
fix: preserve physical page numbers when extraction fails

Keep an error record for the affected page so downstream citations do not shift.

Validation: ingestion regression tests and a fresh three-document extraction.
```

Review `git diff --staged` before committing. Prefer follow-up commits over
rewriting shared history. Use `codex/` as the branch prefix for agent-created
working branches.

## Documentation

Update the README when commands or outputs change. Record data-format and design
changes in `docs/architecture.md`, and keep completed work distinct from planned
work in `docs/roadmap.md`. Do not present planned endpoints as operational.
