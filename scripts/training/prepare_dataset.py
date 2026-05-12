#!/usr/bin/env python3
"""
Prepare ABBY training dataset from collected raw data.

Combines NIST standards, digital statutes, forensic case law,
CSAM investigation methodology, research papers, and synthetic examples
into chat-format JSONL for QLoRA fine-tuning.

Run from the ABBY repository root:
    python scripts/training/prepare_dataset.py
"""

import json
import random
import sys
from pathlib import Path

# Allow running from repo root or scripts/training/
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "training"))
sys.path.insert(0, str(REPO_ROOT / "src" / "abby"))

from abby_system_prompt import SYSTEM_PROMPT

RAW_DIR = REPO_ROOT / "data" / "raw"
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"
OUT_DIR = REPO_ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EVAL_RATIO = 0.05
SEED = 42


def make_example(user_msg: str, assistant_msg: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ]
    }


def load_forensic_standards():
    examples = []
    schema_path = RAW_DIR / "nist" / "forensic_standards_schema.json"
    if not schema_path.exists():
        print(f"  Warning: {schema_path} not found — run fetch_nist_standards.py first")
        return examples

    schema = json.loads(schema_path.read_text())

    for item in schema.get("digital_forensics", []):
        user = f"What is the correct methodology for {item['discipline']}? What tools should I use and what are the chain-of-custody requirements?"
        assistant = (
            f"**Evidence Type:** {item['discipline']}\n\n"
            f"**Recommended Methodology:** {item['requirement']}\n\n"
            f"**Tools:** {', '.join(item['tools'])}\n\n"
            f"**Admissibility Considerations:** {item['court_acceptance']}\n\n"
            f"**Known Defense Challenges:** {'; '.join(item['defense_challenges'])}\n\n"
            f"**Applicable Standards:** {item['standard']}"
        )
        examples.append(make_example(user, assistant))

    for item in schema.get("physical_evidence", []):
        user = f"What are the forensic standards and documentation requirements for {item['discipline']}?"
        assistant = (
            f"**Evidence Type:** {item['discipline']}\n\n"
            f"**Applicable Standards:** {item['standard']}\n\n"
            f"**Required Documentation:** {item['requirement']}\n\n"
            f"**Admissibility:** {item['court_acceptance']}\n\n"
            f"**Defense Challenges to Anticipate:** {'; '.join(item['defense_challenges'])}"
        )
        examples.append(make_example(user, assistant))

    print(f"  Forensic standards: {len(examples)} examples")
    return examples


def load_csam_methodology():
    examples = []
    schema_path = RAW_DIR / "csam_investigation" / "csam_investigation_methodology.json"
    if not schema_path.exists():
        print(f"  Warning: {schema_path} not found — run fetch_csam_investigation.py first")
        return examples

    data = json.loads(schema_path.read_text())

    for statute in data.get("statutes", []):
        user = f"What are the elements and investigation requirements for {statute['usc']} — {statute['title']}?"
        assistant = (
            f"**Statute:** {statute['usc']} — {statute['title']}\n\n"
            f"**Elements the prosecution must prove:**\n" +
            "\n".join(f"- {e}" for e in statute["elements"]) +
            f"\n\n**Investigation Notes:** {statute['investigation_notes']}"
        )
        if statute.get("mandatory_minimum"):
            assistant += f"\n\n**Mandatory Minimum:** {statute['mandatory_minimum']}"
        examples.append(make_example(user, assistant))

    methodology = data.get("methodology", {})
    for phase in methodology.get("phases", []):
        user = f"Walk me through the {phase['phase']} phase of a CSAM investigation. What documentation is required?"
        assistant = (
            f"**Phase:** {phase['phase']}\n\n"
            f"**Sources/Leads:** {', '.join(phase.get('sources', []))}\n\n"
            f"**Required Documentation:** {', '.join(phase.get('documentation', []))}\n\n"
            f"**Legal Notes:** {phase['legal_notes']}"
        )
        examples.append(make_example(user, assistant))

    hash_info = methodology.get("hash_matching", {})
    if hash_info:
        user = "How does PhotoDNA hash matching work and what is its evidentiary value in CSAM cases?"
        assistant = (
            f"**PhotoDNA and Hash-Based CSAM Identification**\n\n"
            f"**Tools:** {', '.join(hash_info['tools'])}\n\n"
            f"**Evidentiary Value:** {hash_info['evidentiary_value']}\n\n"
            f"**Court Acceptance:** {hash_info['court_acceptance']}\n\n"
            f"**Daubert Considerations:** {hash_info['daubert_notes']}"
        )
        examples.append(make_example(user, assistant))

    print(f"  CSAM methodology: {len(examples)} examples")
    return examples


def load_landmark_cases():
    examples = []
    case_files = [
        RAW_DIR / "caselaw" / "landmark_digital_cases.json",
        RAW_DIR / "caselaw" / "landmark_forensic_cases.json",
    ]
    for path in case_files:
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for case in data.get("landmark_cases", []):
            user = f"What was the holding in {case['case']} ({case['year']}) and what are its implications for forensic investigations?"
            assistant = (
                f"**{case['case']} ({case['year']}) — {case['citation']}**\n\n"
                f"**Holding:** {case['holding']}\n\n"
                f"**Implication for Forensic Investigators:** {case['implication']}"
            )
            examples.append(make_example(user, assistant))

    print(f"  Landmark cases: {len(examples)} examples")
    return examples


def load_caselaw_snippets():
    examples = []
    for fname in ["fourth_amendment_digital.jsonl", "forensic_admissibility.jsonl", "csam_investigation_caselaw.jsonl"]:
        path = RAW_DIR / "caselaw" / fname
        if not path.exists():
            continue
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                snippet = r.get("snippet", "").strip()
                case_name = r.get("case_name", "")
                if not snippet or not case_name or len(snippet) < 100:
                    continue
                user = f"What is significant about the case {case_name} for forensic investigators?"
                assistant = f"**{case_name}**\n\n{snippet}\n\n*Source: CourtListener*"
                examples.append(make_example(user, assistant))

    print(f"  Case law snippets: {len(examples)} examples")
    return examples


def load_research_papers():
    examples = []
    paper_files = [
        RAW_DIR / "research_papers" / "arxiv_forensics.jsonl",
        RAW_DIR / "research_papers" / "pubmed_forensics.jsonl",
    ]
    for path in paper_files:
        if not path.exists():
            continue
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                title = r.get("title", "").strip()
                abstract = (r.get("abstract") or r.get("summary") or "").strip()
                source = r.get("source", "research")
                if not title or not abstract or len(abstract) < 100:
                    continue
                user = f"Summarize the forensic significance of this research: {title}"
                assistant = (
                    f"**{title}**\n\n"
                    f"**Summary:** {abstract}\n\n"
                    f"*Source: {source}*"
                )
                examples.append(make_example(user, assistant))

    print(f"  Research papers: {len(examples)} examples")
    return examples


def load_synthetic():
    examples = []
    for path in SYNTHETIC_DIR.glob("*.jsonl"):
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                if "messages" in r:
                    examples.append(r)
    print(f"  Synthetic examples: {len(examples)} examples")
    return examples


def split_and_save(examples: list):
    random.seed(SEED)
    random.shuffle(examples)
    n_eval = max(1, int(len(examples) * EVAL_RATIO))
    eval_examples = examples[:n_eval]
    train_examples = examples[n_eval:]

    train_path = OUT_DIR / "train.jsonl"
    eval_path = OUT_DIR / "eval.jsonl"

    with open(train_path, "w") as f:
        for ex in train_examples:
            f.write(json.dumps(ex) + "\n")

    with open(eval_path, "w") as f:
        for ex in eval_examples:
            f.write(json.dumps(ex) + "\n")

    print(f"\n✓ Train: {len(train_examples)} examples → {train_path}")
    print(f"✓ Eval:  {len(eval_examples)} examples → {eval_path}")


if __name__ == "__main__":
    print("Preparing ABBY training dataset...\n")
    examples = []
    examples += load_forensic_standards()
    examples += load_csam_methodology()
    examples += load_landmark_cases()
    examples += load_caselaw_snippets()
    examples += load_research_papers()
    examples += load_synthetic()

    print(f"\nTotal: {len(examples)} examples")
    split_and_save(examples)
    print("\n✓ Dataset preparation complete.")
