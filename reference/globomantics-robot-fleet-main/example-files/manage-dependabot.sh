#!/bin/bash

# Dependabot Management Script using GitHub CLI
# This script provides various commands to manage Dependabot alerts and PRs
# Requires: gh CLI installed and authenticated
# Uses: GITHUB_TOKEN environment variable if set, otherwise uses gh auth

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get current repository (owner/repo format)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
if [ -z "$REPO" ]; then
    echo -e "${YELLOW}Warning: Not in a git repository, some commands may not work${NC}"
    # Try to get from git remote
    REPO=$(git remote get-url origin 2>/dev/null | sed -E 's/.*github.com[:/](.+)\.git/\1/')
fi

echo -e "${BLUE}Dependabot Management for: ${REPO}${NC}"
echo ""

# Function to list all Dependabot alerts
list_alerts() {
    echo -e "${GREEN}Fetching Dependabot alerts...${NC}"
    
    # Get vulnerability alerts using GraphQL
    gh api graphql -f query='
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        vulnerabilityAlerts(first: 100) {
          nodes {
            id
            createdAt
            dismissedAt
            state
            securityVulnerability {
              package {
                name
                ecosystem
              }
              severity
              vulnerableVersionRange
              firstPatchedVersion {
                identifier
              }
            }
            securityAdvisory {
              summary
              description
              cvss {
                score
              }
              identifiers {
                type
                value
              }
            }
          }
        }
      }
    }' -f owner="${REPO%/*}" -f repo="${REPO#*/}" | jq '.'
}

# Function to list Dependabot PRs
list_dependabot_prs() {
    echo -e "${GREEN}Fetching Dependabot PRs...${NC}"
    
    # List open Dependabot PRs
    echo -e "${YELLOW}Open Dependabot PRs:${NC}"
    gh pr list --author "app/dependabot" --state open --json number,title,createdAt,labels --template '{{range .}}#{{.number}} {{.title}} ({{.createdAt}}){{"\n"}}{{end}}'
    
    echo ""
    echo -e "${YELLOW}Recently merged Dependabot PRs (last 30):${NC}"
    gh pr list --author "app/dependabot" --state merged --limit 30 --json number,title,mergedAt --template '{{range .}}#{{.number}} {{.title}} (merged: {{.mergedAt}}){{"\n"}}{{end}}'
}

# Function to auto-merge a Dependabot PR
merge_dependabot_pr() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        echo -e "${RED}Error: PR number required${NC}"
        echo "Usage: $0 merge <pr-number>"
        return 1
    fi
    
    echo -e "${GREEN}Attempting to merge PR #${pr_number}...${NC}"
    
    # Check if PR is from Dependabot
    author=$(gh pr view "$pr_number" --json author -q .author.login)
    if [[ "$author" != "dependabot[bot]" ]] && [[ "$author" != "app/dependabot" ]]; then
        echo -e "${RED}Error: PR #${pr_number} is not from Dependabot (author: ${author})${NC}"
        return 1
    fi
    
    # Enable auto-merge
    gh pr merge "$pr_number" --auto --merge
}

# Function to review and approve a Dependabot PR
approve_dependabot_pr() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        echo -e "${RED}Error: PR number required${NC}"
        echo "Usage: $0 approve <pr-number>"
        return 1
    fi
    
    echo -e "${GREEN}Reviewing PR #${pr_number}...${NC}"
    
    # Add approval review
    gh pr review "$pr_number" --approve --body "Automated approval for Dependabot update"
}

# Function to batch approve all patch updates
batch_approve_patches() {
    echo -e "${GREEN}Finding all Dependabot patch update PRs...${NC}"
    
    # Get all open Dependabot PRs
    prs=$(gh pr list --author "app/dependabot" --state open --json number,title --jq '.[] | select(.title | test("Update .* from .* to .*")) | .number')
    
    for pr in $prs; do
        # Check if it's a patch update (simple heuristic - checking for patch version pattern)
        title=$(gh pr view "$pr" --json title -q .title)
        if echo "$title" | grep -E "from [0-9]+\.[0-9]+\.[0-9]+ to [0-9]+\.[0-9]+\.[0-9]+"; then
            echo -e "${YELLOW}Approving patch update PR #${pr}: ${title}${NC}"
            approve_dependabot_pr "$pr"
            sleep 1 # Rate limiting
        fi
    done
}

# Function to dismiss a Dependabot alert
dismiss_alert() {
    local alert_number=$1
    local reason=$2
    
    if [ -z "$alert_number" ] || [ -z "$reason" ]; then
        echo -e "${RED}Error: Alert number and reason required${NC}"
        echo "Usage: $0 dismiss <alert-number> <reason>"
        echo "Reasons: fix_started, inaccurate, no_bandwidth, not_used, tolerable_risk"
        return 1
    fi
    
    echo -e "${GREEN}Dismissing alert #${alert_number}...${NC}"
    
    # Note: This requires the repository vulnerability alerts write permission
    gh api \
        --method PATCH \
        -H "Accept: application/vnd.github+json" \
        "/repos/${REPO}/dependabot/alerts/${alert_number}" \
        -f state='dismissed' \
        -f dismissed_reason="${reason}" \
        -f dismissed_comment="Dismissed via CLI script"
}

# Function to enable Dependabot security updates
enable_security_updates() {
    echo -e "${GREEN}Enabling Dependabot security updates...${NC}"
    
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/repos/${REPO}/vulnerability-alerts"
    
    # Enable automated security fixes
    gh api \
        --method PUT \
        -H "Accept: application/vnd.github+json" \
        "/repos/${REPO}/automated-security-fixes"
    
    echo -e "${GREEN}Security updates enabled!${NC}"
}

# Function to get Dependabot secrets
list_dependabot_secrets() {
    echo -e "${GREEN}Listing Dependabot secrets...${NC}"
    
    gh api \
        -H "Accept: application/vnd.github+json" \
        "/repos/${REPO}/dependabot/secrets" | jq '.secrets[] | {name: .name, created_at: .created_at, updated_at: .updated_at}'
}

# Function to create a Dependabot secret
create_dependabot_secret() {
    local secret_name=$1
    local secret_value=$2
    
    if [ -z "$secret_name" ] || [ -z "$secret_value" ]; then
        echo -e "${RED}Error: Secret name and value required${NC}"
        echo "Usage: $0 create-secret <name> <value>"
        return 1
    fi
    
    echo -e "${GREEN}Creating Dependabot secret: ${secret_name}${NC}"
    
    # Get the repository public key
    key_info=$(gh api "/repos/${REPO}/dependabot/secrets/public-key")
    key_id=$(echo "$key_info" | jq -r '.key_id')
    key=$(echo "$key_info" | jq -r '.key')
    
    # Encrypt the secret (requires sodium encryption - simplified example)
    # In practice, you'd need proper encryption here
    echo -e "${YELLOW}Note: This is a simplified example. Proper encryption required for production.${NC}"
    
    # This would need proper implementation
    # encrypted_value=$(encrypt_secret "$secret_value" "$key")
    
    # gh api \
    #     --method PUT \
    #     -H "Accept: application/vnd.github+json" \
    #     "/repos/${REPO}/dependabot/secrets/${secret_name}" \
    #     -f encrypted_value="${encrypted_value}" \
    #     -f key_id="${key_id}"
}

# Function to rebase a Dependabot PR
rebase_dependabot_pr() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        echo -e "${RED}Error: PR number required${NC}"
        echo "Usage: $0 rebase <pr-number>"
        return 1
    fi
    
    echo -e "${GREEN}Rebasing PR #${pr_number}...${NC}"
    
    # Add comment to trigger rebase
    gh pr comment "$pr_number" --body "@dependabot rebase"
}

# Function to recreate a Dependabot PR
recreate_dependabot_pr() {
    local pr_number=$1
    
    if [ -z "$pr_number" ]; then
        echo -e "${RED}Error: PR number required${NC}"
        echo "Usage: $0 recreate <pr-number>"
        return 1
    fi
    
    echo -e "${GREEN}Recreating PR #${pr_number}...${NC}"
    
    # Add comment to trigger recreation
    gh pr comment "$pr_number" --body "@dependabot recreate"
}

# Function to generate Dependabot report
generate_report() {
    echo -e "${GREEN}Generating Dependabot report...${NC}"
    
    # Count open PRs
    open_prs=$(gh pr list --author "app/dependabot" --state open --json number | jq '. | length')
    
    # Count by ecosystem
    echo -e "${BLUE}=== Dependabot Report for ${REPO} ===${NC}"
    echo -e "Open Dependabot PRs: ${open_prs}"
    echo ""
    
    echo "By update type:"
    gh pr list --author "app/dependabot" --state open --json title,labels | \
        jq -r '.[] | .title' | \
        awk '{
            if (/security/) security++
            else if (/major/) major++
            else if (/minor/) minor++
            else if (/patch/) patch++
            else other++
        }
        END {
            print "  Security updates: " security+0
            print "  Major updates: " major+0
            print "  Minor updates: " minor+0
            print "  Patch updates: " patch+0
            print "  Other updates: " other+0
        }'
    
    echo ""
    echo "Recent activity (last 7 days):"
    gh pr list --author "app/dependabot" --state all --json number,state,createdAt,mergedAt,closedAt | \
        jq -r '.[] | select(
            (.createdAt | fromdateiso8601 > (now - 604800)) or
            (.mergedAt | fromdateiso8601 > (now - 604800)) or
            (.closedAt | fromdateiso8601 > (now - 604800))
        ) | "  #\(.number): \(.state)"'
}

# Main command handler
case "$1" in
    "list-alerts")
        list_alerts
        ;;
    "list-prs")
        list_dependabot_prs
        ;;
    "merge")
        merge_dependabot_pr "$2"
        ;;
    "approve")
        approve_dependabot_pr "$2"
        ;;
    "batch-approve-patches")
        batch_approve_patches
        ;;
    "dismiss")
        dismiss_alert "$2" "$3"
        ;;
    "enable-security")
        enable_security_updates
        ;;
    "list-secrets")
        list_dependabot_secrets
        ;;
    "create-secret")
        create_dependabot_secret "$2" "$3"
        ;;
    "rebase")
        rebase_dependabot_pr "$2"
        ;;
    "recreate")
        recreate_dependabot_pr "$2"
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Dependabot Management Script"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  list-alerts              - List all Dependabot security alerts"
        echo "  list-prs                 - List all Dependabot PRs (open and recently merged)"
        echo "  merge <pr-number>        - Auto-merge a Dependabot PR"
        echo "  approve <pr-number>      - Approve a Dependabot PR"
        echo "  batch-approve-patches    - Approve all patch update PRs"
        echo "  dismiss <alert> <reason> - Dismiss a security alert"
        echo "  enable-security          - Enable Dependabot security updates"
        echo "  list-secrets             - List Dependabot secrets"
        echo "  create-secret <name> <value> - Create a Dependabot secret (simplified)"
        echo "  rebase <pr-number>       - Rebase a Dependabot PR"
        echo "  recreate <pr-number>     - Recreate a Dependabot PR"
        echo "  report                   - Generate a summary report"
        echo ""
        echo "Dismiss reasons: fix_started, inaccurate, no_bandwidth, not_used, tolerable_risk"
        echo ""
        echo "Environment variables:"
        echo "  GITHUB_TOKEN - GitHub token (optional if gh is authenticated)"
        echo ""
        echo "Examples:"
        echo "  $0 list-prs"
        echo "  $0 approve 123"
        echo "  $0 merge 123"
        echo "  $0 dismiss 456 tolerable_risk"
        ;;
esac