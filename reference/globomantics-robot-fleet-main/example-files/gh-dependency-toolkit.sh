#!/bin/bash

# GitHub CLI Dependency Toolkit
# Essential dependency management commands that actually work
# Perfect for a 30-minute teaching session

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get repo info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${GREEN}🔧 GitHub Dependency Toolkit for: ${REPO}${NC}\n"

# Function 1: Quick dependency status check
quick_status() {
    echo -e "${YELLOW}📊 Quick Dependency Status${NC}"
    
    # Count Dependabot PRs
    open_prs=$(gh pr list --author "app/dependabot" --state open --json number | jq length)
    echo "• Open Dependabot PRs: $open_prs"
    
    # Show vulnerability alerts if accessible
    vuln_count=$(gh api "/repos/${REPO}/vulnerability-alerts" 2>/dev/null && echo "✓ Enabled" || echo "❌ Disabled")
    echo "• Vulnerability Alerts: $vuln_count"
    
    # Last Dependabot activity
    echo -e "\n${YELLOW}Recent Dependabot Activity:${NC}"
    gh pr list --author "app/dependabot" --state all --limit 5 --json number,title,state,createdAt \
        --template '{{range .}}• PR #{{.number}}: {{.title}} ({{.state}}){{"\n"}}{{end}}'
}

# Function 2: List and filter Dependabot PRs
list_prs() {
    echo -e "${YELLOW}📋 Dependabot PRs${NC}"
    
    # Show open PRs with important details
    gh pr list --author "app/dependabot" --state open \
        --json number,title,createdAt,labels,statusCheckRollup \
        --template '{{range .}}PR #{{.number}}: {{.title}}
  Created: {{.createdAt}}
  Status: {{if .statusCheckRollup}}{{range .statusCheckRollup}}{{.status}}{{end}}{{else}}No checks{{end}}
  Labels: {{range .labels}}{{.name}} {{end}}
{{"\n"}}{{end}}'
}

# Function 3: Auto-merge safe updates (patches only)
merge_patches() {
    echo -e "${YELLOW}🚀 Auto-merging patch updates...${NC}"
    
    # Find patch updates (simple version bump detection)
    prs=$(gh pr list --author "app/dependabot" --state open --json number,title)
    
    echo "$prs" | jq -r '.[] | select(.title | test("from [0-9]+\\.[0-9]+\\.[0-9]+ to [0-9]+\\.[0-9]+\\.[0-9]+")) | .number' | while read -r pr; do
        title=$(gh pr view "$pr" --json title -q .title)
        echo -e "${GREEN}✓ Merging PR #$pr: $title${NC}"
        
        # Approve and merge
        gh pr review "$pr" --approve -b "Auto-approved patch update"
        gh pr merge "$pr" --auto --merge
        sleep 2 # Rate limiting
    done
}

# Function 4: Comment on PRs (trigger Dependabot actions)
pr_command() {
    local pr=$1
    local cmd=$2
    
    case $cmd in
        "rebase")
            echo "Rebasing PR #$pr..."
            gh pr comment "$pr" -b "@dependabot rebase"
            ;;
        "recreate")
            echo "Recreating PR #$pr..."
            gh pr comment "$pr" -b "@dependabot recreate"
            ;;
        "merge")
            echo "Requesting merge for PR #$pr..."
            gh pr comment "$pr" -b "@dependabot merge"
            ;;
        *)
            echo "Unknown command. Use: rebase, recreate, or merge"
            ;;
    esac
}

# Function 5: Security overview
security_check() {
    echo -e "${YELLOW}🔒 Security Overview${NC}"
    
    # Check if Dependabot is enabled
    echo -n "• Dependabot Security Updates: "
    gh api "/repos/${REPO}/vulnerability-alerts" -i 2>&1 | grep -q "204" && echo "✓ Enabled" || echo "❌ Disabled"
    
    # List security-related PRs
    echo -e "\n${YELLOW}Security-related PRs:${NC}"
    gh pr list --author "app/dependabot" --search "security in:title" --state all --limit 10 \
        --json number,title,state --template '{{range .}}• PR #{{.number}}: {{.title}} ({{.state}}){{"\n"}}{{end}}'
}

# Function 6: Enable Dependabot features
enable_features() {
    echo -e "${YELLOW}⚙️ Enabling Dependabot Features${NC}"
    
    # Enable vulnerability alerts
    echo "• Enabling vulnerability alerts..."
    gh api --method PUT "/repos/${REPO}/vulnerability-alerts" && echo "  ✓ Done" || echo "  ❌ Failed"
    
    # Enable automated security fixes
    echo "• Enabling automated security fixes..."
    gh api --method PUT "/repos/${REPO}/automated-security-fixes" && echo "  ✓ Done" || echo "  ❌ Failed"
}

# Function 7: Generate simple report
report() {
    echo -e "${YELLOW}📈 Dependency Report${NC}"
    echo "Repository: $REPO"
    echo "Generated: $(date)"
    echo ""
    
    # Stats
    total=$(gh pr list --author "app/dependabot" --state all --limit 100 --json number | jq length)
    open=$(gh pr list --author "app/dependabot" --state open --json number | jq length)
    merged=$(gh pr list --author "app/dependabot" --state merged --limit 50 --json number | jq length)
    
    echo "Statistics:"
    echo "• Total Dependabot PRs: $total"
    echo "• Open PRs: $open"
    echo "• Recently Merged: $merged"
    echo ""
    
    # Group by package ecosystem
    echo "Open PRs by Type:"
    gh pr list --author "app/dependabot" --state open --json title | \
        jq -r '.[].title' | \
        awk -F'[ :]' '{print $2}' | \
        sort | uniq -c | sort -rn
}

# Main menu
case "${1:-help}" in
    "status")
        quick_status
        ;;
    "list")
        list_prs
        ;;
    "merge-patches")
        merge_patches
        ;;
    "pr")
        pr_command "$2" "$3"
        ;;
    "security")
        security_check
        ;;
    "enable")
        enable_features
        ;;
    "report")
        report
        ;;
    *)
        echo "GitHub Dependency Toolkit - Quick Commands"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  status         - Quick dependency status overview"
        echo "  list           - List all Dependabot PRs with details"
        echo "  merge-patches  - Auto-merge all patch updates"
        echo "  pr <#> <cmd>   - Run Dependabot command (rebase/recreate/merge)"
        echo "  security       - Security-focused overview"
        echo "  enable         - Enable Dependabot features"
        echo "  report         - Generate dependency report"
        echo ""
        echo "Examples:"
        echo "  $0 status"
        echo "  $0 merge-patches"
        echo "  $0 pr 123 rebase"
        echo ""
        echo "Pro tip: Set up an alias for quick access:"
        echo "  alias deps='./example-files/gh-dependency-toolkit.sh'"
        ;;
esac