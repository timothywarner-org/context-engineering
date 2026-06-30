# Remote MCP with OAuth on Azure: APIM as AI Gateway in front of Entra ID

**Audience:** course attendees, ~12-15 minute classroom explainer.
**Deployed asset:** an OAuth-secured remote MCP server at `remote-mcp-apim-functions-python/`.
**Upstream credit:** adapted from the official Microsoft sample **[Azure-Samples/remote-mcp-apim-functions-python](https://github.com/Azure-Samples/remote-mcp-apim-functions-python)** ("Secure Remote MCP Servers using Azure API Management"), MIT licensed. The hands-on connect steps are at [`remote-mcp-apim-functions-python/QUICKSTART.md`](../../remote-mcp-apim-functions-python/QUICKSTART.md).

## What you will learn

This is the **AAA** lesson, mapped to real Azure services:

| AAA pillar | Concern | Service that owns it |
|------------|---------|----------------------|
| **Authentication** | Who is the user? | **Entra ID** (the user signs in, PKCE binds the request) |
| **Authorization** | What may they reach, and on what credential? | **Azure API Management (APIM)** brokers the token exchange and gates `/mcp/sse` |
| **Accounting** | What happened, and can we prove it? | **App Insights + Log Analytics** capture every gateway transaction |

The structural lesson under the acronym: **APIM is the security perimeter**, not the MCP server. The Azure Functions backend never faces the public internet on its own credential. APIM stands in front as an **AI Gateway** that runs the entire OAuth dance, then injects the backend key on each call.

## The architecture in one diagram

APIM plays **two roles at once**:

1. The **OAuth Authorization Server facade** the MCP client talks to. It serves `/.well-known/oauth-authorization-server` (RFC 8414 metadata), `/authorize`, `/token`, and `/register` (RFC 7591 dynamic client registration).
2. A **secretless confidential client to Entra ID**. It authenticates to Entra with a **Federated Identity Credential (FIC)** off its user-assigned managed identity. No client secret is stored anywhere.

```mermaid
sequenceDiagram
    participant C as MCP client (Inspector / Claude)
    participant A as APIM OAuth API (RFC 8414/7591 facade)
    participant E as Entra ID
    participant X as Cosmos DB (registrations)
    participant M as APIM MCP API (/mcp/sse)
    participant F as Azure Functions (mcpToolTrigger)

    C->>A: GET /.well-known/oauth-authorization-server
    A-->>C: AS metadata (authorize/token/register URLs)
    C->>A: POST /register (dynamic client registration)
    A->>X: persist registration (managed-identity RBAC)
    A-->>C: client_id
    C->>A: GET /authorize (PKCE S256 challenge)
    A->>A: serve consent screen (CSRF + Origin/Referer/Sec-Fetch-Site checks)
    A->>E: redirect user to Entra sign-in
    E-->>A: authorization code (to /oauth-callback)
    A->>E: exchange code for real Entra token using FIC assertion
    E-->>A: real Entra access token
    A->>A: cache real token server-side; mint AES-256-CBC opaque session key
    A-->>C: session key (the bearer the client holds)
    C->>M: GET /mcp/sse  (Authorization: Bearer <session key>)
    M->>M: decrypt session key, look up cached Entra token, inject x-functions-key
    M->>F: backend call with x-functions-key
    F-->>C: tool result over SSE
```

The single most important line in that diagram: **the real Entra token never leaves APIM**. The client holds only an opaque, encrypted session key.

## Why a browser hit returns 401

Open the endpoint in a browser and you get:

```json
{ "statusCode": 401, "message": "Not authorized" }
```

**That 401 is the gate working, not a bug.** You connect with an **MCP client**, not a browser. The MCP endpoint speaks JSON-RPC over **SSE**, not HTML, and it refuses anonymous traffic. A browser request carries no session-key bearer, so the APIM policy rejects it before any backend call is made.

To reach the server you need a client that walks the authorization flow: **MCP Inspector** or a remote-MCP-capable client such as **Claude Desktop / Claude Code**. The client discovers the metadata, registers itself, runs the consent and sign-in, then redeems a session key. The browser does none of that, so it stops at 401 by design.

## The secretless highlight: Federated Identity Credential

This is the part to slow down on. APIM is a **confidential OAuth client** to Entra, which classically means it must prove its identity with a **client secret**. Stored secrets are the single most common leak vector: they land in source control, in CI logs, in `.env` files, and they expire on a calendar nobody watches.

The FIC pattern removes the secret entirely:

- APIM has a **user-assigned managed identity**. Azure issues that identity a token automatically.
- The Entra **app registration** is configured with a **Federated Identity Credential** that trusts that managed identity as the subject (`infra/app/apim-oauth/entra-app.bicep`, the `federatedIdentityCredentials` resource named `msiAsFic`).
- At token-exchange time, APIM presents the managed-identity token as a **client assertion**. Entra validates the trust relationship and returns the real access token.

| Confidential client credential | Where it is stored | Leak exposure |
|--------------------------------|--------------------|---------------|
| **Client secret** (classic) | Key Vault, `.env`, app settings | High: copyable string, rotates on a calendar, leaks in logs |
| **Federated Identity Credential** (this sample) | Nowhere - issued at runtime by Azure | Low: no copyable secret exists to leak |

Teaching line: **a secret you never store is a secret that cannot leak.** FIC is the modern, leak-resistant way to do confidential-client OAuth on Azure.

## Walkthrough

The full hands-on connect steps are in [`remote-mcp-apim-functions-python/QUICKSTART.md`](../../remote-mcp-apim-functions-python/QUICKSTART.md). The short shape of the demo:

1. Read the live `apim-<token>.azure-api.net/mcp/sse` endpoint from `azd env get-values` (`SERVICE_API_ENDPOINTS`) or the `azd up` output.
2. Hit it in a browser first - get the **401** and narrate why.
3. Launch **MCP Inspector** (`npx @modelcontextprotocol/inspector`), set **Transport** to `SSE`, paste the endpoint, click **Connect**.
4. The Inspector runs discovery -> dynamic registration -> consent -> Entra sign-in -> session key, automatically.
5. Click **List Tools**, then call **`hello_mcp`** (no arguments). It returns `Hello I am MCPTool!` - your first authenticated tool call.

The backend is an **Azure Functions Python v2** app using the experimental `mcpToolTrigger` binding. It registers three tools: `hello_mcp`, `get_snippet`, `save_snippet`.

## Code pointers

Point at these files in class. The OAuth facade is policy-driven; each endpoint is one APIM policy.

| File | What it does |
|------|--------------|
| `infra/app/apim-mcp/mcp-api.policy.xml` | The data-path gate. Decrypts the session-key bearer, looks up the cached Entra token by the decrypted session id, injects `x-functions-key` to call the backend. **No `validate-jwt` on this path by design** - the gate is the encrypted-session lookup. |
| `infra/app/apim-oauth/authorize.policy.xml` | Handles `/authorize`. Validates the PKCE (S256) challenge and redirects the user toward consent and Entra sign-in. |
| `infra/app/apim-oauth/token.policy.xml` | Handles `/token`. Redeems the authorization code, performs the FIC-based exchange with Entra, caches the real token, mints the AES-256-CBC session key. |
| `infra/app/apim-oauth/oauth-callback.policy.xml` | Receives the authorization code from Entra and routes it back into the token-exchange flow. |
| `infra/app/apim-oauth/register.policy.xml` | Handles `/register` (RFC 7591 dynamic client registration). Persists each registration to **Cosmos DB** via managed-identity RBAC. |
| `infra/app/apim-oauth/oauthmetadata-get.policy.xml` | Serves `/.well-known/oauth-authorization-server` (RFC 8414 Authorization Server metadata) so clients can discover the endpoints. |
| `infra/app/apim-oauth/consent.policy.xml` | Serves the consent screen with a CSRF token and `Origin` / `Referer` / `Sec-Fetch-Site` checks before the Entra redirect. |
| `infra/app/apim-oauth/entra-app.bicep` | Declares the Entra **app registration** and the **Federated Identity Credential** (`msiAsFic`) that trusts APIM's managed identity. This is where "no client secret" is configured. |
| `src/function_app.py` | The Azure Functions Python v2 backend. Registers `hello_mcp`, `get_snippet`, `save_snippet` via the `mcpToolTrigger` binding. |

## Spec-currency caveat

State this honestly. The sample implements the **MCP 2025-03-26** authorization flow: client discovery via **Authorization Server Metadata (RFC 8414)**. It does **not** publish **Protected Resource Metadata (RFC 9728)**, and the 401 does **not** carry a `WWW-Authenticate: Bearer resource_metadata="..."` header.

Practical consequence: newer spec-compliant clients that rely on **PRM auto-discovery** get no bootstrap pointer from the 401. The security gate still holds - this is a **discovery-flow gap, not a hole**. Closing it is the natural lead-in to a future lab: an **Azure Container Apps (ACA) + native APIM MCP mode** pattern that publishes PRM and emits the `WWW-Authenticate` header.

## Cost and teardown

**APIM Basicv2 meters hourly.** Tear down the same day you deploy. From the repo root:

```powershell
cd C:\github\context-engineering\remote-mcp-apim-functions-python
azd down --purge --force
```

`--purge` hard-deletes APIM and Cosmos so they do not soft-delete-linger and keep billing. After teardown, confirm with `az apim list -o table` (empty) and delete the Entra app registration if it lingers (`az ad app delete --id <appId>`).
