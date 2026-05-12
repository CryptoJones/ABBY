# ABBY Changelog

## [v0.1.0-dev] — In Development (Started 2026-05-12)

**Status:** ⏳ Data collection and training pipeline in progress

### Added
- Initial project scaffold and repository
- `README.md` with full project overview, sister project references (SELMA, ATTICUS), and capability description
- `src/abby/prompts.py` — system prompt with Constitutional Override and response format
- `scripts/data_collection/fetch_nist_standards.py` — NIST SP 800-86, 800-101, 800-61, 800-72
- `scripts/data_collection/fetch_digital_statutes.py` — CFAA, ECPA, SCA, Pen Register Act, 4th Amendment digital case law
- `scripts/data_collection/fetch_forensic_caselaw.py` — Daubert hearings, suppression orders, forensic admissibility
- Forensic standards schema covering digital forensics, fingerprints, DNA, ballistics
- Landmark digital case index (Riley, Carpenter, Jones, Kyllo, Warshak, Katz)
- `scripts/data_collection/fetch_csam_investigation.py` — NCMEC CyberTipline guidance, ICAC methodology, CSAM statute schema
- `scripts/data_collection/fetch_scihub_forensics.py` — arXiv and PubMed open-access forensic research papers (400 arXiv + 164 PubMed)
- `scripts/data_collection/generate_synthetic.py` — 13 hand-authored forensic Q&A training examples covering mobile acquisition, laptop forensics, Daubert, CSAM investigation, bloodstain evidence, chain of custody, write blockers, RAID/NAS, PhotoDNA, volatile data, cold case DNA, SCA, and deleted file recovery
- `scripts/training/prepare_dataset.py` — fixed working directory handling (now runs correctly from repo root); added research paper and synthetic data loaders; 445 total training examples

### Data Collection Status
| Source | Count | Status |
|---|---|---|
| NIST SP 800-86/101/61/72 | 4 publications | ✓ Fetched |
| CFAA / ECPA / SCA / Pen Register | 4 statutes | ✓ Fetched |
| Landmark digital case law | 6 cases | ✓ Fetched |
| Landmark forensic case law | 6 cases | ✓ Fetched |
| CSAM investigation methodology | 12 examples | ✓ Fetched |
| Forensic standards schema | 6 examples | ✓ Fetched |
| arXiv forensic research papers | 400 papers | ✓ Fetched |
| PubMed forensic research papers | 164 papers | ✓ Fetched |
| CourtListener case law | 0 | ⚠ Requires API token |
| Synthetic hand-authored examples | 13 examples | ✓ Complete |
| **Total processed** | **445 examples** | |
