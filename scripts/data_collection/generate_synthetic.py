#!/usr/bin/env python3
"""
Generate synthetic ABBY training examples covering forensic investigation scenarios.

Produces chat-format examples matching the ABBY response structure without
requiring any external API — all examples are hand-authored from established
forensic standards and methodology.
"""

import json
import random
from pathlib import Path

OUT_DIR = Path("data/synthetic")
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys_path_hack = Path(__file__).parent
import sys
sys.path.insert(0, str(sys_path_hack))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "abby"))
from prompts import SYSTEM_PROMPT


def ex(user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


EXAMPLES = [
    ex(
        "I have a suspect's iPhone seized incident to arrest. How do I acquire it?",
        """**Evidence Type:** Mobile device — Apple iPhone (seized incident to arrest)

**Constitutional Flag:**
⚠ ADMISSIBILITY CONCERN — *Riley v. California*, 573 U.S. 373 (2014) held that a warrant is required to search a cell phone seized incident to arrest, even though the physical device may be lawfully seized. The search incident to arrest exception does NOT extend to cell phone contents. ABBY recommends obtaining a search warrant before any data extraction.

**Recommended Methodology:**
1. Place device in airplane mode or a Faraday bag immediately to prevent remote wipe
2. Document physical condition with photographs before handling
3. Record IMEI, serial number, and device model
4. Obtain a search warrant specifying the data categories to be searched
5. Select acquisition type based on device state:
   - **Logical acquisition** (Cellebrite UFED, Magnet AXIOM): accessible files, call logs, SMS, app data
   - **Full file system** (if device is unlocked or tool supports it): broader file system access
   - **Physical/chip-off** (last resort for locked/damaged devices): full NAND dump
6. Use a write blocker or ensure the tool operates in read-only mode
7. Generate SHA-256 hash of acquisition image before and after

**Required Documentation:**
- Chain-of-custody form from point of seizure
- Search warrant and return
- Evidence receipt
- Acquisition log (tool version, acquisition type, date/time, hash values)
- Photograph of device before and after handling

**Applicable Standards:**
- NIST SP 800-101 Rev 1: Guidelines on Mobile Device Forensics
- Cellebrite UFED validation documentation
- SWGDE Best Practices for Mobile Device Examination

**Legal Framework:**
- *Riley v. California* (2014): warrant required for cell phone search
- 18 U.S.C. § 1030 (CFAA): governs unauthorized computer access
- Fourth Amendment: unlawful search subjects evidence to suppression under *Mapp v. Ohio*

**Admissibility Considerations:**
Logical and file system acquisitions from validated tools (Cellebrite, AXIOM) are routinely admitted. Be prepared to testify to: tool version, validation status, hash verification, and chain of custody. Defense will challenge tool reliability — have validation reports available.

**Tools:** Cellebrite UFED (preferred), Magnet AXIOM, Oxygen Forensic Detective, GrayKey (for passcode recovery)

**Expert Testimony Guidance:** Explain that the device was isolated to prevent data loss, a warrant was obtained, and a validated tool created a forensic copy. Emphasize hash verification as proof the data was not altered.""",
    ),
    ex(
        "We seized a laptop during a search warrant execution. Walk me through the acquisition.",
        """**Evidence Type:** Laptop computer — seized pursuant to search warrant

**Recommended Methodology:**
1. **At the scene:**
   - If powered OFF: do not power on; transport as-is
   - If powered ON: consider live acquisition for volatile data (RAM, running processes) using tools like Magnet RAM Capture or WinPmem before shutdown
   - Photograph the screen, all connected devices, and the physical environment
   - Document all running applications and network connections before shutdown
   - Pull the power cord (do not shut down normally — normal shutdown may trigger encryption or delete temp files)

2. **Lab acquisition:**
   - Remove hard drive or SSD if possible; connect via hardware write blocker (Tableau, WiebeTech)
   - For encrypted drives (BitLocker, FileVault): check for recovery keys in Active Directory or iCloud; check for keys in RAM dump
   - Image using FTK Imager or `dc3dd` to an evidence-grade drive
   - Generate and record MD5 and SHA-256 hash values of the source and image
   - Verify hash match before proceeding to analysis

**Required Documentation:**
- Chain-of-custody form
- Search warrant and inventory
- Evidence tag with case number, item number, seizing officer, date/time
- Acquisition log: examiner, tool and version, hardware serial numbers, hash values, start/end time
- Write blocker make/model and calibration records

**Applicable Standards:**
- NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response
- SWGDE Best Practices for Computer Forensic Examinations
- ISO/IEC 27037: Guidelines for identification, collection, acquisition, and preservation of digital evidence

**Legal Framework:**
- Fourth Amendment: search conducted pursuant to warrant — document scope carefully
- If laptop contains encrypted communications, may implicate *United States v. Warshak* (2010) for email content
- Fifth Amendment may be implicated if compelled decryption is sought (circuit split on this)

**Admissibility Considerations:**
Write blocker use is essential — without it, defense will argue evidence was altered. Hash verification is your integrity proof. FTK Imager and EnCase are the most-accepted tools. Maintain an unbroken chain of custody from seizure to testimony.

**Tools:** FTK Imager (imaging), EnCase or Autopsy (analysis), Tableau/WiebeTech write blockers, Magnet RAM Capture (live acquisition)

**Expert Testimony Guidance:** Walk the jury through the chain: seized → write-blocked → imaged → hash-verified → analyzed. The original drive was never directly accessed after seizure.""",
    ),
    ex(
        "What is the Daubert standard and how does it apply to digital forensics testimony?",
        """**The Daubert Standard — Forensic Expert Testimony in Federal Court**

*Daubert v. Merrell Dow Pharmaceuticals, Inc.*, 509 U.S. 579 (1993) established that federal judges act as gatekeepers for expert testimony. Before a forensic expert may testify, the court must determine that the methodology is scientifically valid.

**The Four Daubert Factors:**
1. **Testability:** Can the technique be tested? Has it been tested?
2. **Peer review and publication:** Has the methodology been subjected to peer review?
3. **Known or potential error rate:** Is there a known error rate? Is it acceptable?
4. **General acceptance:** Is the methodology generally accepted in the relevant scientific community?

**Application to Digital Forensics:**

| Discipline | Daubert Status | Key Issues |
|---|---|---|
| Cellebrite UFED | Generally accepted | Tool validation logs required; version matters |
| FTK / EnCase | Generally accepted | Widely admitted; have validation documentation |
| Fingerprint (ACE-V) | Accepted post-*Llera Plaza* | Must document methodology; error rate disputed |
| DNA (STR profiling) | Well-established | CODIS standards; lab accreditation required |
| Ballistics/toolmarks | Increasingly challenged | Error rate not well-established; know your circuit |
| Cellebrite Physical | Accepted with foundation | Must show tool was validated for that device model |
| Memory forensics (Volatility) | Emerging; less tested | Be prepared for extensive voir dire |

**What to Prepare Before Testifying:**
- Tool validation reports (NIST CFTT reports where available)
- Version number of all tools used
- Training and certification records
- Any known bugs or limitations in the tool version used
- Error rate data for your methodology

**Key Cases:**
- *Daubert* (1993): established the federal standard
- *Kumho Tire v. Carmichael* (1999): Daubert applies to ALL expert testimony, not just scientific
- *United States v. Llera Plaza* (2002): fingerprint testimony survives Daubert with proper foundation
- *Frye v. United States* (1923): still controls in some states (CA, NY, FL, WA, IL)

**Applicable Standards:** NIST Computer Forensics Tool Testing (CFTT) program provides validation reports used in Daubert hearings.""",
    ),
    ex(
        "We have a CSAM case. The suspect's device has encrypted containers. What are my options and what do I need legally?",
        """**Evidence Type:** Encrypted storage containers — CSAM investigation

**Legal Framework First:**
⚠ ADMISSIBILITY CONCERN — Compelled decryption (ordering the suspect to provide a password) implicates the Fifth Amendment. Courts are split:
- Some circuits hold that providing a password is testimonial and protected (*In re Grand Jury Subpoena*, 11th Cir.)
- Others hold that if the government can independently establish the suspect knows the password ("foregone conclusion" doctrine), it may be compelled
- Get prosecutorial guidance before demanding a password

**Technical Options (No Compelled Decryption):**

1. **Check for keys in memory:** If the device was running when seized, a live RAM acquisition may capture encryption keys. VeraCrypt and BitLocker keys have been recovered this way.

2. **Check cloud backups:** iCloud, Google Drive, and Dropbox may have unencrypted or escrow-keyed versions of files. Serve legal process (18 U.S.C. § 2703) on the provider.

3. **BitLocker/FileVault Recovery Keys:**
   - BitLocker: recovery key may be stored in Active Directory or the suspect's Microsoft account
   - FileVault: recovery key may be in iCloud

4. **Dictionary and brute force attacks:**
   - Hashcat, John the Ripper for password hash attacks
   - Passware Kit Forensic for full-disk encryption
   - Only viable for weak passwords

5. **VeraCrypt hidden volumes:** Be aware of plausible deniability — a VeraCrypt volume may contain a hidden volume. Document your methodology carefully.

6. **NCMEC CyberTipline referrals:** If cloud provider detected CSAM via PhotoDNA, the tip and associated metadata may lead to additional evidence without requiring decryption.

**Required Documentation:**
- Search warrant specifically authorizing examination of encrypted containers
- All decryption attempts and methods documented in your examination notes
- If keys recovered from RAM: document the live acquisition methodology and hash values
- Legal process served on cloud providers and responses received

**Hash Matching:**
Before attempting decryption, run known hash values (MD5, SHA-1) from the NCMEC hash database against any unencrypted files. PhotoDNA and perceptual hashing can identify CSAM even in modified files.

**Applicable Statutes:**
- 18 U.S.C. § 2256: definitions
- 18 U.S.C. § 2252A: distribution and possession
- 18 U.S.C. § 2258A: mandatory reporting to NCMEC
- 18 U.S.C. § 2703: Stored Communications Act — legal process for provider records

**Expert Testimony Guidance:** Document every technical step. The defense will argue you modified the evidence attempting to break encryption. Hash the containers before and after every attempt.""",
    ),
    ex(
        "How do I handle bloodstain pattern evidence at a scene?",
        """**Evidence Type:** Bloodstain pattern evidence

**Recommended Methodology:**

**Scene Documentation (before any collection):**
1. Photograph the entire scene in context before touching anything
2. Use a scale/ruler in all close-up photographs
3. Photograph each bloodstain in situ — overview, midrange, and close-up with scale
4. Use a total station or Leica FARO 3D scanner for scene mapping if available
5. Document lighting conditions and any environmental factors that could affect stains

**Analysis (if Bloodstain Pattern Analyst is present):**
- Identify stain types: passive (drips, pools), projected (cast-off, arterial, impact), transfer (contact, wipe, swipe)
- Measure stain width, length, and directionality
- Calculate area of origin for impact spatter (stringing method or HemoSpat software)
- Document all measurements and calculations in contemporaneous notes

**Collection:**
- Swab fresh liquid blood: use sterile swabs, air dry before packaging, package in paper (NOT plastic — prevents mold)
- Dried stains on moveable surfaces: collect the item
- Dried stains on fixed surfaces: swab with sterile swab moistened with distilled water; collect a dry reference swab from the same area
- Always collect a substrate control (swab from unstained area nearby)

**Chain of Custody:**
- Each item: separate paper bag, sealed, labeled with case number, item number, collector, date/time, location
- Biological evidence must be refrigerated or frozen — document storage temperatures
- Log every transfer between examiner, packaging, and laboratory

**Required Documentation:**
- Scene diagram with stain locations
- Photo log
- Evidence collection log with GPS coordinates if outdoor scene
- Substrate control collection
- Refrigeration/freezer log

**Applicable Standards:**
- SWGMAT (Scientific Working Group for Materials Analysis)
- SWGDAM (Scientific Working Group for DNA Analysis Methods): DNA collection from biological evidence
- OSAC Bloodstain Pattern Analysis Subcommittee standards
- Scientific Working Group for Bloodstain Pattern Analysis (SWGSTAIN)

**Admissibility Considerations:**
Bloodstain pattern analysis faces ongoing Daubert scrutiny regarding error rates. DNA from bloodstains is well-accepted. The analyst must be certified (IAI Bloodstain Pattern Analyst certification) and must document their methodology. Defense will challenge interpretation; collection methodology is harder to attack if properly documented.

**Expert Testimony Guidance:** Separate your testimony into two parts: (1) what you observed and collected (factual), and (2) your pattern analysis interpretation (expert opinion). The collection is objective; the interpretation requires your credentials and methodology to be established first.""",
    ),
    ex(
        "What are the chain of custody requirements for digital evidence from seizure to court?",
        """**Chain of Custody — Digital Evidence: Seizure to Courtroom**

Chain of custody documents the continuous, unbroken possession, control, transfer, analysis, and disposition of evidence. For digital evidence, this has two components: **physical** chain of custody (who had the device) and **logical** chain of custody (proof the data was not altered).

**Physical Chain of Custody:**

At every transfer, document:
- Date and time of transfer
- Names of transferring and receiving parties (badge number, agency)
- Condition of evidence at transfer
- Reason for transfer
- Signature of both parties

**Required Documentation at Each Stage:**

| Stage | Documentation Required |
|---|---|
| Seizure | Evidence tag, field notes, photographs, receipt to owner if required |
| Transport | Chain-of-custody form, sealed evidence packaging, vehicle/courier log |
| Evidence storage | Entry in evidence management system (eCOPS, Guardian, Evidence.com), storage location |
| Lab intake | Lab receipt number, examiner assigned, condition noted |
| Examination | Examination notes, tool logs, hash values, write blocker serial number |
| Return to storage | Re-seal documentation, new evidence tag if original compromised |
| Courthouse transfer | Court evidence receipt, case number assigned |

**Logical Chain of Custody (Digital Integrity):**

This is the mechanism that proves you didn't alter the data:

1. **Hash on acquisition:** Generate SHA-256 (preferred) and MD5 of the source media and the forensic image before examination
2. **Verify hash match:** Image hash must match source hash — document this
3. **Work from the image, never the original:** Preserve the original; all analysis is on the forensic copy
4. **Hash on completion:** Re-hash the image after examination to show it was not modified
5. **Tool logs:** FTK, EnCase, Autopsy, and Cellebrite all generate examination logs — preserve them as part of the case file

**Common Chain-of-Custody Failures (Defense Attack Points):**
- Gap in possession documentation
- Evidence stored in improper conditions (digital media in magnetic fields, biological in heat)
- Original device accessed instead of forensic image
- Hash values not recorded or not matching
- Examiner notes missing or incomplete
- Evidence released to another party without documentation

**Legal Significance:**
Chain-of-custody defects go to weight, not always admissibility (jurisdiction-dependent). But a broken chain invites reasonable doubt. In federal court, FRE 901 requires authentication; chain of custody is the primary authentication method for seized evidence.

**Best Practice:** Treat every piece of evidence as if it will be challenged at trial. If you wouldn't want to explain a gap in front of a jury, don't create the gap.""",
    ),
    ex(
        "Can you explain write blockers and when they are legally and technically required?",
        """**Write Blockers — Technical and Legal Requirements**

A write blocker is a hardware or software device that permits read-only access to a storage medium, preventing any write commands from reaching the evidence. It is the single most important tool for preserving digital evidence integrity.

**Why Write Blockers Matter:**

When a storage device is connected to a computer without a write blocker:
- The OS may write to the device (last access timestamps, swap files, mount logs)
- Windows may auto-run and write to the device
- Even read operations can trigger write activity in some file systems

These writes alter the evidence and can invalidate your examination.

**Hardware Write Blockers (preferred):**
- Tableau (Opentext) — industry standard, widely accepted in court
- WiebeTech (CRU) — equally accepted
- These sit between the evidence drive and the forensic workstation
- They intercept and block all write commands at the hardware level
- They do NOT slow read speeds significantly

**Software Write Blockers:**
- Built into FTK Imager, EnCase, and Autopsy
- Acceptable but less preferred — a software bug could theoretically permit a write
- More commonly used for live acquisitions where hardware blockers aren't practical

**Admissibility Implications:**

Courts do not require write blockers as a matter of law, but SWGDE and NIST standards call for their use whenever practical. Without a write blocker:
- Defense will argue the examination modified the evidence
- You must explain what, if anything, was written to the device and why it doesn't affect your findings
- If timestamps or file metadata changed, expect a Daubert challenge

**When Write Blockers Are NOT Practical:**
- Live acquisitions of running systems (RAM capture, triage)
- Mobile device acquisitions (Cellebrite, AXIOM handle this internally via read-only protocols)
- Cloud acquisitions (no physical media to block)
- Network forensics

In these cases, document your methodology thoroughly and note the absence of a hardware write blocker with the reason.

**Applicable Standards:**
- NIST SP 800-86 recommends write blockers for all disk acquisitions
- SWGDE Best Practices require write blocker use or equivalent methodology
- NIST CFTT has tested and published reports on specific write blocker models — cite the applicable report in testimony

**Expert Testimony Guidance:** If challenged, state: "I used a [make/model] hardware write blocker, which is the industry-standard method for preserving evidence integrity. It physically prevents any write command from reaching the drive. The hash values I calculated before and after examination confirm the data was not altered." """,
    ),
    ex(
        "We executed a warrant on a house and found a NAS (network attached storage) device with a RAID array. How do we handle it?",
        """**Evidence Type:** Network Attached Storage (NAS) with RAID array

**Immediate Scene Decisions:**

1. **Is it running?** If yes:
   - Do NOT pull the power — RAID arrays can lose data or degrade on unclean shutdown
   - Photograph all visible drive activity lights
   - If accessible, do a live triage acquisition of the network share before shutdown
   - If possible, gracefully unmount shares and power down using the NAS admin interface
   - Document any network connections (what else is connected to it?)

2. **What RAID level?**
   - RAID 0 (striping): data split across drives; need ALL drives, and they must be reassembled in correct order
   - RAID 1 (mirroring): each drive has full copy; can image either drive independently
   - RAID 5/6 (parity): requires all drives + parity calculation; specialized tools needed
   - Photograph drive bays in situ, label each drive with its bay position before removal

**Acquisition Procedure:**

Option A — Acquire the logical RAID volume (recommended if NAS is running):
- Access the NAS admin interface and create a forensic network share
- Use FTK Imager or `dc3dd` to image the network share to evidence drive
- Hash the acquisition

Option B — Physical acquisition of individual drives:
- Remove each drive and photograph the bay labels
- Write-block each drive individually
- Image each drive with FTK Imager
- Use a RAID reconstruction tool (ReclaiMe, R-Studio, or open-source `mdadm` on Linux) to reassemble the logical volume
- Document the RAID configuration: level, stripe size, disk order

**Required Documentation:**
- Photograph each drive bay with bay number visible
- Label drives: "NAS Drive 1 of 4 — Bay 0" etc.
- Chain of custody for each drive as a separate evidence item
- RAID configuration documentation (screenshot of admin interface if accessible)
- Hash values for each individual drive image AND the reconstructed logical volume

**Legal Considerations:**
- Warrant must cover stored data on the NAS — ensure scope is adequate
- If NAS is accessed over network, verify the warrant covers network-connected storage
- If NAS contains cloud-synced data, separate legal process may be needed for the cloud portion

**Applicable Standards:**
- NIST SP 800-86 addresses RAID and storage systems
- SWGDE covers acquisition of network storage devices

**Tools:** FTK Imager (imaging), ReclaiMe Free RAID Recovery (RAID reconstruction), Autopsy (analysis), `mdadm` (Linux RAID reassembly)

**Expert Testimony Guidance:** Explain that RAID arrays store data across multiple drives and that reassembly requires specialized methodology. Emphasize that you documented every drive's original position and used validated tools to reconstruct the array before examination.""",
    ),
    ex(
        "What is PhotoDNA and how is it used as evidence in CSAM cases?",
        """**PhotoDNA — Hash Matching for CSAM Detection**

**What It Is:**

PhotoDNA is a perceptual hashing technology developed by Microsoft and donated to the National Center for Missing and Exploited Children (NCMEC). Unlike cryptographic hashes (MD5/SHA-256), which change completely if a single pixel is altered, PhotoDNA generates a "fingerprint" of an image's visual content that remains stable across common modifications: resizing, cropping, color adjustment, and format conversion.

**How It Works:**

1. An image is converted to grayscale and divided into a grid
2. Each cell's gradient and intensity values are calculated
3. These values produce a compact numerical "hash" of the visual content
4. This hash is compared against NCMEC's database of known CSAM hashes

**Evidentiary Use:**

| Purpose | Application |
|---|---|
| Platform detection | ISPs, cloud providers, and social media platforms run PhotoDNA on uploaded content and report matches to NCMEC via CyberTipline (mandatory under 18 U.S.C. § 2258A) |
| Law enforcement examination | Cellebrite and other forensic tools integrate PhotoDNA to scan seized devices against the NCMEC hash database |
| Identifying known victims | Matches link images to documented abuse, potentially identifying victims and series |

**Admissibility:**

PhotoDNA matches have been admitted as evidence in federal and state CSAM prosecutions. Key points for testimony:
- PhotoDNA identifies images as matching the visual content of known CSAM — it does not generate a "positive ID" of a specific file
- A match alone is sufficient for probable cause; prosecution typically relies on the actual image as the primary evidence
- Courts have consistently found PhotoDNA reliable under Daubert when the examiner can explain the methodology

**Limitations:**

- PhotoDNA will NOT match previously unknown CSAM (it only identifies known material)
- A highly degraded or heavily modified image may not match
- PhotoDNA cannot distinguish between a CSAM image and a lawfully held forensic reference copy

**Legal Framework:**
- 18 U.S.C. § 2258A: Electronic service providers must report apparent CSAM to NCMEC via CyberTipline
- 18 U.S.C. § 2258B: Providers acting in good faith are immune from liability
- NCMEC CyberTipline reports are not subject to Fourth Amendment protections (no reasonable expectation of privacy in files shared with a third-party platform — *Smith v. Maryland* third-party doctrine)

**Expert Testimony Guidance:** Explain that PhotoDNA works like a visual fingerprint. The technology is peer-reviewed, deployed at scale by Microsoft, Google, and Apple, and integrated into NCMEC's detection infrastructure. Emphasize that you compared the images on the defendant's device against a database of confirmed CSAM maintained by NCMEC.""",
    ),
    ex(
        "How do I preserve volatile evidence on a running Windows system before shutdown?",
        """**Evidence Type:** Volatile digital evidence — live Windows system

**Why Volatile Evidence Matters:**

When a computer is powered off, volatile data is permanently lost:
- RAM contents (running processes, network connections, encryption keys, logged-in user sessions)
- Active network connections
- Clipboard contents
- Decrypted versions of encrypted files (if volumes are mounted)
- Temporary files in memory

**Live Acquisition Methodology:**

Perform in this order — faster-volatility data first:

1. **System date and time** (note before anything else — timestamps depend on clock accuracy)
2. **RAM acquisition:**
   - Magnet RAM Capture (free, widely accepted)
   - WinPmem (open source)
   - Belkasoft RAM Capturer
   - Write to a write-protected USB or network share — NEVER write to the suspect system
3. **Running processes:** `tasklist /v > processes.txt` or use Sysinternals Process Explorer
4. **Network connections:** `netstat -ano > connections.txt`
5. **Logged-in users:** `query user`
6. **Mapped drives and shares:** `net use`, `net share`
7. **Scheduled tasks:** `schtasks /query /fo LIST /v > tasks.txt`
8. **Prefetch and recent files:** automated by forensic tools, but note that Windows prefetch updates on access
9. **Clipboard:** screenshot or programmatic capture
10. **Mounted encrypted volumes:** identify VeraCrypt, BitLocker mounts before shutdown

**After RAM Acquisition:**

Shut down cleanly ONLY if:
- No encrypted volumes that would lock on shutdown (if present, image first)
- No evidence of active network exfiltration that needs network logs

Otherwise, pull power cord immediately after RAM capture to prevent destruction of temporary files.

**Required Documentation:**
- Time-stamped notes for every action taken on the live system
- Hash values of all captured files
- The commands run (document with `doskey /history` or screen recording)
- Name and version of all tools used
- Chain of custody for the USB drive used to run tools

**Critical Principle:** Every action on a live system changes it. Document what you changed and why. Defense will argue you contaminated the evidence; your contemporaneous documentation is the rebuttal.

**Applicable Standards:**
- NIST SP 800-86: Chapter 2 covers volatile data collection
- RFC 3227: Guidelines for Evidence Collection and Archiving (documents volatility order)

**Legal Considerations:**
The live system examination is still governed by your warrant. Ensure the warrant's scope covers examination of running processes and network connections — some warrant applications are limited to "stored" data.

**Tools:** Magnet RAM Capture, WinPmem, Sysinternals Suite (Process Explorer, TCPView, Autoruns), FTK Imager (for imaging after RAM capture)""",
    ),
    ex(
        "We have DNA evidence from a cold case from 1995. What are the limitations I need to know?",
        """**Evidence Type:** Biological evidence from cold case — 1995

**Degradation and Preservation Issues:**

DNA degrades over time. The degree of degradation depends on storage conditions:
- Properly frozen biological samples can yield usable DNA decades later
- Samples stored at room temperature with exposure to heat, humidity, or light degrade rapidly
- Paper packaging (correct) vs. plastic packaging (incorrect — promotes bacterial growth and mold)

**What to Expect in a 1995 Sample:**

1. **Quantity:** Reduced DNA yield. May require low-template (LT-DNA) or touch DNA techniques
2. **Quality:** Fragmented DNA strands produce partial profiles — fewer loci detected
3. **Contamination:** 30 years of storage increases risk of environmental contamination from handling, storage, and prior examinations
4. **Prior examinations:** If the sample was previously tested using older methods (RFLP — the standard pre-PCR technique), some sample may have been consumed

**Technology Change — RFLP vs. STR:**

In 1995, many labs used RFLP (Restriction Fragment Length Polymorphism):
- Required larger sample quantities than modern STR profiling
- Results cannot be directly compared to modern CODIS STR profiles
- RFLP profiles are not in CODIS

If original results were RFLP, any sample remaining must be re-tested with STR profiling for CODIS comparison.

**Low-Template DNA Considerations:**

- May require STR amplification using more PCR cycles — increases risk of stochastic effects (allele dropout, allele drop-in, stutter)
- Mixed profiles become harder to interpret
- Defense will challenge the reliability of LT-DNA interpretation — know the SWGDAM guidelines

**Chain of Custody for Cold Cases:**

Locate and document the original evidence log from 1995. Key questions:
- How was it stored? (frozen, refrigerated, room temperature)
- How many times was it accessed and by whom?
- How much sample remains?
- Was it tested, and are those results documented?

**CODIS Submission:**

If a profile is obtained, CODIS requires:
- Minimum 7 CODIS core loci for a partial profile upload
- Full 20-locus profile preferred
- Consult with your state CODIS administrator about cold case partial profile policies

**Applicable Standards:**
- SWGDAM (Scientific Working Group for DNA Analysis Methods): published guidelines for low-template and degraded samples
- NIST OSAC Forensic DNA Subcommittee: current standard of practice
- *Melendez-Diaz v. Massachusetts* (2009): lab analyst may need to testify in person — find the original analyst or current lab director

**Expert Testimony Guidance:** Proactively address degradation in testimony. Explain that degradation is expected after 30 years and that partial profiles are still statistically significant. Have the lab's statistical analysis ready — a partial match at 12 loci can still produce a very high likelihood ratio. Defense will claim contamination; your chain-of-custody documentation is the rebuttal.""",
    ),
    ex(
        "Explain the Stored Communications Act and how it affects how I get data from cloud providers.",
        """**The Stored Communications Act (SCA) — 18 U.S.C. §§ 2701–2713**

The SCA is the primary federal statute governing law enforcement access to electronic communications stored by third-party providers. It applies to email, cloud storage, social media, and any electronic communication stored by a provider.

**Two Categories of Providers:**

1. **Electronic Communication Services (ECS):** Services that provide the ability to send or receive wire or electronic communications (email providers, messaging platforms)
2. **Remote Computing Services (RCS):** Services that provide computer storage or processing to the public (cloud storage, file hosting)

**What Process Is Required:**

| Content/Data Type | Required Process |
|---|---|
| Email or messages in storage **< 180 days** (ECS) | Search warrant (probable cause required) |
| Email or messages in storage **> 180 days** (ECS) | Historically: subpoena. But see *Warshak* — warrant now required in most circuits |
| Non-content records (subscriber info, IP logs, date/time) | Subpoena or court order |
| Content stored in cloud (RCS) | Search warrant or court order |
| Real-time interception | Wiretap order (Title III) — different statute entirely |

**Post-*Warshak* Practice:**

*United States v. Warshak*, 631 F.3d 266 (6th Cir. 2010) held that the SCA's authorization for government access to stored email with only a subpoena violates the Fourth Amendment. Most DOJ guidance now recommends using a warrant for all stored content regardless of age.

**Provider-Specific Process:**
- **Google:** Legal process portal at google.com/transparencyreport; warrants produce Drive, Gmail, location history
- **Apple:** Search warrant for iCloud content; Apple publishes a law enforcement guidelines document
- **Meta (Facebook/Instagram):** Legal process at facebook.com/records; warrant for message content
- **Microsoft:** Responds to warrants for Outlook, OneDrive, Teams content
- **Snapchat:** Limited retention; most content deleted; warrants may yield metadata only

**Key Provisions:**
- **§ 2703(d) Order:** Requires government to show "specific and articulable facts" that records are relevant — lower than probable cause, higher than subpoena
- **§ 2703(f) Preservation Letter:** Providers must preserve records for 90 days (renewable) upon law enforcement request — send this immediately before the account is deleted
- **§ 2705 Delayed Notice:** Court may order provider not to notify subscriber (non-disclosure order)

**Practical Steps:**
1. Send a preservation letter (§ 2703(f)) immediately — this stops deletion
2. Serve appropriate legal process based on content/non-content and provider type
3. Allow 1–4 weeks for provider response (varies by provider and volume)
4. Review the legal process review policy for foreign-based providers (MLAT may be required)

**Expert Testimony Guidance:** You do not typically testify about the SCA — the provider's records custodian does. Your role is to authenticate the records received and analyze their contents. The records custodian's certification (business records exception, FRE 902(11)) is what gets the records into evidence.""",
    ),
    ex(
        "I seized a device I think has been wiped. How do I recover deleted files?",
        """**Evidence Type:** Storage device — suspected wiped or deleted data

**Understanding How Deletion Works:**

On most file systems, "deleting" a file does not erase the data — it marks the space as available for reuse and removes the directory entry. The actual data remains until overwritten. Recovery success depends on:
- How much has been written to the device since deletion
- Whether a secure wipe tool was used
- The file system type and how it handles deletion

**File System-Specific Recovery:**

| File System | Recovery Likelihood | Notes |
|---|---|---|
| NTFS (Windows) | High if not overwritten | $MFT records persist; file carving from unallocated space |
| FAT32/exFAT (USB, SD cards) | Moderate | Directory entries zeroed, but data often remains |
| APFS (Apple, SSD) | Lower | APFS uses copy-on-write and encrypts by default; TRIM may zero deleted blocks |
| ext4 (Linux) | Moderate | Journal may contain fragments; file carving effective |
| SSD with TRIM enabled | Low to very low | TRIM instructs the drive to zero deleted blocks immediately — data often unrecoverable |

**Recovery Methodology:**

1. **File system analysis:** Examine unallocated space, deleted directory entries, and file system metadata (MFT on NTFS, journal on ext4)
2. **File carving:** Tools like Foremost, Scalpel, or PhotoRec scan raw unallocated space for file signatures (magic bytes) regardless of file system structure — effective even when directory entries are gone
3. **Volume shadow copies (Windows):** VSS may contain older versions of files. `vssadmin list shadows` to enumerate
4. **Slack space:** Data may persist in file slack (space between end of file and end of cluster)
5. **Pagefile/hibernation file:** Windows pagefile.sys and hiberfil.sys may contain fragments of previously open files
6. **Browser artifacts:** Even if files are deleted, browser history, thumbnails, and cache may corroborate access

**Secure Wipe Detection:**

If a wipe tool was used, you may find evidence of it:
- Prefetch files for wipe tools (CCleaner, Eraser, SDelete)
- Registry entries for tool installation and execution
- Event logs showing file deletion patterns
- Overwrite patterns (all zeros, all ones, or DoD 5220.22-M patterns in unallocated space)
- Document that you found evidence of wiping — it may be relevant to consciousness of guilt

**When Recovery Is Unlikely:**
- SSD with TRIM (data zeroed by firmware)
- Full-disk format (not quick format)
- Encryption with key destruction (secure erase on self-encrypting drives)
- Multiple-pass DoD wipe

Document your recovery attempts and their results even if recovery fails. The jury should understand that the absence of evidence is not evidence of innocence — it may be evidence of wiping.

**Tools:** Autopsy (file carving, deleted file recovery), FTK (carved files, email recovery), Recuva (quick deleted file check), PhotoRec (signature-based carving), Volatility (memory artifacts)

**Expert Testimony Guidance:** Explain that deletion does not equal erasure. Show the jury what was recovered and how. If a wipe tool was found, present that evidence — intent to destroy evidence is relevant to the case.""",
    ),
]


def write_synthetic():
    out_path = OUT_DIR / "forensic_qa.jsonl"
    with open(out_path, "w") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex) + "\n")
    print(f"✓ Synthetic examples: {len(EXAMPLES)} → {out_path}")
    return EXAMPLES


if __name__ == "__main__":
    print("Generating ABBY synthetic training examples...\n")
    write_synthetic()
    print("\n✓ Synthetic data generation complete.")
