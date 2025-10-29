# GitHub Actions Setup for CoreText MCP

This guide shows how to set up automated CI/CD for deploying CoreText MCP to Azure.

## What the Workflow Does

The GitHub Action (`.github/workflows/deploy-coretext-mcp.yml`) automatically:

1. ✅ Triggers on push to `main` branch (when `coretext-mcp/` changes)
2. ✅ Builds Docker image
3. ✅ Pushes to Azure Container Registry
4. ✅ Updates Azure Container App with new image
5. ✅ Performs health check
6. ✅ Creates GitHub deployment record

**Result**: Every commit to `main` automatically deploys to Azure!

## Prerequisites

Before setting up GitHub Actions, you need:

1. **Azure resources deployed** (run `coretext-mcp/azure/deploy.sh` first)
2. **GitHub repository** with this code
3. **Azure Service Principal** with deployment permissions

## Setup Steps

### Step 1: Deploy Azure Infrastructure First

```bash
# Deploy using the manual script first
cd context-engineering-2/coretext-mcp/azure
./deploy.sh
```

**Note the outputs:**
- ACR name (e.g., `coretextacr123456`)
- Container App name (e.g., `coretext-app-abc123`)

### Step 2: Create Azure Service Principal

This gives GitHub permission to deploy to Azure.

```bash
# Get subscription ID
SUBSCRIPTION_ID="92fd53f2-c38e-461a-9f50-e1ef3382c54c"

# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "github-actions-coretext-mcp" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/context-engineering-rg \
  --sdk-auth
```

**Output** (save this - you'll need it for GitHub secrets):
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "92fd53f2-c38e-461a-9f50-e1ef3382c54c",
  "tenantId": "f74b1450-e46a-41df-abee-ebf3621bfd85",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  ...
}
```

**Important**: Copy the ENTIRE JSON output!

### Step 3: Get ACR and Container App Names

```bash
# Get ACR name
ACR_NAME=$(az acr list \
  --resource-group context-engineering-rg \
  --query "[0].name" \
  -o tsv)
echo "ACR_NAME: $ACR_NAME"

# Get Container App name
APP_NAME=$(az containerapp list \
  --resource-group context-engineering-rg \
  --query "[0].name" \
  -o tsv)
echo "APP_NAME: $APP_NAME"
```

### Step 4: Add GitHub Secrets

Go to your GitHub repository:

1. Navigate to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these three secrets:

#### Secret 1: `AZURE_CREDENTIALS`
- **Name**: `AZURE_CREDENTIALS`
- **Value**: Paste the ENTIRE JSON from Step 2

#### Secret 2: `ACR_NAME`
- **Name**: `ACR_NAME`
- **Value**: Your ACR name (e.g., `coretextacr123456`)

#### Secret 3: `CONTAINER_APP_NAME`
- **Name**: `CONTAINER_APP_NAME`
- **Value**: Your Container App name (e.g., `coretext-app-abc123`)

**Screenshot guide**:
```
Settings > Secrets and variables > Actions > New repository secret

Name: AZURE_CREDENTIALS
Value: {
  "clientId": "...",
  "clientSecret": "...",
  ...
}
```

### Step 5: Test the Workflow

#### Option A: Push to Main

```bash
# Make a small change
cd coretext-mcp
echo "# Test change" >> README.md

# Commit and push
git add README.md
git commit -m "test: trigger GitHub Actions"
git push origin main
```

#### Option B: Manual Trigger

1. Go to **Actions** tab in GitHub
2. Select **Deploy CoreText MCP to Azure**
3. Click **Run workflow**
4. Choose environment (production/staging)
5. Click **Run workflow**

### Step 6: Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Click on the running workflow
3. Watch the logs in real-time
4. Look for:
   - ✅ Docker build succeeds
   - ✅ Image pushed to ACR
   - ✅ Container App updated
   - ✅ Health check passes

**Expected output:**
```
Building image: coretextacr123456.azurecr.io/coretext-mcp:abc123
Pushing images...
Updating Container App: coretext-app-abc123
✅ Health check passed (HTTP 200)
```

## Workflow Triggers

The workflow runs when:

1. **Automatic**: Push to `main` branch with changes in:
   - `coretext-mcp/**` (any code changes)
   - `.github/workflows/deploy-coretext-mcp.yml` (workflow changes)

2. **Manual**: Via GitHub Actions UI (workflow_dispatch)

## Troubleshooting

### Issue: "Resource 'GitHub.Actions' was not found"

**Problem**: Service principal doesn't have correct permissions.

**Fix**:
```bash
# Re-create with correct scope
az ad sp create-for-rbac \
  --name "github-actions-coretext-mcp" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/context-engineering-rg \
  --sdk-auth
```

### Issue: "ACR login failed"

**Problem**: Service principal doesn't have ACR push permissions.

**Fix**:
```bash
# Get service principal ID
SP_ID=$(az ad sp list --display-name "github-actions-coretext-mcp" --query "[0].id" -o tsv)

# Grant AcrPush role
az role assignment create \
  --assignee $SP_ID \
  --role AcrPush \
  --scope /subscriptions/$SUBSCRIPTION_ID/resourceGroups/context-engineering-rg/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME
```

### Issue: "Health check failed (HTTP 503)"

**Problem**: Container App is still starting up.

**Fix**: The workflow waits 30 seconds, but you may need more time for cold starts. Edit the workflow:

```yaml
- name: Health Check
  run: |
    echo "Waiting 60 seconds..."  # Changed from 30
    sleep 60
```

### Issue: "Container App update failed"

**Problem**: Image doesn't exist or Container App is misconfigured.

**Fix**:
```bash
# Check if image exists
az acr repository show \
  --name $ACR_NAME \
  --repository coretext-mcp

# Check Container App status
az containerapp show \
  --name $APP_NAME \
  --resource-group context-engineering-rg \
  --query "properties.runningStatus"
```

## Advanced Configuration

### Environment-Specific Deployments

To deploy to staging vs. production:

1. Create multiple Container Apps:
   ```bash
   # Staging
   az containerapp create \
     --name coretext-app-staging \
     --resource-group context-engineering-rg \
     ...

   # Production
   az containerapp create \
     --name coretext-app-prod \
     --resource-group context-engineering-rg \
     ...
   ```

2. Add secrets for each environment:
   - `CONTAINER_APP_NAME_STAGING`
   - `CONTAINER_APP_NAME_PROD`

3. Update workflow to use appropriate secret based on environment

### Notification Setup (Slack)

Add to workflow after health check:

```yaml
- name: Notify Slack
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "CoreText MCP deployment ${{ job.status }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Deployment: *${{ job.status }}*\nCommit: ${{ github.sha }}\nActor: ${{ github.actor }}"
            }
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Approval Gates (Manual Approval)

Add to workflow before deployment:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    # ... build steps ...

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval in GitHub
    # ... deploy steps ...
```

Then configure environment protection rules in GitHub:
Settings → Environments → production → Required reviewers

## Security Best Practices

1. **Rotate Service Principal Secrets**
   - Every 90 days minimum
   - Use Azure Key Vault for production

2. **Limit Service Principal Scope**
   - Only resource group access (not subscription)
   - Only Contributor role (not Owner)

3. **Use GitHub Environments**
   - Configure approval gates
   - Add environment-specific secrets
   - Restrict to specific branches

4. **Enable Branch Protection**
   - Require pull request reviews
   - Require status checks to pass
   - Require signed commits

## Monitoring Deployments

### View Deployment History

GitHub UI:
- Go to **Actions** tab
- See all workflow runs

Azure Portal:
- Container App → Revisions
- See deployment history

### Rollback

```bash
# List revisions
az containerapp revision list \
  --name $APP_NAME \
  --resource-group context-engineering-rg

# Activate previous revision
az containerapp revision activate \
  --name $APP_NAME \
  --resource-group context-engineering-rg \
  --revision <previous-revision-name>
```

## Cost Implications

**GitHub Actions**:
- Free for public repos (unlimited minutes)
- Private repos: 2,000 minutes/month free (then $0.008/minute)

**Azure Container Registry**:
- Basic tier: $5/month (included in deployment)
- No additional cost for CI/CD pushes

**Typical usage**:
- 10 deployments/day = ~300/month
- Each deployment: ~3 minutes
- Total: 900 minutes/month
- Cost: Free (under 2,000 minutes)

## Summary

Once set up:
1. ✅ Push to `main` → Automatic deployment
2. ✅ Health checks verify deployment
3. ✅ GitHub tracks deployment history
4. ✅ Azure Portal shows active revision

**Next steps**:
- Set up branch protection
- Add approval gates for production
- Configure Slack notifications
- Set up monitoring alerts

---

**Setup Version**: 1.0.0
**Last Updated**: 2025-10-29
