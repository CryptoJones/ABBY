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
