// WARNERCO Robotics Schematica - Quick Classroom Deployment
// Simplified template without APIM for fast provisioning (~5 mins)

targetScope = 'resourceGroup'

// Parameters
@description('Environment name')
param environment string = 'classroom'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('User-assigned managed identity resource ID')
param userAssignedIdentityId string = ''

@description('Container image to deploy')
param containerImage string = 'REPLACE_WITH_YOUR_ACR.azurecr.io/warnerco-schematica:latest'

@description('Minimum replicas (0 for scale to zero)')
@minValue(0)
@maxValue(10)
param replicaMin int = 0

@description('Maximum replicas')
@minValue(1)
@maxValue(10)
param replicaMax int = 3

// Variables
var appName = 'warnerco-schematica'
var uniqueSuffix = uniqueString(resourceGroup().id)
var containerAppName = '${appName}-${environment}'
var containerEnvName = '${appName}-env-${uniqueSuffix}'
var logAnalyticsName = '${appName}-logs-${uniqueSuffix}'

// Tags
var tags = {
  Application: 'WARNERCO Robotics Schematica'
  Environment: environment
  ManagedBy: 'Bicep'
  Course: 'Context Engineering with MCP'
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

// Container App with optional managed identity
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: userAssignedIdentityId != '' ? {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  } : {
    type: 'None'
  }
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
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
              value: 'chroma'
            }
            {
              name: 'DEBUG'
              value: 'true'
            }
            {
              name: 'HOST'
              value: '0.0.0.0'
            }
            {
              name: 'PORT'
              value: '8000'
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

// Outputs
output containerAppName string = containerApp.name
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output logAnalyticsWorkspaceId string = logAnalytics.id
output environmentId string = containerAppEnvironment.id
