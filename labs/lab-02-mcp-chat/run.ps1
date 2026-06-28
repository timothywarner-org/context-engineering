<#
.SYNOPSIS
    On-rails launcher for the Lab 02 MCP Chat reference app.

.DESCRIPTION
    One command takes a clean checkout to a running MCP chat REPL. First run is
    idempotent and does three things:

      1. Creates this lab's .env from .env.example if it does not exist.
      2. Lifts ANTHROPIC_API_KEY from the repo-root .env (the one the rest of the
         course already uses) so you do not paste the key twice.
      3. Hands off to `uv run main.py` from this directory, which lets uv
         auto-create .venv on first invocation (~20s cold, ~1.5s warm after).

    The vendored app code is untouched. This wrapper is the only on-rails bridge;
    the upstream manual workflow in README.md still works unchanged.

.PARAMETER ServerScripts
    Additional MCP server scripts to attach as extra clients (forwarded to
    main.py positional args). Useful for instructor demos that plug in a second
    FastMCP server alongside the bundled mcp_server.py. Optional.

.EXAMPLE
    .\run.ps1
    First run from a clean checkout, assuming repo-root .env has ANTHROPIC_API_KEY.
    Creates this lab's .env, lifts the key, then launches the chat REPL.

.EXAMPLE
    .\run.ps1 -ServerScripts ..\..\src\warnerco\backend\app\mcp_server_entry.py
    Launches the CLI with an additional MCP server attached for a hybrid demo.

.NOTES
    Author: Tim Warner
    The lab expects its own .env in this directory, but the course tells learners
    to keep ONE .env at the repo root. Without a bridge they paste the API key
    twice and the copies drift. This script removes that friction without editing
    vendored code (preserves NOTICE.md fidelity).
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$ServerScripts = @()
)

$ErrorActionPreference = 'Stop'

$labDir   = $PSScriptRoot
$labEnv   = Join-Path $labDir '.env'
$labEnvEx = Join-Path $labDir '.env.example'
# Repo root is two levels up: labs/lab-02-mcp-chat -> labs -> <root>
$repoRoot = Split-Path -Parent (Split-Path -Parent $labDir)
$rootEnv  = Join-Path $repoRoot '.env'

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not on PATH. Install with 'winget install astral-sh.uv' or 'pip install uv', then re-run."
}

# Bootstrap the lab .env only on first run. Idempotent on every subsequent run.
if (-not (Test-Path $labEnv)) {
    if (-not (Test-Path $labEnvEx)) {
        throw "$labEnvEx is missing. The vendored .env.example is the template; restore it from git."
    }
    Copy-Item $labEnvEx $labEnv
    Write-Host "Created $labEnv from .env.example."

    # Lift ANTHROPIC_API_KEY from the repo-root .env if present. One source of
    # truth for the key avoids the two-file drift that bites in dry-runs.
    if (Test-Path $rootEnv) {
        $rootKeyLine = Get-Content $rootEnv |
            Where-Object { $_ -match '^\s*ANTHROPIC_API_KEY\s*=' } |
            Select-Object -First 1

        if ($rootKeyLine) {
            $contents = Get-Content $labEnv
            $patched  = $contents -replace '^\s*ANTHROPIC_API_KEY\s*=.*', $rootKeyLine
            Set-Content -Path $labEnv -Value $patched -Encoding utf8
            Write-Host "Lifted ANTHROPIC_API_KEY from repo-root .env into $labEnv."
        }
        else {
            Write-Warning "Repo-root .env exists but has no ANTHROPIC_API_KEY line. Edit $labEnv before re-running."
        }
    }
    else {
        Write-Warning "No repo-root .env found. Edit $labEnv and set ANTHROPIC_API_KEY, then re-run."
        # Exit so the learner cannot burn tokens on a stub key before noticing.
        exit 1
    }
}

# uv run --directory pins both pyproject discovery and CWD to this lab so
# main.py's load_dotenv() and its `uv run mcp_server.py` subprocess both resolve.
$uvArgs = @('run', '--directory', $labDir, 'main.py') + $ServerScripts
& uv @uvArgs
exit $LASTEXITCODE
