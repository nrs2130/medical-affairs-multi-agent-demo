"""
List all agents in Azure AI Foundry project
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import httpx

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_AI_PROJECT_KEY", "")
API_VERSION = "2024-07-01-preview"

url = f"{ENDPOINT}/openai/assistants?api-version={API_VERSION}"
headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 80)
print("📋 Listing all agents in Azure AI Foundry")
print("=" * 80)
print(f"Endpoint: {ENDPOINT}\n")

try:
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        agents = data.get("data", [])
        print(f"Found {len(agents)} agents:\n")
        
        for agent in agents:
            created_at = datetime.fromtimestamp(agent.get("created_at", 0))
            print(f"Name: {agent.get('name', 'N/A')}")
            print(f"ID: {agent.get('id')}")
            print(f"Model: {agent.get('model')}")
            print(f"Created: {created_at.strftime('%b %d, %Y %I:%M %p')}")
            print(f"Description: {agent.get('description', 'N/A')[:80]}")
            print(f"Tools: {[tool.get('type') for tool in agent.get('tools', [])]}")
            print("-" * 80)
        
        # Check for our specific agents
        our_agent_ids = [
            "asst_MA28hc1YMgbtS4xd1DfEBXDn",
            "asst_llk1aTZkgXhhTB9N9NA4gbAK",
            "asst_kajhnBtp10VIjSxQQQGYErCN"
        ]
        
        found_ids = {agent.get('id') for agent in agents}
        print("\n🔍 Checking for our Medical Affairs agents:")
        for agent_id in our_agent_ids:
            if agent_id in found_ids:
                print(f"   ✅ {agent_id} - FOUND")
            else:
                print(f"   ❌ {agent_id} - NOT FOUND")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
