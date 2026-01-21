# 🧪 M4 Demo Flow: **Operational Dependency Security**

**Duration:** ~7 minutes
**Focus:** Policy as code, CI/CD enforcement, Snyk integration, automation scripts, incident response
**Live tools:** Edge, VS Code (Win 11), GitHub, GitHub Actions, Snyk.io

---

## 🧠 M4 Learning Objectives Recap (for script grounding)

1. **Create dependency allowlists and security policies**
2. **Integrate scanning into CI/CD workflows**
3. **Document update procedures**
4. **Build incident response plans for zero-day vulnerabilities**

---

## 🎯 M4 Capstone Demo: DevSecOps in Action

---

### 1. Security Policy Deep Dive (Lead Off)

**Narrate:**

> "We start with policy. SECURITY.md sets disclosure, CVSS thresholds, and update windows. Branch protection and rulesets enforce this at scale."

**Show:**

* Open `SECURITY.md` (disclosure, CVSS, update windows)
* Show branch protection/rulesets (status checks, approvals, dependency review)
* Mention allowlists/blocklists if present

---

### 2. Dependency Policy & Automation

**Narrate:**

> "Dependency-review-action blocks PRs with high/critical vulns. Policy as code, enforced in CI."

**Show:**

* `.github/workflows/dependency-review.yml` (fail-on-severity: high/critical)
* Mention org-wide required workflows for coverage

---

### 3. CI/CD Enforcement

**Narrate:**

> "GitHub Actions blocks merges if new dependencies are risky."

**Show:**

* Open a PR with a vulnerable dep, show failed check
* Actions tab: highlight dependency-review-action result

---

### 4. Snyk Integration

**Narrate:**

> "Snyk adds deeper vuln and license analysis, and auto-fix PRs."

**Show:**

* Snyk dashboard: dependency graph, license issues, fix PRs
* Snyk GitHub Action in workflow (if present)

---

### 5. Run Automation Scripts

**Narrate:**

> "We automate dependency hygiene with scripts."

**Show:**

* Run `gh-dependency-toolkit.sh` or `manage-dependabot.sh` live
* Show alerting, auto PRs, or updates

---

### 6. Dashboard Review

**Narrate:**

> "Security dashboard shows current state and improvements."

**Show:**

* Open `security-dashboard-20250607-0801.md` (or latest)
* Show before/after or current state

---

### 7. Zero-Day/Incident Response

**Narrate:**

> "Simulate a Log4Shell-style emergency. Add a critical vuln, open PR, watch it fail."

**Steps:**

1. Open `package.json`, add `log4shell-vuln` (mock or demo CVE)
2. Create branch, push, open PR (show failed checks)
3. Create GitHub Issue tagged Security
4. Mention notification/escalation (Slack/Teams webhook if set up)
5. Show Security tab for org-wide visibility (optional)

---

### 8. Best Practices Recap & Wrap

**Narrate:**

> "Rapid patching, defense-in-depth, automation, and policy as code. Org-wide required workflows scale this."

---

## 🔁 Recap Table (Optional)

| Security Layer        | Tool                        | Result                           |
| --------------------- | --------------------------- | -------------------------------- |
| PR Blocking           | GHAS + dependency-review    | No vulnerable code merges        |
| Continuous Monitoring | Dependabot + GHAS           | Fixes without manual triage      |
| Deep Vuln Analysis    | Snyk                        | Licenses + expanded CVE coverage |
| Policy Enforcement    | SECURITY.md + branch rules  | Consistent behavior across orgs  |
| Incident Response     | GitHub Issues + CI blocking | Documented, coordinated response |

---

**Demo Complete** - M4 operational dependency security showcase ready for enterprise delivery.
