"""
List all agents in Azure AI Foundry project using Agent Service API
"""

import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import httpx

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")
API_VERSION = "2025-05-01"  # GA version for Agent Service

# Get Entra ID token
try:
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://ai.azure.com"],
        capture_output=True,
        text=True,
        check=True,
        shell=True  # Use shell to find az command in PATH
    )
    token_data = json.loads(result.stdout)
    access_token = token_data["accessToken"]
except Exception as e:
    print(f"❌ Failed to get Entra ID token. Please run 'az login' first.")
    print(f"Error: {e}")
    exit(1)

url = f"{ENDPOINT}/api/projects/{PROJECT_NAME}/assistants?api-version={API_VERSION}"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("📋 Listing all agents in Azure AI Foundry (Agent Service)")
print("=" * 80)
print(f"Endpoint: {ENDPOINT}")
print(f"Project: {PROJECT_NAME}")
print(f"Auth: Entra ID (Azure CLI)\n")

try:
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        agents = data.get("data", [])
        print(f"Found {len(agents)} agents:\n")
        
        for agent in agents:
            created_at = datetime.fromtimestamp(agent.get("created_at", 0))
            description = agent.get('description') or 'N/A'
            print(f"Name: {agent.get('name', 'N/A')}")
            print(f"ID: {agent.get('id')}")
            print(f"Model: {agent.get('model')}")
            print(f"Created: {created_at.strftime('%b %d, %Y %I:%M %p')}")
            print(f"Description: {description[:80] if description != 'N/A' else 'N/A'}")
            print(f"Tools: {[tool.get('type') for tool in agent.get('tools', [])]}")
            print("-" * 80)
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
