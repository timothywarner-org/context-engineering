---
name: azure-iac-bicep
description: Author, refactor, validate, and deploy Azure infrastructure as code in Bicep (preferred) and ARM JSON. Use when creating or editing .bicep / .bicepparam files, designing modules, decompiling or migrating ARM templates to Bicep, wiring what-if and deployment-stack workflows, hardening IaC for security (managed identity, private endpoints, no secrets in templates), or generating GitHub Actions pipelines that deploy Bicep. Triggers on "write a Bicep module", "convert this ARM template", "deploy this to a resource group", "what-if", "bicepparam", "az deployment", or any Azure infrastructure-as-code authoring request.
---

# Azure IaC: Bicep + ARM

Production-grade Azure infrastructure as code. **Bicep is the default authoring language**; ARM JSON is the compile target and the fallback for tooling that has not adopted Bicep. Decompile legacy ARM to Bicep, never hand-author new ARM JSON.

## When to load reference files

This file is the index. Load the deeper material only when the task needs it:

| You are... | Read |
|------------|------|
| Authoring a module, picking a scope, choosing decorators, wiring outputs | `references/module-patterns.md` |
| Migrating ARM JSON to Bicep, or deciding Bicep vs ARM vs Terraform | `references/arm-vs-bicep.md` |
| Running lint / what-if / deploy / deployment stacks, or building a CI pipeline | `references/deploy-runbook.md` |

## Documentation-first mandate

Resource API shapes drift. **Before emitting any resource declaration, confirm the type, apiVersion, and required properties** against the live schema rather than memory:

- Call the `mcp__azure__bicepschema` tool for the exact resource type (for example `Microsoft.Storage/storageAccounts`) to get current apiVersion and property names.
- For Terraform-adjacent questions, call `mcp__azure__azureterraformbestpractices`.
- For broader service guidance, call `mcp__azure__get_azure_bestpractices` and `mcp__ms-learn__microsoft_docs_search`.

If those tools are unavailable, state plainly that you are reasoning from training knowledge and flag that the user must validate the apiVersion against the current provider schema. **Never invent an apiVersion or a property name.** A template that fails at deploy time on a bad property is a sprint blocker.

## Non-negotiable authoring rules

1. **No secrets in templates or parameter files.** Reference Key Vault with the `getSecret()` function from a `.bicepparam` file or a `Microsoft.KeyVault/vaults` `existing` reference. Never a literal password, key, or connection string. Mark sensitive parameters `@secure()`.
2. **Identity over keys.** Default to system-assigned **managed identity** and RBAC role assignments. Reach for shared keys or SAS only when a service genuinely lacks managed-identity support, and say so.
3. **Parameterize environment, not structure.** Parameters carry what changes per environment (name prefixes, SKUs, region, scale). The resource graph stays declarative and identical across environments.
4. **Idempotent by construction.** Bicep deployments are incremental and re-runnable. Use deterministic names (`uniqueString(resourceGroup().id)` patterns) so re-runs converge rather than duplicate.
5. **Every parameter is decorated.** `@description()` on every parameter and output. `@allowed()`, `@minLength()`, `@maxLength()`, `@minValue()`, `@maxValue()` wherever a constraint exists.
6. **Comments justify design, not syntax.** Explain *why* a SKU, a scope, or a dependency exists. The Bicep already shows *what*.
7. **Modules for reuse, not for everything.** Extract a module when a unit is reused or independently testable. Do not shred a single-purpose template into ceremony.

## Minimal module shape

```bicep
// Storage account hardened for an internal data-landing zone.
// TLS1_2 floor and disabled public blob access are compliance requirements, not defaults.
targetScope = 'resourceGroup'

@description('Short environment moniker used in resource naming, e.g. prod, stg, dev.')
@allowed(['dev', 'stg', 'prod'])
param environment string

@description('Azure region for all resources. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('SKU for the storage account. Standard_ZRS for prod resilience.')
@allowed(['Standard_LRS', 'Standard_ZRS', 'Standard_GRS'])
param storageSku string = 'Standard_ZRS'

// Deterministic, globally-unique, lowercase name within the 24-char limit.
var storageName = toLower('st${environment}${uniqueString(resourceGroup().id)}')

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: storageName
  location: location
  sku: {
    name: storageSku
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    networkAcls: {
      defaultAction: 'Deny'
    }
  }
}

@description('Resource ID of the storage account for downstream role assignments.')
output storageId string = storage.id

@description('Primary blob endpoint for application configuration.')
output blobEndpoint string = storage.properties.primaryEndpoints.blob
```

> The `apiVersion` (`2024-01-01`) above is illustrative. **Confirm the current one via `mcp__azure__bicepschema` before shipping.**

## The deploy loop (always in this order)

```bash
# 1. Compile + lint. Fails fast on bad property names and missing required fields.
az bicep build --file main.bicep

# 2. Preview. Shows create/modify/delete BEFORE anything changes.
az deployment group what-if \
  --resource-group rg-warnerco-prod \
  --template-file main.bicep \
  --parameters main.bicepparam

# 3. Deploy incrementally (the default mode; never use Complete unless you mean it).
az deployment group create \
  --resource-group rg-warnerco-prod \
  --template-file main.bicep \
  --parameters main.bicepparam
```

Full lifecycle, deployment stacks, and the GitHub Actions pipeline are in `references/deploy-runbook.md`.

## Parameter files: use `.bicepparam`, not JSON

```bicep
// main.bicepparam — typed, supports expressions and Key Vault references.
using './main.bicep'

param environment = 'prod'
param storageSku = 'Standard_ZRS'
// Pull a secret at deploy time; the value never lands in source control.
param adminPassword = getSecret('00000000-0000-0000-0000-000000000000', 'rg-secrets', 'kv-warnerco', 'sql-admin-password')
```

## Relationship to the azure-architect agent

This skill is the **authoring and deployment** layer. The `azure-architect` agent owns **service selection and Well-Architected trade-offs**. When a request is "which service and why", that is architecture: defer to the agent's WAF assessment first, then return here to express the chosen design as Bicep. The agent is configured to invoke this skill whenever a decision lands in concrete IaC.
