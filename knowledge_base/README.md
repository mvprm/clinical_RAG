# Source corpus

The local corpus contains the WHO *Guideline for the pharmacological treatment
of hypertension in adults* and web annexes A and B. PDFs are tracked unchanged
to make the small baseline corpus reproducible. Their embedded copyright and
licensing notices remain applicable; repository documentation does not relicense
these documents. Original download URLs have not yet been recorded.

| File | Description | Pages in baseline |
| --- | --- | ---: |
| `guidelines_hypertension.pdf` | Main guideline | 61 |
| `annexA_summaryOfEvidence.pdf` | Web annex A: summary of evidence | 188 |
| `annexB_evidenceToDecisionFrameworkds.pdf` | Web annex B: evidence-to-decision frameworks | 63 |

## SHA-256 inventory

```text
57f6376d5c9bc4ea6c44873625547c8a5443d5a6ad8c8c422733681563db05fb  guidelines_hypertension.pdf
34454e463f530dfe329c546321e1e3fb939c47269a862a56bc308f9bcedb2e2e  annexA_summaryOfEvidence.pdf
bff5b6231a927c22bbbfc5d94bc4bf5903277299d8cd360b283ec615c35c9e96  annexB_evidenceToDecisionFrameworkds.pdf
```

Verify locally with `Get-FileHash knowledge_base/*.pdf -Algorithm SHA256`.
When replacing a source, update this inventory and explain the source revision
in the commit body. Re-extract into a new output directory. Preserve the existing
filenames unless a deliberate rename is needed.
