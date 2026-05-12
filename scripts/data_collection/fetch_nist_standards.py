#!/usr/bin/env python3
"""
Fetch NIST forensic science standards for ABBY training.

Downloads:
- NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response
- NIST SP 800-101 Rev 1: Guidelines on Mobile Device Forensics
- NIST SP 800-61 Rev 2: Computer Security Incident Handling Guide
- NIST SP 800-72: Guidelines on PDA Forensics
- NIST NSRL (National Software Reference Library) hash set documentation
"""

import json
from pathlib import Path

import requests
from tqdm import tqdm

RAW_DIR = Path("data/raw/nist")
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ABBY-Research/1.0 (akclark@thenetwerk.net)"}

NIST_PUBLICATIONS = [
    ("https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf",
     "sp800-86_forensic_incident_response.pdf",
     "SP 800-86: Forensic Techniques for Incident Response"),
    ("https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf",
     "sp800-101r1_mobile_device_forensics.pdf",
     "SP 800-101 Rev 1: Mobile Device Forensics"),
    ("https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r2.pdf",
     "sp800-61r2_incident_handling.pdf",
     "SP 800-61 Rev 2: Computer Security Incident Handling"),
    ("https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-72.pdf",
     "sp800-72_pda_forensics.pdf",
     "SP 800-72: PDA Forensics"),
]


def fetch_nist_publications():
    print("\n" + "=" * 60)
    print("Fetching NIST Forensic Standards...")
    print("=" * 60)
    results = []
    for url, fname, title in NIST_PUBLICATIONS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            resp.raise_for_status()
            out = RAW_DIR / fname
            total = int(resp.headers.get("content-length", 0))
            with open(out, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=fname[:40]) as pbar:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
            print(f"  ✓ {title}")
            results.append({"title": title, "file": fname, "url": url, "status": "ok"})
        except Exception as e:
            print(f"  Warning ({fname}): {e}")
            results.append({"title": title, "file": fname, "url": url, "status": str(e)})

    index_out = RAW_DIR / "nist_index.json"
    index_out.write_text(json.dumps(results, indent=2))
    print(f"\nSaved index to {index_out}")


def create_forensic_standards_schema():
    """Create structured training data from known forensic standards."""
    schema = {
        "description": "Key forensic science standards and their evidentiary implications — training signal for ABBY",
        "digital_forensics": [
            {
                "discipline": "Computer Forensics — Disk Imaging",
                "standard": "NIST SP 800-86",
                "requirement": "Forensic duplicate (bit-for-bit copy) with write blocker; hash verification (MD5 + SHA-256) before and after",
                "tools": ["FTK Imager", "dd", "dcfldd", "Guymager"],
                "court_acceptance": "Well-established; examiner must testify to write-blocker use and hash match",
                "defense_challenges": ["Hash mismatch", "No write blocker documented", "Continuity gap"],
            },
            {
                "discipline": "Mobile Device Forensics",
                "standard": "NIST SP 800-101 Rev 1",
                "requirement": "Isolate device from network (Faraday bag) immediately; document screen state; select acquisition level (logical/physical/chip-off) based on lock state",
                "tools": ["Cellebrite UFED", "AXIOM", "Oxygen Forensics", "GrayKey"],
                "court_acceptance": "Cellebrite and AXIOM widely accepted; chip-off methodology requires expert explanation",
                "defense_challenges": ["Faraday failure (remote wipe)", "Timestamp attribution", "Tool reliability (Daubert)"],
            },
            {
                "discipline": "Cloud Evidence",
                "standard": "SCA (18 U.S.C. §§ 2701-2713); ECPA",
                "requirement": "Legal process required (subpoena for subscriber info; warrant for content); preservation letter under 18 U.S.C. § 2703(f) issued immediately",
                "tools": ["Provider law enforcement portals", "MLAT for foreign providers"],
                "court_acceptance": "Legal process compliance is mandatory; Carpenter applies to content",
                "defense_challenges": ["Warrant requirement", "Third-party provider authentication", "Data integrity"],
            },
        ],
        "physical_evidence": [
            {
                "discipline": "Fingerprint Examination",
                "standard": "SWGFAST; FBI Quality Standards",
                "requirement": "Document in situ before collection; use appropriate development technique for substrate; AFIS comparison followed by human verification",
                "court_acceptance": "Universally accepted when ACE-V methodology followed",
                "defense_challenges": ["Partial print reliability", "Examiner bias", "AFIS false positive rate"],
            },
            {
                "discipline": "DNA Evidence",
                "standard": "SWGDAM; FBI Quality Assurance Standards",
                "requirement": "Separate collection of each sample; prevent cross-contamination; cold storage; CODIS-compatible STR profiling",
                "court_acceptance": "Highest scientific acceptance; mixture interpretation increasingly challenged",
                "defense_challenges": ["Mixed profiles", "Low-template DNA", "Lab contamination", "Touch DNA limitations"],
            },
            {
                "discipline": "Ballistics / Firearms",
                "standard": "SWGGUN; NIBIN protocols",
                "requirement": "Photograph in place; test fire for comparison; NIBIN entry within 48 hours for operational leads",
                "court_acceptance": "Accepted; NRC 2009 report raised concerns about subjective comparison",
                "defense_challenges": ["Subjectivity of toolmark comparison", "Error rate disclosure"],
            },
        ],
    }
    out = RAW_DIR / "forensic_standards_schema.json"
    out.write_text(json.dumps(schema, indent=2))
    print(f"Created forensic standards schema → {out}")


if __name__ == "__main__":
    fetch_nist_publications()
    create_forensic_standards_schema()
    print("\n✓ NIST standards collection complete.")
