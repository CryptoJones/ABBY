#!/usr/bin/env python3
"""
Fetch forensic science admissibility case law for ABBY training.

Downloads:
- Daubert and Frye admissibility decisions for forensic disciplines
- Suppression orders based on forensic methodology challenges
- Cases involving forensic tool reliability (Cellebrite, FTK, etc.)
- DNA, fingerprint, ballistics admissibility decisions
"""

import json
import os
import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw/caselaw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ABBY-Research/1.0 (akclark@thenetwerk.net)"}

LANDMARK_FORENSIC_CASES = [
    {"case": "Daubert v. Merrell Dow Pharmaceuticals", "year": 1993, "citation": "509 U.S. 579",
     "holding": "Federal courts must gate expert testimony for scientific validity (Daubert standard)",
     "implication": "All forensic methodology must satisfy: testability, peer review, error rate, general acceptance"},
    {"case": "Kumho Tire Co. v. Carmichael", "year": 1999, "citation": "526 U.S. 137",
     "holding": "Daubert applies to all expert testimony, not just scientific",
     "implication": "Forensic experts must satisfy Daubert regardless of discipline"},
    {"case": "Frye v. United States", "year": 1923, "citation": "293 F. 1013",
     "holding": "Expert testimony must be based on generally accepted scientific method",
     "implication": "Still controlling in some states (CA, NY, FL, WA, IL); Daubert controls in federal courts"},
    {"case": "Maryland v. King", "year": 2013, "citation": "569 U.S. 435",
     "holding": "DNA swab at arrest is reasonable search (identification purpose)",
     "implication": "Arrestee DNA collection without warrant upheld"},
    {"case": "District Attorney's Office v. Osborne", "year": 2009, "citation": "557 U.S. 52",
     "holding": "No constitutional right to post-conviction DNA testing",
     "implication": "Access to biological evidence post-conviction governed by state law"},
    {"case": "United States v. Llera Plaza", "year": 2002, "citation": "188 F. Supp. 2d 549",
     "holding": "Fingerprint comparison testimony limited after Daubert challenge (later reversed)",
     "implication": "ACE-V methodology must be documented; examiner must explain error rate"},
]


def fetch_forensic_admissibility_caselaw():
    print("\n" + "=" * 60)
    print("Fetching Forensic Admissibility Case Law...")
    print("=" * 60)

    cl_token = os.environ.get("COURTLISTENER_TOKEN", "")
    headers = {**HEADERS, "Authorization": f"Token {cl_token}" if cl_token else ""}

    queries = [
        ("daubert_forensics", "daubert forensic expert testimony admissibility"),
        ("dna_admissibility", "DNA evidence admissibility reliability"),
        ("fingerprint_daubert", "fingerprint latent comparison daubert admissibility"),
        ("digital_forensics_daubert", "digital forensics cellebrite FTK reliability daubert"),
        ("ballistics_admissibility", "ballistics toolmark firearms comparison admissibility"),
        ("forensic_suppression", "suppression forensic evidence chain of custody"),
        ("cell_phone_extraction", "cell phone extraction forensic tool reliability"),
    ]

    all_results = []
    for query_name, query in queries:
        try:
            resp = requests.get(
                "https://www.courtlistener.com/api/rest/v4/opinions/",
                params={"q": query, "type": "o", "order_by": "score desc",
                        "page_size": 50, "format": "json"},
                headers=headers,
                timeout=30
            )
            if resp.status_code == 401:
                print(f"  CourtListener requires token — set COURTLISTENER_TOKEN env var")
                break
            resp.raise_for_status()
            results = resp.json().get("results", [])
            for r in results:
                all_results.append({
                    "source": "courtlistener",
                    "query": query_name,
                    "case_name": r.get("case_name", ""),
                    "date_filed": r.get("date_filed", ""),
                    "court": r.get("court", ""),
                    "url": r.get("absolute_url", ""),
                    "snippet": r.get("snippet", ""),
                })
            print(f"  '{query_name}' → {len(results)} opinions")
            time.sleep(1)
        except Exception as e:
            print(f"  Warning ({query_name}): {e}")

    out = RAW_DIR / "forensic_admissibility.jsonl"
    with open(out, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"\nSaved {len(all_results)} opinions to {out}")

    landmark_out = RAW_DIR / "landmark_forensic_cases.json"
    landmark_out.write_text(json.dumps({"landmark_cases": LANDMARK_FORENSIC_CASES}, indent=2))
    print(f"Saved landmark forensic cases → {landmark_out}")


if __name__ == "__main__":
    fetch_forensic_admissibility_caselaw()
    print("\n✓ Forensic case law collection complete.")
