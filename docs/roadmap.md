# Roadmap

## Implemented: ingestion baseline

- Nonrecursive file discovery.
- Content identity and page provenance.
- Page text extraction, quality flags, and inspection artifacts.
- Four regression tests.
- Local corpus run: 312 pages, 9 flagged pages, no extraction failures.

## Next: extraction acceptance and chunking

Review prose, recommendations, tables, footnotes, and flagged pages against the
PDFs. Record failure cases before selecting normalization and chunk boundaries.
Chunks must retain document IDs and physical page references. Completion means
representative chunks are readable and traceable without losing qualifications.

## Retrieval and evaluation

Build an evaluation set with questions and expected evidence. Select a retrieval
baseline, measure evidence recall, and inspect misses before tuning. Establish
explicit acceptance thresholds from measured results.

## Generation

Generate answers with verifiable source references and handle insufficient
evidence explicitly. Evaluate factual support and citation accuracy separately
from retrieval quality.

## Service and delivery

Implement FastAPI routes `POST /ask`, `GET /health`, and `GET /version`
(also recorded in the original `docs.txt` notes). Add configuration, route tests,
Docker packaging, and Cloud Run deployment once the local pipeline is evaluated.

## Observability

Track latency, failures, retrieval evidence, model/version configuration, and
evaluation regressions. Define logging and data-retention requirements before
collecting production queries.
