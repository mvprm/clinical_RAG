import unittest

from ingestion.chunk import chunk_pages


def page(text, number=1):
    return {"document_id": "abc", "page_id": f"abc:{number}",
            "filename": "source.pdf", "page_number": number, "page_label": str(number),
            "text": text, "error": None, "quality": {"flags": []}}


class ChunkingTests(unittest.TestCase):
    def test_exact_spans_overlap_and_complete_coverage(self):
        source = page("  alpha\nbeta  gamma\tdelta epsilon  ")
        chunks, _ = chunk_pages([source], 3, 1)
        self.assertEqual([c["text"].split() for c in chunks],
                         [["alpha", "beta", "gamma"], ["gamma", "delta", "epsilon"]])
        for chunk in chunks:
            self.assertEqual(chunk["text"], source["text"][chunk["char_start"]:chunk["char_end"]])
        self.assertEqual(chunks, chunk_pages([source], 3, 1)[0])

    def test_no_cross_page_chunks_and_empty_pages_recorded(self):
        chunks, skipped = chunk_pages([page("one"), page("", 2), page("two", 3)])
        self.assertEqual([c["page_number"] for c in chunks], [1, 3])
        self.assertEqual(skipped, ["abc:2"])

    def test_invalid_parameters_duplicates_and_failed_pages_rejected(self):
        for size, overlap in [(0, 0), (3, 3), (3, -1)]:
            with self.assertRaises(ValueError):
                chunk_pages([], size, overlap)
        with self.assertRaises(ValueError):
            chunk_pages([page("one"), page("two")])
        failed = page("")
        failed["error"] = "decode failure"
        with self.assertRaises(ValueError):
            chunk_pages([failed])

    def test_identity_changes_with_text_and_quality_flags_propagate(self):
        source = page("short")
        source["quality"]["flags"] = ["sparse_text"]
        chunks, _ = chunk_pages([source])
        self.assertEqual(chunks[0]["quality_flags"], ["sparse_text"])
        self.assertNotEqual(chunks[0]["chunk_id"],
                            chunk_pages([page("different")])[0][0]["chunk_id"])


if __name__ == "__main__":
    unittest.main()
