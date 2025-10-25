"""
Delete existing agents and re-register with correct model (gpt-4.1)
"""

import os
import httpx
from dotenv import load_dotenv
from register_agents_azure import AzureAIFoundryClient, MEDICAL_AFFAIRS_AGENTS

# Load environment variables
load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_AI_PROJECT_KEY", "")

print("=" * 80)
print("🔄 Delete and Re-register Medical Affairs Agents with gpt-4.1")
print("=" * 80)
print(f"\n📍 Endpoint: {ENDPOINT}\n")

# Initialize client
client = AzureAIFoundryClient(ENDPOINT, API_KEY)

# Step 1: List existing agents
print("🔍 Step 1: Listing existing agents...")
existing_agents = client.list_agents()
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
        delete_url = f"{ENDPOINT}/openai/assistants/{agent_id}?api-version=2024-07-01-preview"
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
        result = client.create_agent(agent_config)
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
