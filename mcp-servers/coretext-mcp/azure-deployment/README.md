# Azure Container Apps Deployment

## Quick Start

Deploy CoreText MCP to Azure Container Apps in minutes:

```bash
cd azure-deployment
chmod +x deploy.sh
./deploy.sh
```

## What's Included

- **Dockerfile** - Optimized Node.js 20 Alpine image
- **deploy.sh** - Automated deployment script
- **DEPLOYMENT_GUIDE.md** - Complete documentation

## Files

```
azure-deployment/
├── Dockerfile          # Container image definition
├── .dockerignore       # Excludes unnecessary files from image
├── deploy.sh           # One-command deployment script
├── DEPLOYMENT_GUIDE.md # Detailed instructions
└── README.md           # This file
```

## Requirements

- Azure CLI installed and authenticated
- Existing resource group: `context-engineering-rg`
- (Optional) Deepseek API key for AI enrichment

## Deployment Steps

The `deploy.sh` script automatically:

1. ✅ Creates Azure Container Registry
2. ✅ Builds Docker image
3. ✅ Pushes image to registry
4. ✅ Creates Container Apps Environment
5. ✅ Deploys container app
6. ✅ Outputs public URL

## Configuration

Set environment variables before deploying:

```bash
# Optional: Enable AI enrichment
export DEEPSEEK_API_KEY="your-api-key-here"

# Then deploy
./deploy.sh
```

## Cost

Estimated monthly cost with 1 replica:
- **~$30-40/month** for small workloads
- Can scale to zero (min-replicas=0) for dev/test

## Support

See **DEPLOYMENT_GUIDE.md** for:
- Detailed deployment steps
- Troubleshooting
- Management commands
- Security best practices
- Cost optimization
