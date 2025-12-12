// ============================================================
// CoreText MCP - Azure Infrastructure (MVP Edition)
// ============================================================
// Cost-optimized deployment using:
// - Cosmos DB Free Tier (1000 RU/s, 25GB storage)
// - Azure Container Apps Consumption Plan (pay-per-use)
// - Key Vault for secrets (minimal cost)
// - Managed Identity (no cost)
// ============================================================

targetScope = 'resourceGroup'

// ============================================================
// Parameters
// ============================================================

@description('Location for all resources')
param location string = 'eastus'

@description('Unique suffix for resource names (auto-generated if not provided)')
param uniqueSuffix string = uniqueString(resourceGroup().id)

@description('Container image to deploy (use Azure Container Registry or Docker Hub)')
param containerImage string = 'coretext-mcp:latest'

@description('DeepSeek API Key for AI enrichment')
@secure()
param deepseekApiKey string

@description('Managed Identity Name')
param managedIdentityName string = 'context-msi'

// ============================================================
// Variables
// ============================================================

var cosmosAccountName = 'coretext-cosmos-${uniqueSuffix}'
var containerAppName = 'coretext-app-${uniqueSuffix}'
var containerAppEnvName = 'coretext-env-${uniqueSuffix}'
var keyVaultName = 'coretext-kv-${uniqueSuffix}'
var logAnalyticsName = 'coretext-logs-${uniqueSuffix}'

// ============================================================
// Existing Managed Identity (provided by user)
// ============================================================

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

// ============================================================
// Log Analytics Workspace (required for Container Apps)
// ============================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================
// Cosmos DB Account (FREE TIER - 1000 RU/s, 25GB)
// ============================================================

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    enableFreeTier: true  // FREE TIER - Only one per subscription
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    // Note: Free tier uses provisioned throughput, not serverless
    // Serverless and Free Tier are mutually exclusive
  }
}

// ============================================================
// Cosmos DB Database
// ============================================================

resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: cosmosAccount
  name: 'coretext'
  properties: {
    resource: {
      id: 'coretext'
    }
    options: {
      throughput: 400  // Minimum for shared throughput (free tier provides 1000 RU/s total)
    }
  }
}

// ============================================================
// Cosmos DB Container (Memories Collection)
// ============================================================

resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDatabase
  name: 'memories'
  properties: {
    resource: {
      id: 'memories'
      partitionKey: {
        paths: [
          '/id'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        includedPaths: [
          {
            path: '/*'
          }
        ]
      }
    }
  }
}

// ============================================================
// Key Vault (for secure secret storage)
// ============================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true  // Use RBAC instead of access policies
    enabledForDeployment: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7  // Minimum for cost savings
  }
}

// ============================================================
// Key Vault Secret - DeepSeek API Key
// ============================================================

resource deepseekSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'deepseek-api-key'
  properties: {
    value: deepseekApiKey
  }
}

// ============================================================
// Key Vault Secret - Cosmos DB Connection String
// ============================================================

resource cosmosConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'cosmos-connection-string'
  properties: {
    value: cosmosAccount.listConnectionStrings().connectionStrings[0].connectionString
  }
}

// ============================================================
// RBAC: Grant Managed Identity access to Key Vault Secrets
// ============================================================

// Key Vault Secrets User role definition ID
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'

resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  name: guid(keyVault.id, managedIdentity.id, keyVaultSecretsUserRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ============================================================
// Container Apps Environment
// ============================================================

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppEnvName
  location: location
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

// ============================================================
// Container App (MCP Server)
// ============================================================

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'deepseek-api-key'
          keyVaultUrl: deepseekSecret.properties.secretUri
          identity: managedIdentity.id
        }
        {
          name: 'cosmos-connection-string'
          keyVaultUrl: cosmosConnectionSecret.properties.secretUri
          identity: managedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'coretext-mcp'
          image: containerImage
          resources: {
            cpu: json('0.25')  // Minimum CPU (cost-effective)
            memory: '0.5Gi'    // Minimum memory
          }
          env: [
            {
              name: 'DEEPSEEK_API_KEY'
              secretRef: 'deepseek-api-key'
            }
            {
              name: 'COSMOS_CONNECTION_STRING'
              secretRef: 'cosmos-connection-string'
            }
            {
              name: 'NODE_ENV'
              value: 'production'
            }
            {
              name: 'PORT'
              value: '3000'
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 3000
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 3000
              }
              initialDelaySeconds: 5
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0  // Scale to zero when not in use (COST SAVINGS!)
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
  dependsOn: [
    keyVaultRoleAssignment
  ]
}

// ============================================================
// Outputs
// ============================================================

output cosmosAccountName string = cosmosAccount.name
output cosmosConnectionString string = cosmosAccount.listConnectionStrings().connectionStrings[0].connectionString
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output keyVaultName string = keyVault.name
output managedIdentityClientId string = managedIdentity.properties.clientId
output resourceGroupName string = resourceGroup().name

// ============================================================
// Cost Breakdown (Estimated Monthly)
// ============================================================
// Cosmos DB Free Tier:     $0.00 (1000 RU/s, 25GB included)
// Container Apps:          ~$1-5 (consumption, scales to zero)
// Key Vault:              ~$0.03 (per 10k operations)
// Log Analytics:          ~$2-5 (30 days retention)
// Managed Identity:        $0.00
// ------------------------------------------------------------
// TOTAL ESTIMATED:        ~$3-10/month for MVP workload
// ============================================================
