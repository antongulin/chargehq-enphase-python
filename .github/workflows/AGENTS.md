<!-- FOR AI AGENTS - Human readability is a side effect, not a goal -->
<!-- Managed by agent: keep sections and order; edit content, not structure -->
<!-- Last updated: 2026-09-23 | Last verified: 2026-09-23 -->

# AGENTS.md — .github/workflows

## Purpose

GitHub Actions workflows for this repository. Currently only `code-review.yml`, which runs the
shared **Robin** PR reviewer on pull requests and `/review` comments. There is no build, test, or
deploy workflow here.

## Ownership

Owned by the repository maintainer. The current workflow calls the same-owner reusable Robin
workflow at the mutable `@main` ref. Keep review logic in the shared workflow and review any ref
change deliberately.

## Local Contracts

- `code-review.yml` calls `antongulin/robin/.github/workflows/review.yml@main` and passes the
  secrets `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` explicitly. Never use `secrets: inherit`.
- Permissions are least-privilege: `actions: read` (required by robin#70), `contents: read`,
  `pull-requests: write`.
- Triggers stay limited to `pull_request` (`opened`, `reopened`, `ready_for_review`) and
  `issue_comment` (`created`).

## Work Guidance

- This is a **public** repository, so GitHub-hosted `ubuntu-latest` runners are free here. The
  Robin review workflow is the explicit Ubicloud exception; other workflows follow the existing
  hosted-runner guidance.
- Keep the three Robin secrets configured as repository secrets. Their names are the contract; do
  not rename or replace them without updating this file and the workflow.
- Changing CI/CD configuration is an ask-first action per the root `AGENTS.md`.

## Verification

- Inspect the parsed workflow after edits: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/code-review.yml'))"`
  (requires PyYAML; otherwise read the file directly).
- Confirm the run outcome on the PR in the Actions tab or with `gh run list --workflow=code-review.yml`.

## Child DOX Index

(none)
