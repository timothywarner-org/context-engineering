# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Globomantics Robotics Control API - a demo Node.js/Express REST API for a Pluralsight CircleCI course. Controls a fictional fleet of robots with command execution and sensor calibration capabilities.

## Common Commands

```bash
# Install dependencies
npm install

# Run the API server (port 3000)
npm start

# Run all tests with coverage
npm test

# Run tests in watch mode
npm run test:watch

# Run only unit tests
npm test -- --testPathPattern=unit --passWithNoTests

# Run only integration tests
npm test -- --testPathPattern=integration --passWithNoTests

# Run a single test file
npx jest tests/robot-controller.test.js

# Lint source and test files
npm run lint

# Create distribution build
npm run build
```

## Architecture

**Stack:** Node.js 18.19 / Express.js / Jest

**Source Structure:**
- `src/index.js` - Express server with REST endpoints, in-memory robot fleet storage (Map-based)
- `src/robot-controller.js` - RobotController class handling command execution (move/stop/rotate/grab/release/charge) with battery management
- `src/sensor-calibration.js` - SensorCalibration class for temperature/proximity/pressure sensor calibration
- `src/logger.js` - Winston logger configuration

**Test Structure:**
- `tests/api.test.js` - API integration tests using supertest
- `tests/robot-controller.test.js` - Unit tests for RobotController
- `tests/sensor-calibration.test.js` - Unit tests for SensorCalibration
- `tests/integration/` - Integration test directory

**API Endpoints:**
- `GET /health` - Health check
- `POST /api/robots` - Register robot (requires name, type, location)
- `GET /api/robots` - List all robots
- `GET /api/robots/:id` - Get robot by ID
- `POST /api/robots/:id/command` - Execute command (move/stop/rotate/grab/release/charge)
- `POST /api/robots/:id/calibrate` - Calibrate robot sensors
- `DELETE /api/robots/:id` - Delete robot

## CircleCI Pipeline

The `.circleci/config.yml` defines an 8-job workflow:

1. `install-deps` → caches node_modules
2. `lint` + `test-unit` + `test-integration` → run in parallel after deps
3. `build` → creates dist/ after tests pass
4. `deploy-staging` → auto-deploys non-main branches
5. `hold-for-approval` → manual gate for main branch
6. `deploy-production` → deploys main after approval

Test results output to `test-results/junit.xml` for CircleCI test insights.
