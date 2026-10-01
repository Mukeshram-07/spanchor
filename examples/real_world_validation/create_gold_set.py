#!/usr/bin/env python3
"""
Create a 100-question gold set for CloudSync documentation corpus.

This script:
1. Reads canonical documents
2. Creates 100 realistic questions
3. Identifies source evidence spans in canonical text
4. Creates validated anchors using spanchor
5. Outputs gold.jsonl with all questions and anchors
"""

import json
import sys
from pathlib import Path

# Add src to path to import spanchor
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from spanchor import Anchor, Document
from spanchor.canonical.normalize import compute_hash


def load_documents(corpus_dir: Path) -> dict[str, Document]:
    """Load all documents from corpus directory and canonicalize them."""
    documents = {}
    corpus_files = sorted(corpus_dir.glob("*.txt"))

    for file_path in corpus_files:
        doc_id = file_path.stem  # Use filename without extension
        text = file_path.read_text(encoding="utf-8")
        doc = Document.from_text(doc_id, text)
        documents[doc_id] = doc
        print(f"Loaded {doc_id}: {len(text)} chars -> {len(doc.text)} canonical chars")

    return documents


def find_span(doc: Document, search_text: str) -> tuple[int, int] | None:
    """Find exact span of search_text in canonical document. Returns (start, end) or None."""
    canonical = doc.text
    idx = canonical.find(search_text)
    if idx >= 0:
        return (idx, idx + len(search_text))
    return None


def create_gold_questions(documents: dict[str, Document]) -> list[dict]:
    """Create 100 gold questions with source anchors."""
    questions = []

    # Getting Started questions (25 questions)
    gs_doc = documents["getting_started"]

    questions.extend(
        [
            {
                "query_id": "q001",
                "question": "What is CloudSync?",
                "document_id": "getting_started",
                "search_text": "CloudSync is a distributed file synchronization and backup service designed for teams and enterprises",
            },
            {
                "query_id": "q002",
                "question": "What are the key features of CloudSync?",
                "document_id": "getting_started",
                "search_text": "Real-Time Synchronization",
            },
            {
                "query_id": "q003",
                "question": "How does CloudSync perform synchronization?",
                "document_id": "getting_started",
                "search_text": "CloudSync monitors your source directories and automatically propagates changes to all connected endpoints within milliseconds",
            },
            {
                "query_id": "q004",
                "question": "What encryption does CloudSync use?",
                "document_id": "getting_started",
                "search_text": "All data in transit and at rest is encrypted using AES-256 encryption",
            },
            {
                "query_id": "q005",
                "question": "What operating systems does CloudSync support?",
                "document_id": "getting_started",
                "search_text": "CloudSync works seamlessly across Windows, macOS, Linux, iOS, and Android",
            },
            {
                "query_id": "q006",
                "question": "How does CloudSync optimize bandwidth?",
                "document_id": "getting_started",
                "search_text": "CloudSync uses delta sync technology to transmit only the changed portions of files, reducing bandwidth consumption by up to 95%",
            },
            {
                "query_id": "q007",
                "question": "What Python version is required for CloudSync?",
                "document_id": "getting_started",
                "search_text": "CloudSync requires Python 3.10 or higher",
            },
            {
                "query_id": "q008",
                "question": "How do you install CloudSync?",
                "document_id": "getting_started",
                "search_text": "pip install cloudsync-client",
            },
            {
                "query_id": "q009",
                "question": "What is included in the Free tier of CloudSync?",
                "document_id": "getting_started",
                "search_text": "**Free**: Up to 2 GB of synced data, 2 devices, 30-day version history",
            },
            {
                "query_id": "q010",
                "question": "What version history is available in the Pro tier?",
                "document_id": "getting_started",
                "search_text": "**Pro**: Up to 1 TB of synced data, 10 devices, 90-day version history, $15/month",
            },
            {
                "query_id": "q011",
                "question": "How do you initialize a new CloudSync workspace?",
                "document_id": "getting_started",
                "search_text": 'cloudsync init --name "MyTeam"',
            },
            {
                "query_id": "q012",
                "question": "How do you add directories to CloudSync?",
                "document_id": "getting_started",
                "search_text": "cloudsync add /path/to/data",
            },
            {
                "query_id": "q013",
                "question": "How do you check CloudSync sync status?",
                "document_id": "getting_started",
                "search_text": "cloudsync status",
            },
            {
                "query_id": "q014",
                "question": "How do you invite team members to CloudSync?",
                "document_id": "getting_started",
                "search_text": "cloudsync invite user@example.com",
            },
            {
                "query_id": "q015",
                "question": "What enterprise deployment options does CloudSync offer?",
                "document_id": "getting_started",
                "search_text": "Docker images and Kubernetes Helm charts are available",
            },
            {
                "query_id": "q016",
                "question": "Can you restore files to a previous state?",
                "document_id": "getting_started",
                "search_text": "Every change is tracked with full version history. You can restore any file to any previous state within 90 days of modification",
            },
            {
                "query_id": "q017",
                "question": "Who manages encryption keys in CloudSync?",
                "document_id": "getting_started",
                "search_text": "Encryption keys are managed per workspace and cannot be accessed by CloudSync administrators or any third parties",
            },
            {
                "query_id": "q018",
                "question": "How much bandwidth can CloudSync delta sync save?",
                "document_id": "getting_started",
                "search_text": "reducing bandwidth consumption by up to 95% compared to traditional file transfer methods",
            },
            {
                "query_id": "q019",
                "question": "What is the main purpose of CloudSync?",
                "document_id": "getting_started",
                "search_text": "maintain consistent, up-to-date copies of their critical data across geographically distributed locations",
            },
            {
                "query_id": "q020",
                "question": "What types of data can CloudSync protect?",
                "document_id": "getting_started",
                "search_text": "Whether you're managing project files, databases, or configuration files, CloudSync ensures your data is always protected and accessible",
            },
            {
                "query_id": "q021",
                "question": "What happens when files change in CloudSync?",
                "document_id": "getting_started",
                "search_text": "Changes made on one machine are immediately visible to all team members using the same workspace",
            },
            {
                "query_id": "q022",
                "question": "What compliance does CloudSync require?",
                "document_id": "getting_started",
                "search_text": "This provides both compliance and disaster recovery capabilities",
            },
            {
                "query_id": "q023",
                "question": "Where can you find CloudSync documentation?",
                "document_id": "getting_started",
                "search_text": "Complete documentation is available at https://docs.cloudsync.io",
            },
            {
                "query_id": "q024",
                "question": "How do you contact CloudSync support?",
                "document_id": "getting_started",
                "search_text": "For technical support, contact support@cloudsync.io or visit our community forum",
            },
            {
                "query_id": "q025",
                "question": "What is the relationship between devices and workspaces?",
                "document_id": "getting_started",
                "search_text": "A single workspace can contain devices running different operating systems",
            },
        ]
    )

    # Security and Compliance questions (30 questions)
    sc_doc = documents["security_and_compliance"]

    questions.extend(
        [
            {
                "query_id": "q026",
                "question": "What TLS version does CloudSync use?",
                "document_id": "security_and_compliance",
                "search_text": "All data transmitted between clients and CloudSync servers uses TLS 1.3",
            },
            {
                "query_id": "q027",
                "question": "What is Perfect Forward Secrecy?",
                "document_id": "security_and_compliance",
                "search_text": "Perfect Forward Secrecy (PFS)",
            },
            {
                "query_id": "q028",
                "question": "How are files encrypted at rest in CloudSync?",
                "document_id": "security_and_compliance",
                "search_text": "Files stored in CloudSync datacenters are encrypted using AES-256-GCM",
            },
            {
                "query_id": "q029",
                "question": "How does CloudSync manage encryption keys?",
                "document_id": "security_and_compliance",
                "search_text": "Each workspace uses unique encryption keys that are stored separately from the encrypted data using a hardware security module (HSM)",
            },
            {
                "query_id": "q030",
                "question": "What does Bring Your Own Key (BYOK) mean?",
                "document_id": "security_and_compliance",
                "search_text": "Customers can optionally manage their own encryption keys (Bring Your Own Key - BYOK) using AWS KMS or Azure Key Vault",
            },
            {
                "query_id": "q031",
                "question": "What are CloudSync roles?",
                "document_id": "security_and_compliance",
                "search_text": "CloudSync supports fine-grained RBAC with predefined roles",
            },
            {
                "query_id": "q032",
                "question": "What can an Owner do in CloudSync?",
                "document_id": "security_and_compliance",
                "search_text": "Owner: Full access, can manage billing and team members",
            },
            {
                "query_id": "q033",
                "question": "What can an Admin do in CloudSync?",
                "document_id": "security_and_compliance",
                "search_text": "Admin: Can configure sync rules, invite members, view audit logs",
            },
            {
                "query_id": "q034",
                "question": "What MFA methods does CloudSync support?",
                "document_id": "security_and_compliance",
                "search_text": "MFA using TOTP (Time-based One-Time Password)",
            },
            {
                "query_id": "q035",
                "question": "How long are audit logs retained?",
                "document_id": "security_and_compliance",
                "search_text": "Audit logs are immutable and retained for 2 years",
            },
            {
                "query_id": "q036",
                "question": "What compliance certifications does CloudSync have?",
                "document_id": "security_and_compliance",
                "search_text": "**SOC 2 Type II**",
            },
            {
                "query_id": "q037",
                "question": "Is CloudSync HIPAA compliant?",
                "document_id": "security_and_compliance",
                "search_text": "**HIPAA**: Compliant for healthcare data (PHI - Protected Health Information)",
            },
            {
                "query_id": "q038",
                "question": "Is CloudSync GDPR compliant?",
                "document_id": "security_and_compliance",
                "search_text": "**GDPR**: Full GDPR compliance including data residency options",
            },
            {
                "query_id": "q039",
                "question": "What geographic regions are available in CloudSync?",
                "document_id": "security_and_compliance",
                "search_text": "Available regions include North America, Europe, Asia Pacific, and the Middle East",
            },
            {
                "query_id": "q040",
                "question": "What is the Recovery Time Objective for CloudSync?",
                "document_id": "security_and_compliance",
                "search_text": "recovery time is less than 1 hour for 99% of workspaces",
            },
            {
                "query_id": "q041",
                "question": "What is the Recovery Point Objective for CloudSync?",
                "document_id": "security_and_compliance",
                "search_text": "maximum RPO of 5 minutes",
            },
            {
                "query_id": "q042",
                "question": "How many datacenters replicate CloudSync data?",
                "document_id": "security_and_compliance",
                "search_text": "Data is replicated across at least 3 geographically separate datacenters within each region",
            },
            {
                "query_id": "q043",
                "question": "How often are full backups taken?",
                "document_id": "security_and_compliance",
                "search_text": "full backups are taken every 24 hours",
            },
            {
                "query_id": "q044",
                "question": "What security scanning tools does CloudSync use?",
                "document_id": "security_and_compliance",
                "search_text": "continuously scanned using SAST (Static Application Security Testing) tools",
            },
            {
                "query_id": "q045",
                "question": "How often are security audits conducted?",
                "document_id": "security_and_compliance",
                "search_text": "Third-party security audits are conducted quarterly",
            },
            {
                "query_id": "q046",
                "question": "Does CloudSync have a bug bounty program?",
                "document_id": "security_and_compliance",
                "search_text": "CloudSync maintains an active bug bounty program with a top payout of $50,000",
            },
            {
                "query_id": "q047",
                "question": "Who is responsible for infrastructure security?",
                "document_id": "security_and_compliance",
                "search_text": "Infrastructure security",
            },
            {
                "query_id": "q048",
                "question": "Who is responsible for access control?",
                "document_id": "security_and_compliance",
                "search_text": "Access control and credential management",
            },
            {
                "query_id": "q049",
                "question": "How is SOC 2 Type II audited?",
                "document_id": "security_and_compliance",
                "search_text": "**SOC 2 Type II**: Audited annually by independent third-party auditors",
            },
            {
                "query_id": "q050",
                "question": "What happens when data residency is specified?",
                "document_id": "security_and_compliance",
                "search_text": "Data never leaves the selected region without explicit customer authorization",
            },
            {
                "query_id": "q051",
                "question": "Are backups tested regularly?",
                "document_id": "security_and_compliance",
                "search_text": "Backups are tested monthly to ensure they can be successfully restored",
            },
            {
                "query_id": "q052",
                "question": "What should you do to report a security issue?",
                "document_id": "security_and_compliance",
                "search_text": "security@cloudsync.io",
            },
            {
                "query_id": "q053",
                "question": "What is the maximum incident response time?",
                "document_id": "security_and_compliance",
                "search_text": "CloudSync notifies affected customers within 24 hours",
            },
            {
                "query_id": "q054",
                "question": "How is the incident response plan tested?",
                "document_id": "security_and_compliance",
                "search_text": "incident response plan tested quarterly",
            },
            {
                "query_id": "q055",
                "question": "What is ISO 27001 certification?",
                "document_id": "security_and_compliance",
                "search_text": "**ISO 27001**: Information security management system certification",
            },
        ]
    )

    # API Reference questions (25 questions)
    api_doc = documents["api_reference"]

    questions.extend(
        [
            {
                "query_id": "q056",
                "question": "How do you authenticate with the CloudSync API?",
                "document_id": "api_reference",
                "search_text": "All API requests require authentication using an API token",
            },
            {
                "query_id": "q057",
                "question": "What is the CloudSync API base URL for North America?",
                "document_id": "api_reference",
                "search_text": "North America: https://api.cloudsync.io",
            },
            {
                "query_id": "q058",
                "question": "What is the CloudSync API base URL for Europe?",
                "document_id": "api_reference",
                "search_text": "Europe: https://api.eu.cloudsync.io",
            },
            {
                "query_id": "q059",
                "question": "What is the API endpoint to list workspaces?",
                "document_id": "api_reference",
                "search_text": "GET /api/v1/workspaces",
            },
            {
                "query_id": "q060",
                "question": "What parameters can you pass to list workspaces?",
                "document_id": "api_reference",
                "search_text": "`limit` (optional): Maximum number of results (default: 50, max: 100)",
            },
            {
                "query_id": "q061",
                "question": "How do you get workspace details?",
                "document_id": "api_reference",
                "search_text": "GET /api/v1/workspaces/{workspace_id}",
            },
            {
                "query_id": "q062",
                "question": "What endpoint lists sync items?",
                "document_id": "api_reference",
                "search_text": "GET /api/v1/workspaces/{workspace_id}/items",
            },
            {
                "query_id": "q063",
                "question": "How do you get real-time sync status?",
                "document_id": "api_reference",
                "search_text": "GET /api/v1/workspaces/{workspace_id}/items/{item_id}/status",
            },
            {
                "query_id": "q064",
                "question": "How do you pause synchronization?",
                "document_id": "api_reference",
                "search_text": "POST /api/v1/workspaces/{workspace_id}/items/{item_id}/pause",
            },
            {
                "query_id": "q065",
                "question": "How do you resume synchronization?",
                "document_id": "api_reference",
                "search_text": "POST /api/v1/workspaces/{workspace_id}/items/{item_id}/resume",
            },
            {
                "query_id": "q066",
                "question": "What HTTP status code means success?",
                "document_id": "api_reference",
                "search_text": "200: Success",
            },
            {
                "query_id": "q067",
                "question": "What HTTP status code means unauthorized?",
                "document_id": "api_reference",
                "search_text": "401: Unauthorized (invalid or missing token)",
            },
            {
                "query_id": "q068",
                "question": "What HTTP status code means rate limited?",
                "document_id": "api_reference",
                "search_text": "429: Rate limited (too many requests)",
            },
            {
                "query_id": "q069",
                "question": "What is the rate limit for API requests?",
                "document_id": "api_reference",
                "search_text": "100 requests per minute per API token",
            },
            {
                "query_id": "q070",
                "question": "What is the maximum API request size?",
                "document_id": "api_reference",
                "search_text": "Maximum request size: 10 MB",
            },
            {
                "query_id": "q071",
                "question": "How do you see rate limit status?",
                "document_id": "api_reference",
                "search_text": "Rate limit status is included in response headers",
            },
            {
                "query_id": "q072",
                "question": "What header shows the rate limit reset time?",
                "document_id": "api_reference",
                "search_text": "`X-RateLimit-Reset`: Unix timestamp when limit resets",
            },
            {
                "query_id": "q073",
                "question": "What is the default API token expiration?",
                "document_id": "api_reference",
                "search_text": "default: 90 days",
            },
            {
                "query_id": "q074",
                "question": "Can you revoke API tokens?",
                "document_id": "api_reference",
                "search_text": "can be revoked at any time",
            },
            {
                "query_id": "q075",
                "question": "How do you list sync members?",
                "document_id": "api_reference",
                "search_text": "GET /api/v1/workspaces/{workspace_id}/members",
            },
            {
                "query_id": "q076",
                "question": "What information is in a member object?",
                "document_id": "api_reference",
                "search_text": '"role": "member",',
            },
            {
                "query_id": "q077",
                "question": "What is the maximum items returned per request?",
                "document_id": "api_reference",
                "search_text": "max: 100",
            },
            {
                "query_id": "q078",
                "question": "Does CloudSync support webhooks?",
                "document_id": "api_reference",
                "search_text": "CloudSync supports webhooks for real-time event notifications",
            },
            {
                "query_id": "q079",
                "question": "How many times do webhooks retry?",
                "document_id": "api_reference",
                "search_text": "retry up to 5 times on failure",
            },
            {
                "query_id": "q080",
                "question": "What events trigger webhooks?",
                "document_id": "api_reference",
                "search_text": "Webhook events include sync completion, member invitations, and security alerts",
            },
        ]
    )

    # Troubleshooting questions (20 questions)
    ts_doc = documents["troubleshooting"]

    questions.extend(
        [
            {
                "query_id": "q081",
                "question": "What minimum disk space does CloudSync need?",
                "document_id": "troubleshooting",
                "search_text": "CloudSync requires at least 100 MB of free space to operate",
            },
            {
                "query_id": "q082",
                "question": "How do you fix CloudSync sync not starting?",
                "document_id": "troubleshooting",
                "search_text": "Ensure you have sufficient free disk space",
            },
            {
                "query_id": "q083",
                "question": "How do you set directory permissions for CloudSync?",
                "document_id": "troubleshooting",
                "search_text": "chmod -R u+rw /path/to/directory",
            },
            {
                "query_id": "q084",
                "question": "What minimum network speed does CloudSync need?",
                "document_id": "troubleshooting",
                "search_text": "CloudSync requires at minimum 1 Mbps for reliable operation",
            },
            {
                "query_id": "q085",
                "question": "How do you throttle CloudSync bandwidth?",
                "document_id": "troubleshooting",
                "search_text": "cloudsync config set bandwidth.limit 512KB",
            },
            {
                "query_id": "q086",
                "question": "How do you restart CloudSync?",
                "document_id": "troubleshooting",
                "search_text": "cloudsync stop",
            },
            {
                "query_id": "q087",
                "question": "What command shows detailed CloudSync stats?",
                "document_id": "troubleshooting",
                "search_text": "cloudsync stats --detailed",
            },
            {
                "query_id": "q088",
                "question": "What can slow down large file transfers?",
                "document_id": "troubleshooting",
                "search_text": "Transferring very large files (>10 GB) can take considerable time",
            },
            {
                "query_id": "q089",
                "question": "How long do large file transfers take?",
                "document_id": "troubleshooting",
                "search_text": "may take hours depending on network speed",
            },
            {
                "query_id": "q090",
                "question": "How does antivirus affect CloudSync?",
                "document_id": "troubleshooting",
                "search_text": "Antivirus software scanning files during sync can significantly slow performance",
            },
            {
                "query_id": "q091",
                "question": "What should you do with antivirus for CloudSync?",
                "document_id": "troubleshooting",
                "search_text": "exclude CloudSync directories from real-time scanning",
            },
            {
                "query_id": "q092",
                "question": "How long are API tokens valid?",
                "document_id": "troubleshooting",
                "search_text": "API tokens expire after the configured time period (default 90 days)",
            },
            {
                "query_id": "q093",
                "question": "How do you create a new API token?",
                "document_id": "troubleshooting",
                "search_text": 'cloudsync token create --name "my_token"',
            },
            {
                "query_id": "q094",
                "question": "How do you check your storage quota?",
                "document_id": "troubleshooting",
                "search_text": "cloudsync quota",
            },
            {
                "query_id": "q095",
                "question": "How can you set a custom temporary directory?",
                "document_id": "troubleshooting",
                "search_text": "cloudsync config set temp.dir /path/with/space",
            },
            {
                "query_id": "q096",
                "question": "What should you check if files don't appear on other devices?",
                "document_id": "troubleshooting",
                "search_text": "Verify all devices are connected to the internet",
            },
            {
                "query_id": "q097",
                "question": "What is a conflict file in CloudSync?",
                "document_id": "troubleshooting",
                "search_text": "Conflicted version: `filename.conflict.ext`",
            },
            {
                "query_id": "q098",
                "question": "What information should you include when reporting a problem?",
                "document_id": "troubleshooting",
                "search_text": "support@cloudsync.io with:",
            },
            {
                "query_id": "q099",
                "question": "How do you get CloudSync logs?",
                "document_id": "troubleshooting",
                "search_text": "cloudsync logs --tail 100",
            },
            {
                "query_id": "q100",
                "question": "What excludes prevent unnecessary syncing?",
                "document_id": "troubleshooting",
                "search_text": 'cloudsync exclude "*.tmp" "*.log" "node_modules/" ".git/"',
            },
        ]
    )

    return questions


def create_anchors_for_questions(
    documents: dict[str, Document], questions: list[dict]
) -> list[dict]:
    """Create validated anchors for each question."""
    gold_set = []
    failed_count = 0

    for q in questions:
        doc_id = q["document_id"]
        search_text = q["search_text"]
        doc = documents[doc_id]

        # Find span in canonical text
        span = find_span(doc, search_text)
        if span is None:
            print(f"[WARN] Could not find '{search_text[:50]}...' in {doc_id}")
            failed_count += 1
            continue

        start, end = span
        # Extract the text at this span to verify
        matched_text = doc.text[start:end]

        # Create anchor
        try:
            anchor = Anchor(
                document_id=doc_id,
                start=start,
                end=end,
                expected_text_hash=compute_hash(matched_text),
            )
            # Validate the anchor
            anchor.validate(doc)

            gold_set.append(
                {
                    "schema_version": "0.1.0",
                    "query_id": q["query_id"],
                    "question": q["question"],
                    "anchors": [
                        {
                            "document_id": anchor.document_id,
                            "start": anchor.start,
                            "end": anchor.end,
                            "expected_text_hash": anchor.expected_text_hash,
                        }
                    ],
                }
            )
        except Exception as e:
            print(f"[ERROR] creating anchor for {q['query_id']}: {e}")
            failed_count += 1

    print(f"\n[OK] Created {len(gold_set)} anchors ({failed_count} failed)")
    return gold_set


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    corpus_dir = script_dir / "corpus"
    output_path = script_dir / "gold.jsonl"

    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found at {corpus_dir}")
        sys.exit(1)

    print("Loading documents...")
    documents = load_documents(corpus_dir)

    print("\nCreating 100 gold questions...")
    questions = create_gold_questions(documents)
    print(f"Created {len(questions)} questions")

    print("\nValidating and creating anchors...")
    gold_set = create_anchors_for_questions(documents, questions)

    # Write gold.jsonl
    print(f"\nWriting gold set to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in gold_set:
            f.write(json.dumps(entry) + "\n")

    print(f"\n[OK] Successfully created {len(gold_set)} validated gold entries in {output_path}")


if __name__ == "__main__":
    main()
