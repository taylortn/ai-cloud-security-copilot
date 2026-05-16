# Sample Remediation Report

This report summarizes findings from the sample Checkov JSON and provides simple remediation guidance.

## Summary

- **CRITICAL**: 1
- **HIGH**: 1
- **MEDIUM**: 1

## Findings & Remediation

1. CKV_AWS_79 — IAM role with wildcard permissions (iam_roles.tf)
   - Remediation: Apply least-privilege to IAM roles and remove wildcard permissions (avoid Action: * / Resource: *).

2. CKV_AWS_20 — S3 bucket has public ACL (s3_bucket.tf)
   - Remediation: Enable encryption, block public access, and tighten bucket policies.

3. CKV_AWS_999 — Security group allows 0.0.0.0/0 (security_groups.tf)
   - Remediation: Restrict security group ingress to required CIDR ranges; avoid 0.0.0.0/0 for management ports.
