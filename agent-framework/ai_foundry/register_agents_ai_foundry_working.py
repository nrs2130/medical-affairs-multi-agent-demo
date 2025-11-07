"""
Register Medical Affairs Agents in Azure AI Foundry
===================================================

Simple script using REST API and .env file for credentials.

Setup:
1. Copy .env.example to .env and fill in your values
2. pip install python-dotenv httpx
3. python register_agents_azure.py
"""

import os
import json
import httpx
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure AI Foundry Configuration
ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_AI_PROJECT_KEY", "")
PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")

# Validate configuration
if not ENDPOINT or not API_KEY:
    print("=" * 80)
    print("❌ ERROR: Missing Azure AI Foundry credentials!")
    print("=" * 80)
    print("\n📋 Setup Instructions:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your Azure AI Foundry endpoint and API key")
    print("3. Run this script again\n")
    exit(1)


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

MEDICAL_AFFAIRS_AGENTS = [
    {
        "name": "Literature Scout Agent",
        "description": "Searches PubMed, clinical trials, and product labeling for evidence-based medical information. Ranks evidence by quality and recency.",
        "model": "gpt-4o",
        "instructions": """You are a Literature Scout Agent for pharmaceutical Medical Affairs.

Your role:
- Search medical literature (PubMed, clinical trials, FDA labels)
- Retrieve high-quality evidence for HCP inquiries
- Rank studies by quality (RCTs > observational > case reports)
- Format citations properly
- Assess evidence strength

Always prioritize peer-reviewed research and official regulatory documents.""",
        "tools": ["code_interpreter", "file_search"],
        "capabilities": ["literature_search", "evidence_ranking", "citation_formatting"]
    },
    {
        "name": "MI Orchestrator Agent",
        "description": "Coordinates Medical Information responses, ensures regulatory compliance, and manages multi-agent workflows for complex healthcare professional inquiries.",
        "model": "gpt-4o",
        "instructions": """You are an MI Orchestrator Agent managing Medical Information responses.

Your role:
- Route HCP inquiries to appropriate specialized agents
- Coordinate multi-source evidence gathering
- Synthesize findings into coherent responses
- Ensure compliance with regulatory requirements
- Maintain audit trail of all decisions

You must balance scientific accuracy, regulatory compliance, and timely delivery.""",
        "tools": ["code_interpreter"],
        "capabilities": ["inquiry_routing", "response_coordination", "compliance_checking"]
    },
    {
        "name": "Compliance Guard Agent",
        "description": "Reviews all Medical Information responses for regulatory compliance, flags potential risks, and ensures adherence to FDA, EMA, and company medical governance standards.",
        "model": "gpt-4o",
        "instructions": """You are a Compliance Guard Agent for pharmaceutical Medical Affairs.

Your role:
- Review responses for regulatory compliance (FDA, EMA, ICH)
- Flag promotional language or off-label claims
- Verify all claims are substantiated by approved labeling or peer-reviewed literature
- Ensure adverse event reporting requirements are met
- Maintain audit documentation

You have veto power over any response that poses compliance risk.""",
        "tools": ["code_interpreter"],
        "capabilities": ["compliance_review", "risk_assessment", "regulatory_validation"]
    }
]


# ============================================================================
# AZURE AI FOUNDRY API CLIENT
# ============================================================================

class AzureAIFoundryClient:
    """Simple REST API client for Azure AI Foundry Agent Service."""
    
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        # API version for Azure AI Agent Service
        self.api_version = "2024-07-01-preview"
    
    def create_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an agent in Azure AI Foundry."""
        # Use the OpenAI Assistants API endpoint (Azure AI Foundry compatible)
        url = f"{self.endpoint}/openai/assistants?api-version={self.api_version}"
        
        # Prepare agent payload according to Azure AI Agent Service schema
        payload = {
            "model": agent_config.get("model", "gpt-4o"),
            "name": agent_config["name"],
            "description": agent_config["description"],
            "instructions": agent_config["instructions"],
            "tools": [{"type": tool} for tool in agent_config.get("tools", [])],
            "metadata": {
                "capabilities": json.dumps(agent_config.get("capabilities", [])),
                "registered_at": datetime.now().isoformat(),
                "source": "medical_affairs_multi_agent_demo"
            }
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            print(f"\n❌ HTTP Error {e.response.status_code}")
            print(f"Response: {e.response.text[:500]}")
            raise
        except Exception as e:
            print(f"\n❌ Error creating agent: {e}")
            raise
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents in the project."""
        url = f"{self.endpoint}/openai/assistants?api-version={self.api_version}"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("data", data.get("value", []))
        except Exception as e:
            print(f"⚠️  Could not list agents: {e}")
            return []


# ============================================================================
# REGISTRATION FUNCTIONS
# ============================================================================

def register_all_agents():
    """Register all Medical Affairs agents in Azure AI Foundry."""
    print("=" * 80)
    print("🏥 Medical Affairs Multi-Agent System - Azure AI Foundry Registration")
    print("=" * 80)
    print(f"\n📍 Endpoint: {ENDPOINT}")
    print(f"📦 Project: {PROJECT_NAME}")
    print(f"🔑 API Key: {'*' * 20}{API_KEY[-10:] if API_KEY else 'NOT SET'}\n")
    
    # Initialize client
    client = AzureAIFoundryClient(ENDPOINT, API_KEY)
    
    # Check existing agents
    print("🔍 Checking existing agents...")
    try:
        existing_agents = client.list_agents()
        existing_names = {agent.get("name") for agent in existing_agents}
        print(f"   Found {len(existing_agents)} existing agents\n")
    except Exception as e:
        print(f"   ⚠️  Could not list existing agents: {e}")
        print("   Continuing with registration...\n")
        existing_names = set()
    
    # Register each agent
    registered = []
    skipped = []
    failed = []
    
    for agent_config in MEDICAL_AFFAIRS_AGENTS:
        agent_name = agent_config["name"]
        
        if agent_name in existing_names:
            print(f"⏭️  Skipping '{agent_name}' (already registered)")
            skipped.append(agent_name)
            continue
        
        print(f"📝 Registering: {agent_name}")
        try:
            result = client.create_agent(agent_config)
            agent_id = result.get("id", "unknown")
            print(f"   ✅ Success! (ID: {agent_id})")
            registered.append({
                "name": agent_name,
                "id": agent_id,
                "created_at": result.get("created_at")
            })
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}")
            failed.append(agent_name)
    
    # Summary
    print("\n" + "=" * 80)
    print(f"📊 Registration Summary")
    print("=" * 80)
    print(f"✅ Registered: {len(registered)}")
    print(f"⏭️  Skipped: {len(skipped)}")
    print(f"❌ Failed: {len(failed)}\n")
    
    if registered:
        print("🎉 Successfully registered agents:")
        for agent in registered:
            print(f"   • {agent['name']}")
            print(f"     ID: {agent['id']}\n")
    
    if failed:
        print("⚠️  Failed to register:")
        for name in failed:
            print(f"   • {name}")
        print()
    
    print("🌐 View your agents in Azure Portal:")
    print("   https://ai.azure.com/\n")
    
    # Save registration details
    if registered:
        output_file = "azure_agent_registration.json"
        with open(output_file, "w") as f:
            json.dump({
                "registered_at": datetime.now().isoformat(),
                "endpoint": ENDPOINT,
                "project": PROJECT_NAME,
                "agents": registered
            }, f, indent=2)
        print(f"💾 Registration details saved to: {output_file}\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        register_all_agents()
    except KeyboardInterrupt:
        print("\n\n⏸️  Registration cancelled by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
