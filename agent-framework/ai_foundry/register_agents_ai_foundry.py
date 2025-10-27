"""
Register Medical Affairs Agents with Azure AI Foundry

This script registers the multi-agent Medical Affairs system with Azure AI Foundry,
enabling cloud deployment, monitoring, and management through Azure AI Studio.

Prerequisites:
    - Azure AI Foundry project created
    - Azure OpenAI deployment configured
    - Environment variables set (see .env.example)

Usage:
    python register_agents_ai_foundry.py
"""

import os
import json
from datetime import datetime
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import AgentRole

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Azure AI Foundry Configuration
AI_FOUNDRY_PROJECT_CONNECTION_STRING = os.getenv('AI_FOUNDRY_PROJECT_CONNECTION_STRING')
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')

# Validate configuration
if not AI_FOUNDRY_PROJECT_CONNECTION_STRING:
    print("⚠️  ERROR: AI_FOUNDRY_PROJECT_CONNECTION_STRING not set!")
    print("   Set in your .env file or environment:")
    print("   AI_FOUNDRY_PROJECT_CONNECTION_STRING=<your-project-connection-string>")
    exit(1)


def create_ai_project_client():
    """Create Azure AI Project client with authentication"""
    credential = DefaultAzureCredential()
    client = AIProjectClient.from_connection_string(
        credential=credential,
        conn_str=AI_FOUNDRY_PROJECT_CONNECTION_STRING
    )
    return client


def register_literature_scout_agent(client):
    """Register Literature Scout Agent with Azure AI Foundry"""
    print("\n📚 Registering Literature Scout Agent...")
    
    agent = client.agents.create_agent(
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        name="Literature Scout Agent",
        instructions=(
            "You are LiteratureScoutAgent, a specialized Medical Affairs agent for pharmaceutical companies. "
            "Your role: Search and retrieve relevant scientific literature, product labeling, and clinical evidence. "
            "For any drug-related query, provide:\n"
            "1. Current FDA-approved labeling excerpt (if applicable)\n"
            "2. 2-3 high-quality clinical studies (PubMed-style citations)\n"
            "3. Study quality indicators (RCT, observational, N=, year)\n"
            "4. Key findings relevant to the query\n\n"
            "Format as structured evidence. Be factual and citation-focused. "
            "IMPORTANT: Clearly mark if information is from approved labeling vs. external literature."
        ),
        description="AI agent for pharmaceutical Medical Affairs teams: searches literature, retrieves evidence, and provides structured medical information responses.",
        metadata={
            "category": "medical_affairs",
            "role": "literature_scout",
            "version": "2.0.0",
            "framework": "agent-framework"
        }
    )
    
    print(f"   ✅ Registered: {agent.name}")
    print(f"   Agent ID: {agent.id}")
    print(f"   Created: {agent.created_at}")
    
    return {
        "name": agent.name,
        "id": agent.id,
        "created_at": agent.created_at
    }


def register_mi_orchestrator_agent(client):
    """Register Medical Information Orchestrator Agent with Azure AI Foundry"""
    print("\n📝 Registering MI Orchestrator Agent...")
    
    agent = client.agents.create_agent(
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        name="MI Orchestrator Agent",
        instructions=(
            "You are MedicalInformationAgent, the orchestrator for Medical Affairs workflows. "
            "Create compliant, fair-balanced responses to HCP inquiries. "
            "Your responsibilities:\n"
            "1. Lead with approved labeling guidance\n"
            "2. Support with clinical evidence (properly cited)\n"
            "3. Include safety considerations\n"
            "4. Maintain fair balance (efficacy + safety proportional)\n"
            "5. Use professional, non-promotional tone\n\n"
            "Format responses as Medical Information letters suitable for HCP distribution."
        ),
        description="Orchestrates Medical Information response workflow: calls Literature Scout, formats fair-balanced responses, coordinates compliance validation.",
        metadata={
            "category": "medical_affairs",
            "role": "mi_orchestrator",
            "version": "2.0.0",
            "framework": "agent-framework"
        }
    )
    
    print(f"   ✅ Registered: {agent.name}")
    print(f"   Agent ID: {agent.id}")
    print(f"   Created: {agent.created_at}")
    
    return {
        "name": agent.name,
        "id": agent.id,
        "created_at": agent.created_at
    }


def register_compliance_guard_agent(client):
    """Register Compliance Guard Agent with Azure AI Foundry"""
    print("\n🛡️  Registering Compliance Guard Agent...")
    
    agent = client.agents.create_agent(
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        name="Compliance Guard Agent",
        instructions=(
            "You are ComplianceGuardAgent for pharmaceutical Medical Affairs. "
            "Analyze Medical Information responses for regulatory compliance issues:\n"
            "1. **Off-label content** - Uses not in approved labeling\n"
            "2. **Promotional language** - Overstates benefits, minimizes risks\n"
            "3. **Missing fair balance** - Safety not proportional to efficacy\n"
            "4. **Citation issues** - Claims without proper references\n\n"
            "Return JSON with:\n"
            "{\n"
            '  "risk_level": "LOW|MEDIUM|HIGH",\n'
            '  "flags": ["list of specific issues"],\n'
            '  "requires_medical_review": true/false,\n'
            '  "recommendations": ["suggested edits"]\n'
            "}"
        ),
        description="Validates Medical Information responses for regulatory compliance, flags off-label content and promotional language, routes high-risk responses to medical review.",
        metadata={
            "category": "medical_affairs",
            "role": "compliance_guard",
            "version": "2.0.0",
            "framework": "agent-framework"
        }
    )
    
    print(f"   ✅ Registered: {agent.name}")
    print(f"   Agent ID: {agent.id}")
    print(f"   Created: {agent.created_at}")
    
    return {
        "name": agent.name,
        "id": agent.id,
        "created_at": agent.created_at
    }


def register_grade_evidence_agent(client):
    """Register GRADE Evidence Assessment Agent with Azure AI Foundry"""
    print("\n📊 Registering GRADE Evidence Assessment Agent...")
    
    agent = client.agents.create_agent(
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        name="GRADE Evidence Assessment Agent",
        instructions=(
            "You are GRADEEvidenceAgent, specializing in evidence quality assessment for medical literature. "
            "Apply GRADE methodology (Grading of Recommendations Assessment, Development and Evaluation):\n\n"
            "**Evidence Quality Levels:**\n"
            "- **High**: RCTs with low risk of bias, consistent results, direct evidence\n"
            "- **Moderate**: RCTs with limitations OR strong observational studies\n"
            "- **Low**: Observational studies with limitations\n"
            "- **Very Low**: Case series, expert opinion, high bias\n\n"
            "For each study, assess:\n"
            "1. Study design (RCT, observational, case series)\n"
            "2. Risk of bias (low, moderate, high)\n"
            "3. Consistency across studies\n"
            "4. Directness of evidence\n"
            "5. Sample size and precision\n\n"
            "Return structured GRADE assessment with evidence quality rating and justification."
        ),
        description="Evaluates clinical evidence quality using GRADE methodology, assigns evidence grades, and provides structured evidence tables for Medical Affairs teams.",
        metadata={
            "category": "medical_affairs",
            "role": "evidence_grading",
            "version": "2.0.0",
            "framework": "agent-framework"
        }
    )
    
    print(f"   ✅ Registered: {agent.name}")
    print(f"   Agent ID: {agent.id}")
    print(f"   Created: {agent.created_at}")
    
    return {
        "name": agent.name,
        "id": agent.id,
        "created_at": agent.created_at
    }


def save_registration_metadata(agents, client_info):
    """Save agent registration metadata to JSON file"""
    metadata = {
        "registered_at": datetime.now().isoformat(),
        "endpoint": client_info.get("endpoint", ""),
        "project": client_info.get("project", ""),
        "agents": agents
    }
    
    filename = "azure_agent_registration.json"
    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n💾 Registration metadata saved to: {filename}")
    return filename


def main():
    """Main registration workflow"""
    print("="*80)
    print("🏥 MEDICAL AFFAIRS AGENT REGISTRATION - AZURE AI FOUNDRY")
    print("="*80)
    
    try:
        # Create AI Project client
        print("\n🔐 Authenticating with Azure AI Foundry...")
        client = create_ai_project_client()
        print("   ✅ Connected to Azure AI Foundry")
        
        # Get project info
        project_info = {
            "endpoint": client._config.endpoint if hasattr(client._config, 'endpoint') else "",
            "project": AI_FOUNDRY_PROJECT_CONNECTION_STRING.split(';')[0].split('=')[1] if ';' in AI_FOUNDRY_PROJECT_CONNECTION_STRING else ""
        }
        
        # Register all agents
        agents = []
        agents.append(register_literature_scout_agent(client))
        agents.append(register_mi_orchestrator_agent(client))
        agents.append(register_compliance_guard_agent(client))
        agents.append(register_grade_evidence_agent(client))
        
        # Save metadata
        save_registration_metadata(agents, project_info)
        
        # Summary
        print("\n" + "="*80)
        print("✅ REGISTRATION COMPLETE")
        print("="*80)
        print(f"Total agents registered: {len(agents)}")
        print("\n📍 Next Steps:")
        print("   1. View agents in Azure AI Studio: https://ai.azure.com")
        print("   2. Test agents using list_agents_ai_foundry.py")
        print("   3. Deploy agents to Azure Container Apps (optional)")
        print("   4. Configure monitoring with Application Insights")
        print("\n⚠️  Important:")
        print("   - Agent IDs saved to azure_agent_registration.json")
        print("   - Use these IDs to invoke agents from your applications")
        print("   - Agents use the Azure OpenAI deployment specified in .env")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("   1. Verify AI_FOUNDRY_PROJECT_CONNECTION_STRING in .env")
        print("   2. Ensure Azure CLI is authenticated: az login")
        print("   3. Check Azure AI Foundry project exists and is accessible")
        print("   4. Verify Azure OpenAI deployment name is correct")
        raise


if __name__ == "__main__":
    main()
