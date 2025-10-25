"""
Register Medical Affairs Agents in Azure AI Foundry
===================================================

This script registers external Semantic Kernel agents as OpenAI Assistants in Azure AI Foundry.

How it works:
- Connects to your Azure AI Foundry project endpoint with credentials
- Registers agents via Azure AI Foundry Agent Service API (/openai/assistants)
- Associates agents with your Foundry-hosted model (gpt-4.1)
- Once registered, agents can be monitored and traced in Azure AI Foundry portal

Setup:
1. Copy .env.example to .env and fill in your values
2. pip install python-dotenv httpx
3. python register_agents_azure.py

Monitoring:
- Agents registered via /openai/assistants endpoint
- View in Azure AI Foundry: https://ai.azure.com/ → Build → Assistants
- Or Azure OpenAI Studio: https://oai.azure.com/ → Assistants
- Conversations and traces appear in the Azure AI Foundry portal after agent execution
"""

import os
import json
import httpx
import subprocess
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure AI Foundry Configuration
ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")

# Validate configuration
if not ENDPOINT or not PROJECT_NAME:
    print("=" * 80)
    print("❌ ERROR: Missing Azure AI Foundry configuration!")
    print("=" * 80)
    print("\n📋 Setup Instructions:")
    print("1. Copy .env.example to .env")
    print("2. Fill in AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_PROJECT_NAME")
    print("3. Run 'az login' to authenticate")
    print("4. Run this script again\n")
    exit(1)


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

MEDICAL_AFFAIRS_AGENTS = [
    {
        "name": "Literature Scout Agent",
        "description": "Searches PubMed, clinical trials, and product labeling for evidence-based medical information. Ranks evidence by quality and recency.",
        "model": "gpt-4.1",
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
        "model": "gpt-4.1",
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
        "model": "gpt-4.1",
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
    },
    {
        "name": "GRADE Evidence Assessment Agent",
        "description": "Official GRADE (Grading of Recommendations Assessment, Development and Evaluations) methodology for systematic evidence quality assessment. Assigns quality levels: HIGH ⊕⊕⊕⊕, MODERATE ⊕⊕⊕○, LOW ⊕⊕○○, VERY_LOW ⊕○○○",
        "model": "gpt-4.1",
        "instructions": """You are a GRADE Evidence Assessment Agent implementing the official GRADE Working Group methodology.

Your role:
- Assess evidence quality using GRADE methodology
- Evaluate 5 downgrade factors: risk of bias, inconsistency, indirectness, imprecision, publication bias
- Evaluate 3 upgrade factors: large effect, dose-response, confounding reduction
- Assign quality levels: HIGH, MODERATE, LOW, or VERY_LOW
- Generate certainty ratings and recommendation strength
- Provide detailed rationale for all quality adjustments

GRADE quality levels:
⊕⊕⊕⊕ HIGH: Very confident that true effect lies close to estimate
⊕⊕⊕○ MODERATE: Moderately confident; true effect likely close to estimate
⊕⊕○○ LOW: Limited confidence; true effect may differ substantially
⊕○○○ VERY_LOW: Very little confidence in effect estimate

Starting points:
- Randomized controlled trials (RCTs): Start at HIGH
- Observational studies: Start at LOW
- Case series/reports: Start at VERY_LOW

You must explain all quality adjustments and provide evidence-based rationale.""",
        "tools": ["code_interpreter"],
        "capabilities": ["grade_assessment", "evidence_quality_rating", "systematic_review", "recommendation_strength"]
    }
]


# ============================================================================
# AZURE AI FOUNDRY API CLIENT
# ============================================================================

class AzureAIFoundryClient:
    """
    REST API client for Azure AI Foundry Agent Service.
    
    This client registers externally-built agents (using Semantic Kernel with a 
    Foundry-hosted model) into an Azure AI Foundry project.
    
    Registration process:
    1. Connect to your Foundry project's endpoint with proper credentials
    2. Call the Agent Service API (/api/projects/{project}/assistants) to create a new agent
    3. Associate agent with your deployed model (e.g., gpt-4.1)
    4. Agent and its conversations can then be monitored and traced in Azure AI Foundry portal
    
    Monitoring & Tracing:
    - View registered agents: https://ai.azure.com/ → Build → Agents
    - Track conversations: Agent execution traces appear in portal after running
    - Access metrics: Performance and usage data available in Azure Monitor
    """
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")
        # GA API version for Azure AI Foundry Agent Service
        self.api_version = "2025-05-01"
        # Get Entra ID token for authentication
        self.token = self._get_entra_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _get_entra_token(self) -> str:
        """Get Entra ID access token using Azure CLI."""
        try:
            result = subprocess.run(
                ["az", "account", "get-access-token", "--resource", "https://ai.azure.com"],
                capture_output=True,
                text=True,
                check=True,
                shell=True  # Use shell to find az command in PATH
            )
            token_data = json.loads(result.stdout)
            return token_data["accessToken"]
        except subprocess.CalledProcessError as e:
            print("\n❌ Failed to get Entra ID token!")
            print("Please run 'az login' first to authenticate.\n")
            raise
        except Exception as e:
            print(f"\n❌ Error getting token: {e}")
            print("Make sure Azure CLI is installed and you're logged in.\n")
            raise
    
    def create_agent(self, agent_config: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        """Create an agent in Azure AI Foundry Agent Service."""
        # Use the Azure AI Foundry Agent Service endpoint
        url = f"{self.endpoint}/api/projects/{project_name}/assistants?api-version={self.api_version}"
        
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
    
    def list_agents(self, project_name: str) -> List[Dict[str, Any]]:
        """List all agents in the project."""
        url = f"{self.endpoint}/api/projects/{project_name}/assistants?api-version={self.api_version}"
        
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
    print(f"� Auth: Entra ID (Azure CLI)\n")
    
    # Initialize client (will get Entra ID token)
    try:
        client = AzureAIFoundryClient(ENDPOINT)
        print("✅ Successfully authenticated with Entra ID\n")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # Check existing agents
    print("🔍 Checking existing agents...")
    try:
        existing_agents = client.list_agents(PROJECT_NAME)
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
            result = client.create_agent(agent_config, PROJECT_NAME)
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
