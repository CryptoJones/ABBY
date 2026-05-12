# ABBY — Artifact, Ballistic, and Binary Yield

**An Open-Source Model Trained for Law Enforcement Forensic Investigators**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Ronin48%2Fabby-yellow)](https://huggingface.co/Ronin48/abby)
[![Version](https://img.shields.io/badge/version-v0.1.1--dev-orange)](CHANGELOG.md)

> *"I use my powers for good, not evil."*
> — Abby Sciuto, *NCIS*

```
python3 assets/banner.py
```

---

## Supporters

ABBY is community-funded. Every contribution keeps this project free, open, and in the hands
of the forensic examiners and investigators who need it most.

| Donor | Amount | Note |
|---|---|---|
| Ronin 48, LLC | N/A | Founding donor |

*Want to support ABBY? Reach out to the maintainers.*

---

## Overview

ABBY is an open-source machine learning model fine-tuned to assist law enforcement forensic
investigators. Given a case file, evidence manifest, or examination request, ABBY identifies
applicable forensic methodologies, legal standards for evidence admissibility, chain-of-custody
requirements, and the statutory framework governing digital, physical, and biological evidence.

ABBY was named in the spirit of Abby Sciuto — the forensic scientist who always told the truth
the evidence revealed, regardless of where it pointed. This model carries that same obligation:
to the science, to the standard, and to the chain of custody.

### The Ronin 48 Forensic Suite

ABBY is the third model in a balanced, three-part system designed to serve every phase of the
criminal justice process — from the crime scene to the courtroom.

| | SELMA | ABBY | ATTICUS |
|---|---|---|---|
| **Purpose** | Statute identification and charge analysis | Forensic methodology, evidence standards, chain of custody | Defense strategy and constitutional analysis |
| **Users** | Patrol officers, detectives, special agents | Forensic examiners, digital investigators, crime scene analysts | Public defenders, defense attorneys |
| **Output** | Applicable charges, elements, legal reasoning | Forensic methodology guidance, admissibility standards, chain-of-custody checklists | Defense theories, constitutional violations, evidentiary weaknesses |
| **Repository** | [Ronin48/SELMA](https://codeberg.org/Ronin48/SELMA) | [Ronin48/ABBY](https://codeberg.org/Ronin48/ABBY) | [Ronin48/ATTICUS](https://codeberg.org/Ronin48/ATTICUS) |

Together, these three models reflect the full arc of a criminal case — and the full weight of
the obligation to get it right.

---

## Architecture

- **Base Model:** [Meta Llama 3.3 70B Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) (Llama 3.1 Community License)
- **Fine-tuning Method:** QLoRA (4-bit quantization with Low-Rank Adaptation)
- **Context Window:** 128K tokens (native)
- **Quantization:** NF4 double quantization via bitsandbytes
- **Origin:** Meta Platforms, Inc. (United States)

---

## Capabilities

Given an evidence description, examination request, or case file, ABBY can:

1. **Digital Forensics Guidance** — Identify the correct acquisition methodology for computers,
   mobile devices, cloud storage, and IoT devices; recommend forensic tools (FTK, Cellebrite,
   EnCase, Autopsy, AXIOM) and explain their evidentiary implications
2. **Chain of Custody** — Generate chain-of-custody documentation requirements for any evidence
   type; flag procedural gaps that could result in suppression or challenge
3. **Legal Standards for Admissibility** — Apply Daubert (federal) and Frye (state) standards
   to forensic methodologies; identify which tools and techniques are court-accepted and which
   face documented challenges
4. **Digital Evidence Statutes** — Identify applicable federal statutes governing electronic
   evidence: CFAA (18 U.S.C. § 1030), ECPA, Stored Communications Act, and the Fourth Amendment
   warrant requirements for digital searches
5. **Physical Evidence Standards** — ASTM and SWGMAT standards for trace evidence, fingerprints,
   DNA, ballistics, and bloodstain pattern analysis
6. **Hash Verification** — Explain the evidentiary role of MD5/SHA-256 checksums, write-blocker
   requirements, and how to testify to evidence integrity
7. **Expert Witness Preparation** — Help forensic examiners anticipate cross-examination,
   explain methodology in plain language, and survive Daubert hearings
8. **Biological Evidence** — DNA collection, preservation, and CODIS submission standards;
   touch DNA and mixed-sample interpretation limitations
9. **Counterforensics Identification** — Recognize when evidence suggests attempts to defeat
   forensic analysis (wiping, encryption, anti-forensic tools) and the appropriate response

---

## Constitutional Override

ABBY is trained to know that how evidence is obtained determines whether it can be used.
No forensic finding — however compelling — survives an unlawful search. ABBY will flag
Fourth Amendment concerns at the point of evidence collection, not after the examination:

> ⚠ **ADMISSIBILITY CONCERN** — evidence obtained under these circumstances may be subject to
> suppression under the Fourth Amendment. ABBY recommends consulting with the prosecuting
> attorney before proceeding with examination.

Key Fourth Amendment digital standards ABBY is trained on:

- *Riley v. California* (2014) — warrant required for cell phone search incident to arrest
- *Carpenter v. United States* (2018) — warrant required for historical cell-site location data
- *United States v. Jones* (2012) — GPS tracking constitutes a Fourth Amendment search
- *Kyllo v. United States* (2001) — thermal imaging of home requires a warrant
- *United States v. Warshak* (2010) — warrant required for email content

---

## Forensic Disciplines Covered

### Digital Forensics
- Computer forensics: disk imaging, file system analysis, artifact recovery
- Mobile device forensics: logical, physical, and chip-off acquisitions
- Cloud forensics: legal process for cloud providers, preservation letters
- Network forensics: packet capture, log analysis, traffic reconstruction
- Memory forensics: volatile data acquisition, malware analysis
- Social media and OSINT: legal collection methods, preservation

### Physical and Trace Evidence
- Fingerprint development, comparison, and AFIS submission
- Ballistics and firearms examination (NIBIN)
- Bloodstain pattern analysis
- Trace evidence: fibers, glass, soil, hair
- Toolmark and impression evidence

### Biological Evidence
- DNA collection protocols (touch, biological fluids, degraded samples)
- Chain of custody for biological evidence
- CODIS submission requirements
- Limitations of low-template and mixed-profile DNA

### Document and Financial Evidence
- Questioned document examination
- Digital document metadata analysis
- Financial record analysis and subpoena guidance

---

## Where to Get ABBY

### HuggingFace

- **LoRA Adapter:** `Ronin48/abby-lora-adapter`
- **Merged Model:** `Ronin48/abby-70b`
- **Quantized (GGUF):** `Ronin48/abby-70b-GGUF` — for llama.cpp, LM Studio, Ollama

### Ollama

```bash
ollama run Ronin48/abby
```

### LM Studio

Search for `Ronin48/abby` once GGUF weights are published to HuggingFace.

---

## Project Structure

```
ABBY/
├── LICENSE
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── assets/
│   └── banner.py
├── models/
│   ├── federal/
│   └── [state models]/
├── configs/
│   ├── training_config.yaml
│   └── model_config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
├── scripts/
│   ├── data_collection/
│   │   ├── fetch_nist_standards.py      # NIST SP 800-86, 800-101, 800-61
│   │   ├── fetch_digital_statutes.py    # CFAA, ECPA, SCA, 4th Amendment case law
│   │   ├── fetch_forensic_caselaw.py    # Daubert hearings, suppression orders
│   │   └── fetch_swg_standards.py       # SWGMAT, SWGDAM, SWGFAST, SWGGUN standards
│   ├── training/
│   │   ├── train_qlora.py
│   │   ├── prepare_dataset.py
│   │   └── merge_adapter.py
│   └── evaluation/
├── src/abby/
│   └── prompts.py
├── tests/
└── docs/
    ├── TRAINING.md
    ├── DATA_SOURCES.md
    └── USAGE.md
```

---

## Training Data Sources

| Source | Description | Size | License |
|--------|-------------|------|---------|
| NIST SP 800-86 | Guide to Integrating Forensic Techniques into IR | Full publication | Public Domain |
| NIST SP 800-101 Rev 1 | Guidelines on Mobile Device Forensics | Full publication | Public Domain |
| NIST SP 800-61 Rev 2 | Computer Security Incident Handling Guide | Full publication | Public Domain |
| CFAA / ECPA / SCA | Federal digital crime and evidence statutes | ~200 sections | Public Domain |
| 4th Amendment Digital Case Law | Riley, Carpenter, Jones, Kyllo, Warshak | ~500 opinions | Public Domain |
| Daubert / Frye Case Law | Forensic admissibility decisions | ~1K opinions | Public Domain |
| SWGMAT / SWGDAM / SWGFAST | Scientific working group forensic standards | Full standards | Public Domain |
| NIBIN / AFIS Guidance | Ballistics and fingerprint database standards | Published guides | Public Domain |
| CourtListener Forensic Cases | Cases involving forensic evidence challenges | ~5K opinions | Open |
| Synthetic | Generated evidence-to-methodology mappings | ~50K examples | Apache 2.0 |

---

## Disclaimer

ABBY is a research tool designed to assist forensic investigators. It is **NOT** a substitute
for accredited laboratory procedures, peer-reviewed methodology, or testimony by a qualified
forensic expert. All outputs should be verified by a certified forensic examiner before any
action is taken or testimony is given.

Forensic science carries extraordinary weight in the courtroom. ABBY is a tool to help
examiners work more efficiently and consistently — not a replacement for training,
accreditation, or professional judgment.

This software is provided "AS IS" without warranty of any kind.

---

## Contributing

Contributions from certified forensic examiners, digital investigators, and legal professionals
are especially welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

**Project Code, Data, and Documentation:** Apache License 2.0 — Copyright 2026 Ronin 48, LLC.

**Base Model Weights:** Meta Llama 3.1 Community License. Fine-tuned adapter weights and
all original ABBY contributions remain Apache 2.0.
