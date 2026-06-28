---
name: markdownlint config location
description: Always use markdownlint.json at the repo root for this project — do not search for alternates or create a new config
type: feedback
---

Use `markdownlint.json` at the repository root as the markdownlint config for every audit in this project.

**Why:** Tim has standardized on a single config file at the repo root for this project. The agent's default workflow checks for several variants (`.markdownlint.json`, `.markdownlint-cli2.jsonc`, `.markdownlint.yaml`) and falls back to creating a baseline if none are found — that fallback behavior is wrong here.

**How to apply:** When auditing any markdown file in `C:\github\context-engineering`, pass `--config markdownlint.json` (resolved against the repo root) to `markdownlint-cli2` or `markdownlint`. Do not check for `.markdownlint.json` (with the leading dot), do not look at YAML or JSONC variants, and do not create a baseline config from the agent's default template. If the file is missing at the repo root, surface that to Tim rather than auto-creating one.
