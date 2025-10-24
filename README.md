# Medical Affairs Evidence Synthesis & Response System

A production-ready multi-agent AI system for pharmaceutical Medical Affairs teams, powered by **Azure OpenAI**, **Semantic Kernel**, and the **Agent-to-Agent (A2A) Protocol**.

## 🎯 Overview

This system demonstrates how pharmaceutical companies can use AI agents to transform Medical Information (MI) operations from manual, time-intensive processes into automated, compliant, and traceable workflows.

### The Problem

- **Manual MI Responses**: Healthcare providers (HCPs) ask medical questions → Medical Affairs teams spend hours/days researching → Response delays impact patient care
- **Compliance Risk**: Off-label content, promotional language, or unsupported claims can lead to FDA warnings
- **Audit Requirements**: FDA requires complete tracking of all HCP interactions
- **Scalability**: Limited MI team capacity vs. growing HCP inquiry volume

### The Solution

**AI-Powered Multi-Agent Workflow:**
1. 🔍 **Literature Scout Agent** → Retrieves evidence from FDA labels, clinical trials, publications
2. 📝 **MI Agent** → Generates fair-balanced, compliant responses
3. ⚠️ **Compliance Guard** → Validates for regulatory risks, flags high-risk content
4. 📄 **PDF Generator** → Creates professional MI letters for distribution
5. 📊 **CRM Integration** → Logs interactions to Veeva Medical CRM with full audit trail

**Result:** Hours/days → **Seconds** | Manual → **AI-Assisted** | Risky → **Compliance-Validated**

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture
- **Separation of Concerns**: Each agent specializes (search vs. synthesis vs. compliance)
- **Agent-to-Agent Protocol (A2A)**: Standardized agent communication using Microsoft's A2A SDK
- **Semantic Kernel**: Advanced LLM orchestration with Azure OpenAI GPT-4
- **Reusable Agents**: Literature Scout can serve multiple downstream workflows

### 🛡️ Regulatory Compliance
- **Automated Compliance Checks**: Flags off-label content, promotional language, unsupported claims
- **Risk Stratification**: LOW/MEDIUM/HIGH risk levels for triage
- **Medical Review Routing**: High-risk responses automatically flagged for human review
- **Fair Balance**: Ensures safety information accompanies efficacy claims

### 📄 PDF Generation
- **FDA-Compliant MI Letters**: Industry-standard format with letterhead, reference numbers, disclaimers
- **Professional Output**: ReportLab-generated PDFs ready for field distribution
- **Batch Processing**: Generate multiple letters for common queries

### 📊 CRM Integration
- **Persistent Storage**: SQLite database + JSON export for complete audit trail
- **Veeva Medical CRM Simulation**: Models real-world pharmaceutical CRM workflows
- **Analytics Dashboard**: Query categories, risk distribution, HCP interaction history
- **SQL Query Support**: Advanced analytics on historical data

### 🎨 Streamlit Web Interface
- **5 Interactive Tabs**: Literature Scout, Full MI Workflow, Compliance Check, CRM Analytics, History
- **Real-Time Workflow**: Watch agents execute in sequence with progress indicators
- **Download PDFs**: Generate and download professional MI letters
- **CRM Logging**: One-click interaction logging with complete HCP details

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEDICAL AFFAIRS WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │   HCP Query (via Streamlit or Notebook)  │
        └──────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────────────┐
        │  📚 LITERATURE SCOUT AGENT (A2A Server - Port 9099) │
        │  • Searches FDA labels, clinical trials, literature │
        │  • Returns structured evidence with citations       │
        └─────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │  📝 MEDICAL INFORMATION AGENT (SK)        │
        │  • Formats compliant MI response         │
        │  • Fair balance, professional tone       │
        │  • Cites evidence sources                │
        └──────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │  ⚠️  COMPLIANCE GUARD AGENT (SK)         │
        │  • Validates for off-label content       │
        │  • Checks for promotional language       │
        │  • Assigns risk level (LOW/MED/HIGH)     │
        └──────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │  📄 PDF GENERATOR                        │
        │  • Generates professional MI letter      │
        │  • Reference number tracking             │
        │  • Compliance disclaimers                │
        └──────────────────────────────────────────┘
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │  📊 CRM INTEGRATION (SQLite + JSON)      │
        │  • Logs interaction to database          │
        │  • Exports to JSON for portability       │
        │  • Analytics dashboard                   │
        └──────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **LLM Orchestration** | Microsoft Semantic Kernel 1.0+ |
| **Agent Protocol** | Agent-to-Agent (A2A) SDK |
| **LLM Provider** | Azure OpenAI (GPT-4) |
| **Backend Server** | FastAPI + Uvicorn |
| **Frontend** | Streamlit |
| **PDF Generation** | ReportLab |
| **Database** | SQLite |
| **Export** | JSON |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Azure OpenAI API Access** (GPT-4 deployment)
- **Environment Variables**:
  ```bash
  AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
  AZURE_OPENAI_API_KEY="your-api-key"
  AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
  ```

### Installation

```bash
# Clone the repository
git clone https://github.com/nrs2130/medical-affairs-multi-agent.git
cd medical-affairs-multi-agent

# Install dependencies
pip install -r requirements.txt

# Set environment variables
# Windows PowerShell:
$env:AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
$env:AZURE_OPENAI_API_KEY="your-api-key"
$env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"

# Linux/Mac:
export AZURE_OPENAI_ENDPOINT="https://your-instance.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
```

### Running the Demo

**Option 1: Streamlit Web App (Recommended)**

```bash
# Start the Streamlit app
streamlit run medical_affairs_app.py

# App will open in browser at http://localhost:8501
```

**Option 2: Jupyter Notebook (Developer Mode)**

```bash
# Open the notebook
jupyter notebook life_sciences_agent_demo.ipynb

# Execute cells 1-8 to:
# 1. Configure Azure OpenAI
# 2. Start A2A server (Literature Scout Agent)
# 3. Initialize Semantic Kernel agents
# 4. Run full workflow examples
```

---

## 📖 Usage Guide

### Streamlit Web App

#### Tab 1: Literature Scout
- Test the evidence retrieval agent standalone
- Enter medical queries (e.g., "What is the renal dosing for Drug X?")
- See structured evidence with citations

#### Tab 2: Full MI Workflow
1. **Enter HCP Query**: Type the medical information question
2. **Run Full Workflow**: Click to execute all 3 agents in sequence
3. **Review Results**: Evidence → MI Response → Compliance Assessment
4. **Generate PDF**: Create professional MI letter with reference number
5. **Log to CRM**: Record interaction with HCP details for audit trail

#### Tab 3: Compliance Check
- Test compliance validation standalone
- Enter evidence + proposed response
- See risk level and specific compliance flags

#### Tab 4: CRM Analytics
- **Summary Metrics**: Total interactions, avg response time, pending reviews
- **Risk Distribution**: Pie chart of LOW/MEDIUM/HIGH risk interactions
- **Query Categories**: Bar chart of query types (dosing, DDIs, safety, etc.)
- **Recent Interactions**: Detailed log of recent HCP inquiries

#### Tab 5: History
- View all past queries and responses
- Export session history to JSON

### Jupyter Notebook

#### Cell 8: Start A2A Server
```python
# Starts Literature Scout agent on localhost:9099
await start_a2a_server_literature_scout()
```

#### Cell 9: Run Full Workflow
```python
# Complete MI workflow
mi_query = "What's the renal dosing for Kerendia in severe CKD?"
result = await run_full_mi_workflow(mi_query, A2A_BASE, kernel_B)
```

#### Cell 10: Generate PDF
```python
# Create professional MI letter
ref_number = generate_mi_letter_pdf(
    query=mi_query,
    evidence=result['evidence'],
    response=result['mi_response'],
    compliance_result=result['compliance'],
    output_filename="./mi_responses/MI_Letter.pdf"
)
```

#### Cell 11: Log to CRM
```python
# Record interaction in CRM database
crm_record = crm.log_medical_information_request(
    hcp_info={"name": "Dr. Smith, MD", "specialty": "Cardiology"},
    query=mi_query,
    response=result['mi_response'],
    evidence=result['evidence'],
    compliance_result=result['compliance'],
    pdf_path="./mi_responses/MI_Letter.pdf",
    ref_number=ref_number
)
```

#### Cell 12: SQL Queries
```python
# Find high-risk interactions
high_risk = crm.query_database('''
    SELECT * FROM mi_interactions 
    WHERE compliance_risk_level = 'HIGH'
''')

# Count by HCP
by_hcp = crm.query_database('''
    SELECT hcp_name, COUNT(*) as count
    FROM mi_interactions
    GROUP BY hcp_name
''')
```

---

## 📁 Project Structure

```
medical-affairs-multi-agent/
│
├── medical_affairs_app.py          # Streamlit web application
├── life_sciences_agent_demo.ipynb  # Jupyter notebook demo
│
├── crm_data/                        # CRM persistent storage (auto-created)
│   ├── medical_affairs.db          # SQLite database
│   └── interactions.json           # JSON export
│
├── mi_responses/                    # Generated PDF letters (auto-created)
│   └── MI_Response_*.pdf
│
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── README_PDF_GENERATION.md         # PDF generation documentation
├── README_CRM_INTEGRATION.md        # CRM integration documentation
└── BUGFIX_WORKFLOW_BUTTONS.md       # Technical notes on Streamlit fix
```

---

## 🔧 Configuration

### Azure OpenAI Setup

1. **Create Azure OpenAI Resource**: [Azure Portal](https://portal.azure.com/)
2. **Deploy GPT-4 Model**: Note your deployment name
3. **Get API Credentials**:
   - Endpoint: `https://your-instance.openai.azure.com/`
   - API Key: From "Keys and Endpoint" section
4. **Set Environment Variables** (see Installation section)

### A2A Server Configuration

The Literature Scout agent runs on **localhost:9099** by default. To change:

```python
# In life_sciences_agent_demo.ipynb or medical_affairs_app.py
A2A_PORT = 9099  # Change to desired port
A2A_BASE = f"http://127.0.0.1:{A2A_PORT}"
```

### CRM Storage Location

CRM data is stored in `./crm_data/` by default. To change:

```python
crm = MedicalCRMIntegration(
    db_path="./custom_path/crm.db",
    json_path="./custom_path/interactions.json"
)
```

---

## 📊 CRM Data Structure

### SQLite Database Schema

```sql
CREATE TABLE mi_interactions (
    record_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    mi_reference_number TEXT UNIQUE,
    
    -- HCP Information
    hcp_name TEXT,
    hcp_specialty TEXT,
    hcp_institution TEXT,
    
    -- Query Details
    query_text TEXT,
    query_category TEXT,
    products_mentioned TEXT,  -- JSON array
    
    -- Response
    response_provided TEXT,
    pdf_attachment TEXT,
    
    -- Compliance
    compliance_risk_level TEXT,
    requires_follow_up BOOLEAN,
    
    -- Audit
    approved_by TEXT,
    system_generated BOOLEAN,
    ai_assisted BOOLEAN,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### JSON Export Format

```json
[
  {
    "record_id": "CRM-20241024143022",
    "timestamp": "2024-10-24T14:30:22",
    "mi_reference": "MI-20241024-143020",
    "hcp_name": "Dr. Emily Chen, MD",
    "hcp_specialty": "Cardiology",
    "query_text": "What's the renal dosing for Kerendia in severe CKD?",
    "query_category": "Special Populations - Organ Impairment",
    "products_mentioned": ["Kerendia"],
    "compliance_risk": "LOW",
    "status": "Auto-Approved"
  }
]
```

---

## 🎯 Use Cases

### 1. Medical Information Requests
**Scenario**: HCP calls with dosing question  
**Workflow**: Literature Scout → MI Agent → Compliance Guard → PDF → CRM  
**Outcome**: Compliant response in seconds vs. hours

### 2. Field Medical Support
**Scenario**: MSL needs quick evidence for HCP meeting  
**Workflow**: Literature Scout → Evidence summary  
**Outcome**: Real-time evidence retrieval in the field

### 3. Compliance Audits
**Scenario**: FDA inspection requires MI audit trail  
**Workflow**: SQL query on CRM database  
**Outcome**: Complete interaction history with risk levels

### 4. Medical Review Queue
**Scenario**: High-risk responses need medical review  
**Workflow**: Compliance Guard flags → Medical reviewer dashboard  
**Outcome**: Automated triage, human-in-loop for risky content

---

## 🚧 Production Deployment Considerations

### Security
- [ ] Implement authentication (Azure AD, OAuth)
- [ ] Add role-based access control (RBAC)
- [ ] Encrypt sensitive data at rest
- [ ] Use Azure Key Vault for API keys
- [ ] Enable HTTPS/TLS for all endpoints

### Scalability
- [ ] Deploy A2A server to Azure Container Apps
- [ ] Use Azure App Service for Streamlit frontend
- [ ] Implement Redis caching for frequently requested evidence
- [ ] Add load balancing for multi-user support
- [ ] Monitor with Application Insights

### Compliance (21 CFR Part 11)
- [ ] Add electronic signatures for approvals
- [ ] Implement audit trail with timestamps
- [ ] Add data integrity checks (checksums)
- [ ] Implement user access logs
- [ ] Add retention policies

### Integration
- [ ] Connect to real Veeva Medical CRM API
- [ ] Integrate with internal document repositories (Veeva Vault, SharePoint)
- [ ] Add PubMed API for real-time literature search
- [ ] Connect to clinical trial databases (ClinicalTrials.gov)
- [ ] Implement email notifications for high-risk content

### Monitoring
- [ ] Add LLM usage tracking (token costs)
- [ ] Monitor response quality (human feedback loop)
- [ ] Track compliance flag accuracy
- [ ] Alert on high-risk patterns
- [ ] Dashboard for Medical Affairs leadership

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is provided for **demonstration and educational purposes**. Please ensure compliance with:
- Your organization's data privacy policies
- HIPAA regulations (if handling PHI)
- FDA regulations (21 CFR Part 11 for electronic records)
- Azure OpenAI terms of service

---

## 👨‍💻 Author

**Nick Stewart**  
GitHub: [@nrs2130](https://github.com/nrs2130)

---

## 🙏 Acknowledgments

- **Microsoft Semantic Kernel Team**: LLM orchestration framework
- **Microsoft A2A Team**: Agent-to-Agent protocol
- **Azure OpenAI**: GPT-4 model access
- **Streamlit**: Rapid web app development
- **Pharmaceutical Medical Affairs Community**: Domain expertise

---

## 📚 Additional Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Agent-to-Agent Protocol Spec](https://github.com/microsoft/agent-to-agent)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [FDA Guidance on Medical Information](https://www.fda.gov/regulatory-information/search-fda-guidance-documents)
- [Veeva Medical CRM](https://www.veeva.com/products/veeva-crm/)

---

## ❓ FAQ

**Q: Can this replace Medical Affairs teams?**  
A: No. This is an **AI-assisted tool** that augments human experts. High-risk content is flagged for medical review. Final approval remains with qualified medical professionals.

**Q: Is the evidence retrieval real?**  
A: The current demo uses **simulated responses** from the Literature Scout. In production, you would integrate with:
- PubMed API for real literature
- Internal document repositories (Veeva Vault)
- FDA label database (DailyMed)

**Q: How accurate is the Compliance Guard?**  
A: The LLM-based compliance check is a **first-pass filter**, not a replacement for regulatory review. It can catch obvious issues (off-label claims, promotional language) but should be validated by trained Medical Information professionals.

**Q: Can I use this with other LLMs?**  
A: Yes! The system uses Semantic Kernel, which supports:
- Azure OpenAI
- OpenAI API
- Other LLM providers (with appropriate connectors)

**Q: How does the CRM integration work in production?**  
A: The current implementation uses **SQLite + JSON** for demo purposes. In production, replace the storage layer with:
- Veeva CRM API (`POST /api/v21.1/objects/medical_insight__c`)
- Salesforce Health Cloud API
- Custom REST endpoints

**Q: Is this HIPAA compliant?**  
A: The demo does **not** handle PHI (Protected Health Information). For HIPAA compliance:
- Deploy in Azure with HIPAA BAA
- Enable encryption at rest/in transit
- Implement access controls and audit logs
- Avoid storing patient identifiers

---

## 🚀 Roadmap

- [ ] **Multi-language Support**: Translate MI responses to Spanish, French, etc.
- [ ] **Voice Interface**: Alexa/Google Home integration for MSLs in the field
- [ ] **Mobile App**: React Native app for on-the-go MI requests
- [ ] **Advanced Analytics**: Power BI dashboard for Medical Affairs leadership
- [ ] **RAG Enhancement**: Vector database (Pinecone/Weaviate) for better evidence retrieval
- [ ] **Agent Marketplace**: Share custom agents (Pharmacovigilance Agent, Label Comparison Agent)

---

## 📞 Support

For questions or issues:
- **GitHub Issues**: [Create an issue](https://github.com/nrs2130/medical-affairs-multi-agent/issues)
- **Email**: nstewart@example.com (replace with actual)
- **LinkedIn**: [Nick Stewart](https://linkedin.com/in/nickstewart)

---

**⭐ If you find this project useful, please star the repository!**

---

*Last Updated: October 2024*
