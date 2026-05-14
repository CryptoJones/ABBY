# ABBY — Limitations, Scope, and Use Guidance

Read this before deploying ABBY in any operational context.

---

## What ABBY Does

Given an evidence description or examination request, ABBY identifies the correct forensic methodology, applicable legal standards for admissibility, chain-of-custody requirements, and relevant statutes and case law governing physical and digital evidence.

## What ABBY Does Not Do

- **ABBY is not a certified forensic examiner.** Its outputs do not substitute for credentialed analysis or expert witness testimony.
- **ABBY cannot examine evidence.** It works from descriptions you provide. It has no access to actual files, devices, or physical evidence.
- **ABBY cannot testify.** No AI output is admissible as expert testimony under Daubert or Frye without a qualified human expert.
- **ABBY does not know your lab's accreditation requirements.** ASCLD, ISO 17025, and state lab standards vary and are not modeled.
- **ABBY has a training data cutoff.** Changes to Fourth Amendment case law, new Supreme Court decisions, and evolving digital forensics standards may not be reflected.
- **ABBY can hallucinate case citations.** Always verify any case name, citation, or statutory reference against primary sources before including it in a report or court filing.
- **ABBY does not know your chain of custody.** It can tell you what proper chain of custody requires; it cannot validate that yours is intact.

---

## Scope of Practice

ABBY is designed to assist credentialed forensic examiners, digital investigators, and crime scene analysts in:

- Identifying the correct methodology for a given evidence type
- Understanding admissibility standards (Daubert/Frye) for specific evidence types
- Researching Fourth Amendment case law relevant to digital evidence collection
- Chain-of-custody documentation requirements
- Training and scenario-based learning

**ABBY outputs used in reports, affidavits, or court filings must be reviewed by a qualified forensic examiner or attorney before submission.**

---

## Known Limitations

| Area | Limitation |
|------|-----------|
| Currency | Case law and standards have a cutoff date; recent decisions may not be reflected |
| Lab standards | ASCLD, ISO 17025, and state-specific accreditation requirements not modeled |
| Tool-specific | Specific tool versions (FTK, Cellebrite, EnCase) and their output formats evolve rapidly |
| Physical evidence | Trace, biological, and physical evidence methodology less comprehensive than digital |
| Case citations | Always verify — hallucination risk applies to case names and citations |
| Training size | Fine-tuned on a small dataset; edge cases and novel evidence types may degrade performance |

---

## Before You Deploy

- Have a senior forensic examiner audit sample outputs against your lab's SOPs
- Establish policy on when ABBY may be consulted and what independent verification is required
- Do not use ABBY outputs in court filings without expert review
- Ensure users understand that ABBY identifies methodology — it does not perform analysis

---

## Version and Training Data

| Field | Value |
|-------|-------|
| Base model | meta-llama/Llama-3.3-70B-Instruct |
| Fine-tune method | QLoRA (4-bit) |
| Adapter | [Ronin48LLC/abby-lora-adapter](https://huggingface.co/Ronin48LLC/abby-lora-adapter) |
| Training date | May 2026 |
| Training data cutoff | See base model documentation |

---

## Reporting Errors

If ABBY produces an incorrect, dangerous, or misleading output:

- **GitHub:** [CryptoJones/ABBY/issues](https://github.com/CryptoJones/ABBY/issues)
- **Codeberg:** [Ronin48/ABBY/issues](https://codeberg.org/Ronin48/ABBY/issues)

Include the input, the output, and what the correct answer should have been.
