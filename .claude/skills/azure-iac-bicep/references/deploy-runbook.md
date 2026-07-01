# Deploy Runbook: Lint, What-If, Deploy, Stacks, CI

Load when running deployments or building a pipeline.

## The four-step loop

Always lint, then preview, then deploy. Never deploy a template you have not what-if'd against the target.

```bash
# 1. Build + lint. Catches bad property names and missing required fields offline.
az bicep build --file main.bicep

# 2. What-if. Reports create / modify / delete / no-change BEFORE touching the environment.
az deployment group what-if \
  --resource-group rg-warnerco-prod \
  --template-file main.bicep \
  --parameters main.bicepparam

# 3. Deploy (incremental is the default: adds and updates, leaves unmentioned resources alone).
az deployment group create \
  --resource-group rg-warnerco-prod \
  --template-file main.bicep \
  --parameters main.bicepparam \
  --name "deploy-$(date +%Y%m%d-%H%M%S)"

# 4. Confirm.
az deployment group show \
  --resource-group rg-warnerco-prod \
  --name <deployment-name> \
  --query properties.provisioningState -o tsv
```

PowerShell 7 one-liner for the preview step (paste-ready):

```powershell
az deployment group what-if --resource-group rg-warnerco-prod --template-file main.bicep --parameters main.bicepparam
```

## Deployment mode: incremental vs complete

| Mode | Behavior | When |
|------|----------|------|
| `Incremental` (default) | Adds and updates resources in the template; leaves others untouched | Almost always |
| `Complete` | **Deletes** any resource in the RG not in the template | Only when the template is the sole authority for the RG and you have what-if'd the deletions |

`Complete` mode deletes. Run what-if first and read the delete list out loud before you accept it.

## Scope-matched deploy commands

| Scope | Command |
|-------|---------|
| Resource group | `az deployment group create --resource-group <rg> ...` |
| Subscription | `az deployment sub create --location <region> ...` |
| Management group | `az deployment mg create --management-group-id <mg> --location <region> ...` |
| Tenant | `az deployment tenant create --location <region> ...` |

## Deployment stacks

A deployment stack manages a set of resources as one lifecycle unit and can enforce that nothing drifts outside the template. Use it when you want a managed boundary with controlled teardown.

```bash
# Create or update a stack at resource-group scope.
az stack group create \
  --name stack-warnerco \
  --resource-group rg-warnerco-prod \
  --template-file main.bicep \
  --parameters main.bicepparam \
  --action-on-unmanage detachAll \
  --deny-settings-mode denyDelete
```

- `--action-on-unmanage`: what happens to resources when they leave the stack (`detachAll` keeps them, `deleteAll` removes them).
- `--deny-settings-mode`: `denyDelete` or `denyWriteAndDelete` blocks out-of-band changes to stack-managed resources, which stops portal drift.

## GitHub Actions pipeline

OIDC federated credentials, no stored secrets. This is the default CI pattern for this repo.

```yaml
name: deploy-infra

on:
  push:
    branches: [main]
    paths: ['infra/**']

permissions:
  id-token: write   # Required for OIDC federation to Entra ID.
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Secretless auth via federated credential. No client secret in GitHub.
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      # Preview on every run so the job log shows the planned delta.
      - name: What-if
        uses: azure/cli@v2
        with:
          inlineScript: |
            az deployment group what-if \
              --resource-group rg-warnerco-prod \
              --template-file infra/main.bicep \
              --parameters infra/main.bicepparam

      - name: Deploy
        uses: azure/cli@v2
        with:
          inlineScript: |
            az deployment group create \
              --resource-group rg-warnerco-prod \
              --template-file infra/main.bicep \
              --parameters infra/main.bicepparam
```

The three `secrets.AZURE_*` values are **identifiers, not credentials**. The federated credential trust is configured on an Entra ID app registration or managed identity, so there is no client secret to rotate or leak.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `InvalidTemplate` on a property name | Stale or wrong apiVersion | Check `mcp__azure__bicepschema`, correct the property or bump apiVersion |
| What-if shows changes on an unchanged resource | A default the provider normalizes | Usually benign; confirm the diff is provider noise, not a real edit |
| `AuthorizationFailed` at deploy | Identity lacks the role at that scope | Grant the deploying principal Contributor (or a tighter custom role) at the target scope |
| Storage/KeyVault name rejected | Length or character constraint | Wrap in `toLower()` / `take()`; storage and Key Vault cap at 24 chars |
| Deployment succeeds but resource misconfigured | What-if skipped | Always run what-if; read the delta before accepting |
