# Microsoft Agent Framework Implementation

> Medical Affairs Multi-Agent System using **Microsoft Agent Framework** + **A2A SDK**

This folder contains the **recommended** implementation using Microsoft's modern Agent Framework with native async support and enhanced A2A protocol integration.

---

## 🎯 Why Agent Framework?

The Microsoft Agent Framework represents the **next generation** of agent orchestration with:

- ✅ **Native Async/Await** - Full Python async support for scalable agent execution
- ✅ **Simplified Agent Creation** - `create_agent(name, instructions)` vs. complex Kernel setup
- ✅ **Modern A2A Integration** - Built-in `A2AClient` with Pydantic models
- ✅ **Cleaner API** - `await agent.run(prompt)` returns structured `AgentRunResponse`
- ✅ **Enhanced Observability** - Better logging, tracing, and debugging

---

## 📦 Installation

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

**Key Packages:**
- `agent-framework>=1.0.0` - Core agent orchestration
- `agent-framework-azure-ai` - Azure OpenAI integration
- `agent-framework-a2a` - A2A protocol support
- `a2a-sdk[http-server]` - Agent server implementation
- `streamlit>=1.28.0` - Web UI framework
- `fastapi` - Agent server infrastructure

### 2. Configure Azure OpenAI

```powershell
# Set environment variables (PowerShell)
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key-here'
$env:AZURE_OPENAI_DEPLOYMENT_NAME='gpt-4'
$env:AZURE_OPENAI_API_VERSION='2025-01-01-preview'
```

**Security Note:** Never hardcode API keys! Always use environment variables or Azure Key Vault.

---

## 🚀 Quick Start

### Option 1: Jupyter Notebook (Recommended for Learning)

```powershell
jupyter notebook life_sciences_agent_demo.ipynb
```

**Notebook Contents:**
1. Install packages and configure Azure OpenAI
2. Start Literature Scout Agent (A2A server on port 9099)
3. Create MI Agent and Compliance Guard
4. Run full Medical Affairs workflow
5. Test compliance scenarios
6. Generate PDF responses

### Option 2: Streamlit Web UI (Recommended for Demos)

```powershell
streamlit run medical_affairs_app.py
```

**Access:** http://localhost:8501

**Features:**
- 📝 **Single Query** - Quick literature lookup
- 📚 **Literature Scout Only** - Research mode
- 🔄 **Full MI Workflow** - Complete orchestration
- ⚠️ **Compliance Validation** - Test regulatory risk

### Option 3: PowerShell Launcher

```powershell
.\launch_streamlit.ps1
```

Automatically sets environment variables and launches Streamlit.

---

## 🏗️ Architecture

### Agent Framework Key Concepts

```python
# 1. Create Azure OpenAI Chat Client
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity.aio import AzureCliCredential

chat_client = AzureOpenAIChatClient(
    credential=AzureCliCredential(),
    endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=AZURE_OPENAI_DEPLOYMENT_NAME
)

# 2. Create Agent with Instructions
mi_agent = chat_client.create_agent(
    name="MedicalInformationAgent",
    instructions="You are a Medical Information agent specialized in..."
)

# 3. Run Agent with Prompt
result = await mi_agent.run(
    "What's the renal dosing for Drug X in severe CKD?"
)

# 4. Access Response Text
response_text = result.text
```

### A2A Protocol Integration

```python
# 1. Create A2A Client
from a2a.client import A2AClient
from a2a.utils import new_agent_text_message
from a2a.types import SendMessageRequest, MessageSendParams

async with httpx.AsyncClient() as client:
    a2a_client = A2AClient(httpx_client=client, url="http://localhost:9099")
    
    # 2. Create Message
    message = new_agent_text_message("Search PubMed for Drug X dosing")
    message.message_id = uuid4().hex
    
    # 3. Send Request
    request = SendMessageRequest(
        id=str(uuid4()),
        params=MessageSendParams(message=message)
    )
    
    response = await a2a_client.send_message(request)
    
    # 4. Extract Result
    text = response.root.result.parts[0].root.text
```

### Multi-Agent Workflow

```
┌────────────────────────────────────────────────────────┐
│  Literature Scout Agent (A2A Server)                   │
│  • FastAPI server on port 9099                         │
│  • Publishes AgentCard with skills                     │
│  • Processes queries via A2A protocol                  │
└──────────────────┬─────────────────────────────────────┘
                   │ A2A Protocol (SendMessageRequest)
                   ▼
┌────────────────────────────────────────────────────────┐
│  MI Agent (Orchestrator)                               │
│  • Calls Literature Scout via A2A                      │
│  • Formats fair-balanced response                      │
│  • Returns structured MI letter                        │
└──────────────────┬─────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│  Compliance Guard Agent (Validator)                    │
│  • Analyzes response for regulatory risk               │
│  • Returns JSON: {risk_level, flags, recommendations}  │
│  • Routes high-risk to human review                    │
└────────────────────────────────────────────────────────┘
```

---

## 📝 Core Files

| File | Purpose | Entry Point |
|------|---------|-------------|
| `medical_affairs_app.py` | Streamlit web UI with 4 tabs | `streamlit run medical_affairs_app.py` |
| `life_sciences_agent_demo.ipynb` | Jupyter notebook walkthrough | `jupyter notebook` |
| `grade_evidence_agent.py` | GRADE evidence assessment module | Imported by other scripts |
| `launch_streamlit.ps1` | PowerShell launcher script | `.\launch_streamlit.ps1` |
| `requirements.txt` | Python dependencies | `pip install -r requirements.txt` |
| `azure_agent_registration.json` | Azure AI Foundry configuration | Used by Azure deployment |

---

## 🧪 Testing

### Test Compliance Scenarios

Run the notebook cell "5b) Compliance Scenarios" to test:

- **LOW RISK** - On-label guidance from FDA labeling
- **MEDIUM RISK** - Off-label efficacy claims
- **HIGH RISK** - Pediatric use without approval

### Test Literature Scout

```python
# In notebook or Streamlit
query = "What are the contraindications for Drug X in hepatic impairment?"
evidence = await call_literature_scout(query)
print(evidence)
```

Expected output:
```
**APPROVED LABELING:**
Source: Drug X Prescribing Information...

**PUBLISHED LITERATURE:**
1. Smith et al. (2024). Hepatic safety of Drug X...
2. Jones et al. (2023). Pharmacokinetics in liver impairment...

**EVIDENCE QUALITY:** Moderate (observational studies + labeling)
```

---

## 🔄 Migration from Semantic Kernel

If you're migrating from the Semantic Kernel implementation:

| Semantic Kernel | Agent Framework |
|----------------|-----------------|
| `Kernel()` | `AzureOpenAIChatClient()` |
| `kernel.add_service(AzureChatCompletion(...))` | `create_agent(name, instructions)` |
| `kernel.invoke_prompt(prompt)` | `await agent.run(prompt)` |
| `result.value` | `result.text` |
| Custom A2A setup | Native `A2AClient` |

**Key Differences:**
1. **Agent-centric** vs. Kernel-centric design
2. **Native async** vs. partial async support
3. **Structured responses** vs. string parsing
4. **Simpler API** with less boilerplate

---

## 📊 Performance

**Typical Execution Times:**

| Operation | Time | Notes |
|-----------|------|-------|
| Literature Scout query | 3-8 sec | GPT-4 processing + evidence formatting |
| MI response generation | 5-12 sec | Depends on evidence complexity |
| Compliance validation | 2-5 sec | JSON parsing + risk assessment |
| **Full workflow (end-to-end)** | **15-30 sec** | Sub-minute response time |

**Optimization Tips:**
- Use `gpt-4-turbo` or `gpt-4o` for faster responses
- Cache frequently requested evidence
- Implement async parallel execution for compliance checks

---

## 🐛 Troubleshooting

### Error: "Module not found: agent_framework"

```powershell
pip install -U agent-framework agent-framework-azure-ai agent-framework-a2a
```

### Error: "Could not authenticate with Azure CLI"

```powershell
# Login to Azure CLI
az login

# Or use API key authentication instead
# See: medical_affairs_app.py line 198-205
```

### A2A Server Not Starting

```python
# Check if port 9099 is already in use
netstat -an | findstr "9099"

# Kill existing process or change port
os.environ['A2A_PORT'] = '9100'
```

### Streamlit "Address already in use"

```powershell
# Kill existing Streamlit process
Get-Process streamlit | Stop-Process

# Or run on different port
streamlit run medical_affairs_app.py --server.port 8502
```

---

## 🚀 Next Steps

### Production Readiness

- [ ] **Authentication** - Implement Azure AD/Entra ID for user auth
- [ ] **Rate Limiting** - Add throttling for agent API calls
- [ ] **Error Handling** - Robust retry logic and fallbacks
- [ ] **Monitoring** - Application Insights for observability
- [ ] **Load Testing** - Validate performance under concurrent users

### Integration

- [ ] **Veeva Vault** - Connect to approved labeling repository
- [ ] **PubMed API** - Replace mock data with real literature search
- [ ] **Salesforce/Veeva CRM** - Two-way integration for activity logging
- [ ] **Email Service** - Automated PDF distribution to HCPs
- [ ] **Translation API** - Multi-language MI responses

### Advanced Features

- [ ] **Retrieval-Augmented Generation (RAG)** - Vector search over internal documents
- [ ] **Multi-turn Conversations** - Context-aware follow-up questions
- [ ] **Batch Processing** - Handle multiple inquiries in parallel
- [ ] **Custom GRADE Tables** - Structured evidence visualization
- [ ] **Regulatory Templates** - Country-specific MI letter formats

---

## � Azure AI Foundry Integration

This implementation includes **Azure AI Foundry** integration for enterprise-grade agent management, monitoring, and observability.

### Features

✅ **Agent Registry** - Register all agents in centralized catalog  
✅ **Interaction Tracking** - Monitor every agent call with detailed telemetry  
✅ **Performance Metrics** - Track success rates, latency, and error counts  
✅ **Azure Export** - Export to Azure AI Foundry-compatible format  

### Quick Start

```python
from ai_foundry.ai_foundry_integration import setup_ai_foundry_tracking

# Initialize registry (local demo mode - no Azure required)
registry = setup_ai_foundry_tracking(project_name="medical-affairs-demo")

# Register an agent
agent_id = registry.register_agent(
    agent_name="Literature Scout Agent",
    agent_type="server",
    description="Searches medical literature for evidence",
    capabilities=["pubmed_search", "labeling_retrieval", "evidence_ranking"],
    endpoint="http://localhost:9100",
    tags={"domain": "medical_affairs", "criticality": "high"}
)

# Track interactions
registry.track_interaction(
    agent_id=agent_id,
    input_data={"query": "renal dosing for Drug X"},
    output_data={"evidence_count": 3, "confidence": 0.94},
    duration_ms=125.5,
    status="success"
)

# View metrics
metrics = registry.get_agent_metrics(agent_id)
print(f"Success Rate: {metrics['success_rate']:.1f}%")
```

### Files

- **`ai_foundry/`** - AI Foundry integration module
  - `ai_foundry_integration.py` - Core integration code with local registry and Azure client
  - `AI_FOUNDRY_GUIDE.md` - Comprehensive guide with architecture diagrams and use cases
  - `register_agents_ai_foundry.py` - Script for registering agents
  - `azure_agent_registration.json` - Agent registration metadata
- **`ai_foundry_registry/`** - Local JSON storage (demo mode, gitignored)

### Demo vs Production

**Demo Mode (Default)**  
- ✅ No Azure subscription required  
- ✅ Local JSON file storage  
- ✅ Full tracking capabilities  
- ✅ Azure-compatible export format  

**Production Mode**  
- 🔐 Requires Azure AI Foundry project  
- ☁️ Azure Monitor integration  
- 📊 Real-time dashboards  
- 🔔 Automated alerting  

See **`AI_FOUNDRY_GUIDE.md`** for complete documentation and production setup instructions.

---

## �📚 Additional Resources

- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [A2A Protocol Specification](https://github.com/microsoft/A2A)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 📞 Support

For questions or issues specific to this implementation:

- **Email:** nistewart@microsoft.com
- **LinkedIn:** [linkedin.com/in/nicholas-stewart-phd](https://www.linkedin.com/in/nicholas-stewart-phd/)

---

**Built with Microsoft Agent Framework** 🚀
