# 🧪 M3 Demo Flow: Enterprise Dependabot Optimization

---

## 🟢 **1. Context Setup (30 sec)**

**Narrate:**

> “Let’s revisit an open PR in our `globomantics-robot-fleet` repo. This is a class demo branch where we simulate vulnerable dependencies, and demonstrate enterprise-grade security automation.”

**Show:**

* Open PR titled:
  `Bump project version on README to demonstrate branch protection & dependency review`
* Highlight updated version (`1.0.0 → 2.0.0`)
* Mention Copilot AI review for visibility

---

## 🧱 **2. Branch Protection Blocks Merge (60 sec)**

**Narrate:**

> “Notice this PR is *blocked*. One failing check: `Enterprise Dependency Review / 🛡️ Dependency Security Scan`. That’s our GHAS policy kicking in.”

**Show:**

* Failing status check
* Click through the check details to show what triggered it
* Mention that write-access review is also required

---

## 🛡️ **3. Security Alert Visibility (60 sec)**

**Narrate:**

> “Let's dig into *why* this PR is blocked. We introduced known vulnerable packages as a teaching moment.”

**Show:**

* Open `Files Changed` → `package.json`
* Point to suspicious deps (`event-stream`, etc.)
* Open **Security** tab → highlight active **34 alerts**
* Show dependency graph or alert details

---

## 🤖 **4. Enterprise-Grade Dependabot Config (90 sec)**

**Narrate:**

> “We’ve added a production-ready `dependabot.yml` that groups, schedules, and labels PRs to reduce noise.”

**Show:**

* `.github/dependabot.yml` in VS Code
* Point to:

  * `group` config
  * `open-pull-requests-limit`
  * `assignees`, `labels`
* Mention daily/weekly cadence options
* Explain the value of PR consolidation for large orgs

---

## 🔁 **5. Auto-Generated Dependabot PR (60 sec)**

**Narrate:**

> “Here’s a real Dependabot PR that was auto-generated based on that config.”

**Show:**

* Switch to another recent PR (if one exists), or simulate one
* Explain:

  * Auto-created title and branch
  * Labeled as `dependencies`
  * CI auto-runs dependency scan
  * Devs only need to review and merge

---

## 🧠 **6. Optional Add-on: Audit vs. GitHub (60 sec)**

**Narrate:**

> “Let’s compare what we get from local `npm audit` versus GitHub’s centralized alerts.”

**Show:**

* Run `npm audit` in VS Code
* Show that local insight is *limited to the dev*
* Contrast with GitHub’s org-wide visibility + policies

---

## 📈 **7. Dashboard + Risk Posture (60 sec)**

**Narrate:**

> “Finally, GitHub’s **Security Overview** dashboard gives your org the big picture.”

**Show:**

* Org-level or repo-level security dashboard
* CVSS score distribution
* Open vulnerabilities by severity

---

## 🎤 Wrap It Up

> “That’s the value of enterprise-grade Dependabot:
> • Smart updates
> • Alert consolidation
> • Merge blocking
> • Org-wide visibility
> That’s M3 in action.”
