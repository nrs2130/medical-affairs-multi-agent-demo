# Azure AI Foundry Integration Guide
## Medical Affairs Multi-Agent System

---

## 🎯 Overview

The Medical Affairs system now includes **Azure AI Foundry integration** for enterprise-grade agent management, monitoring, and observability.

### What is Azure AI Foundry?

Azure AI Foundry (formerly Azure AI Studio) is Microsoft's platform for:
- **Agent Registry**: Centralized catalog of AI agents
- **Observability**: Real-time monitoring with Azure Monitor
- **Evaluation**: Quality metrics and performance tracking
- **Governance**: Compliance, versioning, and lifecycle management

---

## ✨ Features Added

### 1. **Agent Registry**
Register all Medical Affairs agents in a centralized catalog:

```python
from ai_foundry_integration import setup_ai_foundry_tracking

registry = setup_ai_foundry_tracking(project_name="medical-affairs-demo")

# Register Literature Scout Agent
agent_id = registry.register_agent(
    agent_name="Literature Scout Agent",
    agent_type="server",
    description="Searches medical literature for evidence",
    capabilities=["pubmed_search", "labeling_retrieval", "evidence_ranking"],
    endpoint="http://localhost:9100",
    tags={"domain": "medical_affairs", "criticality": "high"}
)
```

### 2. **Interaction Tracking**
Track every agent call with detailed telemetry:

```python
registry.track_interaction(
    agent_id=agent_id,
    input_data={"query": "renal dosing for Drug X"},
    output_data={"evidence_count": 3, "confidence": 0.94},
    duration_ms=125.5,
    status="success",
    metadata={"evidence_quality": "high"}
)
```

### 3. **Performance Metrics**
Get real-time metrics for each agent:

```python
metrics = registry.get_agent_metrics(agent_id)
# Returns: {
#   "total_calls": 42,
#   "success_rate": 97.6,
#   "avg_duration_ms": 132.4,
#   "error_count": 1,
#   "last_interaction": "2025-10-24T16:30:00"
# }
```

### 4. **Azure AI Foundry Export**
Export data in Azure AI Foundry-compatible format:

```python
export_data = registry.export_to_foundry_format()
# Creates: ./ai_foundry_registry/foundry_export.json
```

---

## 📊 Tracked Agents

The system automatically registers these agents:

| Agent Name | Type | Capabilities |
|------------|------|--------------|
| **Literature Scout** | Server | PubMed search, labeling retrieval, evidence ranking |
| **MI Response Orchestrator** | Orchestrator | Workflow coordination, response generation |
| **Compliance Guard** | Validator | Off-label detection, risk assessment, approval routing |

---

## 🚀 Quick Start

### Demo Mode (No Azure Required)

1. **Run the notebook cells in Section 7b**:
   - Initializes local registry
   - Registers all agents
   - Tracks simulated interactions
   - Exports metrics

2. **View local registry**:
   ```powershell
   cat ./ai_foundry_registry/agent_registry.json
   cat ./ai_foundry_registry/interactions.json
   cat ./ai_foundry_registry/foundry_export.json
   ```

3. **Benefits**:
   - ✅ No Azure subscription needed
   - ✅ Full tracking capabilities
   - ✅ JSON export for portability
   - ✅ Same API as production mode

### Production Mode (Azure AI Foundry)

1. **Install Azure packages**:
   ```bash
   pip install azure-ai-projects azure-identity azure-monitor-opentelemetry
   ```

2. **Set environment variables**:
   ```powershell
   $env:AZURE_AI_PROJECT_CONNECTION_STRING="<your-connection-string>"
   $env:AZURE_AI_PROJECT_NAME="medical-affairs-agents"
   ```

3. **Update code** to use `AzureAIFoundryClient`:
   ```python
   from ai_foundry_integration import AzureAIFoundryClient
   client = AzureAIFoundryClient()
   ```

4. **View in Azure Portal**:
   - Navigate to Azure AI Foundry
   - Go to "Agents" → "Registry"
   - View dashboards and metrics

---

## 📈 What Gets Tracked

### Agent Metadata
- Unique agent ID
- Name, type, version
- Capabilities and skills
- Endpoint URL (for server agents)
- Registration timestamp
- Custom tags

### Interaction Data
- Input and output payloads
- Execution duration
- Success/error status
- Timestamp
- Custom metadata (e.g., compliance flags, risk level)

### Performance Metrics
- Total call count
- Success rate percentage
- Average latency (ms)
- Error count
- Last interaction timestamp

---

## 🔍 Use Cases

### 1. **Compliance Audits**
Track every agent interaction for regulatory inspections:
- Complete audit trail of all HCP inquiries
- Evidence of automated compliance checks
- Timestamped approval workflows

### 2. **Performance Monitoring**
Identify bottlenecks and optimize agents:
- Which agent is slowest?
- What's the error rate?
- When did performance degrade?

### 3. **Quality Evaluation**
Measure agent effectiveness over time:
- Compliance flag accuracy
- Response quality scores
- Human review frequency

### 4. **Cost Tracking**
Monitor LLM usage per agent:
- Token consumption
- API call costs
- ROI analysis

### 5. **A/B Testing**
Compare agent versions:
- Register v1.0 and v2.0
- Track performance differences
- Deploy the winner

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Medical Affairs Agents                     │
│  (Literature Scout, MI Orchestrator, Compliance Guard)      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ track_interaction()
                         ▼
         ┌───────────────────────────────────────┐
         │   AI Foundry Agent Registry           │
         │   • Register agents                   │
         │   • Track interactions                │
         │   • Calculate metrics                 │
         └───────────────┬───────────────────────┘
                         │
        ┌────────────────┴─────────────────┐
        │                                  │
        ▼ Demo Mode                        ▼ Production Mode
┌───────────────────┐           ┌──────────────────────────┐
│  Local JSON Files │           │  Azure AI Foundry        │
│  • agent_registry │           │  • Agent Registry API    │
│  • interactions   │           │  • Azure Monitor         │
│  • metrics        │           │  • App Insights          │
└───────────────────┘           │  • Evaluation Framework  │
                                └──────────────────────────┘
```

---

## 📝 Files Created

### `ai_foundry_integration.py`
Complete integration module with:
- `AIFoundryAgentRegistry`: Local registry (demo mode)
- `AzureAIFoundryClient`: Production Azure connection
- `AgentMetadata`: Agent registration schema
- `AgentInteraction`: Interaction tracking schema
- Helper functions for setup and export

### Registry Data (Local)
- `./ai_foundry_registry/agent_registry.json`: Agent metadata
- `./ai_foundry_registry/interactions.json`: Interaction history
- `./ai_foundry_registry/foundry_export.json`: Azure-compatible export

### Notebook Additions
**Section 7b: Azure AI Foundry Integration**
- Cell 1: Introduction and benefits
- Cell 2: Register all agents
- Cell 3: Track interactions and show metrics
- Cell 4: Export to Azure AI Foundry format

---

## 💡 Benefits

### For Developers
- ✅ Standardized agent tracking API
- ✅ Local development without Azure
- ✅ Easy migration to production
- ✅ Comprehensive debugging data

### For Operations
- ✅ Real-time monitoring dashboards
- ✅ Automated alerting on errors
- ✅ Performance trending over time
- ✅ Cost attribution per agent

### For Compliance
- ✅ Complete audit trail
- ✅ Regulatory-ready exports
- ✅ Timestamp verification
- ✅ Immutable interaction logs

### For Leadership
- ✅ Agent ROI measurement
- ✅ Quality metrics tracking
- ✅ Resource allocation insights
- ✅ Strategic planning data

---

## 🔐 Security & Privacy

### Data Storage
- **Demo Mode**: Local JSON files (gitignored)
- **Production**: Azure storage with encryption at rest
- **No PHI**: Only metadata and aggregated metrics

### Access Control
- **Demo Mode**: File system permissions
- **Production**: Azure AD authentication + RBAC
- **Audit Logs**: All access tracked in Azure Monitor

---

## 📚 Next Steps

### Immediate
1. ✅ Run Section 7b in the notebook
2. ✅ Review generated JSON files
3. ✅ Explore metrics and dashboards

### Production Deployment
1. Create Azure AI Foundry project
2. Get connection string from Azure portal
3. Install Azure packages
4. Update environment variables
5. Test agent registration
6. Enable Azure Monitor dashboards
7. Set up alerting rules

### Advanced
1. Implement custom evaluation metrics
2. Add LLM token cost tracking
3. Create executive dashboards
4. Set up automated reports
5. Integrate with CI/CD pipelines

---

## 🎓 Learn More

- **Azure AI Foundry Docs**: https://learn.microsoft.com/azure/ai-studio/
- **Agent Registry**: https://learn.microsoft.com/azure/ai-studio/how-to/agents
- **Azure Monitor**: https://learn.microsoft.com/azure/azure-monitor/
- **Microsoft Agent Framework**: https://learn.microsoft.com/azure/ai-services/agents/

---

## ✅ Summary

You now have:
- ✅ **Local agent registry** for demos (no Azure required)
- ✅ **Production-ready integration** with Azure AI Foundry
- ✅ **Complete tracking** of all agent interactions
- ✅ **Performance metrics** for optimization
- ✅ **Export capability** to Azure AI Foundry format
- ✅ **Notebook examples** in Section 7b
- ✅ **Documentation** in README.md

The system can track your Medical Affairs agents locally during development, then seamlessly migrate to Azure AI Foundry for production monitoring! 🚀
