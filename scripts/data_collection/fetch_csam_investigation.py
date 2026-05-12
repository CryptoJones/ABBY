#!/usr/bin/env python3
"""
Fetch CSAM investigation training materials and legal framework for ABBY.

Sources:
- NCMEC CyberTipline reporting requirements (18 U.S.C. § 2258A)
- ICAC Task Force Program guidelines (OJJDP)
- Child exploitation statutes (18 U.S.C. §§ 2252, 2256, 2422, 2423)
- PhotoDNA and hash-matching methodology documentation
- Thorn / NCMEC investigative guidance (publicly available)
- Case law on CSAM investigations, search warrants, undercover operations
"""

import json
import os
import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw/csam_investigation")
CASELAW_DIR = Path("data/raw/caselaw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
CASELAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ABBY-Research/1.0 (akclark@thenetwerk.net)"}

CSAM_STATUTES = [
    {
        "usc": "18 U.S.C. § 2252",
        "title": "Certain activities relating to material involving sexual exploitation of minors",
        "elements": [
            "Knowing transportation, receipt, distribution, or possession",
            "Visual depiction of minor engaged in sexually explicit conduct",
            "Interstate or foreign commerce, or computer",
        ],
        "mandatory_minimum": "5 years (receipt/distribution); 10 years (repeat)",
        "investigation_notes": "Hash matching (PhotoDNA) commonly used for possession/distribution; P2P network monitoring standard",
    },
    {
        "usc": "18 U.S.C. § 2256",
        "title": "Definitions — child pornography",
        "elements": [
            "Minor = under 18",
            "Sexually explicit conduct defined",
            "Visual depiction includes digital/electronic means",
        ],
        "investigation_notes": "Definition section — critical for charging; covers AI-generated CSAM post-PROTECT Act",
    },
    {
        "usc": "18 U.S.C. § 2258A",
        "title": "Reporting requirements of electronic service providers (CyberTipline)",
        "elements": [
            "ESP must report apparent CSAM to NCMEC CyberTipline",
            "Must preserve evidence 90 days pending law enforcement request",
            "Location data and IP address required in report",
        ],
        "investigation_notes": "CyberTipline reports from NCMEC are primary investigative lead; must be corroborated before warrant application",
    },
    {
        "usc": "18 U.S.C. § 2422",
        "title": "Coercion and enticement",
        "elements": [
            "Use of interstate commerce (internet, phone)",
            "Persuade, induce, entice, or coerce",
            "Individual under 18 to engage in sexual activity",
        ],
        "investigation_notes": "Online undercover operations — agent posing as minor; jurisdiction established by interstate communication",
    },
    {
        "usc": "18 U.S.C. § 2423",
        "title": "Transportation of minors",
        "elements": [
            "Transportation of minor in interstate/foreign commerce",
            "With intent minor engage in sexual activity",
        ],
        "investigation_notes": "Travel element key; sting operations — defendant need not actually travel to complete offense",
    },
]

INVESTIGATION_METHODOLOGY = {
    "description": "CSAM investigation methodology standards — training signal for ABBY",
    "phases": [
        {
            "phase": "Initial Lead Development",
            "sources": ["NCMEC CyberTipline report", "P2P network monitoring (ICAC)", "Undercover operations", "Parental/victim report"],
            "documentation": ["CyberTip report number", "IP address and timestamp", "Hash values of reported images", "ESP account information"],
            "legal_notes": "CyberTip alone not sufficient for probable cause; must independently corroborate IP-to-subscriber link",
        },
        {
            "phase": "Subpoena / Legal Process",
            "sources": ["ISP subscriber records (18 U.S.C. § 2703(c) — administrative subpoena)", "ESP account records", "IP geolocation"],
            "documentation": ["Preservation letter sent immediately", "Return of subpoena with subscriber info", "Chain from CyberTip IP to physical address"],
            "legal_notes": "Subscriber info = § 2703(c) subpoena; content requires warrant; Carpenter applies to historical location",
        },
        {
            "phase": "Search Warrant Application",
            "sources": ["Affidavit incorporating CyberTip + ISP return + corroboration"],
            "documentation": ["Probable cause affidavit", "Description of items to be seized (devices, storage media)", "Nexus between device and CSAM"],
            "legal_notes": "Must establish nexus between residence/device and CSAM; collectors tend to retain material (staleness less of an issue); particularity required for digital devices — see Ybarra v. Illinois",
        },
        {
            "phase": "Evidence Seizure",
            "sources": ["On-site triage (if authorized)", "All digital devices, storage media, gaming consoles, smart devices"],
            "documentation": ["Evidence receipt", "Photograph in place before seizure", "Serial numbers documented", "Chain of custody initiated at scene"],
            "legal_notes": "Plain view doctrine applies to observed CSAM during lawful search; scope of warrant governs what may be seized",
        },
        {
            "phase": "Forensic Examination",
            "tools": ["Cellebrite UFED (mobile)", "FTK / EnCase / Autopsy (computers)", "PhotoDNA hash matching", "Internet Evidence Finder (IEF/AXIOM)"],
            "methodology": ["Write-block and hash before examination", "Hash compare known CSAM databases (NCMEC, IWF, Project VIC)", "Document file metadata (creation, access, modification)", "Recover deleted files"],
            "documentation": ["Examination request form", "Hash verification log", "PhotoDNA match report", "Chain-of-custody maintained throughout"],
            "legal_notes": "Hash matching to known CSAM databases provides probable cause and corroboration; examiner must be prepared to testify to methodology",
        },
        {
            "phase": "Victim Identification",
            "sources": ["NCMEC Project VICT", "Interpol ICSE database", "FBI CETS"],
            "documentation": ["Submission of unidentified victim images to NCMEC", "Coordination with ICAC task force"],
            "legal_notes": "Victim identification is separate investigative obligation; examiners should submit unknown victims even if charging is complete",
        },
    ],
    "hash_matching": {
        "description": "PhotoDNA and hash-based CSAM identification",
        "tools": ["Microsoft PhotoDNA", "Project VIC International VICS hash database", "NCMEC hash database", "IWF (Internet Watch Foundation)"],
        "evidentiary_value": "Hash match to known CSAM database is strong corroborating evidence; not conclusive — must view matched file to confirm",
        "court_acceptance": "Widely accepted; examiner must explain hash matching in plain terms; defense may challenge false positive rate",
        "daubert_notes": "PhotoDNA has published error rate; methodology peer reviewed; generally accepted in forensic community",
    },
}


def fetch_icac_guidance():
    print("\n" + "=" * 60)
    print("Fetching ICAC / OJJDP Public Guidance...")
    print("=" * 60)
    urls = [
        ("https://www.ojjdp.gov/programs/antigang/icac.html", "icac_program_overview.html"),
        ("https://www.ncmec.org/cybertipline/", "ncmec_cybertipline.html"),
    ]
    for url, fname in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            out = RAW_DIR / fname
            out.write_bytes(resp.content)
            print(f"  ✓ {fname} ({len(resp.content)//1024}KB)")
        except Exception as e:
            print(f"  Warning ({fname}): {e}")


def fetch_csam_caselaw():
    print("\n" + "=" * 60)
    print("Fetching CSAM Investigation Case Law from CourtListener...")
    print("=" * 60)

    cl_token = os.environ.get("COURTLISTENER_TOKEN", "")
    headers = {**HEADERS, "Authorization": f"Token {cl_token}" if cl_token else ""}

    queries = [
        ("csam_warrant", "child pornography search warrant affidavit probable cause"),
        ("hash_matching_evidence", "photodna hash matching child pornography admissibility"),
        ("p2p_investigation", "peer to peer child pornography investigation"),
        ("cybertip_probable_cause", "cybertipline NCMEC probable cause warrant"),
        ("enticement_undercover", "enticement minor undercover internet 2422"),
        ("csam_sentencing", "child pornography sentencing guidelines 2G2.2"),
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
                print("  CourtListener requires token — set COURTLISTENER_TOKEN env var")
                break
            resp.raise_for_status()
            results = resp.json().get("results", [])
            for r in results:
                all_results.append({
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

    out = CASELAW_DIR / "csam_investigation_caselaw.jsonl"
    with open(out, "w") as f:
        for r in all_results:
            f.write(json.dumps(r) + "\n")
    print(f"\nSaved {len(all_results)} opinions to {out}")


def save_methodology_schema():
    out = RAW_DIR / "csam_investigation_methodology.json"
    out.write_text(json.dumps({
        "statutes": CSAM_STATUTES,
        "methodology": INVESTIGATION_METHODOLOGY,
    }, indent=2))
    print(f"Saved CSAM methodology schema → {out}")


if __name__ == "__main__":
    fetch_icac_guidance()
    save_methodology_schema()
    fetch_csam_caselaw()
    print("\n✓ CSAM investigation data collection complete.")
