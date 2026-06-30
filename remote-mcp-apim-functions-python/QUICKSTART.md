# Quickstart: Connect to the Secured Remote MCP Server

**Teaching point:** OAuth AAA (**A**uthentication, **A**uthorization, **A**ccounting) in an Azure context, with **Entra ID** as the identity provider and **Azure API Management** as the AI Gateway in front of an Azure Functions MCP server.

> This is the *connect-and-demo* guide. For what gets deployed and why, see [`README.md`](README.md). For the upstream source credit, also see `README.md`.

## The live endpoint

After `azd up`, the deploy prints the MCP endpoint. For the current course environment it is:

```
https://apim-t47jhk2ad76m6.azure-api.net/mcp/sse
```

Your APIM host is generated per deploy (`apim-<token>.azure-api.net`) - read the real one from `azd env get-values` (`SERVICE_API_ENDPOINTS`) or the `azd up` output.

## Why a browser hit returns 401 (and that is correct)

Open the endpoint in a browser and you get:

```json
{ "statusCode": 401, "message": "Not authorized" }
```

**That 401 is the lesson, not a bug.** The MCP endpoint refuses anonymous traffic. You cannot "browse" an MCP server - it speaks JSON-RPC over SSE, not HTML, and it is gated by OAuth. To reach it you need an **MCP client** that walks the authorization flow. Two ways below.

## Option 1: MCP Inspector (fastest, visual, best for class)

```powershell
npx @modelcontextprotocol/inspector
```

That opens `http://localhost:6274`. In the Inspector UI:

1. **Transport Type:** `SSE`
2. **URL:** `https://apim-<token>.azure-api.net/mcp/sse`
3. Click **Connect**

The Inspector runs the full OAuth flow automatically:

1. Discovers `/.well-known/oauth-authorization-server` (RFC 8414 metadata)
2. **Dynamically registers** itself as a client (RFC 7591) - APIM persists the registration to Cosmos DB
3. Opens a browser tab to **APIM's consent screen**, then to **Entra ID sign-in**
4. You sign in (e.g. `tim@techtrainertim.com`) and consent
5. Inspector redeems the authorization code at `/token` and receives the session bearer

After connect: click **List Tools** to see `hello_mcp`, `get_snippet`, `save_snippet`. Call **`hello_mcp`** (no arguments) - it returns `Hello I am MCPTool!`. That is your first authenticated tool call.

## Option 2: Claude Desktop / Claude Code (remote MCP client)

Add an SSE server entry to your client config (Claude Desktop on Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "warnerco-remote-mcp": {
      "type": "sse",
      "url": "https://apim-<token>.azure-api.net/mcp/sse"
    }
  }
}
```

Restart the client. On first connect it triggers the same browser-based Entra consent flow.

## What to narrate at the consent screen (the AAA beat)

The MCP client **never receives your real Entra access token**. The flow:

| Stage | Who | What happens |
|-------|-----|--------------|
| **Authentication** | Entra ID | APIM redirects the user to Entra to sign in. PKCE (S256) binds the request. |
| **Authorization** | APIM + Entra | APIM exchanges the auth code for an Entra token using a **Federated Identity Credential off its managed identity - no client secret anywhere**. |
| **Token brokering** | APIM | APIM caches the real Entra token server-side and hands the client only an **AES-encrypted opaque session key**. |
| **Authenticated calls** | APIM | Each `/mcp/sse` call presents the session key; APIM decrypts it, looks up the cached token, and injects the Function host key (`x-functions-key`) to the backend. |
| **Accounting** | App Insights + Log Analytics | Every gateway transaction is logged for audit and metrics. |

The secretless **Federated Identity Credential** is the highlight: APIM proves its identity to Entra with a managed-identity assertion, not a stored secret. That is the modern, leak-resistant way to do confidential-client OAuth in Azure.

## Spec-currency caveat (state it honestly in class)

This sample implements the **MCP 2025-03-26** authorization flow: discovery via **Authorization Server Metadata** (RFC 8414). It does **not** publish **Protected Resource Metadata** (RFC 9728), and the 401 does not carry a `WWW-Authenticate: Bearer resource_metadata="..."` header. Newer spec-compliant clients that rely on PRM auto-discovery will not get that bootstrap pointer here. The security gate still holds - this is a discovery-flow gap, not a hole. Closing it is the natural next lab (see the ACA + native-APIM-MCP pattern note in the course materials).

## Teardown (do this same day - APIM Basicv2 meters hourly)

```powershell
cd C:\github\context-engineering\remote-mcp-apim-functions-python
azd down --purge --force
```

`--purge` hard-deletes APIM and Cosmos so they do not soft-delete-linger and keep billing. After teardown, confirm with `az apim list -o table` (empty) and delete the Entra app registration if it lingers (`az ad app delete --id <appId>`).
