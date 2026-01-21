// WARNERCO Robotics Schematica - Azure Infrastructure
// Main Bicep template for classroom deployment

targetScope = 'resourceGroup'

// Parameters
@description('Environment name (classroom, dev, prod)')
@allowed(['classroom', 'dev', 'prod'])
param environment string = 'classroom'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Enable Azure Front Door with WAF')
param enableWaf bool = false

@description('Enable Azure AI Search')
param enableAiSearch bool = false

@description('Container image to deploy')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Minimum number of replicas')
@minValue(0)
@maxValue(10)
param replicaMin int = 0

@description('Maximum number of replicas')
@minValue(1)
@maxValue(30)
param replicaMax int = 3

// Variables
var appName = 'warnerco-schematica'
var uniqueSuffix = uniqueString(resourceGroup().id)
var containerAppName = '${appName}-${environment}'
var containerEnvName = '${appName}-env-${environment}'
var logAnalyticsName = '${appName}-logs-${uniqueSuffix}'
var apimName = '${appName}-apim-${uniqueSuffix}'

// Tags for resource management
var tags = {
  Application: 'WARNERCO Robotics Schematica'
  Environment: environment
  ManagedBy: 'Bicep'
}

// Log Analytics Workspace
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

// Container Apps Environment
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

// Container App
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
      secrets: []
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
            {
              name: 'MEMORY_BACKEND'
              value: enableAiSearch ? 'azure_search' : 'chroma'
            }
            {
              name: 'DEBUG'
              value: environment == 'classroom' ? 'true' : 'false'
            }
          ]
        }
      ]
      scale: {
        minReplicas: replicaMin
        maxReplicas: replicaMax
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

// API Management (Consumption tier for cost efficiency)
resource apim 'Microsoft.ApiManagement/service@2023-05-01-preview' = {
  name: apimName
  location: location
  tags: tags
  sku: {
    name: 'Consumption'
    capacity: 0
  }
  properties: {
    publisherEmail: 'admin@warnerco.io'
    publisherName: 'WARNERCO Robotics'
  }
}

// APIM API definition
resource apimApi 'Microsoft.ApiManagement/service/apis@2023-05-01-preview' = {
  parent: apim
  name: 'schematica-api'
  properties: {
    displayName: 'WARNERCO Schematica API'
    description: 'Robot schematics API with semantic search'
    path: ''
    protocols: ['https']
    serviceUrl: 'https://${containerApp.properties.configuration.ingress.fqdn}'
    subscriptionRequired: false
  }
}

// API Operations
resource apiOperationRobots 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'get-robots'
  properties: {
    displayName: 'List Robots'
    method: 'GET'
    urlTemplate: '/api/robots'
    description: 'List all robot schematics'
  }
}

resource apiOperationSearch 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'semantic-search'
  properties: {
    displayName: 'Semantic Search'
    method: 'POST'
    urlTemplate: '/api/search'
    description: 'Perform semantic search on schematics'
  }
}

resource apiOperationDash 'Microsoft.ApiManagement/service/apis/operations@2023-05-01-preview' = {
  parent: apimApi
  name: 'dashboard'
  properties: {
    displayName: 'Dashboard'
    method: 'GET'
    urlTemplate: '/dash/*'
    description: 'Serve dashboard static files'
  }
}

// Azure AI Search (optional)
resource aiSearch 'Microsoft.Search/searchServices@2023-11-01' = if (enableAiSearch) {
  name: '${appName}-search-${uniqueSuffix}'
  location: location
  tags: tags
  sku: {
    name: 'free' // Use free tier for classroom
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
  }
}

// Front Door with WAF (optional)
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

// Outputs
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output apimGatewayUrl string = apim.properties.gatewayUrl
output apimPortalUrl string = apim.properties.developerPortalUrl
output aiSearchEndpoint string = enableAiSearch ? aiSearch.properties.hostName : ''
output frontDoorEndpoint string = enableWaf ? frontDoor.outputs.frontDoorEndpoint : ''
