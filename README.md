# 🏥 Medical Affairs Multi-Agent System

> **AI-powered Medical Information response system for pharmaceutical Medical Affairs teams**  
> Demonstrates compliant, evidence-based HCP inquiry responses using multi-agent orchestration with A2A Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Microsoft Agent Framework](https://img.shields.io/badge/Microsoft-Agent%20Framework-0078D4)](https://github.com/microsoft/agent-framework)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Use Case](#use-case)
- [Architecture](#architecture)
- [Framework Implementations](#framework-implementations)
- [Quick Start](#quick-start)
- [Key Features](#key-features)
- [Demo Scenarios](#demo-scenarios)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

This repository demonstrates a **production-ready multi-agent system** designed for pharmaceutical Medical Affairs teams to handle Healthcare Practitioner (HCP) inquiries with:

- ✅ **Regulatory Compliance** - Automated guardrails for FDA/EMA compliance
- 📚 **Evidence-Based Responses** - Grounded in approved labeling + peer-reviewed literature
- 🤖 **Multi-Agent Orchestration** - Specialized agents for search, synthesis, and compliance
- 🔍 **Full Audit Trail** - Complete logging for regulatory inspections (21 CFR Part 11)
- ⚡ **Real-Time Processing** - Sub-minute response times vs. hours/days for manual MI requests

### Why This Matters for Life Sciences

Medical Affairs teams receive hundreds of inquiries monthly from HCPs about product usage, dosing, safety, and efficacy. Each response requires:

1. **Literature search** across PubMed, clinical trials registries, and internal documents
2. **Evidence synthesis** with proper citation and quality grading (GRADE methodology)
3. **Compliance review** to prevent off-label promotion and regulatory violations
4. **Medical review** by qualified personnel before distribution
5. **Audit logging** for regulatory inspections

**Manual process:** 2-5 days per inquiry  
**AI-powered process:** < 5 minutes with human-in-the-loop for high-risk responses

---

## 💼 Use Case

### Scenario: HCP Renal Dosing Inquiry

**Query from Field Team:**  
> *"What's the renal dosing guidance for Drug X in severe CKD (eGFR <30)? HCP needs answer for patient consult."*

### Multi-Agent Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│  📥 HCP INQUIRY                                                 │
│  "Renal dosing for Drug X in severe CKD?"                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  🤖 LITERATURE SCOUT AGENT (A2A Server)                         │
│  • Searches PubMed, ClinicalTrials.gov, FDA labeling            │
│  • Retrieves 3-5 highest quality studies                        │
│  • Returns structured evidence with citations                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  📊 EVIDENCE SYNTHESIZER (Optional)                             │
│  • Creates structured evidence tables                           │
│  • Grades evidence strength (GRADE methodology)                 │
│  • Synthesizes findings across studies                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  ✍️  MEDICAL INFORMATION AGENT                                  │
│  • Formats fair-balanced response                               │
│  • Leads with approved labeling                                 │
│  • Supports with clinical evidence (cited)                      │
│  • Includes safety considerations                               │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  🛡️  COMPLIANCE GUARD AGENT                                     │
│  • Flags off-label content                                      │
│  • Detects promotional language                                 │
│  • Assesses regulatory risk (LOW/MEDIUM/HIGH)                   │
│  • Routes high-risk to medical review                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ├─── LOW RISK ─────────┐
                  │                       │
                  ▼                       ▼
       ┌────────────────────┐  ┌─────────────────────┐
       │  📄 AUTO-APPROVE   │  │  ⚠️  MEDICAL REVIEW │
       │  • Generate PDF    │  │  • Director approval │
       │  • Log to CRM      │  │  • Edit if needed    │
       │  • Distribute      │  │  • Re-run workflow   │
       └────────┬───────────┘  └──────────┬──────────┘
                │                          │
                └──────────┬───────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  📧 FINAL DELIVERY      │
              │  • PDF to field team    │
              │  • Email to HCP         │
              │  • Archive in Veeva     │
              └─────────────────────────┘
```

**Output:**  
- Professional Medical Information letter (PDF)
- CRM activity log with reference number
- Full audit trail with evidence sources

---

## 🏗️ Architecture

### Multi-Agent Design Principles

1. **Separation of Concerns** - Each agent has a single, well-defined responsibility
2. **A2A Protocol** - Standard agent-to-agent communication (extensible to external agents)
3. **Human-in-the-Loop** - Critical decisions flagged for medical review
4. **Compliance-First** - Automated guardrails at every step
5. **Audit Trail** - Complete logging for regulatory inspections

### Core Agents

| Agent | Role | Technology | Protocol |
|-------|------|------------|----------|
| **Literature Scout** | Evidence retrieval from PubMed, labeling, clinical trials | Azure OpenAI GPT-4 | A2A Server (FastAPI) |
| **Evidence Synthesizer** | GRADE assessment, structured evidence tables | Azure OpenAI GPT-4 | Local Function |
| **MI Response Agent** | Fair-balanced response generation | Azure OpenAI GPT-4 | Orchestrator |
| **Compliance Guard** | Regulatory risk assessment | Azure OpenAI GPT-4 | Validation Agent |

### A2A Protocol

The **Agent-to-Agent (A2A) Protocol** enables standardized communication between agents:

```python
# Literature Scout publishes AgentCard
{
  "name": "Medical Affairs Literature Scout",
  "skills": [
    "Literature Search & Retrieval",
    "Evidence Quality Assessment",
    "Dosing & Safety Guidance"
  ],
  "url": "http://127.0.0.1:9099/",
  "capabilities": {"streaming": true}
}

# MI Agent calls Literature Scout via A2A
request = SendMessageRequest(
    id=uuid4(),
    params=MessageSendParams(
        message=new_agent_text_message("Renal dosing for Drug X?")
    )
)
response = await a2a_client.send_message(request)
```

**Benefits:**
- **Reusability** - Literature Scout can serve multiple downstream agents
- **Extensibility** - Easy to add new agents (translation, PDF generation, etc.)
- **Scalability** - Agents can run on separate infrastructure
- **Interoperability** - Can integrate with external A2A-compliant agents

---

## 🔀 Framework Implementations

This repository includes **two complete implementations** of the same Medical Affairs system using different Microsoft agent frameworks:

### 1️⃣ Semantic Kernel Implementation (`semantic-kernel/`)

**Framework:** [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel)  
**Status:** Legacy (maintained for comparison)

- Uses `Kernel`, `AzureChatCompletion`, `KernelArguments`
- Plugin-based architecture
- Mature, production-tested framework

📁 **See:** [`semantic-kernel/README.md`](semantic-kernel/README.md)

### 2️⃣ Microsoft Agent Framework Implementation (`agent-framework/`)

**Framework:** [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) (NEW)  
**Status:** Recommended for new projects

- Uses `AzureOpenAIChatClient`, `ChatAgent`, `await agent.run()`
- Native async/await support
- Modern agent orchestration patterns
- Enhanced A2A SDK integration

📁 **See:** [`agent-framework/README.md`](agent-framework/README.md)

### Framework Comparison

| Feature | Semantic Kernel | Agent Framework |
|---------|----------------|-----------------|
| **Agent Creation** | `Kernel()` + plugins | `create_agent(name, instructions)` |
| **Execution** | `kernel.invoke_prompt()` | `await agent.run(prompt)` |
| **A2A Integration** | Manual setup | Native `A2AClient` |
| **Async Support** | Partial | Full native async |
| **Maturity** | Production-ready | Emerging (2024+) |
| **Recommendation** | Legacy projects | New projects |

**Migration Guide:** Both implementations are functionally identical. The Agent Framework version demonstrates modern patterns and is recommended for new development.

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+**
- **Azure OpenAI Service** (or OpenAI API key)
- **VS Code** with Python extension (recommended)

### 1. Clone Repository

```powershell
git clone https://github.com/YOUR_USERNAME/medical_affairs_agent_framework.git
cd medical_affairs_agent_framework
```

### 2. Choose Framework Implementation

**Option A: Agent Framework (Recommended)**
```powershell
cd agent-framework
```

**Option B: Semantic Kernel**
```powershell
cd semantic-kernel
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Azure OpenAI

Create a `.env` file in the root directory (copy from `.env.example`):

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# A2A Server Configuration (optional - defaults shown)
A2A_HOST=127.0.0.1
A2A_PORT=9099
```

**PowerShell Alternative** (if not using `.env` file):
```powershell
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key-here'
$env:AZURE_OPENAI_DEPLOYMENT_NAME='gpt-4o'
$env:AZURE_OPENAI_API_VERSION='2025-01-01-preview'
```

### 5. Run Demo

**Option A: Streamlit Web UI (✨ Easiest - Fully Automatic):**
```powershell
streamlit run medical_affairs_app.py
```
- **Access:** http://localhost:8501
- **Auto-Configuration Features:** 
  - ✅ Automatically loads credentials from `.env` file
  - ✅ Automatically starts A2A Literature Scout server on port 9099
  - ✅ No need to run notebook cells first
  - ✅ No need to manually enter credentials in UI
  - ✅ Server status indicator in sidebar
  - ✅ Retry button if server fails to start
  - 🎉 **Just launch and use immediately!**

**Option B: Jupyter Notebook (For development/customization):**
```powershell
jupyter notebook life_sciences_agent_demo.ipynb
```
- **Note:** Run cells 1-9 to manually start A2A server
- **Use case:** When you want to customize agent behavior or prompts
- **Tip:** Streamlit will detect and use an existing notebook-launched server

---

## 🎨 Key Features

### 1. Regulatory Compliance

- **Off-Label Detection** - Flags uses not in approved labeling
- **Promotional Language Guard** - Detects superlative claims, competitive comparisons
- **Fair Balance Enforcement** - Ensures proportional safety/efficacy presentation
- **Citation Validation** - Requires proper references for all claims

### 2. Evidence Grading

Implements **GRADE methodology** (Grading of Recommendations Assessment, Development and Evaluation):

- **High Quality:** RCTs with low risk of bias
- **Moderate Quality:** RCTs with limitations or strong observational studies
- **Low Quality:** Observational studies with limitations
- **Very Low Quality:** Case series, expert opinion

### 3. Multi-Modal Output

- **PDF Generation** - Professional MI letters with company letterhead
- **CRM Integration** - SQLite database with JSON export (Veeva/Salesforce ready)
- **Audit Trail** - Complete evidence chain for regulatory inspections
- **Email Templates** - Ready-to-send HCP communications

### 4. Streamlit Web UI

Interactive web interface for Medical Affairs teams:

- **Single Query** - Quick evidence lookup
- **Literature Scout Only** - Research mode
- **Full MI Workflow** - End-to-end response generation
- **Compliance Validation** - Test responses for regulatory risk

### 5. Azure AI Foundry Tracing & Evaluation

Enterprise-grade observability and quality assessment for production deployments:

#### 📊 Performance Tracing

- **Execution Timelines** - Visualize agent call sequences
- **Token Usage Tracking** - Monitor Azure OpenAI consumption per agent
- **Latency Metrics** - Identify performance bottlenecks
- **Input/Output Capture** - See exact prompts and responses
- **Compliance Audit Trail** - Track what agents said and when

#### 🎯 Quality Evaluation

- **Groundedness** (1-5) - How well grounded in retrieved evidence
- **Relevance** (1-5) - How relevant to the medical query
- **Coherence** (1-5) - Logical flow and consistency
- **Fluency** (1-5) - Language quality and readability
- **Custom Medical Affairs Metrics** - Compliance risk, medical accuracy, citation quality

**Quick Setup:**
```bash
# Add to .env file
AI_FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

**Enable in Code:**
```python
# Tracing
from ai_foundry.ai_foundry_tracing import setup_tracing
setup_tracing()  # Auto-configures from .env

# Evaluation (automatically runs in Full MI Workflow)
from ai_foundry.ai_foundry_evaluation import AIFoundryEvaluation
evaluator = AIFoundryEvaluation()
await evaluator.setup_evaluation()
results = await evaluator.evaluate_response(query, response, context)
```

View traces and evaluation results in [Azure AI Foundry Portal](https://ai.azure.com) → Your Project → **Tracing**

📖 **See:** [Complete Tracing Guide](agent-framework/ai_foundry/TRACING_GUIDE.md)

---

## 📊 Quality Evaluation

### Understanding Evaluation Metrics

The system automatically evaluates every Medical Information response for quality using Azure AI Foundry's evaluation framework. This provides objective, quantifiable metrics alongside the qualitative GRADE evidence assessment and compliance risk score.

### Built-in Evaluators (1-5 Scale)

| Metric | What It Measures | Good Score | Bad Score |
|--------|------------------|------------|-----------|
| **Groundedness** | How well the response is grounded in the retrieved evidence | 4-5: All claims cited | 1-2: Unsupported claims |
| **Relevance** | How relevant the response is to the medical query | 4-5: Directly answers question | 1-2: Off-topic |
| **Coherence** | Logical flow and internal consistency | 4-5: Clear structure | 1-2: Contradictory |
| **Fluency** | Language quality and readability | 4-5: Professional writing | 1-2: Grammatical errors |

### Custom Medical Affairs Evaluators

| Metric | What It Measures | Threshold | Action |
|--------|------------------|-----------|--------|
| **Compliance Risk** | Off-label content, promotional language | HIGH | Route to medical review |
| **Medical Accuracy** | Correct dosing, safety information | LOW | Flag for correction |
| **Citation Quality** | Proper references, peer-reviewed sources | MODERATE | Improve citations |

### How Evaluation Works

```python
# Evaluation runs automatically as Step 5 in Full MI Workflow
results = {
    "evidence": [...],           # Step 1: Literature Scout
    "grade_assessment": {...},   # Step 2: GRADE Evidence Quality
    "response": "...",           # Step 3: MI Response Generation
    "compliance": {...},         # Step 4: Compliance Guard
    "evaluation": {              # Step 5: Quality Evaluation (NEW)
        "groundedness": 4.5,
        "relevance": 5.0,
        "coherence": 4.8,
        "fluency": 4.6,
        "overall_quality": "HIGH"
    }
}
```

### Viewing Evaluation Results

**In Streamlit UI:**
- Run **Full MI Workflow** from the sidebar
- Scroll to **"🎯 AI Quality Evaluation"** section after Unified Assessment
- See color-coded scores: 🟢 Green (4-5) | 🟡 Yellow (3-4) | 🔴 Red (1-3)

**In Azure AI Foundry Portal:**
- Navigate to your project → **Evaluation**
- View batch evaluation results and trends over time
- Compare different prompts or models

### Best Practices

✅ **Monitor Trends** - Track evaluation scores over time to identify improvement opportunities  
✅ **Set Thresholds** - Define minimum acceptable scores (e.g., Groundedness ≥ 4.0)  
✅ **Correlate with Outcomes** - Compare evaluation scores to medical review feedback  
✅ **Batch Evaluate** - Use `evaluate_batch()` to test prompt changes before deployment  

### Troubleshooting

**Q: Evaluation shows "Error: Missing required parameters"**  
**A:** Ensure `AI_FOUNDRY_PROJECT_ENDPOINT` is set in `.env` file

**Q: Evaluation scores seem incorrect**  
**A:** Check that `context` parameter includes actual retrieved evidence, not just query/response

**Q: How do I customize evaluators?**  
**A:** See `ai_foundry_evaluation.py` → `add_medical_affairs_evaluators()` for examples

---

## 🔧 Troubleshooting

### A2A Server Shows "Not Running" (Red Status)

**Symptom:** Streamlit sidebar shows "🔴 A2A Server: Not Running"

**Cause:** Auto-start failed, usually due to missing or incorrect credentials in `.env` file

**Solutions:**

1. **Check `.env` file exists and has correct values:**
   ```powershell
   # Verify .env file exists in root directory
   ls .env
   
   # Check contents
   Get-Content .env
   ```

2. **Click "🔄 Retry Server Start"** button in Streamlit sidebar

3. **Check for port conflicts:**
   ```powershell
   # See if port 9099 is already in use
   Get-NetTCPConnection -LocalPort 9099 -State Listen
   
   # If yes, stop the process
   Get-NetTCPConnection -LocalPort 9099 | Stop-Process
   ```

4. **Manual server start (fallback):**
   ```powershell
   # Open notebook and run cells 1-9
   jupyter notebook agent-framework/life_sciences_agent_demo.ipynb
   ```

### "Auto-configured from .env file" Not Appearing

**Symptom:** Credentials not loading automatically

**Solutions:**

1. **Ensure `.env` file is in the root directory** (not in agent-framework/ subfolder)

2. **Check `.env` file format:**
   ```bash
   # Correct (no spaces around =)
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   ```

3. **Restart Streamlit** (Ctrl+C, then relaunch)

### Azure OpenAI Connection Errors

**Symptom:** "Error: 401 Unauthorized" or "Deployment not found"

**Solutions:**

1. **Verify endpoint URL format:**
   ```bash
   # Correct
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   
   # Incorrect (remove /openai/)
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/ ❌
   ```

2. **Check deployment name matches your Azure resource**

3. **Use API version: 2025-01-01-preview or later**

---

## 🧪 Demo Scenarios

### Scenario 1: Renal Dosing Inquiry
**Query:** "What's the renal dosing guidance for Drug X in severe CKD?"  
**Expected Output:** On-label guidance + clinical PK studies + dose adjustment recommendations

### Scenario 2: Drug-Drug Interaction
**Query:** "Are there any interactions between Drug X and warfarin?"  
**Expected Output:** FDA labeling warnings + clinical interaction studies + monitoring recommendations

### Scenario 3: Off-Label Use (High Risk)
**Query:** "Can Drug X be used in pediatric patients?"  
**Expected Output:** No pediatric indication → HIGH RISK → Route to medical review

### Scenario 4: Adverse Event Inquiry
**Query:** "What were the most common adverse events in pivotal trials?"  
**Expected Output:** FDA labeling AE table + pivotal trial data with incidence rates

---

## 📁 Project Structure

```
medical_affairs_agent_framework/
│
├── README.md                          ← You are here
├── LICENSE
├── .gitignore
├── .env.example                       ← Template for environment variables
│
├── agent-framework/                   ← Microsoft Agent Framework implementation ⭐
│   ├── README.md                      ← Setup instructions
│   ├── requirements.txt               ← Python dependencies
│   ├── medical_affairs_app.py         ← Streamlit web UI
│   ├── life_sciences_agent_demo.ipynb ← Jupyter notebook demo
│   ├── grade_evidence_agent.py        ← GRADE assessment module
│   ├── launch_streamlit.ps1           ← PowerShell launcher
│   ├── azure_agent_registration.json  ← Azure AI Foundry config
│   ├── crm_data/                      ← Generated: SQLite CRM database
│   │   ├── medical_affairs.db
│   │   └── interactions.json
│   └── mi_responses/                  ← Generated: PDF responses
│       └── MI_Response_*.pdf
│
└── semantic-kernel/                   ← Semantic Kernel implementation (legacy)
    ├── README.md                      ← Setup instructions
    ├── requirements.txt               ← Python dependencies
    ├── medical_affairs_app.py         ← Streamlit web UI
    ├── life_sciences_agent_demo.ipynb ← Jupyter notebook demo
    ├── grade_evidence_agent.py        ← GRADE assessment module
    ├── crm_data/                      ← Generated: SQLite CRM database (if run)
    └── mi_responses/                  ← Generated: PDF responses (if run)
```

**Note:** Each framework folder is **self-contained** and runnable independently. The `crm_data/` and `mi_responses/` folders are created at runtime when you run the demos.

---

## 🛠️ Technology Stack

### Core Frameworks

- **Microsoft Agent Framework** - Modern agent orchestration (recommended)
- **Semantic Kernel** - Legacy plugin-based framework (maintained)
- **A2A SDK** - Agent-to-agent protocol implementation
- **FastAPI** - High-performance agent server
- **Streamlit** - Interactive web UI

### AI/ML

- **Azure OpenAI Service** - GPT-4 for evidence synthesis
- **Azure AI Foundry** - Agent management and deployment (optional)
- **LangChain** - Document loading and chunking (optional)

### Data & Storage

- **SQLite** - CRM activity logging
- **ReportLab** - Professional PDF generation
- **httpx** - Async HTTP client for A2A communication

### Development

- **Jupyter** - Interactive notebook development
- **Python 3.10+** - Modern async/await support
- **Pydantic** - Data validation and serialization

---

## 🚀 Deployment

### Local Development
```powershell
streamlit run medical_affairs_app.py
```

### Docker Container (Production)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY agent-framework/requirements.txt .
RUN pip install -r requirements.txt
COPY agent-framework/ .
CMD ["streamlit", "run", "medical_affairs_app.py", "--server.port=8501"]
```

### Azure Deployment Options

1. **Azure Container Apps** - Serverless container deployment
2. **Azure App Service** - Managed web app hosting
3. **Azure AI Foundry** - Full agent lifecycle management
4. **Azure Functions** - Event-driven serverless

**See:** [Deployment Guide](docs/DEPLOYMENT.md) *(coming soon)*

---

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- [ ] Real PubMed API integration (replace mock data)
- [ ] Veeva Vault integration for approved labeling
- [ ] Salesforce/Veeva CRM connectors
- [ ] Multi-language support (translate MI responses)
- [ ] Advanced GRADE evidence tables
- [ ] Unit tests and integration tests
- [ ] CI/CD pipelines

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Contact

**Nicholas Stewart, PhD**  
Senior Data & AI Specialist, Microsoft

- 📧 Email: [nistewart@microsoft.com](mailto:nistewart@microsoft.com)
- 💼 LinkedIn: [linkedin.com/in/nicholas-stewart-phd](https://www.linkedin.com/in/nicholas-stewart-phd/)
- 🐙 GitHub: [@nistewart-msft](https://github.com/nistewart-msft)

### Acknowledgments

- **Microsoft Agent Framework Team** - For the modern agent orchestration framework
- **Microsoft Semantic Kernel Team** - For the foundational plugin architecture
- **A2A Protocol Contributors** - For agent interoperability standards
- **Pharmaceutical Medical Affairs Community** - For domain expertise and feedback

---

## 🔗 Related Resources

- [Microsoft Agent Framework Documentation](https://github.com/microsoft/agent-framework)
- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [A2A Protocol Specification](https://github.com/microsoft/A2A)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [GRADE Evidence Quality](https://www.gradeworkinggroup.org/)
- [FDA Guidance: Medical Information](https://www.fda.gov/regulatory-information/search-fda-guidance-documents)

---

**⚠️ Disclaimer:** This is a demonstration system for educational and prototyping purposes. For production use in pharmaceutical Medical Affairs, consult with regulatory, legal, and compliance teams to ensure adherence to all applicable regulations (FDA, EMA, etc.). Always implement human review for medical information responses.

---

**Built with ❤️ by Microsoft Data & AI Specialists**
