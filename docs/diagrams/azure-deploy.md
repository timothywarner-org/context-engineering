# WARNERCO Robotics Schematica - Azure Deployment

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#0078d4', 'primaryTextColor': '#fff', 'primaryBorderColor': '#004578', 'lineColor': '#5a6c7d', 'fontFamily': 'Segoe UI, system-ui, sans-serif'}}}%%
flowchart TB
    subgraph Clients["<b>EXTERNAL CLIENTS</b>"]
        direction LR
        CD["<b>Claude Desktop</b><br/>MCP stdio → HTTP"]
        VSC["<b>VS Code</b><br/>Copilot MCP"]
        WEB["<b>Web Browser</b><br/>Dashboards"]
        API["<b>API Consumers</b><br/>REST/HTTP"]
    end

    subgraph Azure["<b>AZURE CLOUD</b>"]

        subgraph Gateway["<b>INGRESS</b>"]
            APIM["<b>API Management</b><br/><br/>Rate limiting<br/>API key auth<br/>Request routing<br/>Analytics"]
        end

        subgraph Compute["<b>COMPUTE</b>"]
            subgraph CAE["Container Apps Environment"]
                CA["<b>Container App</b><br/><br/>FastAPI + FastMCP<br/>LangGraph pipeline<br/>uvicorn ASGI<br/><br/>Scale: 0-3 replicas<br/>CPU: 0.5 cores<br/>Memory: 1Gi"]
            end
        end

        subgraph Data["<b>DATA SERVICES</b>"]
            direction LR
            AIS["<b>Azure AI Search</b><br/><br/>Vector index<br/>Semantic ranking<br/>Hybrid search<br/><br/>SKU: Basic<br/>Replicas: 1"]
            BLOB["<b>Blob Storage</b><br/><br/>Schematic JSON<br/>Static assets<br/>Backup data"]
        end

        subgraph AI["<b>AI SERVICES</b>"]
            AOAI["<b>Azure OpenAI</b><br/><br/>gpt-4o-mini (chat)<br/>text-embedding-ada-002<br/><br/>TPM: 60K<br/>RPM: 350"]
        end

        subgraph Security["<b>SECURITY</b>"]
            direction TB
            KV["<b>Key Vault</b><br/><br/>API keys<br/>Connection strings<br/>Certificates"]
            MI["<b>Managed Identity</b><br/><br/>Passwordless auth<br/>RBAC assignments<br/>Zero secrets in code"]
        end

        subgraph Monitor["<b>OBSERVABILITY</b>"]
            LAW["<b>Log Analytics</b><br/><br/>Container logs<br/>Request traces<br/>Performance metrics"]
            AI_INS["<b>App Insights</b><br/><br/>APM telemetry<br/>Dependency tracking<br/>Alerts"]
        end

    end

    %% Client connections
    CD -->|"HTTPS"| APIM
    VSC -->|"HTTPS"| APIM
    WEB -->|"HTTPS"| APIM
    API -->|"HTTPS"| APIM

    %% Internal connections
    APIM ==>|"route"| CA
    CA -->|"search"| AIS
    CA -->|"read/write"| BLOB
    CA -->|"embeddings<br/>+ chat"| AOAI

    %% Security connections
    CA -.->|"get secrets"| KV
    MI -.->|"auth"| KV
    MI -.->|"auth"| AIS
    MI -.->|"auth"| AOAI
    MI -.->|"auth"| BLOB
    CA -.->|"identity"| MI

    %% Monitoring
    CA -.->|"logs"| LAW
    CA -.->|"telemetry"| AI_INS

    %% Styling
    classDef clientBox fill:#0078d4,stroke:#004578,color:#fff,stroke-width:2px
    classDef gatewayBox fill:#5c2d91,stroke:#3b1d5e,color:#fff,stroke-width:2px
    classDef computeBox fill:#0e7a0d,stroke:#0a5a0a,color:#fff,stroke-width:3px
    classDef dataBox fill:#008272,stroke:#005a4e,color:#fff,stroke-width:2px
    classDef aiBox fill:#d83b01,stroke:#a62d01,color:#fff,stroke-width:2px
    classDef securityBox fill:#5c5c5c,stroke:#3d3d3d,color:#fff,stroke-width:2px
    classDef monitorBox fill:#0063b1,stroke:#004578,color:#fff,stroke-width:2px

    class CD,VSC,WEB,API clientBox
    class APIM gatewayBox
    class CA computeBox
    class AIS,BLOB dataBox
    class AOAI aiBox
    class KV,MI securityBox
    class LAW,AI_INS monitorBox
```

## Resource Inventory

### Resource Group: `warnerco-rg`

| Resource | Type | SKU | Monthly Cost Est. |
|----------|------|-----|-------------------|
| `warnerco-apim` | API Management | Consumption | ~$3.50 |
| `warnerco-app` | Container App | Consumption | ~$0-5 |
| `warnerco-search` | AI Search | Basic | ~$75 |
| `warnerco-openai` | Azure OpenAI | S0 | ~$0-20 |
| `warnercostorage` | Storage Account | Standard LRS | ~$1 |
| `warnerco-kv` | Key Vault | Standard | ~$0.03 |
| `warnerco-logs` | Log Analytics | Pay-per-GB | ~$2-5 |

**Total Estimated**: ~$85-110/month (classroom/demo workload)

## Deployment

### Prerequisites
```bash
# Login and set subscription
az login
az account set --subscription "Your-Subscription-Name"

# Create resource group
az group create --name warnerco-rg --location eastus
```

### Deploy with Bicep
```bash
cd src/warnerco/infra/bicep

# Deploy all resources
az deployment group create \
  --resource-group warnerco-rg \
  --template-file main.bicep \
  --parameters parameters.json
```

### Environment Variables (Container App)
```bash
MEMORY_BACKEND=azure_search
AZURE_SEARCH_ENDPOINT=https://warnerco-search.search.windows.net
AZURE_SEARCH_INDEX=warnerco-schematics
AZURE_OPENAI_ENDPOINT=https://warnerco-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

## Security Architecture

### Managed Identity Flow
```
Container App
     │
     ├──► Key Vault (get secrets)
     │         └── RBAC: Key Vault Secrets User
     │
     ├──► Azure AI Search (search/index)
     │         └── RBAC: Search Index Data Contributor
     │
     ├──► Azure OpenAI (embeddings/chat)
     │         └── RBAC: Cognitive Services OpenAI User
     │
     └──► Blob Storage (read/write)
               └── RBAC: Storage Blob Data Contributor
```

### Zero Secrets Principle
- No API keys in code or environment variables
- Managed Identity authenticates to all services
- Key Vault stores only external/third-party secrets
- RBAC controls all access permissions

## Scaling

### Container Apps Scaling Rules
```yaml
scale:
  minReplicas: 0      # Scale to zero when idle
  maxReplicas: 3      # Handle traffic spikes
  rules:
    - name: http-rule
      http:
        metadata:
          concurrentRequests: "50"
```

### Cost Optimization
- **Scale to zero**: No charges when idle
- **Consumption tier**: Pay only for actual usage
- **Basic search**: Sufficient for <100K documents
- **Token limits**: Controlled via APIM policies
