# GitHub Actions Setup for Stoic MCP

Complete guide for configuring CI/CD pipeline to deploy Stoic MCP to Azure Container Apps.

## Overview

The GitHub Actions workflow (`.github/workflows/deploy-stoic-mcp.yml`) automates:
1. Building Docker image from TypeScript source
2. Pushing image to Azure Container Registry
3. Deploying infrastructure with Bicep
4. Running health checks
5. Providing deployment summary

## Prerequisites

Before setting up GitHub Actions, you need:
- Azure subscription with Contributor access
- Resource group (`context-engineering-rg`)
- Managed identity (`context-msi`)
- DeepSeek API key

## Setup Steps

### Step 1: Create Azure Service Principal

The service principal allows GitHub Actions to authenticate with Azure.

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "stoic-mcp-github-actions" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/context-engineering-rg \
  --sdk-auth
```

**Important**: Save the entire JSON output. You'll need it for GitHub secrets.

Expected output:
```json
{
  "clientId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "clientSecret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "subscriptionId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "tenantId": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### Step 2: Add Secrets to GitHub Repository

Navigate to your GitHub repository:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

#### Required Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_CREDENTIALS` | Entire JSON output from Step 1 | Service principal credentials |
| `AZURE_SUBSCRIPTION_ID` | Your subscription ID | Azure subscription |
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | For AI explanations |

#### Example Secret Values

**AZURE_CREDENTIALS**:
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-client-secret-here",
  "subscriptionId": "12345678-1234-1234-1234-123456789012",
  "tenantId": "12345678-1234-1234-1234-123456789012",
  ...
}
```

**AZURE_SUBSCRIPTION_ID**:
```
12345678-1234-1234-1234-123456789012
```

**DEEPSEEK_API_KEY**:
```
sk-...your-deepseek-api-key...
```

### Step 3: Verify Workflow File

The workflow file should be at `.github/workflows/deploy-stoic-mcp.yml`.

Key configuration:
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'stoic-mcp/local/**'
      - 'stoic-mcp/azure/**'
      - '.github/workflows/deploy-stoic-mcp.yml'
  workflow_dispatch:
```

This means deployment triggers on:
- Push to `main` branch that changes stoic-mcp files
- Manual trigger via GitHub UI

### Step 4: Trigger First Deployment

#### Option 1: Push to Main Branch
```bash
# Make a small change
cd stoic-mcp/local
echo "# Updated" >> README.md

# Commit and push
git add .
git commit -m "Trigger Stoic MCP deployment"
git push origin main
```

#### Option 2: Manual Trigger
1. Go to **Actions** tab in GitHub
2. Select **Deploy Stoic MCP to Azure** workflow
3. Click **Run workflow** button
4. Select `main` branch
5. Click **Run workflow**

### Step 5: Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Click on the running workflow
3. Watch each step execute in real-time
4. Check deployment summary at the end

Expected steps:
- ✅ Checkout code
- ✅ Azure Login
- ✅ Set up Docker Buildx
- ✅ Get or Create Azure Container Registry
- ✅ Login to Azure Container Registry
- ✅ Build and push Docker image
- ✅ Deploy to Azure with Bicep
- ✅ Get deployment outputs
- ✅ Health check
- ✅ Post deployment info

### Step 6: Verify Deployment

After workflow completes:

```bash
# Get Container App URL from workflow summary or run:
az deployment group list \
  --resource-group context-engineering-rg \
  --query "[0].properties.outputs.containerAppUrl.value" \
  -o tsv

# Test health endpoint
curl https://YOUR_APP_URL/health

# View logs
az containerapp logs show \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --tail 50
```

## Troubleshooting

### Workflow Fails at "Azure Login"

**Error**: `Error: Login failed with Error: Service principal authentication failed`

**Solution**: Verify `AZURE_CREDENTIALS` secret contains valid JSON:
```bash
# Test service principal manually
az login --service-principal \
  -u CLIENT_ID \
  -p CLIENT_SECRET \
  --tenant TENANT_ID
```

If login fails, recreate service principal (Step 1).

### Workflow Fails at "Create Azure Container Registry"

**Error**: `Resource group not found`

**Solution**: Create resource group first:
```bash
az group create --name context-engineering-rg --location eastus
```

### Workflow Fails at "Deploy to Azure with Bicep"

**Error**: `Cosmos DB free tier already in use`

**Solution**: You can only have one Cosmos DB free tier per subscription.
- Option 1: Use different subscription
- Option 2: Edit `stoic-mcp/azure/main.bicep` line 75:
  ```bicep
  enableFreeTier: false  // Change from true to false
  ```
  **Warning**: This will cost ~$25/month instead of $0.

**Error**: `Managed identity not found`

**Solution**: Create managed identity:
```bash
az identity create --name context-msi --resource-group context-engineering-rg
```

### Workflow Succeeds but Health Check Fails

**Issue**: Health check may fail if container is still starting.

**Solution**: Wait 2-3 minutes, then check manually:
```bash
# Get Container App URL
CONTAINER_APP_URL=$(az deployment group list \
  --resource-group context-engineering-rg \
  --query "[0].properties.outputs.containerAppUrl.value" \
  -o tsv)

# Check health
curl $CONTAINER_APP_URL/health

# Check logs for errors
az containerapp logs show \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --tail 100
```

### Docker Build Fails

**Error**: `failed to solve: failed to read dockerfile`

**Solution**: Verify Dockerfile exists at `stoic-mcp/local/Dockerfile`.

**Error**: `npm run build failed`

**Solution**: Test build locally:
```bash
cd stoic-mcp/local
npm install
npm run build
```

Check for TypeScript errors in source files.

### Image Push Fails

**Error**: `unauthorized: authentication required`

**Solution**: Verify service principal has `AcrPush` role:
```bash
# Get ACR name
ACR_NAME=$(az acr list --resource-group context-engineering-rg --query "[0].name" -o tsv)

# Get service principal object ID
SP_OBJECT_ID=$(az ad sp show --id YOUR_CLIENT_ID --query id -o tsv)

# Assign AcrPush role
az role assignment create \
  --assignee $SP_OBJECT_ID \
  --scope /subscriptions/YOUR_SUB_ID/resourceGroups/context-engineering-rg/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME \
  --role AcrPush
```

## Workflow Customization

### Change Trigger Paths

To deploy on changes to specific files:
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'stoic-mcp/local/src/**'      # Only TypeScript source
      - 'stoic-mcp/local/package.json' # Or dependencies
      - 'stoic-mcp/azure/main.bicep'   # Or infrastructure
```

### Add Staging Environment

```yaml
env:
  AZURE_RESOURCE_GROUP: ${{ github.ref == 'refs/heads/main' && 'production-rg' || 'staging-rg' }}
```

### Add Notifications

Add Slack/Teams notification on success/failure:
```yaml
- name: Notify on success
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Stoic MCP deployed successfully to ${{ steps.outputs.container_app_url }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Add Tests Before Deploy

```yaml
- name: Run tests
  run: |
    cd stoic-mcp/local
    npm install
    npm test
```

## Security Best Practices

1. **Rotate Service Principal Secrets**: Rotate every 90 days
   ```bash
   az ad sp credential reset --id YOUR_CLIENT_ID
   ```

2. **Use Least Privilege**: Scope service principal to specific resource group
   ```bash
   --scopes /subscriptions/YOUR_SUB/resourceGroups/context-engineering-rg
   ```

3. **Enable Branch Protection**: Require PR reviews before merging to `main`
   - Settings → Branches → Add rule for `main`
   - Enable "Require pull request reviews before merging"

4. **Audit Deployments**: Review deployment logs regularly
   - Actions tab → Select workflow → Review logs

5. **Secrets Management**: Never commit secrets to repository
   - Use GitHub secrets for all sensitive values
   - Rotate secrets if accidentally exposed

## Cost Considerations

GitHub Actions usage:
- **Free tier**: 2,000 minutes/month for public repos
- **Free tier**: 500 minutes/month for private repos
- This workflow uses ~5-10 minutes per deployment

Azure costs remain ~$8-15/month as per main deployment.

## Monitoring Deployments

### View Deployment History
```bash
# List all deployments
az deployment group list \
  --resource-group context-engineering-rg \
  --query "[].{Name:name, State:properties.provisioningState, Timestamp:properties.timestamp}" \
  -o table

# View specific deployment
az deployment group show \
  --name YOUR_DEPLOYMENT_NAME \
  --resource-group context-engineering-rg
```

### View Container App Revisions
```bash
# List revisions (each deployment creates a new revision)
az containerapp revision list \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  -o table

# Rollback to previous revision if needed
az containerapp revision activate \
  -n YOUR_CONTAINER_APP \
  -g context-engineering-rg \
  --revision PREVIOUS_REVISION_NAME
```

## Next Steps

1. **Set up branch protection**: Require PR reviews before deployment
2. **Add tests**: Include unit/integration tests before deploy step
3. **Add staging environment**: Deploy to staging first, then production
4. **Monitor costs**: Set up Azure budget alerts
5. **Set up notifications**: Add Slack/Teams alerts for deployment status

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Container Apps CI/CD](https://learn.microsoft.com/en-us/azure/container-apps/github-actions)
- [Service Principal Authentication](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**Setup Time**: 10-15 minutes
**Deployment Time**: 5-10 minutes per run
**Difficulty**: Intermediate
