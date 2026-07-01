# Bicep Module Patterns

Deeper authoring guidance. Load when designing modules, choosing scopes, or wiring cross-module references.

## Target scopes

A Bicep file declares the scope it deploys into. Pick the narrowest scope the work needs.

| `targetScope` | Deploys to | Use for |
|---------------|-----------|---------|
| `resourceGroup` (default) | One resource group | Most workloads: app + data + identity in one RG |
| `subscription` | A subscription | Creating resource groups, subscription-level policy, budgets |
| `managementGroup` | A management group | Governance, policy assignment across many subscriptions |
| `tenant` | The whole tenant | Rare: tenant-wide role definitions, management group creation |

A subscription-scope file creates resource groups, then deploys modules **into** them:

```bicep
targetScope = 'subscription'

@description('Region for the resource group and all child resources.')
param location string

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-warnerco-prod'
  location: location
}

// Deploy a module scoped INTO the newly created group.
module app 'modules/app.bicep' = {
  name: 'app-deploy'
  scope: rg
  params: {
    location: location
  }
}
```

## Module composition

Treat a module as a function: typed inputs (`param`), a body, typed returns (`output`). A parent passes params down and consumes outputs.

```bicep
// Parent wires identity -> storage -> role assignment.
module identity 'modules/identity.bicep' = {
  name: 'identity'
  params: { environment: environment }
}

module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: { environment: environment, location: location }
}

// Grant the workload identity Blob Data Contributor on the storage account.
// Consuming both modules' outputs is how you express a dependency without dependsOn.
module rbac 'modules/role-assignment.bicep' = {
  name: 'rbac'
  params: {
    principalId: identity.outputs.principalId
    storageAccountId: storage.outputs.storageId
  }
}
```

**Prefer implicit dependencies.** Referencing `storage.outputs.storageId` makes Bicep order the deployment correctly on its own. Reach for explicit `dependsOn` only when there is no data flow to express the ordering, which is rare and usually a smell.

## Existing resources

Reference something you did not create in this deployment with `existing`. No properties, no redeploy, just a typed handle.

```bicep
// Read an existing Key Vault to wire a secret reference. We are not managing this vault here.
resource kv 'Microsoft.KeyVault/vaults@2024-11-01' existing = {
  name: 'kv-warnerco-shared'
  scope: resourceGroup('rg-shared-secrets')
}
```

## Loops and conditions

```bicep
@description('Names of the data containers to provision.')
param containerNames array = ['raw', 'curated', 'published']

// One blob container per name. The index is available as a second loop variable if needed.
resource containers 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = [
  for name in containerNames: {
    name: '${storage.name}/default/${name}'
  }
]

// Conditional resource: only stand up a private endpoint in prod.
resource pe 'Microsoft.Network/privateEndpoints@2024-05-01' = if (environment == 'prod') {
  name: 'pe-storage'
  location: location
  properties: { /* ... */ }
}
```

## Naming

- Deterministic and idempotent: `uniqueString(resourceGroup().id)` gives a stable 13-char hash that survives re-runs.
- Respect per-service constraints: storage accounts are 3-24 chars, lowercase, no hyphens. Key Vault is 3-24. Wrap in `toLower()` and a `take()` when a hash could overflow the limit.
- Carry the environment moniker so resources are self-describing: `st`, `kv`, `app`, `func` prefixes by convention.

## User-defined types

Replace loose `object` and `array` params with named types so the editor and the compiler catch shape errors early.

```bicep
@description('Network configuration for the workload.')
type networkConfig = {
  vnetName: string
  addressSpace: string
  subnetPrefix: string
}

param network networkConfig
```

## Decorators worth knowing

| Decorator | Purpose |
|-----------|---------|
| `@description('...')` | Mandatory on every param and output |
| `@secure()` | Marks a string/object param sensitive; value is omitted from logs and history |
| `@allowed([...])` | Constrains to an enum; fails validation outside the set |
| `@minLength()` / `@maxLength()` | String/array length bounds |
| `@minValue()` / `@maxValue()` | Numeric bounds |
| `@metadata({...})` | Arbitrary structured annotation for tooling |
