# Globomantics Robot Fleet Manager V2

**Enterprise Security Demo - GitHub Advanced Security Course**

This is a fictional internal business application for Globomantics Robotics Corporation's robot fleet management system. This application demonstrates **production-grade GitHub Advanced Security** features used by Fortune 500 companies.

## 🎯 Module 3: Automated Dependency Management

This repository showcases the **complete enterprise security pipeline** that 80% of production teams use in the real world:

### 🔒 Enterprise Security Features

✅ **Dependency Review Workflow** (`.github/workflows/dependency.review.yml`)
- Advanced vulnerability filtering (moderate severity threshold)
- License compliance checking (allow/deny lists)
- Automated security reporting in PR comments
- Multi-trigger event handling for efficiency

✅ **Enterprise Dependabot Configuration** (`.github/dependabot.yml`)
- Security-first: Daily vulnerability scans
- Noise reduction: Grouped updates by risk level
- Team workflow: Auto-assign + Copilot reviews
- Smart labeling: `dependencies`, `security`, `automated`
- Risk management: Ignore breaking changes for critical packages

✅ **Production Security Labels**
- 🔵 `dependencies` - All dependency updates
- 🔴 `security` - High-priority security fixes
- 🟣 `automated` - Bot-generated PRs

## ⚠️ IMPORTANT - Educational Use Only

This application contains **intentionally vulnerable dependencies** for security training purposes. **DO NOT use in production environments.**

## Vulnerable Dependencies (For Class Demos)

The following dependencies contain known vulnerabilities for demonstration purposes:

### Original Vulnerable Packages
- `express` 4.17.1 - Various security vulnerabilities
- `lodash` 4.17.20 - Prototype pollution vulnerabilities
- `axios` 0.21.1 - Server-side request forgery vulnerabilities
- `ejs` 3.1.6 - Code injection vulnerabilities
- `moment` 2.29.1 - ReDoS vulnerabilities (deprecated)

### Added for Enhanced Demo
- `debug` 2.6.8 - Known security issues
- `serialize-javascript` 3.0.0 - XSS vulnerabilities
- `handlebars` 4.0.0 - Prototype pollution
- `ws` 5.2.0 - DoS vulnerabilities
- `tar` 4.4.8 - Path traversal issues

## 🚀 Quick Start

```bash
npm install
npm start
```

Visit `http://localhost:3000` to access the Globomantics Robot Fleet Manager.

## 📊 Demo Workflow

1. **Branch Protection** - Main branch protected with required reviews
2. **Dependency Review** - Automated security scanning on PRs
3. **Vulnerability Detection** - 34+ known vulnerabilities flagged
4. **Enterprise Dependabot** - Automated dependency management
5. **Security Dashboard** - Complete visibility into dependency risks

## 🎓 Learning Objectives

This demonstration shows enterprise teams how to:

### Security-First Development
- Implement **daily vulnerability scanning**
- Configure **license compliance** checking
- Set up **automated security reporting**

### Team Workflow Integration
- **Smart PR labeling** for security priorities
- **Grouped dependency updates** to reduce noise
- **Automated reviewer assignment** (including Copilot)

### Risk Management
- **Severity thresholds** for production environments
- **Breaking change protection** for critical packages
- **Vendor restrictions** for trusted registries only

### Production Pipeline
- **Multi-ecosystem support** (NPM + GitHub Actions)
- **Conventional commit messages** for automation
- **Enterprise permission models** (least privilege)

## 🏢 Enterprise Standards Demonstrated

This setup represents **real-world production practices** used by:
- Microsoft Azure DevOps teams
- GitHub's own internal security workflows
- Fortune 500 dependency management strategies
- Open source project security standards

---

**Course:** GitHub Advanced Security - Module 3
**Instructor:** Tim Warner (@timothywarner-org)
**Platform:** Pluralsight

*Globomantics Robotics Corporation - Internal Use Only*
