# Azure Deployment Reference

## Resource Architecture

```
warnerco-rg/
├── warnerco-app (Container App)
│   └── FastAPI + FastMCP server
├── warnerco-apim (API Management - Basic)
│   └── Proxy to Container App
├── warnerco-search (Azure AI Search - Free)
│   └── Schematic vectors
├── warnerco-openai (Azure OpenAI)
│   ├── gpt-4o-mini (reasoning)
│   └── text-embedding-ada-002 (embeddings)
└── warnercostorage (Storage Account)
    └── Blob containers
```

## Deployment Steps

### 1. Create Resource Group

```bash
az group create --name warnerco-rg --location eastus
```

### 2. Deploy Container App

```bash
# Create Container App Environment
az containerapp env create \
  --name warnerco-env \
  --resource-group warnerco-rg \
  --location eastus

# Deploy from registry or local build
az containerapp create \
  --name warnerco-app \
  --resource-group warnerco-rg \
  --environment warnerco-env \
  --image ghcr.io/yourorg/warnerco-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    MEMORY_BACKEND=azure_search \
    AZURE_SEARCH_ENDPOINT=https://warnerco-search.search.windows.net \
    AZURE_SEARCH_INDEX=warnerco-schematics
```

### 3. Configure APIM

```bash
az apim create \
  --name warnerco-apim \
  --resource-group warnerco-rg \
  --publisher-name "WARNERCO" \
  --publisher-email admin@warnerco.io \
  --sku-name Basic

# Import OpenAPI spec
az apim api import \
  --resource-group warnerco-rg \
  --service-name warnerco-apim \
  --path schematica \
  --specification-format OpenApi \
  --specification-url https://warnerco-app.azurecontainerapps.io/openapi.json
```

### 4. Create AI Search Index

```bash
az search service create \
  --name warnerco-search \
  --resource-group warnerco-rg \
  --sku free \
  --location eastus
```

Index schema:
```json
{
  "name": "warnerco-schematics",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "model", "type": "Edm.String", "filterable": true},
    {"name": "name", "type": "Edm.String", "searchable": true},
    {"name": "summary", "type": "Edm.String", "searchable": true},
    {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "status", "type": "Edm.String", "filterable": true},
    {"name": "embedding", "type": "Collection(Edm.Single)", "dimensions": 1536, "vectorSearchProfile": "default"}
  ],
  "vectorSearch": {
    "profiles": [{"name": "default", "algorithm": "hnsw"}],
    "algorithms": [{"name": "hnsw", "kind": "hnsw"}]
  }
}
```

### 5. Deploy OpenAI Models

```bash
az cognitiveservices account create \
  --name warnerco-openai \
  --resource-group warnerco-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus

# Deploy models
az cognitiveservices account deployment create \
  --name warnerco-openai \
  --resource-group warnerco-rg \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard

az cognitiveservices account deployment create \
  --name warnerco-openai \
  --resource-group warnerco-rg \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard
```

## Environment Variables (Production)

```bash
# Container App secrets
MEMORY_BACKEND=azure_search
AZURE_SEARCH_ENDPOINT=https://warnerco-search.search.windows.net
AZURE_SEARCH_KEY=<from-portal>
AZURE_SEARCH_INDEX=warnerco-schematics
AZURE_OPENAI_ENDPOINT=https://warnerco-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=<from-portal>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

## Cost Estimates (Monthly)

| Resource | SKU | Est. Cost |
|----------|-----|-----------|
| Container App | Consumption | ~$5-20 |
| APIM | Basic | ~$150 |
| AI Search | Free | $0 |
| Azure OpenAI | Pay-per-token | ~$5-50 |
| Storage | Standard | ~$1 |

**Total**: ~$160-220/month (classroom POC)

## Teardown

```bash
az group delete --name warnerco-rg --yes --no-wait
```
