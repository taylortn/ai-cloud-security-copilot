from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from collections import Counter

app = FastAPI(title="AI Cloud Security Remediation Copilot - MVP")

# Allow requests from the frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_report(path: Path = None):
    if path is None:
        path = Path(__file__).resolve().parent / "sample_checkov_report.json"
    with path.open() as fh:
        return json.load(fh)


def parse_failed_checks(report: dict):
    # Try several common Checkov JSON shapes
    failed = []
    if isinstance(report.get("results"), dict) and "failed_checks" in report["results"]:
        failed = report["results"]["failed_checks"]
    elif "failed_checks" in report:
        failed = report["failed_checks"]
    elif isinstance(report.get("checks"), list):
        failed = [c for c in report.get("checks", []) if c.get("result") in ("FAILED", "fail")]

    findings = []
    for f in failed:
        findings.append({
            "check_id": f.get("check_id") or f.get("id") or f.get("check_name") or "unknown",
            "check_name": f.get("check_name") or f.get("check") or "",
            "file_path": f.get("file_path") or f.get("resource") or "",
            "severity": (f.get("severity") or f.get("level") or "MEDIUM").upper(),
            "start_line": f.get("start_line"),
            "end_line": f.get("end_line"),
            "message": f.get("message") or f.get("comment") or "",
        })
    return findings


def summarize_by_severity(findings):
    ctr = Counter()
    for f in findings:
        ctr[f.get("severity", "UNKNOWN")] += 1
    return dict(ctr)


def generate_remediation(finding: dict) -> str:
    name = (finding.get("check_name") or "").lower()
    cid = (finding.get("check_id") or "").upper()
    message = (finding.get("message") or "").lower()

    if "s3" in name or "s3" in cid:
        return "Ensure the S3 bucket has encryption enabled, public access blocked, and access policies tightened."
    if "iam" in name or "iam" in cid or "policy" in message:
        return "Apply least-privilege to IAM roles and avoid wildcard permissions (Action: * / Resource: *)."
    if "security group" in name or "0.0.0.0/0" in message or "ingress" in name:
        return "Restrict inbound rules on security groups to required CIDR ranges; avoid 0.0.0.0/0 for management ports."
    if "encryption" in name or "encrypt" in message:
        return "Enable encryption at rest and, where applicable, in transit for this resource."

    return f"Review the resource in {finding.get('file_path')} and address: {finding.get('message') or finding.get('check_name')}."


@app.get("/analyze")
def analyze():
    """Load the sample Checkov report, parse failed checks, and return a simple remediation summary."""
    report = load_report()
    findings = parse_failed_checks(report)
    for f in findings:
        f["remediation"] = generate_remediation(f)

    summary = summarize_by_severity(findings)
    return {
        "summary_by_severity": summary,
        "total_findings": len(findings),
        "findings": findings,
    }


@app.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):
    """Accept an uploaded Checkov JSON file, parse failed checks, and return remediation guidance.

    Returns 400 on invalid JSON with a clear message.
    """
    # Basic content-type hint acceptance but allow common JSON-like uploads
    try:
        content = await file.read()
        report = json.loads(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON file uploaded: {str(e)}",
        )

    findings = parse_failed_checks(report)
    for f in findings:
        f["remediation"] = generate_remediation(f)

    summary = summarize_by_severity(findings)
    remediation_text = "\n".join([f"- {f.get('check_id')}: {f.get('remediation')}" for f in findings])

    return {
        "summary_by_severity": summary,
        "total_findings": len(findings),
        "findings": findings,
        "remediation_text": remediation_text,
    }
