#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import time

LESSON_MAP = {
    135: "Lesson 4.1: Establishing a Baseline for Detection",
    136: "Lesson 3.3: Secure Network Architecture – VLAN Segmentation",
    137: "Lesson 5.3: Incident Response Testing Methods",
    138: "Lesson 4.1: Red, Blue, and Purple Teams",
    139: "Lesson 4.2: Investigating Alerts and False Positives",
    140: "Lesson 4.2: SIEM Tuning",
    141: "Lesson 4.3: Physical Penetration Testing",
    142: "Lesson 3.4: Group Policy and Centralized Management",
    143: "Lesson 1.4: Social Engineering Techniques – Whaling",
    144: "Lesson 2.4: Deception and Threat Intelligence – Honeypots",
    145: "Lesson 4.2: Threat Hunting",
    146: "Lesson 5.2: Incident Response Process – Detection & Analysis",
    147: "Lesson 3.6: High Availability & Load Balancing",
    148: "Lesson 4.1: Red Team Operations",
    149: "Lesson 1.4: Social Engineering – BEC",
    150: "Lesson 5.2: Incident Response Process – Preparation",
    151: "Lesson 5.4: Automation and Orchestration",
    152: "Lesson 1.2: DoS Attacks",
    153: "Lesson 2.5: Email Security Controls",
    154: "Lesson 2.5: DLP Controls",
    155: "Lesson 5.3: Evidence Handling",
    156: "Lesson 4.2: Threat Hunting",
    157: "Lesson 2.5: Data Classification for DLP",
    158: "Lesson 4.3: Penetration Testing Methodologies",
    159: "Lesson 4.2: CVSS Scoring",
    160: "Lesson 5.2: Incident Response Process – Analysis",
    161: "Lesson 5.1: MFA Implementation",
    162: "Lesson 5.3: Backup Types – Image Backups",
    163: "Lesson 5.2: Detective Controls",
    164: "Lesson 5.4: SOAR Platforms",
    165: "Lesson 1.1: Brute Force Attacks",
    166: "Lesson 4.1: Red Team Activities",
    167: "Lesson 5.2: Endpoint Monitoring",
    168: "Lesson 4.4: Exploit Frameworks",
    169: "Lesson 2.2: Fileless Malware",
    172: "Lesson 4.3: Penetration Testing – Unknown Environment (Black Box)",
    173: "Lesson 2.2: Ransomware",
    174: "Lesson 5.1: Access Control Models – Role-Based Access Control (RBAC)",
    175: "Lesson 2.3: Zero-Day Vulnerabilities",
    176: "Lesson 5.1: Access Control Lists (ACLs)",
    177: "Lesson 3.4: Application Security – Static Application Security Testing (SAST)",
    178: "Lesson 1.4: Physical Security Controls – Door Locks",
    179: "Lesson 5.2: Log Analysis – Network Logs",
    180: "Lesson 1.3: Risk Response Strategies – Avoidance",
    181: "Lesson 5.3: Backup Types – Differential Backups",
    183: "Lesson 1.1: Supply Chain Attacks",
    184: "Lesson 2.1: Social Engineering – Pretexting",
    185: "Lesson 2.3: Privilege Escalation",
    186: "Lesson 3.1: Secure Protocols – HTTPS",
    187: "Lesson 5.2: Log Analysis – Firewall Logs",
    188: "Lesson 3.5: Cloud Security Architectures – SASE",
    189: "Lesson 4.2: Advanced SIEM and SOAR Integration",
    190: "Lesson 2.1: Social Engineering – Smishing",
    191: "Lesson 4.2: Incident Response – Log Sources for C2 Detection",
    192: "Lesson 4.2: Incident Response – Log Sources for C2 Detection",
    193: "Lesson 2.2: Rootkits",
    194: "Lesson 5.2: Monitoring – File Integrity Monitoring (FIM)",
    195: "Lesson 4.2: Incident Response – Containment",
    196: "Lesson 2.2: Logic Bombs",
    197: "Lesson 5.3: Backup Types – Full Backups",
    198: "Lesson 5.2: Log Analysis – DNS Logs",
    199: "Lesson 5.1: Identity Federation",
    200: "Lesson 5.1: Single Sign-On (SSO)",
    201: "Lesson 5.3: Disaster Recovery Sites – Hot Site",
    202: "Lesson 5.2: Monitoring – Unified Threat Management (UTM)",
    203: "Lesson 2.1: Phishing",
    204: "Lesson 2.3: DLL Injection",
    205: "Lesson 5.2: Monitoring – IDS vs. IPS",
    206: "Lesson 2.3: ARP Poisoning",
    207: "Lesson 1.2: Security Controls – Compensating Controls",
    208: "Lesson 3.3: Secure Network Architecture – DMZ",
    209: "Lesson 3.1: Secure Protocols – SFTP",
    210: "Lesson 5.1: Biometric Factors",
    211: "Lesson 5.3: Recovery Objectives – RTO and RPO",
    212: "Lesson 5.3: Backup Types – Incremental Backups",
    213: "Lesson 1.4: Security Awareness Training – Tailgating Prevention",
    214: "Lesson 5.3: Data Sovereignty",
    215: "Lesson 2.1: Watering Hole Attacks",
}


def append_lesson(expl: str, tag: str) -> str:
    if not expl:
        return tag
    if tag in expl:
        return expl
    # ensure single space before the tag
    if expl.endswith(" "):
        return expl + tag
    return expl + " " + tag


def main():
    ap = argparse.ArgumentParser(description="Append lesson references to explanations by ID.")
    ap.add_argument("json_file", help="Path to security-operations.json")
    ap.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = ap.parse_args()

    path = args.json_file
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return 1

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print("Unexpected JSON structure (expected a list). Aborting.")
        return 1

    updated = []
    missing_ids = []

    for i, q in enumerate(data):
        qid = q.get("id")
        if not isinstance(qid, int):
            continue
        if qid in LESSON_MAP:
            tag = LESSON_MAP[qid]
            prev = q.get("explanation", "")
            new = append_lesson(prev, tag)
            if new != prev:
                data[i]["explanation"] = new
                updated.append(qid)
        else:
            # Track gaps requested by user that might not exist in file, only if in the range
            pass

    if args.dry_run:
        print(f"Would update {len(updated)} items: {sorted(updated)}")
        return 0

    # Backup
    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(os.path.dirname(path), "backup")
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, f"{os.path.basename(path)}.{ts}.bak")
    shutil.copy2(path, backup_path)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {len(updated)} items. Backup: {backup_path}")
    if updated:
        print("IDs:", ", ".join(str(x) for x in sorted(updated)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
