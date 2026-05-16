# AI Cloud Security Remediation Copilot — MVP

This repository contains a minimal FastAPI backend that demonstrates parsing a Checkov JSON report, summarizing failed IaC security checks by severity, and generating plain-English remediation guidance.

## Structure

- [backend/main.py](backend/main.py)
- [backend/sample_checkov_report.json](backend/sample_checkov_report.json)
- [backend/requirements.txt](backend/requirements.txt)
- [reports/sample-remediation-report.md](reports/sample-remediation-report.md)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)

## Setup (local)

1. Create a Python 3.11+ virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate    # Windows (Powershell)
```

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Run the API locally:

```bash
uvicorn backend.main:app --reload --port 8000
```

4. Query the sample analysis endpoint:

```bash
curl http://127.0.0.1:8000/analyze
```

The `/analyze` endpoint loads the sample Checkov report at `backend/sample_checkov_report.json`, parses failed checks, returns a severity summary, and adds simple, human-friendly remediation suggestions.

## Testing file upload via /docs (Swagger UI)

1. Start the API as above:

```bash
uvicorn backend.main:app --reload --port 8000
```

2. Open the interactive docs at `http://127.0.0.1:8000/docs`.

3. Use the `POST /analyze/upload` endpoint, choose `file` and upload `backend/sample_checkov_report.json`, then click `Execute` to see the parsed findings and remediation text.

You can also test upload with `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/analyze/upload" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@backend/sample_checkov_report.json;type=application/json"
```

If an invalid JSON file is uploaded the API will return HTTP 400 with a clear error message.

## Notes & Next Steps

- This MVP is intentionally simple and beginner-friendly. Next improvements could include:
  - Accepting uploaded reports or report paths via the API
  - Richer remediation templates and links to docs
  - Authentication and logging

