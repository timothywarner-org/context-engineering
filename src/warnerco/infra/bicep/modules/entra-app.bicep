// WARNERCO Schematica - Entra ID App Registration module
// Uses the microsoftGraphV1 extension - requires bicepconfig.json enablement (see below).
//
// PREVIEW CAVEAT:
//   The 'microsoftGraphV1' Bicep extension is in public preview as of mid-2025.
//   Enable it in bicepconfig.json:
//     { "experimentalFeaturesEnabled": { "extensibility": true } }
//   The extension ships with the Bicep CLI >= 0.28. Older pipeline agents need a
//   CLI upgrade before this module deploys.
//
// DEPLOYING PRINCIPAL PERMISSIONS REQUIRED:
//   The identity running 'az deployment group create' (or the azd pipeline SP)
//   must hold one of:
//     - Application Administrator (Entra role)
//     - Cloud Application Administrator (Entra role)
//   ...on the tenant where the app registration is created.
//   It also needs 'AppRoleAssignment.ReadWrite.All' Graph permission to write
//   the appRoleAssignedTo record.
//
// GRAPH USER LOOKUP DECISION:
//   Microsoft.Graph/users@v1.0 'existing' reads are supported in the extension
//   but only when the deploying identity has User.Read.All. To keep the
//   permission surface minimal this module accepts the user's Entra objectId
//   directly via the timUserObjectId parameter instead of resolving by UPN at
//   deploy time. Pass it from: az ad user show --id tim@techtrainertim.com --query id -o tsv

extension microsoftGraphV1

@description('Unique name token for the Entra app (used as uniqueName and in displayName)')
param appUniqueName string = 'warnerco-schematica'

@description('Display name for the Entra app registration')
param appDisplayName string = 'WARNERCO Schematica'

@description('Tenant ID where the app is registered')
param tenantId string = tenant().tenantId

@description('Object ID of the Entra user to assign the Schematica.Access app role. Resolve before deploy: az ad user show --id tim@techtrainertim.com --query id -o tsv')
param timUserObjectId string

// Stable GUIDs for oauth2PermissionScopes and appRoles.
// These are hard-coded so re-deployments are idempotent (Graph rejects
// duplicate id values; stable ids prevent churn on each run).
var userImpersonationScopeId = 'a3b4c5d6-e7f8-9012-abcd-ef1234567890'
var schematicaAccessRoleId   = 'b2c3d4e5-f6a7-8901-bcde-f01234567891'

resource entraApp 'Microsoft.Graph/applications@v1.0' = {
  // uniqueName is the stable idempotency key across deployments
  uniqueName: appUniqueName
  displayName: appDisplayName

  // Application ID URI. The tenant's default app policy rejects a bare
  // api://<name> unless it contains a verified domain, tenant ID, or app ID
  // (error InvalidUniqueTenantIdentifierAsPerAppPolicy) - UNLESS the app issues
  // v2 access tokens (requestedAccessTokenVersion: 2 below), which lifts the
  // restriction. The tenant-ID form is used to satisfy the policy either way.
  // This is what makes the app a valid token resource; without it Entra returns
  // AADSTS650057 "List of valid resources from app registration: <empty>".
  identifierUris: [
    'api://${tenantId}/${appUniqueName}'
  ]

  // Expose an API scope so downstream clients can request delegated tokens
  api: {
    // v2 access tokens: required so the api:// identifier URI above is accepted
    // under the tenant app policy, and so the token aud/claims are v2-shaped.
    requestedAccessTokenVersion: 2
    oauth2PermissionScopes: [
      {
        id: userImpersonationScopeId
        adminConsentDescription: 'Allow the application to access WARNERCO Schematica on behalf of the signed-in user'
        adminConsentDisplayName: 'Access WARNERCO Schematica'
        isEnabled: true
        type: 'User'
        userConsentDescription: 'Allow this app to access WARNERCO Schematica on your behalf'
        userConsentDisplayName: 'Access WARNERCO Schematica'
        value: 'user_impersonation'
      }
    ]
    // Pre-authorize the Azure CLI (and VS) so `az account get-access-token`
    // and `az login --scope <appId>/.default` can request user_impersonation
    // without a separate consent grant. Well-known first-party client IDs:
    //   04b07795-8ddb-461a-bbee-02f9e1bf7b46  Microsoft Azure CLI
    //   872cd9fa-d31f-45e0-9eab-6e460a02d1f1  Visual Studio
    preAuthorizedApplications: [
      {
        appId: '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
        delegatedPermissionIds: [userImpersonationScopeId]
      }
      {
        appId: '872cd9fa-d31f-45e0-9eab-6e460a02d1f1'
        delegatedPermissionIds: [userImpersonationScopeId]
      }
    ]
  }

  // App role used for daemon / service-principal access and for the
  // validate-jwt required-claims check in APIM
  appRoles: [
    {
      id: schematicaAccessRoleId
      allowedMemberTypes: ['User']
      description: 'Full access to WARNERCO Schematica API and MCP endpoints'
      displayName: 'Schematica.Access'
      isEnabled: true
      value: 'Schematica.Access'
    }
  ]

  // Microsoft Graph - User.Read for the signed-in user (standard consent)
  requiredResourceAccess: [
    {
      resourceAppId: '00000003-0000-0000-c000-000000000000' // Microsoft Graph
      resourceAccess: [
        {
          id: 'e1fe6dd8-ba31-4d61-89e7-88639da4683d' // User.Read (delegated)
          type: 'Scope'
        }
      ]
    }
  ]

}

// The app registration alone has no service principal (enterprise app) in the
// tenant, and appRoleAssignedTo writes to the SP's collection - not the app's.
// The first deploy failed with Request_ResourceNotFound because resourceId
// pointed at the application object id and no SP existed yet. Fix: explicitly
// create the SP from the app's appId, then reference the SP object id.
resource entraSp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: entraApp.appId
}

// Assign Schematica.Access app role to Tim's user account.
// resourceId MUST be the service principal object id (entraSp.id), and appRoleId
// is the role defined on the app. Graph deduplicates on
// (principalId, resourceId, appRoleId), so re-deploys are idempotent.
resource roleAssignment 'Microsoft.Graph/appRoleAssignedTo@v1.0' = {
  principalId: timUserObjectId    // the user being granted the role
  resourceId: entraSp.id          // the SP backing this app
  appRoleId: schematicaAccessRoleId
}

// Outputs consumed by main.bicep for APIM named values and policy interpolation
@description('Client (application) ID of the registered Entra app')
output entraAppId string = entraApp.appId

@description('Tenant ID where the app is registered')
output entraAppTenantId string = tenantId
