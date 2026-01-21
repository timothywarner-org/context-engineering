"""Index schematics into Azure AI Search with embeddings."""

import json
import os
import sys
from pathlib import Path

import httpx
from openai import AzureOpenAI

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Force load from the backend .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)
print(f"Loaded environment from {env_path}")

# Configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "warnerco-schematics")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

SCHEMATICS_PATH = Path(__file__).parent.parent / "data" / "schematics" / "schematics.json"


def get_embedding(client: AzureOpenAI, text: str) -> list[float]:
    """Generate embedding for text using Azure OpenAI."""
    response = client.embeddings.create(
        input=text,
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding


def create_embed_text(schematic: dict) -> str:
    """Create text for embedding from schematic fields."""
    parts = [
        f"Model: {schematic['model']}",
        f"Name: {schematic['name']}",
        f"Component: {schematic['component']}",
        f"Category: {schematic['category']}",
        f"Summary: {schematic['summary']}",
    ]
    if schematic.get("tags"):
        parts.append(f"Tags: {', '.join(schematic['tags'])}")
    if schematic.get("specifications"):
        specs = schematic["specifications"]
        if isinstance(specs, dict):
            spec_str = ", ".join(f"{k}: {v}" for k, v in specs.items())
            parts.append(f"Specifications: {spec_str}")
    return "\n".join(parts)


def main():
    print(f"Loading schematics from {SCHEMATICS_PATH}")
    with open(SCHEMATICS_PATH) as f:
        schematics = json.load(f)
    print(f"Found {len(schematics)} schematics")

    # Initialize Azure OpenAI client
    print(f"Connecting to Azure OpenAI at {AZURE_OPENAI_ENDPOINT}")
    openai_client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-02-01"
    )

    # Prepare documents with embeddings
    documents = []
    for i, schematic in enumerate(schematics):
        print(f"  [{i+1}/{len(schematics)}] Generating embedding for {schematic['id']}...")

        embed_text = create_embed_text(schematic)
        embedding = get_embedding(openai_client, embed_text)

        doc = {
            "id": schematic["id"],
            "model": schematic["model"],
            "name": schematic["name"],
            "component": schematic["component"],
            "version": schematic["version"],
            "summary": schematic["summary"],
            "category": schematic["category"],
            "status": schematic["status"],
            "url": schematic.get("url", ""),
            "tags": schematic.get("tags", []),
            "last_verified": schematic.get("last_verified", ""),
            "specifications": json.dumps(schematic.get("specifications", {})),
            "embedding": embedding
        }
        documents.append(doc)

    # Upload to Azure AI Search
    print(f"\nUploading {len(documents)} documents to Azure AI Search...")

    upload_url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}/docs/index?api-version=2024-07-01"

    payload = {
        "value": [
            {"@search.action": "upload", **doc}
            for doc in documents
        ]
    }

    response = httpx.post(
        upload_url,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "api-key": AZURE_SEARCH_KEY
        },
        timeout=60.0
    )

    if response.status_code in (200, 201):
        result = response.json()
        success_count = sum(1 for r in result.get("value", []) if r.get("status"))
        print(f"Successfully uploaded {success_count} documents")
    else:
        print(f"Upload failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

    print("\nDone! Azure AI Search index is ready.")


if __name__ == "__main__":
    main()
