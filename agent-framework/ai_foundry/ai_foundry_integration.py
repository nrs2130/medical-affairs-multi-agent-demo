"""
Azure AI Foundry Integration for Medical Affairs Multi-Agent System
====================================================================

This module provides integration with Azure AI Foundry (formerly Azure AI Studio)
for agent registration, tracing, and monitoring.

Features:
- Register agents in AI Foundry agent registry
- Track agent interactions and performance
- Enable observability with Azure Monitor
- Collect metrics and evaluation data
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import uuid


@dataclass
class AgentMetadata:
    """Metadata for an agent registered in AI Foundry"""
    agent_id: str
    agent_name: str
    agent_type: str  # "orchestrator", "server", "validator"
    description: str
    version: str
    capabilities: List[str]
    endpoint: Optional[str] = None
    registered_at: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


@dataclass
class AgentInteraction:
    """Record of an agent interaction for tracking"""
    interaction_id: str
    agent_id: str
    timestamp: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    duration_ms: float
    status: str  # "success", "error", "pending"
    metadata: Optional[Dict[str, Any]] = None


class AIFoundryAgentRegistry:
    """
    Manages agent registration and tracking with Azure AI Foundry.
    
    In a production environment, this would connect to:
    - Azure AI Foundry API for agent registration
    - Azure Monitor for tracing and metrics
    - Azure Application Insights for telemetry
    
    For demo purposes, this maintains a local registry with JSON export.
    """
    
    def __init__(self, 
                 project_name: str = "medical-affairs-agents",
                 registry_path: str = "./ai_foundry_registry"):
        """
        Initialize the AI Foundry agent registry.
        
        Args:
            project_name: Name of the AI Foundry project
            registry_path: Local path for registry storage (demo mode)
        """
        self.project_name = project_name
        self.registry_path = registry_path
        self.agents: Dict[str, AgentMetadata] = {}
        self.interactions: List[AgentInteraction] = []
        
        # Create registry directory
        os.makedirs(registry_path, exist_ok=True)
        
        # Load existing registry if available
        self._load_registry()
    
    def register_agent(self, 
                      agent_name: str,
                      agent_type: str,
                      description: str,
                      capabilities: List[str],
                      version: str = "1.0.0",
                      endpoint: Optional[str] = None,
                      tags: Optional[Dict[str, str]] = None) -> str:
        """
        Register an agent in the AI Foundry registry.
        
        Args:
            agent_name: Unique name for the agent
            agent_type: Type of agent (orchestrator, server, validator)
            description: Description of agent capabilities
            capabilities: List of skills/capabilities
            version: Agent version
            endpoint: API endpoint (for server agents)
            tags: Additional metadata tags
        
        Returns:
            agent_id: Unique identifier for the registered agent
        """
        agent_id = f"agent-{agent_name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}"
        
        agent_metadata = AgentMetadata(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            description=description,
            version=version,
            capabilities=capabilities,
            endpoint=endpoint,
            registered_at=datetime.now().isoformat(),
            tags=tags or {}
        )
        
        self.agents[agent_id] = agent_metadata
        self._save_registry()
        
        print(f"✅ Agent registered in AI Foundry:")
        print(f"   ID: {agent_id}")
        print(f"   Name: {agent_name}")
        print(f"   Type: {agent_type}")
        print(f"   Capabilities: {', '.join(capabilities)}")
        
        return agent_id
    
    def track_interaction(self,
                         agent_id: str,
                         input_data: Dict[str, Any],
                         output_data: Dict[str, Any],
                         duration_ms: float,
                         status: str = "success",
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Track an agent interaction for monitoring and evaluation.
        
        Args:
            agent_id: ID of the agent
            input_data: Input received by the agent
            output_data: Output produced by the agent
            duration_ms: Duration of the interaction in milliseconds
            status: Status of the interaction
            metadata: Additional metadata (e.g., compliance flags, risk level)
        
        Returns:
            interaction_id: Unique identifier for this interaction
        """
        interaction_id = f"int-{uuid.uuid4().hex[:12]}"
        
        interaction = AgentInteraction(
            interaction_id=interaction_id,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            input_data=input_data,
            output_data=output_data,
            duration_ms=duration_ms,
            status=status,
            metadata=metadata or {}
        )
        
        self.interactions.append(interaction)
        self._save_interactions()
        
        return interaction_id
    
    def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific agent.
        
        Args:
            agent_id: ID of the agent
        
        Returns:
            Dictionary with metrics (call count, avg duration, success rate, etc.)
        """
        agent_interactions = [i for i in self.interactions if i.agent_id == agent_id]
        
        if not agent_interactions:
            return {
                "agent_id": agent_id,
                "total_calls": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "error_count": 0
            }
        
        total_calls = len(agent_interactions)
        successful_calls = sum(1 for i in agent_interactions if i.status == "success")
        error_calls = sum(1 for i in agent_interactions if i.status == "error")
        avg_duration = sum(i.duration_ms for i in agent_interactions) / total_calls
        
        return {
            "agent_id": agent_id,
            "agent_name": self.agents[agent_id].agent_name if agent_id in self.agents else "Unknown",
            "total_calls": total_calls,
            "success_rate": (successful_calls / total_calls) * 100,
            "avg_duration_ms": round(avg_duration, 2),
            "error_count": error_calls,
            "last_interaction": agent_interactions[-1].timestamp if agent_interactions else None
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all registered agents."""
        return {
            agent_id: self.get_agent_metrics(agent_id)
            for agent_id in self.agents.keys()
        }
    
    def export_to_foundry_format(self) -> Dict[str, Any]:
        """
        Export registry in Azure AI Foundry compatible format.
        
        This format is compatible with Azure AI Foundry agent registry schema.
        """
        return {
            "project": self.project_name,
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "agents": [asdict(agent) for agent in self.agents.values()],
            "metrics": self.get_all_metrics(),
            "interaction_summary": {
                "total_interactions": len(self.interactions),
                "date_range": {
                    "start": self.interactions[0].timestamp if self.interactions else None,
                    "end": self.interactions[-1].timestamp if self.interactions else None
                }
            }
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents with their metadata."""
        return [
            {
                **asdict(agent),
                **self.get_agent_metrics(agent.agent_id)
            }
            for agent in self.agents.values()
        ]
    
    def _save_registry(self):
        """Save agent registry to local JSON file."""
        registry_file = os.path.join(self.registry_path, "agent_registry.json")
        with open(registry_file, 'w') as f:
            json.dump(
                [asdict(agent) for agent in self.agents.values()],
                f,
                indent=2
            )
    
    def _save_interactions(self):
        """Save interaction history to local JSON file."""
        interactions_file = os.path.join(self.registry_path, "interactions.json")
        with open(interactions_file, 'w') as f:
            json.dump(
                [asdict(interaction) for interaction in self.interactions],
                f,
                indent=2
            )
    
    def _load_registry(self):
        """Load existing registry from local JSON file."""
        registry_file = os.path.join(self.registry_path, "agent_registry.json")
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                agents_data = json.load(f)
                for agent_data in agents_data:
                    agent = AgentMetadata(**agent_data)
                    self.agents[agent.agent_id] = agent
        
        interactions_file = os.path.join(self.registry_path, "interactions.json")
        if os.path.exists(interactions_file):
            with open(interactions_file, 'r') as f:
                interactions_data = json.load(f)
                self.interactions = [
                    AgentInteraction(**interaction_data)
                    for interaction_data in interactions_data
                ]


# Production: Azure AI Foundry Connection
class AzureAIFoundryClient:
    """
    Production client for Azure AI Foundry integration.
    
    This would connect to actual Azure AI Foundry APIs for:
    - Agent registration
    - Telemetry streaming
    - Evaluation metrics
    - Monitoring dashboards
    
    Required environment variables:
    - AZURE_AI_PROJECT_CONNECTION_STRING
    - AZURE_AI_PROJECT_NAME
    """
    
    def __init__(self):
        """Initialize Azure AI Foundry client."""
        self.connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        self.project_name = os.getenv("AZURE_AI_PROJECT_NAME", "medical-affairs-agents")
        
        if not self.connection_string:
            print("⚠️  Azure AI Foundry connection not configured.")
            print("   Set AZURE_AI_PROJECT_CONNECTION_STRING to enable cloud tracking.")
            print("   Using local registry mode instead.")
    
    def register_agent(self, agent_metadata: AgentMetadata) -> str:
        """
        Register agent with Azure AI Foundry.
        
        In production, this would call:
        azure.ai.projects.AgentRegistryClient.register_agent()
        """
        if not self.connection_string:
            raise ValueError("Azure AI Foundry not configured")
        
        # Production implementation would use Azure SDK
        # from azure.ai.projects import AIProjectClient
        # client = AIProjectClient.from_connection_string(self.connection_string)
        # return client.agents.register(agent_metadata)
        
        print("📡 Would register with Azure AI Foundry in production mode")
        return agent_metadata.agent_id
    
    def log_trace(self, agent_id: str, interaction: AgentInteraction):
        """
        Log interaction trace to Azure Monitor.
        
        In production, this would stream to Application Insights.
        """
        if not self.connection_string:
            return
        
        # Production implementation would use Azure Monitor SDK
        # from azure.monitor.opentelemetry import configure_azure_monitor
        # tracer.start_span() and tracer.add_event()
        
        print(f"📊 Would log trace to Azure Monitor: {interaction.interaction_id}")


# Convenience function for quick setup
def setup_ai_foundry_tracking(project_name: str = "medical-affairs-agents") -> AIFoundryAgentRegistry:
    """
    Quick setup for AI Foundry agent tracking.
    
    Returns:
        AIFoundryAgentRegistry instance ready to use
    """
    print("🚀 Initializing AI Foundry Agent Registry")
    print(f"   Project: {project_name}")
    print(f"   Mode: Local Registry (Demo)")
    print()
    
    registry = AIFoundryAgentRegistry(project_name=project_name)
    
    if registry.agents:
        print(f"   Loaded {len(registry.agents)} existing agents")
    if registry.interactions:
        print(f"   Loaded {len(registry.interactions)} interaction records")
    
    print()
    return registry


if __name__ == "__main__":
    # Demo usage
    print("AI Foundry Integration Demo")
    print("=" * 80)
    
    # Setup registry
    registry = setup_ai_foundry_tracking()
    
    # Register Medical Affairs agents
    literature_scout_id = registry.register_agent(
        agent_name="Literature Scout",
        agent_type="server",
        description="Searches medical literature and retrieves evidence",
        capabilities=["pubmed_search", "labeling_retrieval", "evidence_ranking"],
        endpoint="http://localhost:9100",
        tags={"domain": "medical_affairs", "criticality": "high"}
    )
    
    mi_agent_id = registry.register_agent(
        agent_name="MI Response Orchestrator",
        agent_type="orchestrator",
        description="Coordinates multi-agent workflow for medical information responses",
        capabilities=["agent_coordination", "response_generation", "citation_formatting"],
        tags={"domain": "medical_affairs", "criticality": "critical"}
    )
    
    compliance_guard_id = registry.register_agent(
        agent_name="Compliance Guard",
        agent_type="validator",
        description="Validates responses for regulatory compliance",
        capabilities=["off_label_detection", "promotional_risk_assessment", "approval_routing"],
        tags={"domain": "compliance", "criticality": "critical"}
    )
    
    print("\n" + "=" * 80)
    print("📊 REGISTERED AGENTS")
    print("=" * 80)
    for agent in registry.list_agents():
        print(f"\n{agent['agent_name']} ({agent['agent_id']})")
        print(f"  Type: {agent['agent_type']}")
        print(f"  Capabilities: {', '.join(agent['capabilities'])}")
    
    # Simulate some interactions
    print("\n" + "=" * 80)
    print("🔄 SIMULATING AGENT INTERACTIONS")
    print("=" * 80)
    
    registry.track_interaction(
        agent_id=literature_scout_id,
        input_data={"query": "renal dosing for Drug X"},
        output_data={"evidence": "FDA Label + 3 studies", "confidence": 0.95},
        duration_ms=1250.5,
        status="success"
    )
    
    registry.track_interaction(
        agent_id=compliance_guard_id,
        input_data={"response": "Drug X is indicated..."},
        output_data={"risk_level": "LOW", "approved": True},
        duration_ms=450.2,
        status="success",
        metadata={"flags": []}
    )
    
    # Show metrics
    print("\n" + "=" * 80)
    print("📈 AGENT METRICS")
    print("=" * 80)
    metrics = registry.get_all_metrics()
    for agent_id, agent_metrics in metrics.items():
        agent_name = agent_metrics.get('agent_name', registry.agents[agent_id].agent_name if agent_id in registry.agents else 'Unknown')
        print(f"\n{agent_name}:")
        print(f"  Total Calls: {agent_metrics['total_calls']}")
        print(f"  Success Rate: {agent_metrics['success_rate']:.1f}%")
        print(f"  Avg Duration: {agent_metrics['avg_duration_ms']:.2f}ms")
    
    # Export to AI Foundry format
    export_data = registry.export_to_foundry_format()
    export_path = os.path.join(registry.registry_path, "foundry_export.json")
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n✅ Exported to: {export_path}")
    print("   This file can be imported into Azure AI Foundry")
