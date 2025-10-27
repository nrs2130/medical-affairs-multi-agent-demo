"""
Delete and Re-register Medical Affairs Agents
==============================================

Deletes existing agents and optionally re-registers them.
Uses Microsoft Agent Framework's AIProjectClient.

Usage:
    python delete_and_reregister_agents.py
"""

import os
import json
from datetime import datetime
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# Configuration
CONN_STR = os.getenv('AI_FOUNDRY_PROJECT_CONNECTION_STRING')
MODEL = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')

AGENT_NAMES = [
    "Literature Scout Agent",
    "MI Orchestrator Agent", 
    "Compliance Guard Agent",
    "GRADE Evidence Assessment Agent"
]

if not CONN_STR:
    print("ERROR: AI_FOUNDRY_PROJECT_CONNECTION_STRING not set")
    exit(1)

# Create client
print("=" * 80)
print("DELETE AND RE-REGISTER MEDICAL AFFAIRS AGENTS")
print("=" * 80)
print("\nConnecting to Azure AI Foundry...")

client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=CONN_STR
)
print("Connected!\n")

# Step 1: List and delete
print("Step 1: Deleting existing agents")
print("-" * 80)
agents = list(client.agents.list_agents())
deleted = 0

for agent in agents:
    if agent.name in AGENT_NAMES:
        print(f"Deleting: {agent.name} (ID: {agent.id})")
        try:
            client.agents.delete_agent(agent.id)
            deleted += 1
            print("  ✅ Deleted")
        except Exception as e:
            print(f"  ❌ Error: {e}")

print(f"\nDeleted {deleted} agents\n")

# Step 2: Ask to re-register
print("=" * 80)
print("To re-register agents, run:")
print("  python register_agents_ai_foundry.py")
print("=" * 80)
