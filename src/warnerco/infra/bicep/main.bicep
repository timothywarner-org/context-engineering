// WARNERCO Robotics Schematica - Azure Infrastructure
// Main Bicep template for classroom deployment
//
// apiVersions (all confirmed via bicepschema tool on 2026-06-30):
//   Microsoft.OperationalInsights/workspaces       2022-10-01
//   Microsoft.ContainerRegistry/registries         2025-04-01
//   Microsoft.ManagedIdentity/userAssignedIdentities 2024-11-30
//   Microsoft.Authorization/roleAssignments         2022-04-01
//   Microsoft.Storage/storageAccounts              2025-01-01
//   Microsoft.Storage/storageAccounts/fileServices/shares  2025-01-01
//   Microsoft.App/managedEnvironments              2024-03-01  (unchanged)
//   Microsoft.App/managedEnvironments/storages     2025-01-01
//   Microsoft.App/containerApps                    2025-01-01
//   Microsoft.ApiManagement/service                2024-05-01  (promoted from preview)
//   Microsoft.ApiManagement/service/apis           2024-05-01
//   Microsoft.ApiManagement/service/apis/policies  2024-05-01
//   Microsoft.ApiManagement/service/namedValues    2024-05-01
//   Microsoft.Search/searchServices                2023-11-01  (unchanged)
//
// IDENTITY DESIGN:
//   One UAMI (acrPullIdentity) handles ACR pull from the Container App.
//   A second UAMI (apimFicIdentity) is attached to APIM as the FIC subject for
//   the Entra app registration. Keeping them separate follows least-privilege:
//   ACR pull RBAC is scoped only to the registry; the APIM FIC identity has no
//   ARM role assignments.
//
// SINGLE-REPLICA CONSTRAINT:
//   replicaMin and replicaMax are overridden to 1 when an Azure Files volume is
//   mounted. SQLite does not tolerate concurrent writers across separate replica
//   processes accessing the same NFS/SMB share. If you switch MEMORY_BACKEND to
//   azure_search only (no local SQLite), remove the override and restore the
//   incoming params.

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------

@description('Environment name (classroom, dev, prod)')
@allowed(['classroom', 'dev', 'prod'])
param environment string = 'classroom'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Enable Azure Front Door with WAF')
param enableWaf bool = false

@description('Enable Azure AI Search')
param enableAiSearch bool = false

@description('Container image to deploy (must be in the ACR created by this template)')
param containerImage string = 'REPLACE_WITH_YOUR_ACR.azurecr.io/warnerco-schematica:latest'

@description('Anthropic API key injected as an ACA secret')
@secure()
param anthropicApiKey string

@description('Azure AI Search admin key - only required when enableAiSearch=true')
@secure()
param azureSearchKey string = ''

@description('Azure AI Search endpoint URL')
param azureSearchEndpoint string = ''

@description('Claude model identifier for the reason node')
param claudeModel string = 'claude-sonnet-4-6'

@description('Object ID of the Entra user to receive the Schematica.Access app role (tim@techtrainertim.com)')
param timUserObjectId string

@description('Name of the Entra app unique identifier (must be globally unique within the tenant)')
param entraAppUniqueName string = 'warnerco-schematica'

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------

var appName        = 'warnerco-schematica'
var uniqueSuffix   = uniqueString(resourceGroup().id)
// ACR name: alphanumeric only, 5-50 chars
var acrName        = 'warnerco${uniqueSuffix}'
var containerAppName   = '${appName}-${environment}'
var containerEnvName   = '${appName}-env-${environment}'
var logAnalyticsName   = '${appName}-logs-${uniqueSuffix}'
var apimName           = '${appName}-apim-${uniqueSuffix}'
// Storage account name: lowercase alphanumeric, 3-24 chars
var storageName        = 'warnercosa${uniqueSuffix}'
var fileShareName      = 'schematica-data'
var envStorageName     = 'schematica-azfile'

// AcrPull built-in role definition ID (stable across all tenants)
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

var tags = {
  Application: 'WARNERCO Robotics Schematica'
  Environment: environment
  ManagedBy: 'Bicep'
}

// ---------------------------------------------------------------------------
// Log Analytics Workspace
// ---------------------------------------------------------------------------

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ---------------------------------------------------------------------------
// Azure Container Registry  (Basic SKU, admin disabled, UAMI pull)
// ---------------------------------------------------------------------------

resource acr 'Microsoft.ContainerRegistry/registries@2025-04-01' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false          // secretless: pull via managed identity only
    publicNetworkAccess: 'Enabled'   // adequate for classroom; tighten with PE for prod
  }
}

// ---------------------------------------------------------------------------
// User-Assigned Managed Identity - ACR pull
// Used by the Container App to authenticate against ACR without credentials.
// ---------------------------------------------------------------------------

resource acrPullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: '${appName}-acr-pull-${environment}'
  location: location
  tags: tags
}

// AcrPull role assignment scoped to the registry only (least privilege)
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  // Scope to ACR so this identity cannot pull from other registries
  scope: acr
  // Deterministic GUID prevents duplicate assignments on re-deploy
  name: guid(acr.id, acrPullIdentity.id, acrPullRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId: acrPullIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ---------------------------------------------------------------------------
// Storage Account + File Share  (for SQLite persistence via Azure Files)
// Standard_LRS is sufficient; classroom doesn't need geo-redundancy.
// ---------------------------------------------------------------------------

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-01-01' = {
  name: storageName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowSharedKeyAccess: true   // required: ACA Azure Files volume mount uses account key
    publicNetworkAccess: 'Enabled'
  }
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2025-01-01' = {
  // parent path: storageAccount -> fileServices (implicit singleton) -> shares
  name: '${storageAccount.name}/default/${fileShareName}'
  properties: {
    shareQuota: 5    // 5 GiB is more than enough for SQLite classroom data
    enabledProtocols: 'SMB'
  }
}

// ---------------------------------------------------------------------------
// Container Apps Environment
// ---------------------------------------------------------------------------

resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerEnvName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Wire the Azure Files share into the ACA environment so the Container App
// can reference it by the envStorageName alias in its volume definition.
resource acaStorage 'Microsoft.App/managedEnvironments/storages@2025-01-01' = {
  parent: containerAppEnvironment
  name: envStorageName
  properties: {
    azureFile: {
      accountName: storageAccount.name
      accountKey: storageAccount.listKeys().keys[0].value
      shareName: fileShareName
      accessMode: 'ReadWrite'
    }
  }
}

// ---------------------------------------------------------------------------
// Container App
// replicaMin/Max forced to 1 - SQLite cannot handle concurrent writers
// on a shared Azure Files mount.
// ---------------------------------------------------------------------------

resource containerApp 'Microsoft.App/containerApps@2025-01-01' = {
  name: containerAppName
  location: location
  tags: tags

  // Attach the ACR-pull UAMI so the runtime can authenticate to ACR
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${acrPullIdentity.id}': {}
    }
  }

  properties: {
    environmentId: containerAppEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          // Tightened at deploy time: only allow traffic from APIM gateway
          allowedOrigins: [apim.properties.gatewayUrl]
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }

      // Pull image from ACR using the UAMI (no password stored)
      registries: [
        {
          server: acr.properties.loginServer
          identity: acrPullIdentity.id
        }
      ]

      // ACA secrets - values are @secure() params, never appear in plan output
      secrets: [
        {
          name: 'anthropic-api-key'
          value: anthropicApiKey
        }
        {
          // Sourced directly from the AI Search resource created in this same
          // deployment - removes the chicken/egg of needing the key in Key Vault
          // before Search exists. Empty string when AI Search is disabled.
          name: 'azure-search-key'
          value: enableAiSearch ? aiSearch.listAdminKeys().primaryKey : ''
        }
        {
          name: 'storage-account-key'
          value: storageAccount.listKeys().keys[0].value
        }
      ]
    }

    template: {
      containers: [
        {
          name: 'schematica'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            // Memory backend - force azure_search when enabled, else chroma
            {
              name: 'MEMORY_BACKEND'
              value: enableAiSearch ? 'azure_search' : 'chroma'
            }
            // Replace debug flag with APP_DEBUG as per spec requirement
            {
              name: 'APP_DEBUG'
              value: 'false'
            }
            // Anthropic key via secretRef - never in plaintext env
            {
              name: 'ANTHROPIC_API_KEY'
              secretRef: 'anthropic-api-key'
            }
            {
              name: 'CLAUDE_MODEL'
              value: claudeModel
            }
            // CORS_ORIGINS set to APIM gateway so the app also enforces it server-side
            {
              name: 'CORS_ORIGINS'
              value: apim.properties.gatewayUrl
            }
            // Azure Search config (only meaningful when enableAiSearch=true)
            {
              // Endpoint of the AI Search service created in this deployment.
              name: 'AZURE_SEARCH_ENDPOINT'
              value: enableAiSearch ? 'https://${aiSearch.name}.search.windows.net' : azureSearchEndpoint
            }
            {
              name: 'AZURE_SEARCH_INDEX'
              value: 'warnerco-schematics'
            }
            {
              name: 'AZURE_SEARCH_KEY'
              secretRef: 'azure-search-key'
            }
            // SQLite data paths inside the mounted volume
            {
              name: 'SCRATCHPAD_DB_PATH'
              value: '/app/data/scratchpad/notes.db'
            }
            {
              name: 'EPISODIC_DB_PATH'
              value: '/app/data/episodic/events.db'
            }
          ]
          volumeMounts: [
            {
              volumeName: 'sqlite-data'
              mountPath: '/app/data'
            }
          ]
        }
      ]

      volumes: [
        {
          name: 'sqlite-data'
          storageType: 'AzureFile'
          // storageName references the ACA environment storage alias
          storageName: envStorageName
        }
      ]

      scale: {
        // Locked to 1 replica while SQLite is on a shared file volume.
        // Remove this constraint if migrating fully to azure_search + Chroma cloud.
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }

  // acaStorage must exist before the Container App references the volume
  dependsOn: [acaStorage]
}

// ---------------------------------------------------------------------------
// API Management  (BasicV2)
// Promoted from Consumption to BasicV2: Consumption cannot host the validate-jwt
// gateway with a stable IP/SLA the way a classroom demo wants. The auth model is
// "APIM validates an Entra-issued JWT" (Option B) - APIM never MINTS tokens, so
// it needs NO managed identity and NO federated credential. (The heavier OAuth
// facade that DOES need a FIC lives in remote-mcp-apim-functions-python/ as the
// advanced lesson.) SystemAssigned identity is kept only as a no-cost hook for a
// future App Insights logger or Key Vault reference; nothing depends on it today.
//
// NOTE: BasicV2 provisions in ~15-20 min on first deploy vs ~2 min for
// Consumption. Trade-off accepted for the stable SLA-backed gateway.
// ---------------------------------------------------------------------------

resource apim 'Microsoft.ApiManagement/service@2024-05-01' = {
  name: apimName
  location: location
  tags: tags
  sku: {
    name: 'BasicV2'
    capacity: 1
  }
  properties: {
    publisherEmail: 'admin@warnerco.io'
    publisherName: 'WARNERCO Robotics'
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// ---------------------------------------------------------------------------
// APIM API definition
// Two wildcard operations replace the original three specific ones.
// This covers any path under /api/* and /mcp/* with a single policy.
// ---------------------------------------------------------------------------

resource apimApi 'Microsoft.ApiManagement/service/apis@2024-05-01' = {
  parent: apim
  name: 'schematica-api'
  properties: {
    displayName: 'WARNERCO Schematica API'
    description: 'Robot schematics API and MCP endpoints - secured by Entra ID'
    path: ''
    protocols: ['https']
    serviceUrl: 'https://${containerApp.properties.configuration.ingress.fqdn}'
    subscriptionRequired: false
  }
}

// Wildcard operation covering all /api/* routes (GET and POST)
resource apiOperationApiAll 'Microsoft.ApiManagement/service/apis/operations@2024-05-01' = {
  parent: apimApi
  name: 'api-all'
  properties: {
    displayName: 'API Wildcard'
    method: 'GET'
    urlTemplate: '/api/*'
    description: 'All GET requests under /api/'
  }
}

resource apiOperationApiPost 'Microsoft.ApiManagement/service/apis/operations@2024-05-01' = {
  parent: apimApi
  name: 'api-all-post'
  properties: {
    displayName: 'API Wildcard POST'
    method: 'POST'
    urlTemplate: '/api/*'
    description: 'All POST requests under /api/'
  }
}

// Wildcard operation covering all /mcp/* routes (POST - MCP JSON-RPC)
resource apiOperationMcpAll 'Microsoft.ApiManagement/service/apis/operations@2024-05-01' = {
  parent: apimApi
  name: 'mcp-all'
  properties: {
    displayName: 'MCP Wildcard'
    method: 'POST'
    urlTemplate: '/mcp/*'
    description: 'All MCP JSON-RPC POST requests'
  }
}

// ---------------------------------------------------------------------------
// APIM API Policy - validate-jwt applied at API scope
//
// Token substitution: Bicep replaces {tenantId} and {appId} placeholders in
// the policy XML using string interpolation (replace()). This is simpler than
// named values for a single-template deployment: no extra namedValue resources
// needed, no {{}} syntax in the XML, and no APIM-side lookup round-trip.
// Trade-off: the policy blob is re-deployed on every run (idempotent, low cost).
//
// The XML template file uses literal {tenantId} and {appId} as placeholder
// tokens; Bicep replace() substitutes the actual values at deploy time.
// ---------------------------------------------------------------------------

resource apimApiPolicy 'Microsoft.ApiManagement/service/apis/policies@2024-05-01' = {
  parent: apimApi
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: replace(
      replace(
        loadTextContent('../apim/validate-jwt.policy.xml'),
        '{tenantId}',
        tenant().tenantId
      ),
      '{appId}',
      entraApp.outputs.entraAppId
    )
  }
}

// ---------------------------------------------------------------------------
// Entra App Registration module
// Must deploy after APIM so the UAMI principalId is available.
// ---------------------------------------------------------------------------

module entraApp 'modules/entra-app.bicep' = {
  name: 'entra-app-deployment'
  params: {
    appUniqueName: entraAppUniqueName
    appDisplayName: 'WARNERCO Schematica'
    tenantId: tenant().tenantId
    timUserObjectId: timUserObjectId
  }
}

// ---------------------------------------------------------------------------
// Azure AI Search (optional - free tier for classroom)
// ---------------------------------------------------------------------------

resource aiSearch 'Microsoft.Search/searchServices@2023-11-01' = if (enableAiSearch) {
  name: '${appName}-search-${uniqueSuffix}'
  location: location
  tags: tags
  sku: {
    name: 'free'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
  }
}

// ---------------------------------------------------------------------------
// Front Door with WAF (optional module - unchanged)
// ---------------------------------------------------------------------------

module frontDoor 'modules/frontdoor.bicep' = if (enableWaf) {
  name: 'frontdoor-deployment'
  params: {
    appName: appName
    environment: environment
    location: location
    tags: tags
    backendFqdn: apim.properties.gatewayUrl
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('FQDN of the Container App (direct, behind APIM)')
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn

@description('HTTPS URL of the Container App')
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'

@description('APIM gateway URL - the public entry point for all API traffic')
output apimGatewayUrl string = apim.properties.gatewayUrl

@description('APIM developer portal URL (empty on BasicV2; portal is Developer/Premium-tier only)')
output apimPortalUrl string = apim.properties.?developerPortalUrl ?? ''

@description('Azure AI Search endpoint (empty when enableAiSearch=false). The Search resource has no hostName property; the endpoint is derived from the service name.')
output aiSearchEndpoint string = enableAiSearch ? 'https://${aiSearch.name}.search.windows.net' : ''

@description('Front Door endpoint (empty when enableWaf=false)')
output frontDoorEndpoint string = enableWaf ? frontDoor.outputs.frontDoorEndpoint : ''

@description('ACR login server (e.g. warnercoxyz.azurecr.io)')
output acrLoginServer string = acr.properties.loginServer

@description('Entra app (client) ID for the Schematica registration')
output entraAppId string = entraApp.outputs.entraAppId

@description('Tenant ID where the Entra app is registered')
output tenantId string = tenant().tenantId
