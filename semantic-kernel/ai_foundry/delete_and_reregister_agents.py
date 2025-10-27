"""
Delete and Re-register Medical Affairs Agents with Updated Configuration
=========================================================================

This script:
1. Deletes existing agents from Azure AI Foundry
2. Re-registers them with updated model or configuration

Use cases:
- Update agent model (e.g., gpt-4o → gpt-4.1)
- Modify agent instructions or capabilities
- Reset agent state

Note: This uses the Azure AI Foundry Agent Service API (/api/projects/{project}/assistants)
      to manage externally-built Semantic Kernel agents in the Foundry project.

Prerequisites:
- Agents must be already registered (run register_agents_azure.py first)
- Valid .env file with Azure AI Foundry credentials
- Azure CLI authentication (run 'az login')
"""

import os
import subprocess
import json
import httpx
from dotenv import load_dotenv
from register_agents_azure import AzureAIFoundryClient, MEDICAL_AFFAIRS_AGENTS

# Load environment variables
load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")

print("=" * 80)
print("🔄 Delete and Re-register Medical Affairs Agents with gpt-4.1")
print("=" * 80)
print(f"\n📍 Endpoint: {ENDPOINT}")
print(f"📦 Project: {PROJECT_NAME}")
print(f"🔐 Auth: Entra ID (Azure CLI)\n")

# Initialize client (will get Entra ID token)
try:
    client = AzureAIFoundryClient(ENDPOINT)
    print("✅ Successfully authenticated with Entra ID\n")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    exit(1)

# Step 1: List existing agents
print("🔍 Step 1: Listing existing agents...")
existing_agents = client.list_agents(PROJECT_NAME)
print(f"   Found {len(existing_agents)} agents\n")

# Step 2: Delete existing Medical Affairs agents
medical_affairs_names = {agent["name"] for agent in MEDICAL_AFFAIRS_AGENTS}
deleted_count = 0

for agent in existing_agents:
    if agent.get("name") in medical_affairs_names:
        agent_id = agent.get("id")
        agent_name = agent.get("name")
        print(f"🗑️  Deleting: {agent_name} (ID: {agent_id})")
        
        # Delete via API
        delete_url = f"{ENDPOINT}/api/projects/{PROJECT_NAME}/assistants/{agent_id}?api-version={client.api_version}"
        try:
            with httpx.Client(timeout=30.0) as http_client:
                response = http_client.delete(delete_url, headers=client.headers)
                response.raise_for_status()
                print(f"   ✅ Deleted successfully")
                deleted_count += 1
        except Exception as e:
            print(f"   ❌ Failed to delete: {e}")

print(f"\n📊 Deleted {deleted_count} agents\n")

# Step 3: Re-register all agents with gpt-4.1
print("=" * 80)
print("📝 Step 2: Re-registering agents with gpt-4.1...")
print("=" * 80 + "\n")

registered = []
failed = []

for agent_config in MEDICAL_AFFAIRS_AGENTS:
    agent_name = agent_config["name"]
    model = agent_config["model"]
    
    print(f"📝 Registering: {agent_name} (model: {model})")
    try:
        result = client.create_agent(agent_config, PROJECT_NAME)
        agent_id = result.get("id", "unknown")
        print(f"   ✅ Success! (ID: {agent_id})")
        registered.append({
            "name": agent_name,
            "id": agent_id,
            "model": model
        })
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        failed.append(agent_name)

# Summary
print("\n" + "=" * 80)
print(f"📊 Re-registration Summary")
print("=" * 80)
print(f"✅ Registered: {len(registered)}")
print(f"❌ Failed: {len(failed)}\n")

if registered:
    print("🎉 Successfully registered agents with gpt-4.1:")
    for agent in registered:
        print(f"   • {agent['name']}")
        print(f"     ID: {agent['id']}")
        print(f"     Model: {agent['model']}\n")

print("🌐 View your agents in Azure Portal:")
print("   https://ai.azure.com/\n")
