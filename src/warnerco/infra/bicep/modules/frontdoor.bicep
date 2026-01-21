// WARNERCO Robotics Schematica - Front Door with WAF Module
// Optional enterprise security layer

@description('Application name prefix')
param appName string

@description('Environment name')
param environment string

@description('Azure region')
param location string = 'global'

@description('Resource tags')
param tags object

@description('Backend FQDN to route to')
param backendFqdn string

// Variables
var frontDoorName = '${appName}-fd-${environment}'
var wafPolicyName = '${appName}-waf-${environment}'

// WAF Policy
resource wafPolicy 'Microsoft.Network/FrontDoorWebApplicationFirewallPolicies@2022-05-01' = {
  name: wafPolicyName
  location: location
  tags: tags
  sku: {
    name: 'Premium_AzureFrontDoor'
  }
  properties: {
    policySettings: {
      mode: 'Prevention'
      enabledState: 'Enabled'
      requestBodyCheck: 'Enabled'
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'Microsoft_DefaultRuleSet'
          ruleSetVersion: '2.1'
          ruleSetAction: 'Block'
        }
        {
          ruleSetType: 'Microsoft_BotManagerRuleSet'
          ruleSetVersion: '1.0'
          ruleSetAction: 'Block'
        }
      ]
    }
    customRules: {
      rules: [
        {
          name: 'RateLimitRule'
          priority: 100
          enabledState: 'Enabled'
          ruleType: 'RateLimitRule'
          rateLimitDurationInMinutes: 1
          rateLimitThreshold: 100
          matchConditions: [
            {
              matchVariable: 'RemoteAddr'
              operator: 'IPMatch'
              matchValue: ['0.0.0.0/0']
            }
          ]
          action: 'Block'
        }
      ]
    }
  }
}

// Front Door Profile
resource frontDoor 'Microsoft.Cdn/profiles@2023-05-01' = {
  name: frontDoorName
  location: location
  tags: tags
  sku: {
    name: 'Premium_AzureFrontDoor'
  }
  properties: {
    originResponseTimeoutSeconds: 60
  }
}

// Front Door Endpoint
resource frontDoorEndpoint 'Microsoft.Cdn/profiles/afdEndpoints@2023-05-01' = {
  parent: frontDoor
  name: 'schematica-endpoint'
  location: location
  properties: {
    enabledState: 'Enabled'
  }
}

// Origin Group
resource originGroup 'Microsoft.Cdn/profiles/originGroups@2023-05-01' = {
  parent: frontDoor
  name: 'apim-origin-group'
  properties: {
    loadBalancingSettings: {
      sampleSize: 4
      successfulSamplesRequired: 3
      additionalLatencyInMilliseconds: 0
    }
    healthProbeSettings: {
      probePath: '/api/health'
      probeRequestType: 'GET'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 30
    }
    sessionAffinityState: 'Disabled'
  }
}

// Origin
resource origin 'Microsoft.Cdn/profiles/originGroups/origins@2023-05-01' = {
  parent: originGroup
  name: 'apim-origin'
  properties: {
    hostName: replace(backendFqdn, 'https://', '')
    httpPort: 80
    httpsPort: 443
    originHostHeader: replace(backendFqdn, 'https://', '')
    priority: 1
    weight: 1000
    enabledState: 'Enabled'
  }
}

// Route
resource route 'Microsoft.Cdn/profiles/afdEndpoints/routes@2023-05-01' = {
  parent: frontDoorEndpoint
  name: 'default-route'
  properties: {
    originGroup: {
      id: originGroup.id
    }
    supportedProtocols: ['Https']
    patternsToMatch: ['/*']
    forwardingProtocol: 'HttpsOnly'
    linkToDefaultDomain: 'Enabled'
    httpsRedirect: 'Enabled'
  }
  dependsOn: [origin]
}

// Security Policy (links WAF to endpoint)
resource securityPolicy 'Microsoft.Cdn/profiles/securityPolicies@2023-05-01' = {
  parent: frontDoor
  name: 'waf-policy'
  properties: {
    parameters: {
      type: 'WebApplicationFirewall'
      wafPolicy: {
        id: wafPolicy.id
      }
      associations: [
        {
          domains: [
            {
              id: frontDoorEndpoint.id
            }
          ]
          patternsToMatch: ['/*']
        }
      ]
    }
  }
}

// Outputs
output frontDoorEndpoint string = frontDoorEndpoint.properties.hostName
output wafPolicyId string = wafPolicy.id
