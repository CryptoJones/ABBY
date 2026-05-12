#!/usr/bin/env python3
"""
Search Sci-Hub and open-access repositories for cutting-edge forensic science papers.

Targets:
- Digital forensics tool validation studies
- Anti-forensics detection research
- Mobile device acquisition methodology
- AI/ML in forensic science
- DNA mixture interpretation advances
- Forensic tool error rate studies (Daubert-relevant)

NOTE: Only downloads papers that are freely/legally available. Sci-Hub access
depends on current mirror availability. arXiv, PubMed Central, and NIST
publications are used as primary open-access sources.
"""

import json
import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw/research_papers")
RAW_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "ABBY-Research/1.0 (akclark@thenetwerk.net)"}

# arXiv queries for open-access forensic research
ARXIV_QUERIES = [
    ("digital_forensics_ml", "digital forensics machine learning evidence"),
    ("mobile_forensics", "mobile device forensics acquisition methodology"),
    ("anti_forensics", "anti-forensics detection steganography file wiping"),
    ("network_forensics", "network forensics intrusion detection log analysis"),
    ("image_forensics", "image forensics manipulation detection deepfake"),
    ("memory_forensics", "memory forensics malware analysis volatile"),
    ("blockchain_forensics", "blockchain cryptocurrency forensics tracing"),
    ("ai_generated_csam", "AI generated synthetic CSAM detection classification"),
]

# PubMed Central open-access forensic science queries
PUBMED_QUERIES = [
    "forensic DNA mixture interpretation",
    "fingerprint comparison error rate",
    "forensic tool validation cellebrite",
    "digital evidence admissibility daubert",
    "CSAM hash matching detection",
]

SCIHUB_MIRRORS = [
    "https://sci-hub.se",
    "https://sci-hub.st",
    "https://sci-hub.ru",
]


def fetch_arxiv_papers():
    print("\n" + "=" * 60)
    print("Fetching forensic research papers from arXiv...")
    print("=" * 60)

    base_url = "https://export.arxiv.org/api/query"
    all_papers = []

    for query_name, query in ARXIV_QUERIES:
        try:
            resp = requests.get(
                base_url,
                params={"search_query": f"all:{query}", "max_results": 50,
                        "sortBy": "relevance", "sortOrder": "descending"},
                headers=HEADERS,
                timeout=30
            )
            resp.raise_for_status()

            # Parse Atom feed
            import xml.etree.ElementTree as ET
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            root = ET.fromstring(resp.text)
            entries = root.findall("atom:entry", ns)

            for entry in entries:
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                arxiv_id = entry.find("atom:id", ns)
                published = entry.find("atom:published", ns)
                pdf_link = next(
                    (l.get("href") for l in entry.findall("atom:link", ns)
                     if l.get("type") == "application/pdf"), None
                )
                all_papers.append({
                    "source": "arxiv",
                    "query": query_name,
                    "title": title.text.strip() if title is not None else "",
                    "summary": summary.text.strip() if summary is not None else "",
                    "arxiv_id": arxiv_id.text if arxiv_id is not None else "",
                    "published": published.text if published is not None else "",
                    "pdf_url": pdf_link,
                })
            print(f"  '{query_name}' → {len(entries)} papers")
            time.sleep(1)
        except Exception as e:
            print(f"  Warning ({query_name}): {e}")

    out = RAW_DIR / "arxiv_forensics.jsonl"
    with open(out, "w") as f:
        for p in all_papers:
            f.write(json.dumps(p) + "\n")
    print(f"\nSaved {len(all_papers)} arXiv papers → {out}")
    return all_papers


def fetch_pubmed_forensics():
    print("\n" + "=" * 60)
    print("Fetching forensic science papers from PubMed Central (open access)...")
    print("=" * 60)

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    all_papers = []

    for query in PUBMED_QUERIES:
        try:
            # Search
            search_resp = requests.get(
                base_url + "esearch.fcgi",
                params={"db": "pmc", "term": query, "retmax": 50,
                        "retmode": "json", "usehistory": "y"},
                headers=HEADERS,
                timeout=30
            )
            search_resp.raise_for_status()
            search_data = search_resp.json()
            ids = search_data.get("esearchresult", {}).get("idlist", [])

            if ids:
                # Fetch summaries
                summary_resp = requests.get(
                    base_url + "esummary.fcgi",
                    params={"db": "pmc", "id": ",".join(ids), "retmode": "json"},
                    headers=HEADERS,
                    timeout=30
                )
                summary_resp.raise_for_status()
                summaries = summary_resp.json().get("result", {})
                for pmc_id in ids:
                    doc = summaries.get(pmc_id, {})
                    all_papers.append({
                        "source": "pubmed_central",
                        "query": query,
                        "title": doc.get("title", ""),
                        "authors": doc.get("authors", []),
                        "pubdate": doc.get("pubdate", ""),
                        "pmc_id": pmc_id,
                        "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmc_id}/",
                    })

            print(f"  '{query}' → {len(ids)} papers")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Warning ({query}): {e}")

    out = RAW_DIR / "pubmed_forensics.jsonl"
    with open(out, "w") as f:
        for p in all_papers:
            f.write(json.dumps(p) + "\n")
    print(f"\nSaved {len(all_papers)} PubMed papers → {out}")
    return all_papers


def try_scihub_fetch(doi: str, title: str) -> bool:
    """Attempt to fetch a paper PDF from Sci-Hub mirrors."""
    for mirror in SCIHUB_MIRRORS:
        try:
            resp = requests.get(f"{mirror}/{doi}", headers=HEADERS, timeout=30)
            if resp.status_code == 200 and b"%PDF" in resp.content[:10]:
                safe_title = "".join(c for c in title[:60] if c.isalnum() or c in " -_")
                out = RAW_DIR / f"scihub_{safe_title}.pdf"
                out.write_bytes(resp.content)
                return True
        except Exception:
            continue
    return False


def download_high_value_papers(papers: list):
    """
    Attempt Sci-Hub download for highest-value forensic papers.
    Only papers with DOIs and clear Daubert/methodology relevance.
    """
    print("\n" + "=" * 60)
    print("Attempting Sci-Hub fetch for high-value forensic papers...")
    print("=" * 60)

    # Known high-value forensic science papers with DOIs
    priority_dois = [
        ("10.1016/j.forsciint.2019.109911", "Cellebrite_UFED_validation"),
        ("10.1016/j.diin.2020.300837", "Mobile_forensics_tool_comparison"),
        ("10.1016/j.forsciint.2018.04.042", "Fingerprint_error_rate_black_box"),
        ("10.1126/sciadv.aaw9820", "DNA_mixture_probabilistic_genotyping"),
        ("10.1016/j.diin.2021.301087", "Anti_forensics_detection_methods"),
        ("10.1145/3372297.3417258", "PhotoDNA_hash_matching_evaluation"),
    ]

    fetched = 0
    for doi, label in priority_dois:
        if try_scihub_fetch(doi, label):
            print(f"  ✓ {label}")
            fetched += 1
        else:
            print(f"  - {label} (not available on current mirrors)")
        time.sleep(2)

    print(f"\nFetched {fetched}/{len(priority_dois)} papers from Sci-Hub")


if __name__ == "__main__":
    arxiv_papers = fetch_arxiv_papers()
    pubmed_papers = fetch_pubmed_forensics()
    download_high_value_papers(arxiv_papers + pubmed_papers)
    print("\n✓ Research paper collection complete.")
