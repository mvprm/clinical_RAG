from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from importlib.metadata import version

from pypdf import PdfReader


def inspect_text(text):
    """Heuristics for review, not a guarantee of faithful extraction."""
    flags = []
    if not text.strip():
        flags.append("empty_text")
    elif len(text.strip()) < 100:
        flags.append("sparse_text")
    if "\ufffd" in text:
        flags.append("replacement_characters")
    return {"character_count": len(text), "word_count": len(text.split()),
            "flags": flags}


def extract_document(path):
    """Hash and extract the same open file; retain physical page numbering."""
    path = Path(path).resolve()
    with path.open("rb") as stream:
        document_id = hashlib.file_digest(stream, "sha256").hexdigest()
        stream.seek(0)
        reader = PdfReader(stream)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF is not supported: {path.name}")
        labels = reader.page_labels
        metadata = {
            "schema_version": 1,
            "document_id": document_id,
            "filename": path.name,
            "source_path": str(path),
            "size_bytes": path.stat().st_size,
            "page_count": len(reader.pages),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "extractor": {"name": "pypdf", "version": version("pypdf"),
                          "mode": "plain"},
        }
        pages = []
        for number, page in enumerate(reader.pages, start=1):
            error = None
            try:
                text = page.extract_text() or ""
            except Exception as exc:
                text = ""
                error = f"{type(exc).__name__}: {exc}"
            quality = inspect_text(text)
            if error:
                quality["flags"].append("extraction_error")
            pages.append({
                "document_id": document_id,
                "page_id": f"{document_id}:{number}",
                "filename": path.name,
                "page_number": number,
                "page_label": labels[number - 1],
                "text": text,
                "quality": quality,
                "error": error,
            })
    return metadata, pages


def ingest_files(files, output):
    """Write each run into a fresh directory so stale pages cannot survive."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    documents, pages, failures = [], [], []
    for path in files:
        try:
            document, extracted = extract_document(path)
            documents.append(document)
            pages.extend(extracted)
        except Exception as exc:
            failures.append({"source_path": str(path.resolve()),
                             "error": f"{type(exc).__name__}: {exc}"})
    for name, records in (("documents.jsonl", documents), ("pages.jsonl", pages)):
        with (output / name).open("w", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    report = {
        "document_count": len(documents), "page_count": len(pages),
        "failed_documents": failures,
        "flagged_pages": [{key: page[key] for key in
                           ("page_id", "filename", "page_number", "quality", "error")}
                          for page in pages if page["quality"]["flags"]],
        "limitations": "No OCR or table reconstruction. Flags require human review; "
                        "unflagged pages may still have reading-order or table errors.",
    }
    (output / "quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Extraction inspection", "", report["limitations"], ""]
    for page in pages:
        if page["page_number"] == 1 or page["quality"]["flags"]:
            lines.extend([f"## {page['filename']} - PDF page {page['page_number']}",
                          f"Flags: {', '.join(page['quality']['flags']) or 'none'}", "",
                          "```text", page["text"][:1500], "```", ""])
    (output / "inspection.md").write_text("\n".join(lines), encoding="utf-8")
    return report


def discover_files(directory, extensions):
    """Return files matching the extensions in the given directory."""
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    # Accept both "pdf" and ".pdf", regardless of case.
    normalized_extensions = {
        f".{extension.lstrip('.').lower()}"
        for extension in extensions
    }

    return sorted(
        (
            file
            for file in directory.iterdir()
            if file.is_file()
            and file.suffix.lower() in normalized_extensions
        ),
        key=lambda file: file.name.casefold(),
    )


def main():
    parser = ArgumentParser(
        description="Discover files in a directory by extension."
    )
    parser.add_argument(
        "--dir",
        dest="directory",
        required=True,
        help="Directory to search.",
    )
    parser.add_argument(
        "--ext",
        dest="extensions",
        nargs="+",
        required=True,
        help="Extensions to include, for example: pdf docx.",
    )

    parser.add_argument("--output", type=Path,
                        help="Extract PDFs into a new output directory; omit to discover only.")
    args = parser.parse_args()

    try:
        files = discover_files(args.directory, args.extensions)
    except OSError as error:
        parser.exit(status=1, message=f"Error: {error}\n")

    print(f"Discovered {len(files)} file(s):")
    for file in files:
        print(f"  {file}")
    if args.output is not None:
        if not files:
            parser.exit(1, "Error: no input files found.\n")
        if any(file.suffix.lower() != ".pdf" for file in files):
            parser.exit(1, "Error: extraction supports PDFs only.\n")
        try:
            report = ingest_files(files, args.output)
        except OSError as error:
            parser.exit(1, f"Error: {error}\n")
        print(f"Extracted {report['page_count']} pages from "
              f"{report['document_count']} documents; "
              f"{len(report['flagged_pages'])} pages need review.")
        print(f"Inspection artifacts: {args.output.resolve()}")
        if report["failed_documents"] or any(
            "extraction_error" in page["quality"]["flags"]
            for page in report["flagged_pages"]
        ):
            parser.exit(1, "Extraction had errors; see quality_report.json.\n")


if __name__ == "__main__":
    main()
