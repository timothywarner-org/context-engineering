# Azure Container Registry & CI/CD Explained

## Your Questions Answered

### Q: Do we need Azure Container Registry?

**Yes!** You need ACR to store Docker images that Azure Container Apps will run.

**Why?**

- Container Apps needs a container image to deploy
- That image must be stored somewhere Azure can access it
- ACR (Azure Container Registry) is Azure's private Docker registry

### Q: How is ACR created?

**Answer**: The `deploy.sh` script creates it for you!

**See line 137 in deploy.sh:**

```bash
az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --location "$LOCATION" \
    --admin-enabled false
```

**Why not in Bicep?**

- ACR must exist BEFORE we build/push the Docker image
- Docker image must exist BEFORE Bicep deployment (Container App needs the image URL)
- So the order is:
  1. Create ACR (deploy.sh)
  2. Build Docker image (deploy.sh)
  3. Push to ACR (deploy.sh)
  4. Deploy Bicep with image URL from ACR (deploy.sh)

### Q: Do we need GitHub Actions for CI/CD?

**Not required, but highly recommended!**

**Two workflows:**

#### Workflow 1: Manual Deployment (Good for Testing)

```bash
# Every time you make changes:
cd coretext-mcp/azure
./deploy.sh
```

**Pros:**

- ✅ Simple, no GitHub setup needed
- ✅ Good for learning and testing

**Cons:**

- ❌ Manual - you must run script every time
- ❌ Can forget to deploy
- ❌ Requires your laptop

#### Workflow 2: GitHub Actions (Good for Production)

```bash
# Once set up:
git push origin main
# Deployment happens automatically!
```

**Pros:**

- ✅ Automatic deployment on every commit
- ✅ No manual steps
- ✅ Deployment history in GitHub
- ✅ Can deploy from anywhere

**Cons:**

- ❌ Requires initial setup (service principal, secrets)
- ❌ Slightly more complex

## How They Work Together

### Manual Deployment Flow

```
1. You run deploy.sh
   ↓
2. Script creates ACR (if needed)
   ↓
3. Script builds Docker image
   ↓
4. Script pushes image to ACR
   ↓
5. Script deploys Bicep (creates Cosmos DB, Container App, Key Vault)
   ↓
6. Container App pulls image from ACR and runs it
```

### GitHub Actions Flow

```
1. You push code to main branch
   ↓
2. GitHub Actions triggers automatically
   ↓
3. Workflow builds Docker image
   ↓
4. Workflow pushes image to ACR (ACR already exists from initial setup)
   ↓
5. Workflow updates Container App with new image
   ↓
6. Container App pulls new image from ACR and restarts
```

## Cost Implications

### Azure Container Registry

- **Basic Tier**: $5/month
- **Storage**: ~$0.10/GB/month
- **Typical usage**: ~1-2GB = **~$5-6/month**

### GitHub Actions

- **Public repos**: Free unlimited minutes
- **Private repos**: 2,000 minutes/month free
- **Typical usage**: 10 deployments/day × 3 minutes = 900 minutes/month = **$0** (under free tier)

## Recommended Setup

### For Course/Teaching

**Use manual deployment:**

- Run `deploy.sh` during demos
- Show students the step-by-step process
- Easy to understand and troubleshoot

### For Personal Projects

**Use GitHub Actions:**

- Set it up once
- Never think about deployment again
- Push code, it deploys automatically

### For Production Apps

**Use GitHub Actions + Approval Gates:**

- Automatic deployment to staging
- Manual approval for production
- Full deployment history

## Setup Summary

### Initial Setup (One Time)

```bash
# 1. Create resource group
az group create --name context-engineering-rg --location eastus

# 2. Create managed identity
az identity create --name context-msi --resource-group context-engineering-rg

# 3. Run deploy script
cd coretext-mcp/azure
./deploy.sh
```

**Result:**

- ✅ ACR created
- ✅ Docker image built and pushed
- ✅ All Azure resources deployed
- ✅ App running at <https://your-app.azurecontainerapps.io>

### Optional: Add GitHub Actions (One Time)

```bash
# 1. Create service principal
az ad sp create-for-rbac \
  --name "github-actions-coretext-mcp" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUB/resourceGroups/context-engineering-rg \
  --sdk-auth

# 2. Copy the JSON output
# 3. Add to GitHub Secrets (Settings > Secrets):
#    - AZURE_CREDENTIALS (entire JSON)
#    - ACR_NAME (from deploy.sh output)
#    - CONTAINER_APP_NAME (from deploy.sh output)
```

**Result:**

- ✅ Every push to main deploys automatically
- ✅ Deployment history in GitHub
- ✅ Health checks verify deployment

## Files Explained

### ACR-Related Files

| File | Purpose | Contains |
|------|---------|----------|
| `deploy.sh` | Creates ACR, builds/pushes image | ACR creation logic |
| `Dockerfile` | Defines container image | Image configuration |
| `.dockerignore` | Excludes files from image | Build optimization |
| `.github/workflows/deploy-coretext-mcp.yml` | GitHub Actions CI/CD | Automated deployment |
| `.github/GITHUB_ACTIONS_SETUP.md` | Setup guide | How to configure CI/CD |

### Non-ACR Files

| File | Purpose | ACR Involved? |
|------|---------|---------------|
| `main.bicep` | Infrastructure template | ❌ No - uses image URL as parameter |
| `parameters.json` | Deployment parameters | ✅ Yes - specifies image URL |

## Common Confusion Cleared Up

### "Why isn't ACR in the Bicep template?"

**Answer**: Timing!

```
❌ Wrong Order:
1. Run Bicep (creates ACR, Container App)
2. Build Docker image
3. Push to ACR
Problem: Container App created with no image!

✅ Correct Order (what we do):
1. Create ACR (deploy.sh)
2. Build Docker image (deploy.sh)
3. Push to ACR (deploy.sh)
4. Run Bicep with image URL (deploy.sh)
Result: Container App has image ready!
```

### "Do I need to create ACR manually?"

**No!** The `deploy.sh` script checks if ACR exists:

- **If exists**: Uses it
- **If doesn't exist**: Creates it

See lines 124-148 in `deploy.sh`:

```bash
# Look for existing ACR
EXISTING_ACR=$(az acr list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv)

if [ -n "$EXISTING_ACR" ]; then
    ACR_NAME="$EXISTING_ACR"
    log_success "Found existing ACR: $ACR_NAME"
else
    # Generate unique name
    ACR_NAME="coretextacr$(date +%s | tail -c 6)"

    # Create new ACR
    az acr create ...
fi
```

### "Will GitHub Actions create ACR?"

**No!** GitHub Actions assumes ACR already exists (from your initial manual deployment).

**The workflow:**

1. Manual deployment (first time) - creates ACR
2. GitHub Actions (ongoing) - uses existing ACR

## Troubleshooting

### Error: "ACR not found"

**Problem**: ACR doesn't exist yet

**Fix**: Run `deploy.sh` first to create it

### Error: "Failed to push image"

**Problem**: Not logged into ACR

**Fix**: Run `az acr login --name YOUR_ACR_NAME`

### Error: "Container App can't pull image"

**Problem**: Container App doesn't have permission to ACR

**Fix**: The deploy script handles this automatically via managed identity

### Error: "GitHub Actions can't push to ACR"

**Problem**: Service principal doesn't have ACR push permissions

**Fix**:

```bash
az role assignment create \
  --assignee YOUR_SP_ID \
  --role AcrPush \
  --scope /subscriptions/YOUR_SUB/resourceGroups/context-engineering-rg/providers/Microsoft.ContainerRegistry/registries/YOUR_ACR
```

## Summary

**Yes, you need ACR:**

- ✅ Created automatically by deploy.sh
- ✅ Stores Docker images
- ✅ ~$5-6/month

**Yes, GitHub Actions are helpful (but optional):**

- ✅ Automated CI/CD on every commit
- ✅ Free for most use cases
- ✅ Requires one-time setup

**The deploy.sh script handles everything:**

1. ✅ Creates ACR if needed
2. ✅ Builds Docker image
3. ✅ Pushes to ACR
4. ✅ Deploys all infrastructure
5. ✅ Configures permissions

**You're all set!** Just run `./deploy.sh` and it works.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-29
