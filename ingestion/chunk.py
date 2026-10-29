"""Create auditable, page-local word windows from extraction records."""

from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import re


def chunk_pages(pages, max_words=300, overlap_words=50):
    if max_words < 1 or not 0 <= overlap_words < max_words:
        raise ValueError("Require max_words > 0 and 0 <= overlap_words < max_words")
    chunks, skipped, seen = [], [], set()
    for page in pages:
        page_id = page["page_id"]
        if page_id in seen:
            raise ValueError(f"Duplicate page ID: {page_id}")
        seen.add(page_id)
        if page_id != f"{page['document_id']}:{page['page_number']}":
            raise ValueError(f"Inconsistent page identity: {page_id}")
        if page["error"] or "extraction_error" in page["quality"]["flags"]:
            raise ValueError(f"Extraction failed on {page_id}; repair before chunking")
        text = page["text"]
        words = list(re.finditer(r"\S+", text))
        if not words:
            skipped.append(page_id)
            continue
        for start in range(0, len(words), max_words - overlap_words):
            stop = min(start + max_words, len(words))
            char_start, char_end = words[start].start(), words[stop - 1].end()
            content = text[char_start:char_end]
            identity = json.dumps(["page-words-v1", page_id, max_words,
                                   overlap_words, char_start, char_end, content],
                                  ensure_ascii=False)
            chunks.append({
                "schema_version": 1,
                "chunk_id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
                "document_id": page["document_id"], "page_id": page_id,
                "filename": page["filename"], "page_number": page["page_number"],
                "page_label": page["page_label"],
                "char_start": char_start, "char_end": char_end,
                "word_count": stop - start, "text": content,
                "quality_flags": list(page["quality"]["flags"]),
            })
            if stop == len(words):
                break
    return chunks, skipped


def run(source, output, max_words=300, overlap_words=50):
    source, output = Path(source), Path(output)
    raw = source.read_bytes()
    pages = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    if not pages:
        raise ValueError("No page records found")
    chunks, skipped = chunk_pages(pages, max_words, overlap_words)
    report = {
        "algorithm": "page-words-v1", "max_words": max_words,
        "overlap_words": overlap_words,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "page_count": len(pages), "chunk_count": len(chunks),
        "skipped_empty_pages": skipped,
        "flagged_chunk_count": sum(bool(c["quality_flags"]) for c in chunks),
        "limitations": "Word windows may split sentences; no table reconstruction "
                        "or cross-page context. Not approved for clinical answering.",
    }
    output.mkdir(parents=True, exist_ok=False)
    with (output / "chunks.jsonl").open("w", encoding="utf-8") as stream:
        for chunk in chunks:
            stream.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    (output / "chunk_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-words", type=int, default=300)
    parser.add_argument("--overlap-words", type=int, default=50)
    args = parser.parse_args()
    try:
        report = run(args.pages, args.output, args.max_words, args.overlap_words)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Created {report['chunk_count']} chunks from {report['page_count']} pages; "
          f"skipped {len(report['skipped_empty_pages'])} empty pages.")


if __name__ == "__main__":
    main()
