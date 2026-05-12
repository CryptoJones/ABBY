#!/usr/bin/env python3
"""
Fetch federal digital evidence statutes and Fourth Amendment case law for ABBY.

Downloads:
- Computer Fraud and Abuse Act (18 U.S.C. § 1030)
- Electronic Communications Privacy Act (ECPA, 18 U.S.C. §§ 2510-2523)
- Stored Communications Act (SCA, 18 U.S.C. §§ 2701-2713)
- Pen Register Act (18 U.S.C. §§ 3121-3127)
- Key 4th Amendment digital search/seizure case law from CourtListener
"""

import json
import os
import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw/statutes")
CASELAW_DIR = Path("data/raw/caselaw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
CASELAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ABBY-Research/1.0 (akclark@thenetwerk.net)"}

LANDMARK_DIGITAL_CASES = [
    {"case": "Riley v. California", "year": 2014, "citation": "573 U.S. 373",
     "holding": "Warrant required to search cell phone incident to arrest",
     "implication": "No cell phone search without warrant, regardless of arrest"},
    {"case": "Carpenter v. United States", "year": 2018, "citation": "585 U.S. 296",
     "holding": "Warrant required for historical CSLI (cell-site location information)",
     "implication": "Third-party doctrine does not apply to CSLI spanning 7+ days"},
    {"case": "United States v. Jones", "year": 2012, "citation": "565 U.S. 400",
     "holding": "Attaching GPS tracker to vehicle is a Fourth Amendment search",
     "implication": "Physical installation of tracking device requires warrant"},
    {"case": "Kyllo v. United States", "year": 2001, "citation": "533 U.S. 27",
     "holding": "Thermal imaging of home requires warrant",
     "implication": "Technology revealing inside-home information = search"},
    {"case": "United States v. Warshak", "year": 2010, "citation": "631 F.3d 266",
     "holding": "Warrant required for email content (6th Circuit)",
     "implication": "Email has reasonable expectation of privacy; SCA compelled disclosure = 4th Am. violation"},
    {"case": "Katz v. United States", "year": 1967, "citation": "389 U.S. 347",
     "holding": "Fourth Amendment protects people, not places; reasonable expectation of privacy test",
     "implication": "Foundational test for all electronic surveillance"},
    {"case": "Smith v. Maryland", "year": 1979, "citation": "442 U.S. 735",
     "holding": "No REP in numbers dialed (pen register); third-party doctrine",
     "implication": "Basis for SCA pen register provisions — but see Carpenter"},
    {"case": "United States v. Davis", "year": 2015, "citation": "785 F.3d 498",
     "holding": "11th Circuit: historical CSLI obtainable with D-order (pre-Carpenter)",
     "implication": "Superseded by Carpenter for federal investigations"},
]

DIGITAL_STATUTES = [
    ("https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section1030&num=0&edition=prelim",
     "cfaa_1030.html", "CFAA 18 USC 1030"),
    ("https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section2510&num=0&edition=prelim",
     "ecpa_2510.html", "ECPA 18 USC 2510"),
    ("https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section2701&num=0&edition=prelim",
     "sca_2701.html", "SCA 18 USC 2701"),
    ("https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title18-section3121&num=0&edition=prelim",
     "pen_register_3121.html", "Pen Register 18 USC 3121"),
]


def fetch_statutes():
    print("\n" + "=" * 60)
    print("Fetching Digital Evidence Statutes...")
    print("=" * 60)
    for url, fname, title in DIGITAL_STATUTES:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            out = RAW_DIR / fname
            out.write_bytes(resp.content)
            print(f"  ✓ {title} ({len(resp.content)//1024}KB)")
        except Exception as e:
            print(f"  Warning ({title}): {e}")


def fetch_fourth_amendment_caselaw():
    print("\n" + "=" * 60)
    print("Fetching 4th Amendment Digital Case Law from CourtListener...")
    print("=" * 60)

    cl_token = os.environ.get("COURTLISTENER_TOKEN", "")
    headers = {**HEADERS, "Authorization": f"Token {cl_token}" if cl_token else ""}

    queries = [
        ("digital_search_seizure", "fourth amendment digital search seizure warrant"),
        ("cell_phone_warrant", "cell phone search warrant riley california"),
        ("csli_carpenter", "cell site location information carpenter warrant"),
        ("computer_search", "computer search warrant fourth amendment"),
        ("cloud_warrant", "cloud storage email warrant stored communications"),
        ("gps_tracking", "GPS tracking fourth amendment jones"),
        ("cfaa_prosecutions", "computer fraud abuse act 1030 unauthorized access"),
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

    out = CASELAW_DIR / "fourth_amendment_digital.jsonl"
    with open(out, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"\nSaved {len(all_results)} opinions to {out}")

    # Save landmark cases as structured training data
    landmark_out = CASELAW_DIR / "landmark_digital_cases.json"
    landmark_out.write_text(json.dumps({"landmark_cases": LANDMARK_DIGITAL_CASES}, indent=2))
    print(f"Saved landmark digital cases → {landmark_out}")


if __name__ == "__main__":
    fetch_statutes()
    fetch_fourth_amendment_caselaw()
    print("\n✓ Digital statutes and case law collection complete.")
