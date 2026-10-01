import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfWriter
from ingestion.ingest import discover_files, extract_document, ingest_files, inspect_text


class IngestionTests(unittest.TestCase):
    def test_discovery_is_nonrecursive_and_case_insensitive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "B.PDF").touch()
            (root / "a.pdf").touch()
            (root / "nested").mkdir()
            (root / "nested" / "hidden.pdf").touch()
            self.assertEqual([p.name for p in discover_files(root, ["PDF"])],
                             ["a.pdf", "B.PDF"])

    def test_identity_and_blank_page_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "original.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=300, height=300)
            writer.add_blank_page(width=300, height=300)
            writer.write(path)
            metadata, pages = extract_document(path)
            self.assertEqual(metadata["document_id"],
                             hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual([p["page_number"] for p in pages], [1, 2])
            self.assertEqual(pages[1]["page_id"], metadata["document_id"] + ":2")
            self.assertIn("empty_text", pages[0]["quality"]["flags"])
            renamed = path.rename(path.with_name("renamed.pdf"))
            self.assertEqual(extract_document(renamed)[0]["document_id"],
                             metadata["document_id"])

    def test_corrupt_document_is_reported_and_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corrupt = root / "bad.pdf"
            corrupt.write_bytes(b"not a PDF")
            output = root / "out"
            report = ingest_files([corrupt], output)
            self.assertEqual(len(report["failed_documents"]), 1)
            self.assertEqual(json.loads((output / "quality_report.json").read_text())
                             ["page_count"], 0)
            with self.assertRaises(FileExistsError):
                ingest_files([corrupt], output)

    def test_quality_flags(self):
        self.assertIn("sparse_text", inspect_text("short")["flags"])
        self.assertIn("replacement_characters", inspect_text("bad \ufffd")["flags"])
        self.assertEqual(inspect_text("Readable text. " * 20)["flags"], [])


if __name__ == "__main__":
    unittest.main()
