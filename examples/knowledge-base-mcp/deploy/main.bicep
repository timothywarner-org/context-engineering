// Azure Bicep template for Knowledge Base MCP Server
// Deploys to Azure Container Apps with managed identity and logging

@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string = 'dev'

@description('API key for MCP server authentication')
@secure()
param apiKey string

@description('Container image tag')
param imageTag string = 'latest'

@description('Container registry name')
param containerRegistryName string

@description('Enable Application Insights')
param enableAppInsights bool = true

// Variables
var resourceNamePrefix = 'kb-mcp-${environmentName}'
var containerAppName = '${resourceNamePrefix}-app'
var containerAppEnvName = '${resourceNamePrefix}-env'
var logAnalyticsName = '${resourceNamePrefix}-logs'
var appInsightsName = '${resourceNamePrefix}-insights'

// Log Analytics Workspace
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

// Application Insights (optional)
resource appInsights 'Microsoft.Insights/components@2020-02-02' = if (enableAppInsights) {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    Flow_Type: 'Bluefield'
  }
}

// Container Apps Environment
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

// Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: 'system'
        }
      ]
      secrets: [
        {
          name: 'api-key'
          value: apiKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'knowledge-base-mcp'
          image: '${containerRegistryName}.azurecr.io/knowledge-base-mcp:${imageTag}'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'PORT'
              value: '3000'
            }
            {
              name: 'API_KEY'
              secretRef: 'api-key'
            }
            {
              name: 'NODE_ENV'
              value: environmentName == 'prod' ? 'production' : 'development'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: enableAppInsights ? appInsights.properties.ConnectionString : ''
            }
          ]
          probes: [
            {
              type: 'liveness'
              httpGet: {
                path: '/health'
                port: 3000
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'readiness'
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
        minReplicas: environmentName == 'prod' ? 1 : 0
        maxReplicas: environmentName == 'prod' ? 10 : 3
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
}

// Outputs
output containerAppFQDN string = containerApp.properties.configuration.ingress.fqdn
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output resourceGroupName string = resourceGroup().name
output containerAppName string = containerApp.name
