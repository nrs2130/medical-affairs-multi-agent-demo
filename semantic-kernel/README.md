# Semantic Kernel Implementation

> Medical Affairs Multi-Agent System using **Microsoft Semantic Kernel** + **A2A SDK**

This folder contains the **legacy** implementation using Microsoft's Semantic Kernel framework. This version is maintained for compatibility and comparison purposes.

⚠️ **For new projects, we recommend the [Agent Framework implementation](../agent-framework/)** which offers modern async patterns and simplified APIs.

---

## 📋 Overview

This implementation demonstrates the same Medical Affairs multi-agent system using Semantic Kernel's plugin-based architecture. It includes:

- ✅ Literature Scout Agent (A2A server)
- ✅ Medical Information Response Agent
- ✅ Compliance Guard validation
- ✅ PDF generation and CRM logging
- ✅ Streamlit web UI

**Framework:** [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel)  
**Status:** Legacy (maintained for comparison)

---

## 📦 Installation

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

**Key Packages:**
- `semantic-kernel>=1.0.0` - Core SK framework
- `a2a-sdk[http-server]` - A2A protocol support
- `streamlit>=1.28.0` - Web UI framework
- `fastapi` - Agent server infrastructure

### 2. Configure Azure OpenAI

```powershell
# Set environment variables (PowerShell)
$env:AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'
$env:AZURE_OPENAI_API_KEY='your-api-key-here'
$env:AZURE_OPENAI_DEPLOYMENT_NAME='gpt-4'
$env:AZURE_OPENAI_API_VERSION='2024-12-01-preview'
```

---

## 🚀 Quick Start

### Option 1: Jupyter Notebook

```powershell
jupyter notebook life_sciences_agent_demo.ipynb
```

### Option 2: Streamlit Web UI

```powershell
streamlit run medical_affairs_app.py
```

**Access:** http://localhost:8501

---

## 🏗️ Semantic Kernel Architecture

### Key Concepts

```python
# 1. Create Kernel
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

kernel = Kernel()

# 2. Add Azure OpenAI Service
kernel.add_service(
    AzureChatCompletion(
        deployment_name="gpt-4",
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )
)

# 3. Invoke Prompt
prompt = "What's the renal dosing for Drug X?"
result = await kernel.invoke_prompt(prompt)

# 4. Access Response
response_text = str(result)
```

### Plugin-Based Design

Semantic Kernel uses a **plugin architecture** where functions are organized into plugins:

```python
from semantic_kernel.functions import kernel_function

class LiteratureScoutPlugin:
    @kernel_function(name="search_pubmed")
    def search_pubmed(self, query: str) -> str:
        """Search PubMed for medical literature"""
        # Implementation here
        return evidence_text

# Add plugin to kernel
kernel.add_plugin(LiteratureScoutPlugin(), plugin_name="literature")

# Invoke plugin function
result = await kernel.invoke(plugin_name="literature", function_name="search_pubmed")
```

---

## 🔄 Comparison: Semantic Kernel vs. Agent Framework

| Feature | Semantic Kernel | Agent Framework |
|---------|----------------|-----------------|
| **Agent Creation** | `Kernel()` + plugins | `create_agent(name, instructions)` |
| **Execution** | `kernel.invoke_prompt()` | `await agent.run(prompt)` |
| **Response Type** | String (`str(result)`) | Structured `AgentRunResponse` |
| **A2A Integration** | Manual setup | Native `A2AClient` |
| **Async Support** | Partial | Full native async |
| **API Complexity** | Higher (plugins, services) | Lower (agent-centric) |
| **Maturity** | Production-ready | Emerging (2024+) |

**Migration Path:** The Agent Framework implementation in `../agent-framework/` demonstrates how to migrate from Semantic Kernel to the modern framework.

---

## 📝 Core Files

| File | Purpose |
|------|---------|
| `medical_affairs_app.py` | Streamlit web UI with 4 tabs |
| `life_sciences_agent_demo.ipynb` | Jupyter notebook walkthrough |
| `grade_evidence_agent.py` | GRADE evidence assessment module |
| `requirements.txt` | Python dependencies (Semantic Kernel) |

---

## 🔧 Key Differences from Agent Framework

### 1. Agent Creation

**Semantic Kernel:**
```python
kernel = Kernel()
kernel.add_service(AzureChatCompletion(...))
```

**Agent Framework:**
```python
chat_client = AzureOpenAIChatClient(...)
agent = chat_client.create_agent(name="...", instructions="...")
```

### 2. Prompt Execution

**Semantic Kernel:**
```python
result = await kernel.invoke_prompt(prompt)
response_text = str(result)
```

**Agent Framework:**
```python
result = await agent.run(prompt)
response_text = result.text
```

### 3. A2A Integration

**Semantic Kernel:**
```python
# Manual A2A setup with custom message handling
response = await a2a_client.send_message(request)
text = response['result']['parts'][0]['text']  # Dict-style access
```

**Agent Framework:**
```python
# Native A2A with Pydantic models
response = await a2a_client.send_message(request)
text = response.root.result.parts[0].root.text  # Typed attributes
```

---

## 🐛 Troubleshooting

### Error: "No service of type AzureChatCompletion registered"

```python
# Ensure you added the service to the kernel
kernel.add_service(
    AzureChatCompletion(
        deployment_name="gpt-4",
        endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )
)
```

### Error: "KernelArguments object has no attribute 'get'"

```python
# Use KernelArguments correctly
from semantic_kernel.functions import KernelArguments

args = KernelArguments(query="What is the dosing?")
result = await kernel.invoke_prompt(prompt, arguments=args)
```

---

## 📚 Resources

- [Semantic Kernel Documentation](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)
- [Semantic Kernel Samples](https://github.com/microsoft/semantic-kernel/tree/main/python/samples)

---

## ⚠️ Deprecation Notice

This implementation is maintained for:
1. **Legacy support** - Existing SK-based deployments
2. **Comparison** - Demonstrating framework migration
3. **Learning** - Understanding SK plugin architecture

**For new development, use the Agent Framework implementation:** [`../agent-framework/`](../agent-framework/)

---

## 📞 Support

For questions about this implementation:

- **Email:** nistewart@microsoft.com
- **LinkedIn:** [linkedin.com/in/nicholas-stewart-phd](https://www.linkedin.com/in/nicholas-stewart-phd/)

---

**Legacy Implementation - Consider Migrating to Agent Framework** 🔄
