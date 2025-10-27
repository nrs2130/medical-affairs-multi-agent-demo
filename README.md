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

```powershell
# PowerShell
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key-here'
$env:AZURE_OPENAI_DEPLOYMENT_NAME='gpt-4'
$env:AZURE_OPENAI_API_VERSION='2025-01-01-preview'
```

### 5. Run Demo

**Jupyter Notebook (Recommended):**
```powershell
jupyter notebook life_sciences_agent_demo.ipynb
```

**Streamlit Web UI:**
```powershell
streamlit run medical_affairs_app.py
```

**Access:** http://localhost:8501

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
