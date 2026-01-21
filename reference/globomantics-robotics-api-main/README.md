# Globomantics Robotics Control API 🤖

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/timothywarner-org/globomantics-robotics-api/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/timothywarner-org/globomantics-robotics-api/tree/main) [![Release](https://github.com/timothywarner-org/globomantics-robotics-api/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/timothywarner-org/globomantics-robotics-api/actions/workflows/release.yml)

> **Pluralsight Course Demo:** Master CircleCI pipelines with a real-world Node.js API

Welcome to the Globomantics Robotics Control API! This project serves as the hands-on companion to the Pluralsight CircleCI course. You'll use this fully functional REST API to learn CI/CD concepts in a practical, engaging way.

## What You're Building

Globomantics (our fictional robotics company) needs a control system for their robot fleet. This API lets you:

- **Register robots** into the fleet with unique identifiers
- **Execute commands** like move, rotate, grab, and release
- **Monitor battery levels** that drain realistically with usage
- **Calibrate sensors** including temperature, proximity, and pressure
- **Manage the fleet** with full CRUD operations

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/globomantics-robotics-api.git
cd globomantics-robotics-api
npm install

# Start the server
npm start
# API running at http://localhost:3000

# Run tests
npm test
```

## API Reference

### Health Check
```bash
GET /health
# Returns: { "status": "healthy", "timestamp": "..." }
```

### Register a Robot
```bash
POST /api/robots
Content-Type: application/json

{
  "name": "Atlas-7",
  "type": "arm",          # arm, manipulator, or mobile
  "location": "Factory Floor A"
}
```

### Execute Commands
```bash
POST /api/robots/:id/command
Content-Type: application/json

# Movement (mobile robots)
{ "command": "move", "direction": "forward" }
{ "command": "rotate", "degrees": 90 }
{ "command": "stop" }

# Manipulation (arm/manipulator robots)
{ "command": "grab" }
{ "command": "release" }

# Battery management
{ "command": "charge" }
```

### Calibrate Sensors
```bash
POST /api/robots/:id/calibrate
# Recalibrates temperature, proximity, and pressure sensors
```

### Other Endpoints
```bash
GET /api/robots           # List all robots
GET /api/robots/:id       # Get specific robot
DELETE /api/robots/:id    # Remove robot from fleet
```

---

## CircleCI Course Content

This project demonstrates key CircleCI concepts you'll master in the course:

### Pipeline Architecture

```
┌──────────────┐
│ install-deps │ ← Caches node_modules for speed
└──────┬───────┘
       │
       ├──────────────┬─────────────────┐
       ▼              ▼                 ▼
┌──────────┐   ┌───────────┐   ┌─────────────────┐
│   lint   │   │ test-unit │   │ test-integration│
└────┬─────┘   └─────┬─────┘   └────────┬────────┘
     │               │                  │
     └───────────────┴──────────────────┘
                     │
                     ▼
              ┌───────────┐
              │   build   │ ← Creates dist/ artifact
              └─────┬─────┘
                    │
       ┌────────────┴────────────┐
       ▼                         ▼
┌──────────────┐         ┌──────────────────┐
│deploy-staging│         │hold-for-approval │ ← Manual gate
│(all branches)│         │  (main only)     │
└──────────────┘         └────────┬─────────┘
                                  ▼
                         ┌─────────────────┐
                         │deploy-production│
                         │  (main only)    │
                         └─────────────────┘
```

### Concepts You'll Practice

| Concept | Where It's Used |
|---------|-----------------|
| **Dependency Caching** | `install-deps` job caches npm packages |
| **Workspace Persistence** | node_modules shared across jobs |
| **Parallel Jobs** | lint, unit tests, and integration tests run simultaneously |
| **Artifacts** | Build output and test results stored for download |
| **Branch Filtering** | Different deploy paths for main vs feature branches |
| **Approval Gates** | Manual approval required for production deploys |
| **Test Splitting** | Unit and integration tests run as separate jobs |

### Key Files to Explore

- **`.circleci/config.yml`** - The complete pipeline definition
- **`package.json`** - Script definitions referenced by CircleCI
- **`jest.config`** (in package.json) - Test output configured for CircleCI insights

---

## Development Commands

```bash
# Full test suite with coverage report
npm test

# Watch mode for TDD
npm run test:watch

# Run specific test file
npx jest tests/robot-controller.test.js

# Lint check
npm run lint

# Production build
npm run build
```

## Project Structure

```
├── .circleci/
│   └── config.yml          # ⭐ CircleCI pipeline config
├── src/
│   ├── index.js            # Express server & routes
│   ├── robot-controller.js # Command execution logic
│   ├── sensor-calibration.js # Sensor management
│   └── logger.js           # Winston logging setup
├── tests/
│   ├── api.test.js         # API integration tests
│   ├── robot-controller.test.js
│   ├── sensor-calibration.test.js
│   └── integration/
└── scripts/
    └── build.js            # Build script for dist/
```

## Course Exercises

As you progress through the course, you'll:

1. **Module 1:** Examine the existing pipeline and understand job dependencies
2. **Module 2:** Modify caching strategies and measure build time improvements
3. **Module 3:** Add new test jobs and configure parallelism
4. **Module 4:** Implement branch-based deployment rules
5. **Module 5:** Set up approval workflows and environment variables

---

## Troubleshooting

**Tests failing locally but passing in CI?**
- Ensure you're on Node 18.19: `node --version`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

**CircleCI build not triggering?**
- Check that `.circleci/config.yml` is valid: `circleci config validate`
- Ensure the project is connected in the CircleCI dashboard

**Port 3000 already in use?**
- Kill the process: `npx kill-port 3000`
- Or use a different port: `PORT=3001 npm start`

---

## Tech Stack

- **Runtime:** Node.js 18.19
- **Framework:** Express.js 4.18
- **Testing:** Jest 29 + Supertest
- **Linting:** ESLint 8
- **Logging:** Winston 3
- **CI/CD:** CircleCI 2.1

---

Built with ❤️ for Pluralsight learners | [Report Issues](../../issues)
