---
paths:
  - "**/*.tf"
---

# Terraform Conventions

These govern code you write. A repo's existing conventions win, and so does existing code: if something already in a file breaks one of these, assume it's deliberate and mention it rather than changing it.


## Layout

- Two blank lines between top-level blocks. Inside a block, one blank line between logical groups of arguments, never more.
- Three header levels: every file opens with `### Title ###`; `## Section ##` groups blocks within a file; `# Subsection #` groups blocks within a section.


## Comments

- Headers are structure, not comments; the no-comments default covers everything else.
- Never explain what an AWS service or resource does. Comment only a choice a reader would otherwise question: an IAM wildcard, a hop limit, a permission that looks optional but isn't.


## Files

- Every stack has `backend.tf`, `providers.tf`, and `main.tf` (data sources, then locals), plus `variables.tf` and `outputs.tf` when it has any. Once a stack outgrows `main.tf`, resources go in one file per service (`iam.tf`, `s3.tf`, `vpc.tf`).
- State lives in the `jacobfgrant-tfstate` bucket (`us-west-1`, `use_lockfile = true`) under `github/jacobfgrant/<repo>/terraform/<stack>/terraform.tfstate`.
- `templatefile` sources live in `templates/`.


## Resources

Strong defaults. If a case seems to call for something else, say why and ask before deviating.

- Modules: my own where one fits; `terraform-aws-modules/*` for the big pieces (VPC, Lambda, usually S3), never for IAM, security groups, or Route 53; raw resources for everything else. No other third-party modules; the bar for an exception is very high.
- Write IAM policies inline with `jsonencode`; no `data "aws_iam_policy_document"`.
- `name_prefix` rather than `name` on IAM resources and security groups.
- Bucket names end in the account ID.
- Common tags live in `local.tags` and reach resources through the provider's `default_tags`. Tag keys are snake_case; `Name` is the one exception.
- Add a `Name` tag only where it's needed, not on a resource that already carries its own name.


## Variables and Versions

- Variables and outputs lead with `description`; variables then give `type` and any `default`. Add `validation` only where it catches a real failure from outside input.
- `required_version` and `required_providers` go in `providers.tf`. Pin both, and module versions, with `~>`.
