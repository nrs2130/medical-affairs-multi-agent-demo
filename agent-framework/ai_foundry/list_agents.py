""""""

List All Agents in Azure AI Foundry ProjectList all agents in Azure AI Foundry project using Agent Service API

==========================================="""



This script lists all agents registered in your Azure AI Foundry projectimport os

with details about their configuration, models, and metadata.import json

import subprocess

Prerequisites:from datetime import datetime

- Azure AI Foundry project with connection string in .envfrom dotenv import load_dotenv

- Azure CLI authentication (run 'az login')import httpx



Usage:load_dotenv()

    python list_agents.py

"""ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")

PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")

import osAPI_VERSION = "2025-05-01"  # GA version for Agent Service

import json

from datetime import datetime# Get Entra ID token

from azure.ai.projects import AIProjectClienttry:

from azure.identity import DefaultAzureCredential    result = subprocess.run(

from dotenv import load_dotenv        ["az", "account", "get-access-token", "--resource", "https://ai.azure.com"],

        capture_output=True,

# Load environment variables        text=True,

load_dotenv()        check=True,

        shell=True  # Use shell to find az command in PATH

# Azure AI Foundry Configuration    )

AI_FOUNDRY_PROJECT_CONNECTION_STRING = os.getenv('AI_FOUNDRY_PROJECT_CONNECTION_STRING')    token_data = json.loads(result.stdout)

    access_token = token_data["accessToken"]

# Validate configurationexcept Exception as e:

if not AI_FOUNDRY_PROJECT_CONNECTION_STRING:    print(f"❌ Failed to get Entra ID token. Please run 'az login' first.")

    print("⚠️  ERROR: AI_FOUNDRY_PROJECT_CONNECTION_STRING not set!")    print(f"Error: {e}")

    print("   Set in your .env file or environment:")    exit(1)

    print("   AI_FOUNDRY_PROJECT_CONNECTION_STRING=<your-connection-string>")

    exit(1)url = f"{ENDPOINT}/api/projects/{PROJECT_NAME}/assistants?api-version={API_VERSION}"

headers = {

    "Authorization": f"Bearer {access_token}",

def create_client():    "Content-Type": "application/json"

    """Create Azure AI Project client with authentication"""}

    credential = DefaultAzureCredential()

    client = AIProjectClient.from_connection_string(print("=" * 80)

        credential=credential,print("📋 Listing all agents in Azure AI Foundry (Agent Service)")

        conn_str=AI_FOUNDRY_PROJECT_CONNECTION_STRINGprint("=" * 80)

    )print(f"Endpoint: {ENDPOINT}")

    return clientprint(f"Project: {PROJECT_NAME}")

print(f"Auth: Entra ID (Azure CLI)\n")



def list_agents(client):try:

    """List all agents in the project"""    with httpx.Client(timeout=30.0) as client:

    print("=" * 80)        response = client.get(url, headers=headers)

    print("📋 LISTING ALL AGENTS IN AZURE AI FOUNDRY")        response.raise_for_status()

    print("=" * 80)        data = response.json()

    print(f"Project: {AI_FOUNDRY_PROJECT_CONNECTION_STRING.split(';')[0].split('=')[1] if ';' in AI_FOUNDRY_PROJECT_CONNECTION_STRING else 'Unknown'}")        

    print(f"Auth: Azure Default Credential (Azure CLI)\n")        agents = data.get("data", [])

            print(f"Found {len(agents)} agents:\n")

    try:        

        agents = list(client.agents.list_agents())        for agent in agents:

                    created_at = datetime.fromtimestamp(agent.get("created_at", 0))

        if not agents:            description = agent.get('description') or 'N/A'

            print("No agents found in this project.")            print(f"Name: {agent.get('name', 'N/A')}")

            print("\nTo register agents, run: python register_agents_ai_foundry.py\n")            print(f"ID: {agent.get('id')}")

            return            print(f"Model: {agent.get('model')}")

                    print(f"Created: {created_at.strftime('%b %d, %Y %I:%M %p')}")

        print(f"Found {len(agents)} agent(s):\n")            print(f"Description: {description[:80] if description != 'N/A' else 'N/A'}")

        print("=" * 80)            print(f"Tools: {[tool.get('type') for tool in agent.get('tools', [])]}")

                    print("-" * 80)

        for i, agent in enumerate(agents, 1):                

            print(f"\n{i}. {agent.name}")except Exception as e:

            print(f"   ID: {agent.id}")    print(f"❌ Error: {e}")

            print(f"   Model: {agent.model}")    import traceback

            print(f"   Created: {agent.created_at}")    traceback.print_exc()

            
            if agent.description:
                desc = agent.description[:100] + "..." if len(agent.description) > 100 else agent.description
                print(f"   Description: {desc}")
            
            if hasattr(agent, 'metadata') and agent.metadata:
                print(f"   Metadata: {json.dumps(agent.metadata, indent=2)}")
            
            if hasattr(agent, 'tools') and agent.tools:
                tools = [tool.type if hasattr(tool, 'type') else str(tool) for tool in agent.tools]
                print(f"   Tools: {tools}")
            
            print("   " + "-" * 76)
        
        print("\n" + "=" * 80)
        print(f"✅ Total Agents: {len(agents)}")
        print("=" * 80)
        print("\n🌐 View agents in Azure AI Studio:")
        print("   https://ai.azure.com/\n")
        
        # Save to JSON for reference
        agents_data = []
        for agent in agents:
            agents_data.append({
                "name": agent.name,
                "id": agent.id,
                "model": agent.model,
                "created_at": str(agent.created_at),
                "description": agent.description if agent.description else None,
                "metadata": agent.metadata if hasattr(agent, 'metadata') else None
            })
        
        with open("ai_foundry_agents_list.json", 'w') as f:
            json.dump(agents_data, f, indent=2)
        
        print(f"💾 Agent list saved to: ai_foundry_agents_list.json\n")
        
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Main function"""
    try:
        print("\n🔐 Connecting to Azure AI Foundry...")
        client = create_client()
        print("   ✅ Connected\n")
        
        list_agents(client)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("   1. Verify AI_FOUNDRY_PROJECT_CONNECTION_STRING in .env")
        print("   2. Ensure Azure CLI is authenticated: az login")
        print("   3. Check Azure AI Foundry project exists and is accessible")
        raise


if __name__ == "__main__":
    main()
