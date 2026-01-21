# CircleCI Setup Documentation for Schematica

Complete guide for setting up CircleCI CI/CD pipeline for the Schematica project with automated deployments to Azure Container Apps.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Azure Resource Setup](#2-azure-resource-setup)
3. [GitHub Container Registry Setup](#3-github-container-registry-setup)
4. [CircleCI Project Setup](#4-circleci-project-setup)
5. [Pipeline Configuration Reference](#5-pipeline-configuration-reference)
6. [Triggering Deployments](#6-triggering-deployments)
7. [Manual Approval for Production](#7-manual-approval-for-production)
8. [Troubleshooting](#8-troubleshooting)
9. [Monitoring and Logs](#9-monitoring-and-logs)
10. [Security Best Practices](#10-security-best-practices)

---

## 1. Prerequisites

Before setting up the CircleCI pipeline, ensure you have the following:

### Required Accounts and Access

- **Azure Subscription**: Active subscription with Owner or Contributor role
  - Subscription ID: `92fd53f2-c38e-461a-9f50-e1ef3382c54c`
- **GitHub Account**: With admin access to the Schematica repository
- **CircleCI Account**: Connected to your GitHub account
  - Sign up at: https://circleci.com/signup/

### Required Tools

Install the following tools on your local machine:

#### Azure CLI

```bash
# macOS
brew install azure-cli

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Windows (PowerShell as Administrator)
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'

# Verify installation
az --version
```

#### GitHub CLI (optional but recommended)

```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Verify installation
gh --version
```

#### jq (for JSON processing)

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Verify installation
jq --version
```

### Azure Permissions Required

Your Azure account needs the following permissions:

- **Application.ReadWrite.All** - To create Azure AD app registrations
- **Contributor** role on the subscription - To create and manage resources
- **User Access Administrator** role - To assign RBAC roles

Verify your access:

```bash
az login
az account show --output table
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv) --output table
```

---

## 2. Azure Resource Setup

This section provides exact Azure CLI commands to set up all required Azure resources.

### 2.1 Create Resource Group

The resource group will contain all Azure resources for Schematica.

```bash
# Login to Azure
az login

# Set the subscription
az account set --subscription 92fd53f2-c38e-461a-9f50-e1ef3382c54c

# Create the resource group
az group create \
  --name globomantics-rg \
  --location eastus \
  --tags environment=production project=schematica team=globomantics

# Verify creation
az group show --name globomantics-rg --output table
```

**Expected Output:**
```
Name             Location    Status
---------------  ----------  ---------
globomantics-rg  eastus      Succeeded
```

### 2.2 Create Azure Key Vault

Key Vault will store sensitive secrets like MCP API keys.

```bash
# Create Key Vault
az keyvault create \
  --name schematica-kv-eastus \
  --resource-group globomantics-rg \
  --location eastus \
  --enable-rbac-authorization true \
  --tags environment=production project=schematica

# Grant yourself Key Vault Administrator role
CURRENT_USER_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Key Vault Administrator" \
  --assignee $CURRENT_USER_ID \
  --scope /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.KeyVault/vaults/schematica-kv-eastus

# Add MCP API Key secret (replace with your actual key)
az keyvault secret set \
  --vault-name schematica-kv-eastus \
  --name mcp-api-key \
  --value "your-actual-mcp-api-key-here"

# Verify secret creation
az keyvault secret list --vault-name schematica-kv-eastus --output table
```

**Important:** Replace `your-actual-mcp-api-key-here` with your actual MCP API key.

### 2.3 Create Container Apps Environment

Container Apps Environment is a secure boundary around Container Apps.

```bash
# Install Container Apps extension for Azure CLI
az extension add --name containerapp --upgrade

# Create Log Analytics workspace for Container Apps
az monitor log-analytics workspace create \
  --resource-group globomantics-rg \
  --workspace-name schematica-logs-eastus \
  --location eastus \
  --tags environment=production project=schematica

# Get Log Analytics workspace ID and key
LOG_ANALYTICS_WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group globomantics-rg \
  --workspace-name schematica-logs-eastus \
  --query customerId \
  --output tsv)

LOG_ANALYTICS_WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group globomantics-rg \
  --workspace-name schematica-logs-eastus \
  --query primarySharedKey \
  --output tsv)

# Create Container Apps Environment
az containerapp env create \
  --name schematica-cae-eastus \
  --resource-group globomantics-rg \
  --location eastus \
  --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_ID \
  --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_KEY \
  --tags environment=production project=schematica

# Verify environment creation
az containerapp env show \
  --name schematica-cae-eastus \
  --resource-group globomantics-rg \
  --output table
```

**Expected Output:**
```
Name                    Location    ResourceGroup     ProvisioningState
----------------------  ----------  ----------------  -------------------
schematica-cae-eastus   eastus      globomantics-rg   Succeeded
```

### 2.4 Create Container Apps (Staging and Production)

#### 2.4.1 Create Staging Container App

```bash
# Get Key Vault resource ID
KEY_VAULT_ID=$(az keyvault show \
  --name schematica-kv-eastus \
  --resource-group globomantics-rg \
  --query id \
  --output tsv)

# Create staging container app
az containerapp create \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --environment schematica-cae-eastus \
  --image ghcr.io/globomantics/schematica:latest \
  --target-port 3000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars "NODE_ENV=staging" \
  --tags environment=staging project=schematica

# Add managed identity to staging app
az containerapp identity assign \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --system-assigned

# Get staging app managed identity ID
STAGING_IDENTITY_ID=$(az containerapp show \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --query identity.principalId \
  --output tsv)

# Grant staging app access to Key Vault secrets
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $STAGING_IDENTITY_ID \
  --scope $KEY_VAULT_ID

# Add secret reference for MCP API key
az containerapp secret set \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --secrets mcp-api-key=keyvaultref:https://schematica-kv-eastus.vault.azure.net/secrets/mcp-api-key,identityref:system

# Update environment variable to use secret
az containerapp update \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --set-env-vars "MCP_API_KEY=secretref:mcp-api-key"

# Get staging URL
STAGING_URL=$(az containerapp show \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Staging URL: https://${STAGING_URL}"
```

#### 2.4.2 Create Production Container App

```bash
# Create production container app
az containerapp create \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --environment schematica-cae-eastus \
  --image ghcr.io/globomantics/schematica:latest \
  --target-port 3000 \
  --ingress external \
  --min-replicas 2 \
  --max-replicas 10 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars "NODE_ENV=production" \
  --tags environment=production project=schematica \
  --revisions-mode multiple

# Add managed identity to production app
az containerapp identity assign \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --system-assigned

# Get production app managed identity ID
PROD_IDENTITY_ID=$(az containerapp show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --query identity.principalId \
  --output tsv)

# Grant production app access to Key Vault secrets
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $PROD_IDENTITY_ID \
  --scope $KEY_VAULT_ID

# Add secret reference for MCP API key
az containerapp secret set \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --secrets mcp-api-key=keyvaultref:https://schematica-kv-eastus.vault.azure.net/secrets/mcp-api-key,identityref:system

# Update environment variable to use secret
az containerapp update \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --set-env-vars "MCP_API_KEY=secretref:mcp-api-key"

# Get production URL
PROD_URL=$(az containerapp show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Production URL: https://${PROD_URL}"
```

**Note:** Production uses `--revisions-mode multiple` to enable blue-green deployments and traffic splitting.

### 2.5 Create Azure AD App Registration for CircleCI

This app registration will be used for OIDC authentication from CircleCI.

```bash
# Create app registration
az ad app create \
  --display-name schematica-circleci-deployer \
  --sign-in-audience AzureADMyOrg

# Get the Application (client) ID
APP_ID=$(az ad app list \
  --display-name schematica-circleci-deployer \
  --query [0].appId \
  --output tsv)

echo "Application (Client) ID: $APP_ID"

# Get Tenant ID
TENANT_ID=$(az account show --query tenantId --output tsv)
echo "Tenant ID: $TENANT_ID"

# Create service principal for the app
az ad sp create --id $APP_ID

# Get service principal object ID
SP_OBJECT_ID=$(az ad sp list \
  --filter "appId eq '$APP_ID'" \
  --query [0].id \
  --output tsv)

echo "Service Principal Object ID: $SP_OBJECT_ID"
```

**IMPORTANT:** Save these values - you'll need them for CircleCI configuration:
- Application (Client) ID: `$APP_ID`
- Tenant ID: `$TENANT_ID`
- Service Principal Object ID: `$SP_OBJECT_ID`

### 2.6 Configure Federated Credentials for CircleCI OIDC

CircleCI uses OIDC tokens to authenticate to Azure without storing long-lived credentials.

#### 2.6.1 Get Your CircleCI Organization ID

First, you need to find your CircleCI Organization ID:

1. Go to https://app.circleci.com/
2. Navigate to **Organization Settings** (click your organization name in the top-left)
3. Go to **Overview** tab
4. Copy your **Organization ID** (it's a UUID like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

Alternatively, use the CircleCI API:

```bash
# Set your CircleCI personal API token
CIRCLECI_TOKEN="your-circleci-personal-api-token"

# Get organization ID
curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/me | jq -r '.organizations[0].id'
```

#### 2.6.2 Create Federated Credentials

```bash
# Set your CircleCI Organization ID
CIRCLECI_ORG_ID="your-circleci-org-id-here"

# Get the app's object ID
APP_OBJECT_ID=$(az ad app list \
  --display-name schematica-circleci-deployer \
  --query [0].id \
  --output tsv)

# Create federated credential for main branch deployments
az ad app federated-credential create \
  --id $APP_OBJECT_ID \
  --parameters '{
    "name": "circleci-main-branch",
    "issuer": "https://oidc.circleci.com/org/'$CIRCLECI_ORG_ID'",
    "subject": "org/'$CIRCLECI_ORG_ID'/project/YOUR_PROJECT_ID/user/YOUR_USER_ID/vcs-origin/github.com/YOUR_ORG/schematica/vcs-ref/refs/heads/main",
    "description": "CircleCI OIDC for main branch deployments",
    "audiences": [
      "api://AzureADTokenExchange"
    ]
  }'
```

**Note:** The subject format for CircleCI OIDC tokens is:
```
org/{organization_id}/project/{project_id}/user/{user_id}/vcs-origin/{vcs-origin}/vcs-ref/{vcs-ref}
```

However, CircleCI also supports wildcard subjects for flexibility:

```bash
# Alternative: Use wildcard for any branch in the project
az ad app federated-credential create \
  --id $APP_OBJECT_ID \
  --parameters '{
    "name": "circleci-all-branches",
    "issuer": "https://oidc.circleci.com/org/'$CIRCLECI_ORG_ID'",
    "subject": "org/'$CIRCLECI_ORG_ID'/project/*",
    "description": "CircleCI OIDC for all branches and projects",
    "audiences": [
      "api://AzureADTokenExchange"
    ]
  }'
```

**Recommended:** Use the wildcard approach for simplicity. The specific RBAC permissions will still limit what actions can be performed.

#### 2.6.3 Verify Federated Credentials

```bash
# List all federated credentials
az ad app federated-credential list \
  --id $APP_OBJECT_ID \
  --output table
```

**Expected Output:**
```
Name                    Issuer                                        Subject                      Audiences
----------------------  --------------------------------------------  ---------------------------  ---------------------------
circleci-all-branches   https://oidc.circleci.com/org/ORG_ID         org/ORG_ID/project/*         api://AzureADTokenExchange
```

### 2.7 Assign RBAC Permissions

Grant the service principal permissions to manage Container Apps.

```bash
# Get service principal object ID
SP_OBJECT_ID=$(az ad sp list \
  --filter "appId eq '$APP_ID'" \
  --query [0].id \
  --output tsv)

# Assign Contributor role at resource group level
az role assignment create \
  --role "Contributor" \
  --assignee $SP_OBJECT_ID \
  --scope /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg

# Verify role assignment
az role assignment list \
  --assignee $SP_OBJECT_ID \
  --output table
```

**Alternative:** For more granular permissions, assign only to specific Container Apps:

```bash
# Get Container App resource IDs
STAGING_APP_ID=$(az containerapp show \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --query id \
  --output tsv)

PROD_APP_ID=$(az containerapp show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --query id \
  --output tsv)

# Assign Contributor role to specific apps
az role assignment create \
  --role "Contributor" \
  --assignee $SP_OBJECT_ID \
  --scope $STAGING_APP_ID

az role assignment create \
  --role "Contributor" \
  --assignee $SP_OBJECT_ID \
  --scope $PROD_APP_ID
```

### 2.8 Summary of Azure Resources Created

Run this command to verify all resources were created successfully:

```bash
echo "=== Resource Group ==="
az group show --name globomantics-rg --output table

echo -e "\n=== Key Vault ==="
az keyvault show --name schematica-kv-eastus --output table

echo -e "\n=== Container Apps Environment ==="
az containerapp env show \
  --name schematica-cae-eastus \
  --resource-group globomantics-rg \
  --output table

echo -e "\n=== Container Apps ==="
az containerapp list \
  --resource-group globomantics-rg \
  --output table

echo -e "\n=== App Registration ==="
az ad app list \
  --display-name schematica-circleci-deployer \
  --output table

echo -e "\n=== Important IDs for CircleCI ==="
echo "Subscription ID: 92fd53f2-c38e-461a-9f50-e1ef3382c54c"
echo "Tenant ID: $(az account show --query tenantId --output tsv)"
echo "Client ID: $(az ad app list --display-name schematica-circleci-deployer --query [0].appId --output tsv)"
echo "Resource Group: globomantics-rg"
```

---

## 3. GitHub Container Registry Setup

GitHub Container Registry (GHCR) will store Docker images for the Schematica application.

### 3.1 Create GitHub Personal Access Token

CircleCI needs a GitHub Personal Access Token (PAT) to push images to GHCR.

#### 3.1.1 Generate Token via GitHub UI

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Configure the token:
   - **Note:** `CircleCI GHCR Access for Schematica`
   - **Expiration:** Choose an appropriate duration (90 days or custom)
   - **Select scopes:**
     - ✅ `write:packages` - Upload packages to GitHub Package Registry
     - ✅ `read:packages` - Download packages from GitHub Package Registry
     - ✅ `delete:packages` - Delete packages from GitHub Package Registry (optional)
     - ✅ `repo` - Full control of private repositories (if repo is private)
4. Click **Generate token**
5. **IMPORTANT:** Copy the token immediately - you won't see it again!

**Token format:** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### 3.1.2 Alternative: Generate Token via GitHub CLI

```bash
# Login to GitHub CLI
gh auth login

# Create personal access token
gh auth token

# Or create a new token with specific scopes
gh auth refresh --scopes write:packages,read:packages,repo
```

### 3.2 Test GHCR Authentication

Verify that your token works before adding it to CircleCI.

```bash
# Set your GitHub username and token
GITHUB_USERNAME="your-github-username"
GHCR_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Login to GHCR
echo $GHCR_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Test by pulling a public image (if available)
docker pull ghcr.io/globomantics/schematica:latest || echo "Image doesn't exist yet - this is expected for new projects"

# Logout
docker logout ghcr.io
```

**Expected Output:**
```
Login Succeeded
```

### 3.3 Configure GitHub Package Permissions

Ensure the GitHub repository has the correct permissions for packages.

1. Go to your repository: `https://github.com/YOUR_ORG/schematica`
2. Navigate to **Settings** → **Actions** → **General**
3. Scroll to **Workflow permissions**
4. Select: ✅ **Read and write permissions**
5. Check: ✅ **Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

### 3.4 GHCR Package Visibility

After the first image is pushed, configure package visibility:

1. Go to `https://github.com/orgs/YOUR_ORG/packages/container/schematica/settings`
2. Or navigate via: **Your profile** → **Packages** → **schematica** → **Package settings**
3. Choose visibility:
   - **Private**: Only accessible to organization members
   - **Public**: Accessible to everyone (no authentication required for pulls)

**Recommendation:** Keep it **Private** for production applications.

### 3.5 Allow Repository Access to Package

If using a private package, grant the repository access:

1. In package settings, scroll to **Manage Actions access**
2. Click **Add repository**
3. Select: `YOUR_ORG/schematica`
4. Role: **Write** (allows pushing images)
5. Click **Add**

---

## 4. CircleCI Project Setup

This section covers connecting your repository to CircleCI and configuring contexts with environment variables.

### 4.1 Connect Repository to CircleCI

#### 4.1.1 Via CircleCI Web UI

1. Go to https://app.circleci.com/
2. Click **Projects** in the left sidebar
3. Find **schematica** in the repository list
4. Click **Set Up Project**
5. Choose configuration:
   - Select: **Use the .circleci/config.yml in my repo**
   - Branch: `main`
6. Click **Set Up Project**

CircleCI will automatically detect the `.circleci/config.yml` file and trigger the first pipeline run.

#### 4.1.2 Via CircleCI CLI (Alternative)

```bash
# Install CircleCI CLI
curl -fLSs https://raw.githubusercontent.com/CircleCI-public/circleci-cli/master/install.sh | bash

# Login to CircleCI
circleci setup

# Validate config file
circleci config validate .circleci/config.yml

# Follow project (replace VCS and ORG)
circleci follow YOUR_ORG/schematica
```

### 4.2 Create CircleCI Contexts

Contexts store environment variables that can be shared across multiple projects. We need two contexts:

1. **ghcr-credentials** - For GitHub Container Registry authentication
2. **azure-credentials** - For Azure deployment authentication

#### 4.2.1 Create Contexts via Web UI

1. Go to https://app.circleci.com/
2. Click **Organization Settings** (in the top-left, click your org name)
3. In the left sidebar, click **Contexts**
4. Click **Create Context**

**Create First Context:**
- Context Name: `ghcr-credentials`
- Description: `GitHub Container Registry authentication for Schematica`
- Click **Create Context**

**Create Second Context:**
- Context Name: `azure-credentials`
- Description: `Azure deployment credentials for Schematica`
- Click **Create Context**

#### 4.2.2 Create Contexts via API (Alternative)

```bash
# Set your CircleCI API token
CIRCLECI_TOKEN="your-circleci-api-token"

# Get your organization ID
ORG_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/me | jq -r '.organizations[0].id')

# Create ghcr-credentials context
curl -X POST \
  -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ghcr-credentials",
    "owner": {
      "id": "'$ORG_ID'",
      "type": "organization"
    }
  }' \
  https://circleci.com/api/v2/context

# Create azure-credentials context
curl -X POST \
  -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "azure-credentials",
    "owner": {
      "id": "'$ORG_ID'",
      "type": "organization"
    }
  }' \
  https://circleci.com/api/v2/context
```

### 4.3 Add Environment Variables to Contexts

#### 4.3.1 Add Variables to `ghcr-credentials` Context

**Via Web UI:**

1. Go to **Organization Settings** → **Contexts**
2. Click on **ghcr-credentials**
3. Click **Add Environment Variable** for each variable:

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `GHCR_USERNAME` | `your-github-username` | Your GitHub username (or org name) |
| `GHCR_TOKEN` | `ghp_xxxxxxxxxxxx` | GitHub Personal Access Token with `write:packages` scope |

**Via API:**

```bash
# Set variables
GHCR_USERNAME="your-github-username"
GHCR_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Get context ID
CONTEXT_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context?owner-id=$ORG_ID | \
  jq -r '.items[] | select(.name == "ghcr-credentials") | .id')

# Add GHCR_USERNAME
curl -X PUT \
  -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "'$GHCR_USERNAME'"
  }' \
  https://circleci.com/api/v2/context/$CONTEXT_ID/environment-variable/GHCR_USERNAME

# Add GHCR_TOKEN
curl -X PUT \
  -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "'$GHCR_TOKEN'"
  }' \
  https://circleci.com/api/v2/context/$CONTEXT_ID/environment-variable/GHCR_TOKEN
```

#### 4.3.2 Add Variables to `azure-credentials` Context

**Via Web UI:**

1. Go to **Organization Settings** → **Contexts**
2. Click on **azure-credentials**
3. Click **Add Environment Variable** for each variable:

| Variable Name | Value | Description | Example |
|---------------|-------|-------------|---------|
| `AZURE_CLIENT_ID` | *from section 2.5* | App registration Client ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_TENANT_ID` | *from section 2.5* | Azure AD Tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_SUBSCRIPTION_ID` | `92fd53f2-c38e-461a-9f50-e1ef3382c54c` | Azure Subscription ID | Fixed value |
| `AZURE_RESOURCE_GROUP` | `globomantics-rg` | Resource group name | Fixed value |
| `AZURE_CONTAINERAPPS_NAME` | `schematica-prod` | Production Container App name | Fixed value |
| `AZURE_CONTAINERAPPS_ENV` | `schematica-cae-eastus` | Container Apps Environment name | Fixed value |

**Get your Azure IDs:**

```bash
# Get Client ID
echo "AZURE_CLIENT_ID: $(az ad app list --display-name schematica-circleci-deployer --query [0].appId --output tsv)"

# Get Tenant ID
echo "AZURE_TENANT_ID: $(az account show --query tenantId --output tsv)"

# All values
echo "AZURE_SUBSCRIPTION_ID: 92fd53f2-c38e-461a-9f50-e1ef3382c54c"
echo "AZURE_RESOURCE_GROUP: globomantics-rg"
echo "AZURE_CONTAINERAPPS_NAME: schematica-prod"
echo "AZURE_CONTAINERAPPS_ENV: schematica-cae-eastus"
```

**Via API:**

```bash
# Set variables
AZURE_CLIENT_ID=$(az ad app list --display-name schematica-circleci-deployer --query [0].appId --output tsv)
AZURE_TENANT_ID=$(az account show --query tenantId --output tsv)
AZURE_SUBSCRIPTION_ID="92fd53f2-c38e-461a-9f50-e1ef3382c54c"
AZURE_RESOURCE_GROUP="globomantics-rg"
AZURE_CONTAINERAPPS_NAME="schematica-prod"
AZURE_CONTAINERAPPS_ENV="schematica-cae-eastus"

# Get context ID
AZURE_CONTEXT_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context?owner-id=$ORG_ID | \
  jq -r '.items[] | select(.name == "azure-credentials") | .id')

# Add each variable
for VAR in "AZURE_CLIENT_ID" "AZURE_TENANT_ID" "AZURE_SUBSCRIPTION_ID" "AZURE_RESOURCE_GROUP" "AZURE_CONTAINERAPPS_NAME" "AZURE_CONTAINERAPPS_ENV"; do
  curl -X PUT \
    -H "Circle-Token: ${CIRCLECI_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "value": "'"${!VAR}"'"
    }' \
    https://circleci.com/api/v2/context/$AZURE_CONTEXT_ID/environment-variable/$VAR
  echo "Added $VAR"
done
```

### 4.4 Verify Context Configuration

**Via Web UI:**

1. Go to **Organization Settings** → **Contexts**
2. Click on **ghcr-credentials**
3. Verify you see:
   - `GHCR_USERNAME` (value hidden)
   - `GHCR_TOKEN` (value hidden)
4. Click on **azure-credentials**
5. Verify you see all 6 Azure variables

**Via API:**

```bash
# List contexts
curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context?owner-id=$ORG_ID | \
  jq '.items[] | {name: .name, id: .id}'

# List variables in ghcr-credentials context
GHCR_CONTEXT_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context?owner-id=$ORG_ID | \
  jq -r '.items[] | select(.name == "ghcr-credentials") | .id')

curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context/$GHCR_CONTEXT_ID | \
  jq '.resources[].variable'

# List variables in azure-credentials context
AZURE_CONTEXT_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context?owner-id=$ORG_ID | \
  jq -r '.items[] | select(.name == "azure-credentials") | .id')

curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/context/$AZURE_CONTEXT_ID | \
  jq '.resources[].variable'
```

### 4.5 Configure Context Restrictions (Security)

For production security, restrict which workflows can access sensitive contexts.

**Via Web UI:**

1. Go to **Organization Settings** → **Contexts**
2. Click on **azure-credentials**
3. Click **Add Security Group** or **Add Project Restriction**
4. Options:
   - **Security Groups**: Restrict to specific teams (GitHub Teams)
   - **Project Restrictions**: Restrict to specific repositories
5. Add restriction: `YOUR_ORG/schematica` for the `main` branch only

**Recommended Restriction:**
- Repository: `YOUR_ORG/schematica`
- Branch: `main` (only main branch can deploy)

### 4.6 Enable OIDC Token for CircleCI Project

CircleCI needs to be configured to provide OIDC tokens.

1. Go to **Project Settings** for the Schematica project
2. Navigate to **Advanced**
3. Find **OpenID Connect Token**
4. Enable: ✅ **Allow projects to request OIDC tokens**
5. Click **Save**

**Note:** This is usually enabled by default in newer CircleCI accounts.

---

## 5. Pipeline Configuration Reference

The CircleCI pipeline is defined in `.circleci/config.yml`. Here's an overview of the pipeline structure.

### 5.1 Pipeline Overview

The pipeline consists of two workflows:

1. **build-and-deploy** - Full CI/CD pipeline for the `main` branch
2. **pr-validation** - Validation-only pipeline for pull requests

### 5.2 Build and Deploy Workflow (Main Branch)

```
┌─────────────────────┐
│ lint-and-typecheck  │
└──────────┬──────────┘
           │
           ├──────────────────┐
           │                  │
┌──────────▼──────────┐      ┌▼──────┐
│      test           │      │ (parallel)
└──────────┬──────────┘      └───────┘
           │
           │
┌──────────▼──────────┐
│   build-docker      │
└──────────┬──────────┘
           │
           │ (main branch only)
┌──────────▼──────────┐
│    push-ghcr        │ (uses: ghcr-credentials context)
└──────────┬──────────┘
           │
           │
┌──────────▼──────────┐
│  deploy-staging     │ (uses: azure-credentials context)
└──────────┬──────────┘
           │
           │ (manual approval)
┌──────────▼──────────┐
│ hold-for-production │ ⏸️  [APPROVAL GATE]
└──────────┬──────────┘
           │
           │ (after approval)
┌──────────▼──────────┐
│ deploy-production   │ (uses: azure-credentials context)
└─────────────────────┘
```

### 5.3 Key Jobs Explained

#### 5.3.1 lint-and-typecheck

- **Executor:** `node-executor` (Docker with Node.js 20.10)
- **Purpose:** Code quality checks
- **Steps:**
  1. Checkout code
  2. Install dependencies (with caching)
  3. Run ESLint
  4. Run TypeScript type checking
  5. Build project

#### 5.3.2 test

- **Executor:** `node-executor`
- **Purpose:** Run unit tests
- **Note:** Currently a placeholder - add tests later

#### 5.3.3 build-docker

- **Executor:** `machine-executor` (Ubuntu VM with Docker)
- **Purpose:** Build Docker image
- **Steps:**
  1. Setup Docker buildx
  2. Build Docker image with tags:
     - `ghcr.io/globomantics/schematica:SHORT_SHA`
     - `ghcr.io/globomantics/schematica:latest`
  3. Add OCI labels (revision, created timestamp)
  4. Save image to workspace for next job

#### 5.3.4 push-ghcr

- **Executor:** `machine-executor`
- **Context:** `ghcr-credentials`
- **Purpose:** Push Docker image to GitHub Container Registry
- **Steps:**
  1. Load Docker image from workspace
  2. Authenticate to GHCR using `GHCR_TOKEN`
  3. Push both tags (`SHORT_SHA` and `latest`)

#### 5.3.5 deploy-staging

- **Executor:** `machine-executor`
- **Context:** `azure-credentials`
- **Purpose:** Deploy to staging environment
- **Steps:**
  1. Install Azure CLI
  2. Authenticate using OIDC (federated credentials)
  3. Update `schematica-staging` Container App with new image
  4. Verify deployment with health check (10 retries, 10s interval)

#### 5.3.6 hold-for-production

- **Type:** `approval`
- **Purpose:** Manual approval gate before production deployment
- **Who can approve:** Users with write access to the repository

#### 5.3.7 deploy-production

- **Executor:** `machine-executor`
- **Context:** `azure-credentials`
- **Purpose:** Deploy to production environment
- **Steps:**
  1. Install Azure CLI
  2. Authenticate using OIDC
  3. Update `schematica-prod` Container App with new image
  4. Create new revision with suffix `rev-SHORT_SHA`
  5. Verify deployment with health check

### 5.4 PR Validation Workflow

For pull requests (non-`main` branches):

```
┌─────────────────────┐
│ lint-and-typecheck  │
└─────────────────────┘

┌─────────────────────┐
│      test           │
└─────────────────────┘

┌─────────────────────┐
│   build-docker      │ (validates Dockerfile)
└─────────────────────┘
```

**Note:** PR validation does NOT push to GHCR or deploy to Azure.

### 5.5 Environment Variables Used

The pipeline uses these environment variables from CircleCI contexts and built-in variables:

| Variable | Source | Description |
|----------|--------|-------------|
| `GHCR_USERNAME` | ghcr-credentials context | GitHub username |
| `GHCR_TOKEN` | ghcr-credentials context | GitHub PAT |
| `AZURE_CLIENT_ID` | azure-credentials context | Azure AD app client ID |
| `AZURE_TENANT_ID` | azure-credentials context | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | azure-credentials context | Azure subscription ID |
| `AZURE_RESOURCE_GROUP` | azure-credentials context | Resource group name |
| `AZURE_CONTAINERAPPS_NAME` | azure-credentials context | Production app name |
| `AZURE_CONTAINERAPPS_ENV` | azure-credentials context | Environment name |
| `CIRCLE_SHA1` | Built-in | Full git commit SHA |
| `CIRCLE_PROJECT_USERNAME` | Built-in | GitHub organization/user |
| `CIRCLE_PROJECT_REPONAME` | Built-in | Repository name |
| `CIRCLE_OIDC_TOKEN_V2` | Built-in | CircleCI OIDC token |

### 5.6 Image Tagging Strategy

Images are tagged with:

1. **Short SHA**: First 7 characters of git commit SHA
   - Example: `ghcr.io/globomantics/schematica:a1b2c3d`
   - Used for: Deployments (immutable reference)

2. **Latest**: Always points to the most recent main branch build
   - Example: `ghcr.io/globomantics/schematica:latest`
   - Used for: Initial container app creation, development

### 5.7 Caching Strategy

The pipeline uses caching to speed up builds:

| Cache Key | Cached Content | TTL |
|-----------|----------------|-----|
| `v1-deps-{{ checksum "package-lock.json" }}` | `node_modules` | Until package-lock.json changes |

**Cache invalidation:** Changing `package-lock.json` creates a new cache key, invalidating the old cache.

---

## 6. Triggering Deployments

### 6.1 Automatic Triggers

#### 6.1.1 Push to Main Branch

Triggers the full **build-and-deploy** workflow:

```bash
# Make changes
git checkout main
git pull origin main

# Make your changes
echo "console.log('New feature');" >> src/index.ts

# Commit and push
git add .
git commit -m "feat: Add new feature"
git push origin main
```

**What happens:**
1. Lint and type check runs
2. Tests run
3. Docker image builds
4. Image pushes to GHCR
5. **Staging deployment** happens automatically
6. Pipeline **pauses** at approval gate
7. After approval → **Production deployment**

#### 6.1.2 Pull Request

Triggers the **pr-validation** workflow:

```bash
# Create feature branch
git checkout -b feature/new-api

# Make changes
echo "export const newAPI = () => {};" >> src/api.ts

# Commit and push
git add .
git commit -m "feat: Add new API endpoint"
git push origin feature/new-api

# Create PR via GitHub UI or CLI
gh pr create --title "Add new API endpoint" --body "Description of changes"
```

**What happens:**
1. Lint and type check runs
2. Tests run
3. Docker image builds (validates Dockerfile)
4. **NO deployment** occurs

### 6.2 Manual Triggers

#### 6.2.1 Re-run Pipeline from CircleCI UI

1. Go to https://app.circleci.com/
2. Navigate to **Projects** → **schematica**
3. Click on the pipeline you want to re-run
4. Click **Rerun** (top-right)
5. Choose:
   - **Rerun workflow from start** - Starts from the beginning
   - **Rerun workflow from failed** - Only re-runs failed jobs

#### 6.2.2 Trigger via API

```bash
# Set variables
CIRCLECI_TOKEN="your-circleci-api-token"
PROJECT_SLUG="gh/YOUR_ORG/schematica"

# Trigger pipeline on main branch
curl -X POST \
  -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "branch": "main",
    "parameters": {}
  }' \
  https://circleci.com/api/v2/project/$PROJECT_SLUG/pipeline
```

### 6.3 Deployment Frequency

**Recommended deployment cadence:**

| Environment | Deployment Frequency | Triggered By |
|-------------|---------------------|--------------|
| Staging | Every push to `main` | Automatic |
| Production | 1-2 times per week | Manual approval |

### 6.4 Emergency Hotfix Deployment

For critical production issues:

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Make fix
# ... edit files ...

# Commit
git add .
git commit -m "fix: Critical bug in authentication"

# Push and create PR
git push origin hotfix/critical-bug
gh pr create --title "Hotfix: Critical authentication bug" --body "Emergency fix"

# Get PR approved and merge to main
# Pipeline will automatically deploy to staging

# Monitor staging deployment
# Then approve production deployment immediately in CircleCI UI
```

---

## 7. Manual Approval for Production

The pipeline includes a manual approval gate before production deployment for safety and control.

### 7.1 Approval Process

#### 7.1.1 Via CircleCI Web UI

1. **Notification:** CircleCI will send notifications when approval is needed:
   - Email notification (if enabled)
   - Slack notification (if configured)
   - In-app notification

2. **Navigate to approval:**
   - Go to https://app.circleci.com/
   - Click **Projects** → **schematica**
   - Find the pipeline with **"Needs Approval"** status
   - Click on the pipeline

3. **Review staging deployment:**
   - Check the **deploy-staging** job logs
   - Verify staging URL is working: `https://schematica-staging.HASH.eastus.azurecontainerapps.io`
   - Test the staging deployment manually

4. **Approve deployment:**
   - Click the **hold-for-production** job
   - Click **Approve** button
   - Add optional comment (e.g., "Tested on staging, looks good")
   - Click **Confirm**

5. **Monitor production deployment:**
   - The **deploy-production** job will start automatically
   - Watch the logs for any issues
   - Verify production URL: `https://schematica-prod.HASH.eastus.azurecontainerapps.io`

#### 7.1.2 Via CircleCI API

```bash
# Set variables
CIRCLECI_TOKEN="your-circleci-api-token"
PROJECT_SLUG="gh/YOUR_ORG/schematica"

# Get the workflow ID that needs approval
WORKFLOW_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  "https://circleci.com/api/v2/project/$PROJECT_SLUG/pipeline" | \
  jq -r '.items[0].id')

# Get the approval job ID
APPROVAL_JOB_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  "https://circleci.com/api/v2/workflow/$WORKFLOW_ID/job" | \
  jq -r '.items[] | select(.name == "hold-for-production") | .id')

# Approve the job
curl -X POST \
  -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  https://circleci.com/api/v2/workflow/$WORKFLOW_ID/approve/$APPROVAL_JOB_ID
```

### 7.2 Who Can Approve?

Approval permissions are based on GitHub repository access:

| GitHub Role | Can Approve? |
|-------------|--------------|
| Admin | ✅ Yes |
| Write | ✅ Yes |
| Read | ❌ No |

### 7.3 Approval Timeout

**Default behavior:**
- No automatic timeout - approval request stays open indefinitely
- Pipeline status: "On Hold"

**Best practices:**
- Approve or cancel within 24 hours
- Don't let approvals queue up

### 7.4 Canceling a Deployment

If you need to cancel a deployment:

1. Go to the pipeline in CircleCI
2. Click **Cancel Workflow** (top-right)
3. Confirm cancellation

**Note:** This only cancels the CircleCI workflow. If staging deployment already completed, it will remain deployed.

### 7.5 Approval Notifications

Configure Slack notifications for approval requests:

1. Go to **Organization Settings** → **Integrations**
2. Click **Slack**
3. Click **Add Slack Channel**
4. Authorize CircleCI in Slack
5. Configure notification settings:
   - ✅ **Workflow Status**: On hold
   - Channel: `#deployments`
6. Click **Save**

Example Slack notification:
```
🔔 Deployment Approval Required
Project: schematica
Workflow: build-and-deploy
Branch: main
Commit: a1b2c3d - "feat: Add new feature"
Status: Waiting for approval to deploy to production

[Approve] [View Pipeline]
```

---

## 8. Troubleshooting

This section covers common issues and their solutions.

### 8.1 OIDC Token Exchange Failures

#### 8.1.1 Error: "AADSTS700024: Client assertion is not within its valid time range"

**Cause:** Clock skew between CircleCI and Azure AD.

**Solution:**
```bash
# This is a CircleCI infrastructure issue
# Retry the job - usually resolves itself
```

In CircleCI UI:
1. Click the failed job
2. Click **Rerun** → **Rerun job with SSH** (for debugging)
3. Or **Rerun workflow from failed**

#### 8.1.2 Error: "AADSTS700016: Application with identifier was not found"

**Cause:** Incorrect `AZURE_CLIENT_ID` in CircleCI context.

**Solution:**
```bash
# Verify the correct Client ID
az ad app list --display-name schematica-circleci-deployer --query [0].appId --output tsv

# Update in CircleCI context
# Go to Organization Settings → Contexts → azure-credentials
# Edit AZURE_CLIENT_ID variable
```

#### 8.1.3 Error: "AADSTS70021: No matching federated identity record found"

**Cause:** Federated credential subject doesn't match CircleCI OIDC token.

**Solution:**

1. Check the current federated credentials:
```bash
APP_OBJECT_ID=$(az ad app list --display-name schematica-circleci-deployer --query [0].id --output tsv)
az ad app federated-credential list --id $APP_OBJECT_ID --output table
```

2. Verify CircleCI OIDC token claims:
   - Enable SSH in failed job
   - SSH into the job
   - Run:
   ```bash
   curl -H "Circle-Token: ${CIRCLE_OIDC_TOKEN_V2}" \
     "https://circleci.com/api/v2/project/gh/${CIRCLE_PROJECT_USERNAME}/${CIRCLE_PROJECT_REPONAME}/oidc-token" | \
     jq -r '.token' | \
     cut -d. -f2 | \
     base64 -d | \
     jq .
   ```

3. Update federated credential to match the subject claim:
```bash
# Delete old credential
az ad app federated-credential delete \
  --id $APP_OBJECT_ID \
  --federated-credential-id OLD_CREDENTIAL_ID

# Create new credential with correct subject
# Use wildcard for simplicity
CIRCLECI_ORG_ID="your-org-id"
az ad app federated-credential create \
  --id $APP_OBJECT_ID \
  --parameters '{
    "name": "circleci-all-branches",
    "issuer": "https://oidc.circleci.com/org/'$CIRCLECI_ORG_ID'",
    "subject": "org/'$CIRCLECI_ORG_ID'/project/*",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### 8.2 GHCR Authentication Issues

#### 8.2.1 Error: "unauthorized: authentication required"

**Cause:** Invalid or expired `GHCR_TOKEN`.

**Solution:**

1. Verify token works locally:
```bash
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin
```

2. If it fails, create a new token:
   - Go to https://github.com/settings/tokens
   - Generate new token with `write:packages` scope
   - Update `GHCR_TOKEN` in CircleCI context

3. Update context:
   - Go to Organization Settings → Contexts → ghcr-credentials
   - Edit `GHCR_TOKEN` variable
   - Paste new token

#### 8.2.2 Error: "denied: installation not allowed to write"

**Cause:** GitHub package doesn't have write access for the repository.

**Solution:**

1. Go to package settings:
   - `https://github.com/orgs/YOUR_ORG/packages/container/schematica/settings`

2. Add repository access:
   - Scroll to **Manage Actions access**
   - Click **Add repository**
   - Select `YOUR_ORG/schematica`
   - Role: **Write**
   - Click **Add**

#### 8.2.3 Error: "429 Too Many Requests"

**Cause:** Rate limiting from GHCR.

**Solution:**
- Wait 60 minutes
- Reduce deployment frequency
- Consider using Azure Container Registry instead

### 8.3 Container App Update Failures

#### 8.3.1 Error: "ContainerAppNotFound"

**Cause:** Container App doesn't exist or wrong name.

**Solution:**
```bash
# List all container apps
az containerapp list --resource-group globomantics-rg --output table

# Verify the app name
az containerapp show \
  --name schematica-prod \
  --resource-group globomantics-rg

# Update AZURE_CONTAINERAPPS_NAME in CircleCI context if needed
```

#### 8.3.2 Error: "ImagePullFailed"

**Cause:** Container App can't pull the image from GHCR.

**Solution:**

1. Verify image exists:
```bash
# Check if image was pushed
docker pull ghcr.io/globomantics/schematica:latest
```

2. If image is private, add GHCR credentials to Container App:
```bash
# Add registry credentials
az containerapp registry set \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --server ghcr.io \
  --username $GITHUB_USERNAME \
  --password $GHCR_TOKEN
```

3. Or make package public:
   - Go to package settings
   - Change visibility to **Public**

#### 8.3.3 Error: "InsufficientPermissions"

**Cause:** Service principal doesn't have permissions to update Container App.

**Solution:**
```bash
# Get service principal ID
APP_ID=$(az ad app list --display-name schematica-circleci-deployer --query [0].appId --output tsv)
SP_OBJECT_ID=$(az ad sp list --filter "appId eq '$APP_ID'" --query [0].id --output tsv)

# Grant Contributor role
az role assignment create \
  --role "Contributor" \
  --assignee $SP_OBJECT_ID \
  --scope /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg

# Verify role assignment
az role assignment list --assignee $SP_OBJECT_ID --output table
```

### 8.4 Health Check Timeouts

#### 8.4.1 Error: "Staging health check failed!"

**Cause:** Application not responding to health checks within timeout.

**Solution:**

1. Check Container App logs:
```bash
az containerapp logs show \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --tail 100
```

2. Check if health endpoint exists:
```bash
STAGING_URL=$(az containerapp show \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

curl -v "https://${STAGING_URL}/health"
```

3. Increase timeout in `.circleci/config.yml`:
```yaml
# Change from 10 retries to 20
for i in {1..20}; do
  if curl -s "https://${STAGING_URL}/health" | grep -q "healthy"; then
    echo "Staging deployment verified successfully!"
    exit 0
  fi
  echo "Waiting for staging to be ready... (attempt $i/20)"
  sleep 10
done
```

4. Check if health endpoint returns correct response:
```javascript
// Ensure /health endpoint returns "healthy" in the response
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});
```

### 8.5 Build Failures

#### 8.5.1 Error: "npm ERR! code ELIFECYCLE"

**Cause:** Build script failed (lint, typecheck, or build).

**Solution:**

1. Run locally to reproduce:
```bash
npm ci
npm run lint
npm run typecheck
npm run build
```

2. Fix the errors shown in the output

3. Commit and push the fix

#### 8.5.2 Error: "Docker build failed"

**Cause:** Dockerfile has errors or dependencies can't be installed.

**Solution:**

1. Test Docker build locally:
```bash
docker build -t schematica-test .
```

2. Check Dockerfile syntax

3. Verify all files referenced in Dockerfile exist

### 8.6 Context Access Denied

#### 8.6.1 Error: "Project not authorized to use context"

**Cause:** Repository doesn't have access to the context.

**Solution:**

1. Go to Organization Settings → Contexts
2. Click on the context (e.g., `azure-credentials`)
3. Check **Project Restrictions**
4. Add the repository:
   - Click **Add Project**
   - Select `YOUR_ORG/schematica`
   - Click **Add**

### 8.7 SSH Debugging

For complex issues, enable SSH access to the job:

1. In CircleCI UI, click the failed job
2. Click **Rerun** → **Rerun job with SSH**
3. Wait for the job to start
4. Copy the SSH command from the job output
5. SSH into the job:
```bash
ssh -p PORT HASH@IP_ADDRESS
```

6. Debug the issue:
```bash
# Check environment variables
env | grep AZURE

# Test Azure login manually
az login --service-principal \
  --username "${AZURE_CLIENT_ID}" \
  --tenant "${AZURE_TENANT_ID}" \
  --federated-token "$(curl -s -H "Circle-Token: ${CIRCLE_OIDC_TOKEN_V2}" \
    "https://circleci.com/api/v2/project/gh/${CIRCLE_PROJECT_USERNAME}/${CIRCLE_PROJECT_REPONAME}/oidc-token" | \
    jq -r '.token')"

# Test GHCR login
echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME}" --password-stdin
```

---

## 9. Monitoring and Logs

### 9.1 CircleCI Pipeline Monitoring

#### 9.1.1 View Pipeline Status

**Via Web UI:**
1. Go to https://app.circleci.com/
2. Click **Projects** → **schematica**
3. View recent pipelines:
   - ✅ Green: Success
   - 🔴 Red: Failed
   - 🟡 Yellow: Running
   - ⏸️ Gray: On hold (waiting for approval)

**Via API:**
```bash
# Get recent pipelines
CIRCLECI_TOKEN="your-token"
PROJECT_SLUG="gh/YOUR_ORG/schematica"

curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  "https://circleci.com/api/v2/project/$PROJECT_SLUG/pipeline?branch=main" | \
  jq '.items[] | {id: .id, state: .state, created_at: .created_at, branch: .vcs.branch}'
```

#### 9.1.2 View Job Logs

1. Click on a pipeline
2. Click on a specific job (e.g., `deploy-staging`)
3. View real-time or historical logs
4. Search logs with Cmd/Ctrl + F

**Download logs:**
```bash
# Get workflow ID
WORKFLOW_ID="workflow-id-here"

# Get job ID
JOB_ID=$(curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  "https://circleci.com/api/v2/workflow/$WORKFLOW_ID/job" | \
  jq -r '.items[] | select(.name == "deploy-staging") | .id')

# Get job details and logs
curl -s -H "Circle-Token: ${CIRCLECI_TOKEN}" \
  "https://circleci.com/api/v2/project/$PROJECT_SLUG/job/$JOB_ID" | \
  jq .
```

#### 9.1.3 Pipeline Insights

View metrics and trends:

1. Go to **Insights** in CircleCI sidebar
2. Select **schematica** project
3. View:
   - Success rate
   - Duration trends
   - Most failed jobs
   - Credit usage

### 9.2 Azure Container Apps Monitoring

#### 9.2.1 View Application Logs

**Via Azure CLI:**

```bash
# Real-time logs for staging
az containerapp logs show \
  --name schematica-staging \
  --resource-group globomantics-rg \
  --tail 100 \
  --follow

# Real-time logs for production
az containerapp logs show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --tail 100 \
  --follow

# Filter logs by time
az containerapp logs show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --since 1h
```

**Via Azure Portal:**

1. Go to https://portal.azure.com
2. Navigate to **Resource groups** → **globomantics-rg**
3. Click on **schematica-prod**
4. In the left menu, click **Monitoring** → **Log stream**
5. View live logs

#### 9.2.2 View System Logs (Container App Events)

```bash
# Show recent revisions
az containerapp revision list \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --output table

# Show replica details
az containerapp replica list \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --revision REVISION_NAME \
  --output table
```

#### 9.2.3 Query Logs with Log Analytics

```bash
# Get Log Analytics workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group globomantics-rg \
  --workspace-name schematica-logs-eastus \
  --query customerId \
  --output tsv)

# Query logs (last 24 hours)
az monitor log-analytics query \
  --workspace $WORKSPACE_ID \
  --analytics-query "
    ContainerAppConsoleLogs_CL
    | where ContainerAppName_s == 'schematica-prod'
    | where TimeGenerated > ago(24h)
    | project TimeGenerated, Log_s
    | order by TimeGenerated desc
    | limit 100
  " \
  --output table
```

**Via Azure Portal:**

1. Go to **globomantics-rg** → **schematica-logs-eastus** (Log Analytics workspace)
2. Click **Logs** in the left menu
3. Run KQL queries:

```kql
// All logs from production in last 1 hour
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "schematica-prod"
| where TimeGenerated > ago(1h)
| project TimeGenerated, Log_s
| order by TimeGenerated desc

// Error logs only
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "schematica-prod"
| where Log_s contains "error" or Log_s contains "ERROR"
| where TimeGenerated > ago(24h)
| project TimeGenerated, Log_s

// Count logs by severity
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "schematica-prod"
| where TimeGenerated > ago(24h)
| summarize count() by bin(TimeGenerated, 1h)
| render timechart
```

### 9.3 Application Metrics

#### 9.3.1 View Container App Metrics

**Via Azure Portal:**

1. Go to **globomantics-rg** → **schematica-prod**
2. Click **Monitoring** → **Metrics**
3. Select metrics:
   - **Requests** - HTTP request count
   - **CPU Usage** - CPU utilization percentage
   - **Memory Working Set Bytes** - Memory usage
   - **Replica Count** - Number of active replicas
   - **Response Time** - Average response time

**Via Azure CLI:**

```bash
# Get CPU usage (last 1 hour)
az monitor metrics list \
  --resource /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.App/containerApps/schematica-prod \
  --metric "UsageNanoCores" \
  --start-time "2024-01-01T00:00:00Z" \
  --end-time "2024-01-01T01:00:00Z" \
  --interval PT1M \
  --aggregation Average \
  --output table

# Get request count
az monitor metrics list \
  --resource /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.App/containerApps/schematica-prod \
  --metric "Requests" \
  --aggregation Total \
  --output table
```

#### 9.3.2 Set Up Alerts

Create alerts for critical metrics:

```bash
# Create alert rule for high CPU usage
az monitor metrics alert create \
  --name "High CPU Usage - Production" \
  --resource-group globomantics-rg \
  --scopes /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.App/containerApps/schematica-prod \
  --condition "avg UsageNanoCores > 800000000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --description "Alert when CPU usage exceeds 80%" \
  --severity 2

# Create alert rule for failed requests
az monitor metrics alert create \
  --name "High Error Rate - Production" \
  --resource-group globomantics-rg \
  --scopes /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.App/containerApps/schematica-prod \
  --condition "total Requests > 100" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --description "Alert when error rate is high" \
  --severity 1
```

### 9.4 Deployment History

#### 9.4.1 View Container App Revisions

```bash
# List all revisions
az containerapp revision list \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --output table

# Show specific revision details
az containerapp revision show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --revision REVISION_NAME
```

#### 9.4.2 View Revision Traffic Split

```bash
# Show traffic distribution across revisions
az containerapp ingress traffic show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --output table
```

### 9.5 Health Checks

#### 9.5.1 Manual Health Check

```bash
# Get app URL
PROD_URL=$(az containerapp show \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

# Check health endpoint
curl -s "https://${PROD_URL}/health" | jq .

# Check with detailed timing
curl -w "\nTime: %{time_total}s\nHTTP Code: %{http_code}\n" \
  -s -o /dev/null \
  "https://${PROD_URL}/health"
```

#### 9.5.2 Automated Health Monitoring

Set up external monitoring with a service like:
- **Azure Application Insights**
- **Datadog**
- **New Relic**
- **Pingdom**

Example with Azure Application Insights:

```bash
# Create Application Insights instance
az monitor app-insights component create \
  --app schematica-insights \
  --location eastus \
  --resource-group globomantics-rg \
  --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app schematica-insights \
  --resource-group globomantics-rg \
  --query instrumentationKey \
  --output tsv)

# Add to Container App environment variables
az containerapp update \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$INSTRUMENTATION_KEY"
```

---

## 10. Security Best Practices

### 10.1 Credential Management

#### 10.1.1 Rotate GHCR Tokens Regularly

**Schedule:** Every 90 days

**Process:**

1. Generate new GitHub PAT:
   - Go to https://github.com/settings/tokens
   - Create new token with `write:packages` scope
   - Copy the new token

2. Update CircleCI context:
   - Go to Organization Settings → Contexts → ghcr-credentials
   - Edit `GHCR_TOKEN`
   - Replace with new token

3. Test the new token:
   - Trigger a new deployment
   - Verify push to GHCR succeeds

4. Revoke old token:
   - Go to https://github.com/settings/tokens
   - Find the old token
   - Click **Delete**

#### 10.1.2 Azure Service Principal Credentials

**OIDC (Federated Credentials):** No secrets to rotate! This is the recommended approach.

**If using client secret (not recommended):**
- Maximum expiry: 2 years
- Rotate every 6 months
- Use Azure Key Vault for storage

### 10.2 Least Privilege Access

#### 10.2.1 Azure RBAC

Instead of Contributor at resource group level, use specific roles:

```bash
# Remove broad Contributor role
az role assignment delete \
  --assignee $SP_OBJECT_ID \
  --scope /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg

# Assign specific role for Container Apps
az role assignment create \
  --role "Contributor" \
  --assignee $SP_OBJECT_ID \
  --scope /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.App

# Or create custom role
az role definition create --role-definition '{
  "Name": "Container App Deployer",
  "Description": "Can update Container Apps only",
  "Actions": [
    "Microsoft.App/containerApps/write",
    "Microsoft.App/containerApps/read"
  ],
  "AssignableScopes": [
    "/subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg"
  ]
}'
```

#### 10.2.2 CircleCI Context Restrictions

Restrict contexts to specific projects and branches:

1. Go to Organization Settings → Contexts
2. Click on **azure-credentials**
3. Add **Project Restrictions**:
   - Repository: `YOUR_ORG/schematica`
   - Branch: `main`
4. Click **Add**

Now only the `main` branch can access Azure credentials.

### 10.3 Secrets Management

#### 10.3.1 Never Hardcode Secrets

**Bad:**
```yaml
- run:
    name: Deploy
    command: |
      export API_KEY="hardcoded-secret-here"  # ❌ NEVER DO THIS
```

**Good:**
```yaml
- run:
    name: Deploy
    command: |
      export API_KEY="${MCP_API_KEY}"  # ✅ Use environment variable
```

#### 10.3.2 Use Azure Key Vault for Application Secrets

All application secrets should be in Azure Key Vault:

```bash
# Add secret to Key Vault
az keyvault secret set \
  --vault-name schematica-kv-eastus \
  --name database-password \
  --value "super-secret-password"

# Reference in Container App
az containerapp secret set \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --secrets database-password=keyvaultref:https://schematica-kv-eastus.vault.azure.net/secrets/database-password,identityref:system

# Use in environment variable
az containerapp update \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --set-env-vars "DATABASE_PASSWORD=secretref:database-password"
```

#### 10.3.3 Audit Secret Access

Enable Key Vault logging:

```bash
# Enable diagnostic settings for Key Vault
az monitor diagnostic-settings create \
  --name KeyVaultAuditLogs \
  --resource /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.KeyVault/vaults/schematica-kv-eastus \
  --logs '[
    {
      "category": "AuditEvent",
      "enabled": true,
      "retentionPolicy": {
        "enabled": true,
        "days": 90
      }
    }
  ]' \
  --workspace /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/globomantics-rg/providers/Microsoft.OperationalInsights/workspaces/schematica-logs-eastus
```

Query access logs:

```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| where OperationName == "SecretGet"
| project TimeGenerated, CallerIPAddress, identity_claim_appid_g, ResultType
| order by TimeGenerated desc
```

### 10.4 Network Security

#### 10.4.1 Restrict Container App Ingress

**Current setup:** External ingress (publicly accessible)

**For sensitive applications:**

```bash
# Change to internal ingress (only accessible within VNet)
az containerapp ingress update \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --type internal

# Or restrict to specific IPs (requires Application Gateway or Front Door)
```

#### 10.4.2 Enable HTTPS Only

```bash
# Ensure HTTPS is enforced
az containerapp ingress update \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --allow-insecure false
```

### 10.5 Container Image Security

#### 10.5.1 Scan Images for Vulnerabilities

Add to CircleCI pipeline:

```yaml
- run:
    name: Scan Docker image
    command: |
      # Install Trivy scanner
      wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
      echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
      sudo apt-get update
      sudo apt-get install trivy

      # Scan image
      trivy image --severity HIGH,CRITICAL ghcr.io/globomantics/schematica:${SHORT_SHA}
```

#### 10.5.2 Use Specific Base Image Tags

**Bad:**
```dockerfile
FROM node:latest  # ❌ Version can change unexpectedly
```

**Good:**
```dockerfile
FROM node:20.10-alpine  # ✅ Pinned version
```

#### 10.5.3 Run as Non-Root User

```dockerfile
# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs
```

### 10.6 Audit Logging

#### 10.6.1 Enable Azure Activity Log

Azure Activity Log is enabled by default. Query it:

```bash
# Show recent Container App updates
az monitor activity-log list \
  --resource-group globomantics-rg \
  --offset 7d \
  --query "[?contains(resourceId, 'containerApps')]" \
  --output table
```

#### 10.6.2 CircleCI Audit Logs

Available on paid plans:

1. Go to Organization Settings → Security
2. Click **Audit Log**
3. Filter by:
   - Event type: `context.secrets.accessed`
   - Date range

### 10.7 Compliance

#### 10.7.1 Data Residency

Ensure all resources are in the same region:

```bash
# Verify all resources are in eastus
az resource list \
  --resource-group globomantics-rg \
  --query "[].{name:name, location:location}" \
  --output table
```

#### 10.7.2 Encryption at Rest

Azure Container Apps encrypts data at rest by default using Microsoft-managed keys.

For customer-managed keys:

```bash
# Create customer-managed key in Key Vault
az keyvault key create \
  --vault-name schematica-kv-eastus \
  --name container-encryption-key \
  --protection software

# Use with Container Apps Environment (requires premium tier)
```

### 10.8 Incident Response

#### 10.8.1 Emergency Rollback

If a deployment causes issues:

**Option 1: Rollback to previous revision**

```bash
# List revisions
az containerapp revision list \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --output table

# Set 100% traffic to previous revision
az containerapp ingress traffic set \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --revision-weight PREVIOUS_REVISION=100 CURRENT_REVISION=0
```

**Option 2: Deploy previous image**

```bash
# Deploy known good image
az containerapp update \
  --name schematica-prod \
  --resource-group globomantics-rg \
  --image ghcr.io/globomantics/schematica:KNOWN_GOOD_SHA
```

#### 10.8.2 Emergency Access

For emergency situations, you can temporarily disable OIDC and use client secret:

```bash
# Create client secret (expires in 1 day)
az ad app credential reset \
  --id $APP_ID \
  --years 0 \
  --display-name "Emergency Access - $(date +%Y-%m-%d)" \
  --query password \
  --output tsv

# Use for manual login
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password "CLIENT_SECRET_HERE" \
  --tenant $AZURE_TENANT_ID
```

**Remember to delete the secret after the emergency!**

---

## Conclusion

This documentation provides a complete guide for setting up and operating the CircleCI CI/CD pipeline for Schematica. Key takeaways:

1. **Security First**: Use OIDC for Azure authentication (no long-lived secrets)
2. **Automation**: Staging deploys automatically, production requires approval
3. **Monitoring**: Use Azure Log Analytics and Application Insights
4. **Safety**: Manual approval gates prevent accidental production deployments
5. **Compliance**: All secrets in Azure Key Vault, audit logs enabled

### Quick Reference Commands

```bash
# View pipeline status
circleci project list

# View Container App logs
az containerapp logs show --name schematica-prod -g globomantics-rg --follow

# Rollback deployment
az containerapp ingress traffic set --name schematica-prod -g globomantics-rg \
  --revision-weight PREVIOUS_REVISION=100

# View metrics
az monitor metrics list --resource RESOURCE_ID --metric Requests

# Check health
curl https://$(az containerapp show --name schematica-prod -g globomantics-rg \
  --query properties.configuration.ingress.fqdn -o tsv)/health
```

### Support Resources

- **CircleCI Documentation**: https://circleci.com/docs/
- **Azure Container Apps Documentation**: https://learn.microsoft.com/azure/container-apps/
- **GitHub Container Registry Documentation**: https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- **Azure OIDC Documentation**: https://learn.microsoft.com/azure/active-directory/develop/workload-identity-federation

### Maintenance Schedule

| Task | Frequency | Responsible |
|------|-----------|-------------|
| Rotate GHCR tokens | Every 90 days | DevOps team |
| Review Azure role assignments | Monthly | Security team |
| Update base Docker images | Monthly | Development team |
| Review and archive old revisions | Weekly | DevOps team |
| Audit Key Vault access logs | Weekly | Security team |
| Review pipeline insights | Weekly | Development team |

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Maintained By:** Globomantics DevOps Team
