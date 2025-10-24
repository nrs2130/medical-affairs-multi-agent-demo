"""
Medical Affairs Evidence Synthesis & Response System
Multi-Agent Streamlit Application

This app provides a frontend interface for pharmaceutical Medical Affairs teams
to interact with the multi-agent system for generating compliant medical information responses.
"""

import streamlit as st
import asyncio
import os
import json
import sqlite3
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import httpx

# A2A Client imports
from a2a.client import A2AClient
from a2a.client.card_resolver import A2ACardResolver
from a2a.types import SendMessageRequest, MessageSendParams

# Semantic Kernel imports
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

# PDF generation imports
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Page configuration
st.set_page_config(
    page_title="Medical Affairs AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 1rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0078D4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'azure_configured' not in st.session_state:
    st.session_state.azure_configured = False
if 'a2a_configured' not in st.session_state:
    st.session_state.a2a_configured = False
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None
if 'workflow_query' not in st.session_state:
    st.session_state.workflow_query = ""
if 'workflow_completed' not in st.session_state:
    st.session_state.workflow_completed = False

# Sample prompts for each agent type (using J&J products)
SAMPLE_PROMPTS = {
    "Literature Scout": [
        "What is the renal dosing guidance for Kerendia (finerenone) in severe CKD (eGFR <30)?",
        "Are there any known drug-drug interactions between Tremfya (guselkumab) and warfarin?",
        "What are the contraindications for Stelara (ustekinumab) in patients with hepatic impairment?",
        "What adverse events were most common in the Tremfya pivotal trials for plaque psoriasis?",
        "Is dose adjustment needed for Invega (paliperidone) in moderate renal impairment (CrCl 30-60)?",
        "What is the mechanism of action of Erleada (apalutamide) for treating prostate cancer?",
        "Can Stelara be used in pregnant or breastfeeding women?",
        "What is the recommended monitoring for patients starting Xarelto (rivaroxaban)?",
    ],
    "Full MI Workflow": [
        "What's the renal dosing guidance for Kerendia (finerenone) in severe CKD (eGFR <30)?",
        "What are the cardiovascular safety considerations for Xarelto (rivaroxaban) in elderly patients?",
        "How should Tremfya be dosed in patients with moderate hepatic impairment?",
        "What are the key drug interactions to monitor when prescribing Invega Sustenna?",
    ],
    "Compliance Check": [
        "Tremfya is the best treatment available and has no significant side effects.",
        "Stelara can be used off-label for pediatric patients with excellent results.",
        "Studies show Tremfya is superior to all competitors in the market.",
        "Invega is approved for schizophrenia and also works great for anxiety disorders.",
    ]
}

# Agent descriptions
AGENT_INFO = {
    "Literature Scout": {
        "icon": "📚",
        "description": "Searches literature, retrieves evidence, and provides structured medical information with citations.",
        "capabilities": [
            "Searches PubMed and clinical trial registries",
            "Retrieves FDA-approved product labeling",
            "Ranks studies by quality and recency",
            "Formats evidence with proper citations"
        ]
    },
    "Evidence Summarizer": {
        "icon": "📊",
        "description": "Produces structured evidence tables and assesses quality of clinical evidence.",
        "capabilities": [
            "Creates evidence tables from literature",
            "Assesses study quality and bias",
            "Synthesizes findings across studies",
            "Identifies evidence gaps",
            "Notes: Could integrate GRADE methodology for formal guidelines"
        ]
    },
    "Medical Information Agent": {
        "icon": "📝",
        "description": "Assembles compliant, fair-balanced responses for HCP inquiries with proper citations.",
        "capabilities": [
            "Formats professional MI responses",
            "Ensures fair balance (efficacy + safety)",
            "Maintains on-label guidance priority",
            "Non-promotional, evidence-based tone"
        ]
    },
    "Compliance Guard": {
        "icon": "⚠️",
        "description": "Validates responses for FDA/regulatory compliance, flags risks, and ensures adherence to medical affairs standards.",
        "capabilities": [
            "Detects off-label content (not in FDA label)",
            "Identifies promotional language",
            "Checks fair balance requirements (21 CFR 202.1)",
            "Assigns regulatory risk levels (LOW/MEDIUM/HIGH)",
            "Ensures adherence to approved product labeling"
        ]
    },
    "PDF Letter Generator": {
        "icon": "📄",
        "description": "Creates professional, FDA-compliant Medical Information response letters in PDF format.",
        "capabilities": [
            "Generates industry-standard MI letter format",
            "Includes company letterhead and branding",
            "Adds unique tracking reference numbers",
            "Embeds compliance assessment and disclaimers",
            "Ready for distribution to field teams/HCPs"
        ]
    },
    "CRM Integration": {
        "icon": "📊",
        "description": "Logs Medical Information interactions to pharmaceutical CRM systems (Veeva, Salesforce) for compliance tracking.",
        "capabilities": [
            "Auto-categorizes queries by type",
            "Extracts product names from queries",
            "Tracks HCP information and interactions",
            "Generates compliance analytics dashboards",
            "Maintains complete audit trail for FDA inspections"
        ]
    }
}

# ============================================================================
# Helper Functions
# ============================================================================

def init_semantic_kernel(azure_endpoint: str, azure_key: str, deployment: str, api_version: str):
    """Initialize Semantic Kernel with Azure OpenAI"""
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=deployment,
            endpoint=azure_endpoint,
            api_key=azure_key,
            api_version=api_version,
            service_id="chat"
        )
    )
    return kernel

async def call_literature_scout_agent(query: str, a2a_base: str) -> str:
    """Call the Literature Scout Agent via A2A protocol"""
    timeout = httpx.Timeout(30.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        resolver = A2ACardResolver(httpx_client=client, base_url=a2a_base)
        agent_card = await resolver.get_agent_card()
        a2a_client = A2AClient(httpx_client=client, agent_card=agent_card)
        
        req = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    'messageId': uuid4().hex,
                    'role': 'user',
                    'parts': [{'text': query}],
                    'contextId': f'streamlit-session-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
                }
            ),
        )
        
        resp = await a2a_client.send_message(req)
        data = resp.model_dump(mode='json', exclude_none=True)
        return data.get('result', {}).get('parts', [{}])[0].get('text', json.dumps(data, indent=2))

async def run_compliance_check(evidence: str, response: str, kernel) -> dict:
    """Run Compliance Guard validation with strict FDA/regulatory standards"""
    compliance_prompt = f"""You are ComplianceGuardAgent for pharmaceutical Medical Affairs with STRICT FDA regulatory oversight.

CRITICAL RULES - AUTOMATIC HIGH RISK:
1. ANY use not explicitly stated in FDA label = OFF-LABEL = HIGH RISK
2. ANY pediatric use outside approved age range = HIGH RISK
3. ANY contraindicated population mentioned = HIGH RISK
4. Comparative claims ("better than", "superior to") without head-to-head trials = HIGH RISK
5. Promotional language ("best", "excellent", "great") = HIGH RISK
6. Missing safety information when discussing efficacy = MEDIUM-HIGH RISK

EVIDENCE BASE (FDA-Approved Labeling):
{evidence}

PROPOSED MI RESPONSE TO HCP:
{response}

COMPLIANCE ANALYSIS REQUIRED:

**Step 1: Check for OFF-LABEL content**
- Does response discuss ANY indication not in the evidence?
- Does response discuss ANY population (age, organ impairment) not approved?
- Does response discuss ANY dosing not in approved labeling?
→ If YES to any: AUTOMATIC HIGH RISK

**Step 2: Check for PROMOTIONAL language**
- Words like: "best", "superior", "excellent", "great", "proven", "guaranteed"
- Comparative claims without proper citations
- Overstating benefits or minimizing risks
→ If YES: HIGH RISK

**Step 3: Check FAIR BALANCE**
- If efficacy mentioned, is safety equally prominent?
- Are contraindications/warnings present?
→ If NO: MEDIUM-HIGH RISK

**Step 4: Citation check**
- Are claims supported by evidence provided?
- Are references to "studies" or "data" properly cited?
→ If NO: MEDIUM RISK

RETURN STRICT JSON FORMAT:
{{
  "risk_level": "LOW|MEDIUM|HIGH",
  "flags": ["specific issue 1", "specific issue 2", ...],
  "requires_medical_review": true/false,
  "recommendations": ["specific edit 1", "specific edit 2", ...]
}}

BE EXTREMELY STRICT. When in doubt, escalate to HIGHER risk level. Patient safety and regulatory compliance are paramount.
"""
    result = await kernel.invoke_prompt(compliance_prompt, arguments=KernelArguments())
    try:
        compliance_result = json.loads(str(result))
    except:
        compliance_result = {
            "risk_level": "MEDIUM",
            "flags": [str(result)],
            "requires_medical_review": True,
            "recommendations": []
        }
    return compliance_result

def generate_mi_letter_pdf(query: str, evidence: str, response: str, 
                           compliance_result: dict, output_filename: str) -> str:
    """Generate a professional Medical Information response letter in PDF format"""
    
    # Create PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=1*inch, rightMargin=1*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'], fontSize=16,
        textColor=colors.HexColor('#003087'), spaceAfter=12, alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'Header', parent=styles['Normal'], fontSize=9,
        textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=6
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'], fontSize=12,
        textColor=colors.HexColor('#003087'), spaceAfter=8, spaceBefore=12, bold=True
    )
    
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontSize=10, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=10
    )
    
    disclaimer_style = ParagraphStyle(
        'Disclaimer', parent=styles['Normal'], fontSize=8,
        textColor=colors.HexColor('#666666'), alignment=TA_JUSTIFY,
        leftIndent=20, rightIndent=20, spaceBefore=20, spaceAfter=10
    )
    
    # Generate reference number and date
    ref_number = f"MI-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Letterhead
    story.append(Paragraph("<b>MEDICAL INFORMATION SERVICES</b>", title_style))
    story.append(Paragraph("Pharmaceutical Company Name", header_style))
    story.append(Paragraph("Medical Affairs Department", header_style))
    story.append(Paragraph("Phone: 1-800-XXX-XXXX | Email: medinfo@company.com", header_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Divider
    story.append(Table([['']], colWidths=[6.5*inch], 
                      style=[('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#003087'))]))
    story.append(Spacer(1, 0.2*inch))
    
    # Header info
    header_data = [
        ['Date:', current_date],
        ['Reference Number:', ref_number],
        ['Response Type:', 'Medical Information'],
    ]
    header_table = Table(header_data, colWidths=[1.5*inch, 5*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#003087')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Query
    story.append(Paragraph("<b>Healthcare Provider Query:</b>", section_header_style))
    story.append(Paragraph(query, body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Response
    story.append(Paragraph("<b>Medical Information Response:</b>", section_header_style))
    for para in response.split('\n\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Compliance status
    risk_level = compliance_result.get('risk_level', 'UNKNOWN')
    requires_review = compliance_result.get('requires_medical_review', False)
    
    risk_colors_map = {
        'LOW': colors.green, 'MEDIUM': colors.orange,
        'HIGH': colors.red, 'UNKNOWN': colors.grey
    }
    
    story.append(Paragraph("<b>Compliance Assessment:</b>", section_header_style))
    compliance_data = [
        ['Risk Level:', risk_level],
        ['Medical Review Status:', '🟡 PENDING REVIEW' if requires_review else '✅ APPROVED']
    ]
    
    compliance_table = Table(compliance_data, colWidths=[2*inch, 4.5*inch])
    compliance_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#003087')),
        ('TEXTCOLOR', (1,0), (1,0), risk_colors_map.get(risk_level, colors.grey)),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F5F5')),
        ('BOX', (0,0), (-1,-1), 1, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(compliance_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Disclaimer
    disclaimer_text = """
    <b>IMPORTANT NOTICE:</b> This Medical Information response is provided for educational and 
    informational purposes only in response to your unsolicited request. This information is not 
    intended to substitute for professional medical advice, diagnosis, or treatment. Healthcare 
    professionals should use their independent professional judgment in treating patients. 
    This response is based on currently available scientific information and FDA-approved 
    product labeling. Please refer to the full Prescribing Information for complete safety 
    and efficacy information. For additional medical information or to report an adverse event, 
    please contact Medical Information Services at 1-800-XXX-XXXX.
    """
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Signature block
    story.append(Spacer(1, 0.3*inch))
    signature_text = f"""
    <b>Prepared by:</b> Medical Information Services<br/>
    <b>Date:</b> {current_date}<br/>
    <b>Reference:</b> {ref_number}<br/>
    """
    story.append(Paragraph(signature_text, body_style))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(Table([['']], colWidths=[6.5*inch], 
                      style=[('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#003087'))]))
    footer_text = "<i>This document is confidential and intended for healthcare professionals only.</i>"
    story.append(Paragraph(footer_text, disclaimer_style))
    
    # Build PDF
    doc.build(story)
    
    return ref_number

class MedicalCRMIntegration:
    """
    Enhanced CRM integration with persistent storage (JSON + SQLite)
    
    Simulates pharmaceutical CRM systems (Veeva Medical CRM, Salesforce) with:
    - In-memory storage for quick access (using Streamlit session state)
    - JSON file export for portability
    - SQLite database for structured queries
    
    In production, this would connect to:
    - Veeva Vault API for document management
    - Veeva CRM API for Medical Insights/Call Reports
    - Salesforce Health Cloud API
    """
    
    def __init__(self, 
                 system_name: str = "Veeva Medical CRM",
                 db_path: str = "./crm_data/medical_affairs.db",
                 json_path: str = "./crm_data/interactions.json"):
        self.system_name = system_name
        self.db_path = Path(db_path)
        self.json_path = Path(json_path)
        
        # Create directories if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize session state for in-memory cache
        if 'crm_log' not in st.session_state:
            st.session_state.crm_log = []
        
        # Initialize database
        self._init_database()
        
        # Load existing data from database into session state
        self._load_from_storage()
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mi_interactions (
                record_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                interaction_type TEXT,
                channel TEXT,
                mi_reference_number TEXT UNIQUE,
                
                -- HCP Information
                hcp_name TEXT,
                hcp_npi TEXT,
                hcp_specialty TEXT,
                hcp_institution TEXT,
                hcp_email TEXT,
                hcp_consent_status TEXT,
                
                -- Medical Affairs Rep
                msl_name TEXT,
                territory TEXT,
                
                -- Query Details
                query_text TEXT,
                query_category TEXT,
                products_mentioned TEXT,  -- JSON array as string
                
                -- Response Details
                response_provided TEXT,
                evidence_sources TEXT,  -- JSON array as string
                pdf_attachment TEXT,
                
                -- Compliance
                compliance_risk_level TEXT,
                requires_follow_up BOOLEAN,
                compliance_flags TEXT,  -- JSON array as string
                
                -- Metrics
                response_time_minutes REAL,
                satisfaction_rating INTEGER,
                
                -- Audit
                approved_by TEXT,
                system_generated BOOLEAN,
                ai_assisted BOOLEAN,
                
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for common queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON mi_interactions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_risk_level ON mi_interactions(compliance_risk_level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_hcp_name ON mi_interactions(hcp_name)')
        
        conn.commit()
        conn.close()
    
    def _load_from_storage(self):
        """Load existing interactions from database into session state"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM mi_interactions ORDER BY timestamp DESC')
            rows = cursor.fetchall()
            
            # Only load if session state is empty
            if not st.session_state.crm_log:
                for row in rows:
                    record = dict(row)
                    # Parse JSON fields
                    record['products_mentioned'] = json.loads(record.pop('products_mentioned', '[]'))
                    record['evidence_sources'] = json.loads(record.pop('evidence_sources', '[]'))
                    record['compliance_flags'] = json.loads(record.pop('compliance_flags', '[]'))
                    # Map field names for backwards compatibility
                    record['mi_reference'] = record.get('mi_reference_number')
                    record['compliance_risk'] = record.get('compliance_risk_level')
                    record['status'] = record.get('approved_by')
                    st.session_state.crm_log.append(record)
            
            conn.close()
        except Exception as e:
            pass  # Silent fail for first run
    
    def _save_to_database(self, record: dict):
        """Save single interaction to SQLite database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Prepare data for insertion
            cursor.execute('''
                INSERT OR REPLACE INTO mi_interactions 
                (record_id, timestamp, interaction_type, channel, mi_reference_number,
                 hcp_name, hcp_specialty, hcp_institution,
                 query_text, query_category, products_mentioned,
                 pdf_attachment, compliance_risk_level, requires_follow_up,
                 approved_by, system_generated, ai_assisted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record['record_id'], record['timestamp'], 
                record.get('interaction_type', 'Medical Information Request'),
                record.get('channel', 'Unsolicited Medical Information'),
                record.get('mi_reference'),
                record.get('hcp_name'), record.get('hcp_specialty'), record.get('hcp_institution'),
                record.get('query_text'), record.get('query_category'),
                json.dumps(record.get('products_mentioned', [])),
                record.get('pdf_attachment'), record.get('compliance_risk'),
                record.get('requires_follow_up', False),
                record.get('status'), True, True
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass  # Silent fail for demo
    
    def _save_to_json(self):
        """Export all interactions to JSON file"""
        try:
            with open(self.json_path, 'w') as f:
                json.dump(st.session_state.crm_log, f, indent=2, default=str)
        except Exception as e:
            pass  # Silent fail for demo
    
    def log_interaction(self, hcp_info: dict, query: str, response: str, 
                       compliance_result: dict, ref_number: str, pdf_path: str = None) -> dict:
        """Log MI interaction to all storage backends"""
        
        crm_record = {
            "record_id": f"CRM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "interaction_type": "Medical Information Request",
            "channel": "Unsolicited Medical Information",
            "mi_reference": ref_number,
            "hcp_name": hcp_info.get("name", "Unknown HCP"),
            "hcp_specialty": hcp_info.get("specialty", "Not Specified"),
            "hcp_institution": hcp_info.get("institution", "Not Specified"),
            "query_text": query,
            "query_category": self._categorize_query(query),
            "products_mentioned": self._extract_products(query),
            "compliance_risk": compliance_result.get("risk_level", "UNKNOWN"),
            "requires_follow_up": compliance_result.get("requires_medical_review", False),
            "pdf_attachment": pdf_path or "Not Generated",
            "status": "Auto-Approved" if compliance_result.get("risk_level") == "LOW" else "Pending Medical Review"
        }
        
        # Store in all backends
        st.session_state.crm_log.append(crm_record)  # Session state (in-memory)
        self._save_to_database(crm_record)           # SQLite
        self._save_to_json()                         # JSON export
        
        return crm_record
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query type"""
        query_lower = query.lower()
        if any(word in query_lower for word in ["dosing", "dose", "administration"]):
            return "Dosing & Administration"
        elif "interaction" in query_lower or "ddi" in query_lower:
            return "Drug Interactions"
        elif any(word in query_lower for word in ["adverse", "side effect", "safety", "toxicity"]):
            return "Safety & Adverse Events"
        elif any(word in query_lower for word in ["contraindication", "warning", "precaution"]):
            return "Contraindications & Warnings"
        elif "renal" in query_lower or "hepatic" in query_lower or "kidney" in query_lower or "liver" in query_lower:
            return "Special Populations - Organ Impairment"
        elif any(word in query_lower for word in ["pediatric", "geriatric", "elderly", "children"]):
            return "Special Populations - Age"
        else:
            return "General Product Information"
    
    def _extract_products(self, query: str) -> list:
        """Extract product names"""
        products = ["Tremfya", "Stelara", "Kerendia", "Finerenone", "Invega", 
                   "Erleada", "Xarelto", "Spravato", "Darzalex"]
        mentioned = [p for p in products if p.lower() in query.lower()]
        return mentioned if mentioned else ["Product Not Specified"]
    
    def get_recent_interactions(self, limit: int = 10) -> list:
        """Get recent CRM interactions"""
        return st.session_state.crm_log[-limit:] if st.session_state.crm_log else []
    
    def get_summary_stats(self) -> dict:
        """Get CRM analytics summary"""
        if not st.session_state.crm_log:
            return {"total": 0}
        
        total = len(st.session_state.crm_log)
        risk_counts = {}
        category_counts = {}
        
        for record in st.session_state.crm_log:
            risk = record["compliance_risk"]
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            category = record["query_category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total": total,
            "risk_distribution": risk_counts,
            "query_categories": category_counts,
            "pending_review": sum(1 for r in st.session_state.crm_log if r["requires_follow_up"])
        }
    
    def clear_all_data(self):
        """Clear all CRM data from all backends"""
        st.session_state.crm_log = []
        
        # Clear database
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('DELETE FROM mi_interactions')
            conn.commit()
            conn.close()
        except:
            pass
        
        # Clear JSON
        self._save_to_json()

# Initialize CRM with persistent storage
crm = MedicalCRMIntegration()

async def run_full_mi_workflow(query: str, a2a_base: str, kernel) -> dict:
    """Run the full Medical Affairs workflow"""
    results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "evidence": "",
        "mi_response": "",
        "compliance": {}
    }
    
    # Step 1: Literature Scout
    results["evidence"] = await call_literature_scout_agent(query, a2a_base)
    
    # Step 2: MI Agent formats response
    mi_prompt = f"""You are MedicalInformationAgent. Create a compliant, fair-balanced response to this HCP inquiry.

QUERY: {query}

EVIDENCE BASE:
{results["evidence"]}

Format as a professional Medical Information response:
- Lead with approved labeling guidance
- Support with clinical evidence (cited)
- Include safety considerations
- Maintain fair balance
- Professional, non-promotional tone
- Max 200 words

Response:"""
    
    mi_response_result = await kernel.invoke_prompt(mi_prompt, arguments=KernelArguments())
    results["mi_response"] = str(mi_response_result)
    
    # Step 3: Compliance Guard validates
    results["compliance"] = await run_compliance_check(
        results["evidence"],
        results["mi_response"],
        kernel
    )
    
    return results

def add_to_history(entry: dict):
    """Add entry to session history"""
    st.session_state.history.insert(0, entry)
    if len(st.session_state.history) > 50:
        st.session_state.history = st.session_state.history[:50]

def display_compliance_result(compliance: dict):
    """Display compliance check results with appropriate styling"""
    risk_level = compliance.get('risk_level', 'UNKNOWN')
    
    if risk_level == 'LOW':
        box_class = "success-box"
        icon = "✅"
        color = "#28a745"
    elif risk_level == 'MEDIUM':
        box_class = "warning-box"
        icon = "⚠️"
        color = "#ffc107"
    else:  # HIGH
        box_class = "danger-box"
        icon = "🚨"
        color = "#dc3545"
    
    st.markdown(f"""
    <div class="{box_class}">
        <h3>{icon} Risk Level: {risk_level}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Requires Medical Review:**", 
                 "Yes" if compliance.get('requires_medical_review') else "No")
        
        if compliance.get('flags'):
            st.write("**Compliance Flags:**")
            for flag in compliance['flags']:
                st.write(f"• {flag}")
    
    with col2:
        if compliance.get('recommendations'):
            st.write("**Recommendations:**")
            for rec in compliance['recommendations']:
                st.write(f"• {rec}")

# ============================================================================
# Main Application
# ============================================================================

def main():
    # Header
    st.markdown('<p class="main-header">🏥 Medical Affairs AI Assistant</p>', unsafe_allow_html=True)
    st.markdown("**Multi-Agent System for Evidence Synthesis & Compliant Response Generation**")
    st.divider()
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Azure OpenAI Configuration
        with st.expander("🔐 Azure OpenAI Settings", expanded=not st.session_state.azure_configured):
            azure_endpoint = st.text_input(
                "Azure OpenAI Endpoint",
                value=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                type="default",
                help="Your Azure OpenAI endpoint URL"
            )
            azure_key = st.text_input(
                "Azure OpenAI API Key",
                value=os.getenv("AZURE_OPENAI_API_KEY", ""),
                type="password",
                help="Your Azure OpenAI API key"
            )
            deployment_name = st.text_input(
                "Deployment Name",
                value=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                help="Your model deployment name"
            )
            api_version = st.text_input(
                "API Version",
                value="2025-01-01-preview",
                help="Azure OpenAI API version"
            )
            
            if st.button("💾 Save Azure Config"):
                if azure_endpoint and azure_key and deployment_name:
                    st.session_state.azure_endpoint = azure_endpoint
                    st.session_state.azure_key = azure_key
                    st.session_state.deployment_name = deployment_name
                    st.session_state.api_version = api_version
                    st.session_state.azure_configured = True
                    st.success("✅ Azure OpenAI configured!")
                else:
                    st.error("Please fill in all fields")
        
        # A2A Server Configuration
        with st.expander("🔗 A2A Server Settings", expanded=not st.session_state.a2a_configured):
            a2a_host = st.text_input("A2A Host", value="127.0.0.1")
            a2a_port = st.text_input("A2A Port", value="9099")
            
            if st.button("💾 Save A2A Config"):
                st.session_state.a2a_base = f"http://{a2a_host}:{a2a_port}"
                st.session_state.a2a_configured = True
                st.success(f"✅ A2A configured: {st.session_state.a2a_base}")
        
        st.divider()
        
        # Multi-Agent Workflow
        st.header("🔄 Workflow Overview")
        st.markdown("""
        **Complete Medical Affairs Workflow:**
        
        1️⃣ **Literature Scout** 📚  
        → Retrieves evidence from PubMed, FDA labels
        
        2️⃣ **Evidence Summarizer** 📊  
        → Grades quality, synthesizes findings
        
        3️⃣ **Medical Information Agent** 📝  
        → Formats compliant MI response
        
        4️⃣ **Compliance Guard** ⚠️  
        → Validates for regulatory risks
        
        5️⃣ **PDF Letter Generator** 📄  
        → Creates distribution-ready letter
        
        6️⃣ **CRM Integration** 📊  
        → Logs interaction for audit trail
        
        **Result:** Complete, compliant, trackable MI response in seconds!
        """)
        
        st.divider()
        
        # Agent Information
        st.header("🤖 Agent Details")
        for agent_name, info in AGENT_INFO.items():
            with st.expander(f"{info['icon']} {agent_name}"):
                st.write(f"**{info['description']}**")
                st.write("**Capabilities:**")
                for cap in info['capabilities']:
                    st.write(f"• {cap}")
        
        st.divider()
        
        # Session Statistics
        st.header("📊 Session Stats")
        crm_stats = crm.get_summary_stats()
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Queries", len(st.session_state.history))
        with col_stat2:
            st.metric("CRM Logs", crm_stats.get("total", 0))
        
        if crm_stats.get("total", 0) > 0:
            st.caption(f"✅ Low Risk: {crm_stats['risk_distribution'].get('LOW', 0)}")
            st.caption(f"⚠️ Med/High: {crm_stats['risk_distribution'].get('MEDIUM', 0) + crm_stats['risk_distribution'].get('HIGH', 0)}")
        
        st.divider()
        
        # Quick Actions
        st.header("⚡ Quick Actions")
        
        col_action1, col_action2 = st.columns(2)
        
        with col_action1:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.history = []
                st.success("History cleared!")
        
        with col_action2:
            if st.button("🔄 Clear CRM", use_container_width=True):
                st.session_state.crm_log = []
                st.success("CRM cleared!")
        
        if st.button("📥 Export History", use_container_width=True):
            if st.session_state.history:
                history_json = json.dumps(st.session_state.history, indent=2)
                st.download_button(
                    "Download JSON",
                    history_json,
                    file_name=f"medical_affairs_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    # Main Content Area
    if not st.session_state.azure_configured:
        st.warning("⚠️ Please configure Azure OpenAI in the sidebar to get started")
        return
    
    if not st.session_state.a2a_configured:
        st.warning("⚠️ Please configure A2A Server in the sidebar")
        return
    
    # Initialize kernel
    kernel = init_semantic_kernel(
        st.session_state.azure_endpoint,
        st.session_state.azure_key,
        st.session_state.deployment_name,
        st.session_state.api_version
    )
    
    # Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Literature Scout",
        "📝 Full MI Workflow",
        "⚠️ Compliance Check",
        "📊 CRM Analytics",
        "📜 History"
    ])
    
    # ========================================================================
    # TAB 1: Literature Scout
    # ========================================================================
    with tab1:
        st.header("📚 Literature Scout Agent")
        st.markdown("""
        Query the Literature Scout Agent to retrieve evidence-based medical information 
        from literature, clinical trials, and approved product labeling.
        """)
        
        # Initialize session state for query text
        if 'lit_query_text' not in st.session_state:
            st.session_state.lit_query_text = ""
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.write("**Sample Queries:**")
            st.caption("Click to populate query box")
            for i, sample in enumerate(SAMPLE_PROMPTS["Literature Scout"][:4]):
                if st.button(f"📋 Example {i+1}", key=f"lit_sample_{i}", use_container_width=True):
                    st.session_state.lit_query_text = sample
                    st.rerun()
            
            # Show full sample on hover
            with st.expander("View all examples"):
                for i, sample in enumerate(SAMPLE_PROMPTS["Literature Scout"]):
                    st.caption(f"{i+1}. {sample}")
        
        with col1:
            query_text = st.text_area(
                "Enter your medical affairs query:",
                height=150,
                placeholder="e.g., What is the renal dosing guidance for Kerendia in severe CKD?",
                value=st.session_state.lit_query_text,
                key="lit_query_input"
            )
        
        if st.button("🔍 Search Literature", type="primary", use_container_width=True):
            if query_text:
                with st.spinner("🔄 Literature Scout Agent searching evidence..."):
                    try:
                        result = asyncio.run(call_literature_scout_agent(
                            query_text,
                            st.session_state.a2a_base
                        ))
                        
                        st.success("✅ Evidence retrieved successfully!")
                        
                        st.markdown("### 📄 Evidence Report")
                        st.markdown(result)
                        
                        # Add to history
                        add_to_history({
                            "timestamp": datetime.now().isoformat(),
                            "type": "Literature Scout",
                            "query": query_text,
                            "result": result
                        })
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("Make sure the A2A server is running (execute the notebook cell 8)")
            else:
                st.warning("Please enter a query")
    
    # ========================================================================
    # TAB 2: Full MI Workflow
    # ========================================================================
    with tab2:
        st.header("📝 Full Medical Information Workflow")
        st.markdown("""
        Run the complete multi-agent workflow:
        1. **Literature Scout** retrieves evidence
        2. **MI Agent** formats compliant response
        3. **Compliance Guard** validates for regulatory risks
        """)
        
        # Initialize session state for MI query
        if 'mi_query_text' not in st.session_state:
            st.session_state.mi_query_text = ""
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            st.write("**Sample HCP Inquiries:**")
            st.caption("Click to populate query box")
            for i, sample in enumerate(SAMPLE_PROMPTS["Full MI Workflow"]):
                if st.button(f"📋 Example {i+1}", key=f"mi_sample_{i}", use_container_width=True):
                    st.session_state.mi_query_text = sample
                    st.rerun()
            
            # Show full sample on hover
            with st.expander("View all examples"):
                for i, sample in enumerate(SAMPLE_PROMPTS["Full MI Workflow"]):
                    st.caption(f"{i+1}. {sample}")
        
        with col1:
            mi_query = st.text_area(
                "Enter HCP inquiry:",
                height=150,
                placeholder="e.g., What's the renal dosing guidance for Kerendia in severe CKD?",
                value=st.session_state.mi_query_text,
                key="mi_query_input"
            )
        
        if st.button("▶️ Run Full Workflow", type="primary", use_container_width=True):
            if mi_query:
                progress_bar = st.progress(0, text="Starting workflow...")
                
                try:
                    # Run full workflow
                    progress_bar.progress(10, text="📚 Step 1/3: Literature Scout searching...")
                    results = asyncio.run(run_full_mi_workflow(
                        mi_query,
                        st.session_state.a2a_base,
                        kernel
                    ))
                    
                    progress_bar.progress(100, text="✅ Workflow complete!")
                    progress_bar.empty()
                    
                    # Store results in session state
                    st.session_state.workflow_results = results
                    st.session_state.workflow_query = mi_query
                    st.session_state.workflow_completed = True
                    
                    # Add to history
                    add_to_history({
                        "timestamp": datetime.now().isoformat(),
                        "type": "Full MI Workflow",
                        "query": mi_query,
                        "results": results
                    })
                    
                except Exception as e:
                    progress_bar.empty()
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Make sure the A2A server is running (execute the notebook cell 8)")
                    st.session_state.workflow_completed = False
            else:
                st.warning("Please enter a query")
        
        # Display results from session state (outside button conditional to persist across reruns)
        if st.session_state.get('workflow_completed', False) and st.session_state.get('workflow_results'):
            results = st.session_state.workflow_results
            mi_query = st.session_state.workflow_query
            
            # Display results
            st.success("✅ Medical Affairs workflow completed!")
            
            # Evidence
            with st.expander("📚 Step 1: Evidence from Literature Scout", expanded=True):
                st.markdown(results["evidence"])
            
            # MI Response
            with st.expander("📝 Step 2: Medical Information Response", expanded=True):
                st.markdown(results["mi_response"])
            
            # Compliance
            with st.expander("⚠️ Step 3: Compliance Assessment", expanded=True):
                display_compliance_result(results["compliance"])
            
            # Summary
            st.divider()
            st.subheader("📊 Workflow Summary")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Evidence Retrieved", "✓")
            with col2:
                st.metric("MI Response Generated", "✓")
            with col3:
                risk = results["compliance"].get("risk_level", "UNKNOWN")
                st.metric("Compliance Risk", risk)
            
            # PDF Generation
            st.divider()
            st.subheader("📄 Generate PDF Letter")
            
            col_pdf1, col_pdf2 = st.columns([2, 1])
            with col_pdf1:
                st.info("Generate a professional Medical Information letter in PDF format for distribution to field teams.")
            with col_pdf2:
                if st.button("📄 Generate PDF", type="primary", use_container_width=True):
                    try:
                        # Create output directory
                        os.makedirs("./mi_responses", exist_ok=True)
                        
                        # Generate PDF
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        pdf_filename = f"./mi_responses/MI_Response_{timestamp}.pdf"
                        
                        ref_number = generate_mi_letter_pdf(
                            query=mi_query,
                            evidence=results["evidence"],
                            response=results["mi_response"],
                            compliance_result=results["compliance"],
                            output_filename=pdf_filename
                        )
                        
                        # Read the PDF for download
                        with open(pdf_filename, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        
                        st.success(f"✅ PDF Generated! Reference: {ref_number}")
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download PDF Letter",
                            data=pdf_bytes,
                            file_name=f"Medical_Information_Response_{ref_number}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Store PDF info for CRM logging
                        st.session_state.last_pdf_path = pdf_filename
                        st.session_state.last_ref_number = ref_number
                        
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")
            
            # CRM Integration
            st.divider()
            st.subheader("📊 Log to CRM System")
            
            col_crm1, col_crm2 = st.columns([2, 1])
            with col_crm1:
                st.info("Log this Medical Information interaction to Veeva Medical CRM for compliance tracking and analytics.")
            
            with col_crm2:
                # HCP Information for CRM
                with st.expander("HCP Information", expanded=False):
                    hcp_name = st.text_input("HCP Name", value="Dr. John Smith, MD", key="hcp_name_workflow")
                    hcp_specialty = st.selectbox(
                        "Specialty",
                        ["Cardiology", "Nephrology", "Dermatology", "Endocrinology", "Oncology", "Other"],
                        key="hcp_specialty_workflow"
                    )
                    hcp_institution = st.text_input("Institution", value="University Medical Center", key="hcp_inst_workflow")
                
                if st.button("📊 Log to CRM", type="primary", use_container_width=True):
                    hcp_info = {
                        "name": hcp_name,
                        "specialty": hcp_specialty,
                        "institution": hcp_institution
                    }
                    
                    ref_num = st.session_state.get('last_ref_number', f"MI-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
                    pdf_path = st.session_state.get('last_pdf_path', 'Not Generated')
                    
                    crm_record = crm.log_interaction(
                        hcp_info=hcp_info,
                        query=mi_query,
                        response=results["mi_response"],
                        compliance_result=results["compliance"],
                        ref_number=ref_num,
                        pdf_path=pdf_path
                    )
                    
                    st.success(f"✅ Logged to CRM! Record ID: {crm_record['record_id']}")
                    
                    # Display CRM record summary
                    with st.expander("📋 View CRM Record", expanded=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Record ID:** {crm_record['record_id']}")
                            st.write(f"**MI Reference:** {crm_record['mi_reference']}")
                            st.write(f"**HCP:** {crm_record['hcp_name']}")
                            st.write(f"**Specialty:** {crm_record['hcp_specialty']}")
                            st.write(f"**Institution:** {crm_record['hcp_institution']}")
                        with col_b:
                            st.write(f"**Category:** {crm_record['query_category']}")
                            st.write(f"**Products:** {', '.join(crm_record['products_mentioned'])}")
                            st.write(f"**Risk Level:** {crm_record['compliance_risk']}")
                            st.write(f"**Status:** {crm_record['status']}")
                            st.write(f"**PDF:** {crm_record['pdf_attachment']}")
            
            # Next steps
            st.info("""
            **✅ Workflow Complete! Next Steps:**
            1. 📄 Generate PDF handout (button above)
            2. 📊 Log to CRM system (button above)
            3. 📧 Distribute to field team / HCP
            4. 📁 Archive in Medical Information database
            5. ⚠️ Route to medical reviewer if flagged
            """)
    
    # ========================================================================
    # TAB 3: Compliance Check
    # ========================================================================
    with tab3:
        st.header("⚠️ Compliance Guard Agent")
        st.markdown("""
        Test the Compliance Guard to validate responses for regulatory compliance issues.
        Enter evidence and a proposed response to check for off-label content, promotional language, and other risks.
        """)
        
        # Initialize session state for compliance check
        if 'comp_evidence_text' not in st.session_state:
            st.session_state.comp_evidence_text = ""
        if 'comp_response_text' not in st.session_state:
            st.session_state.comp_response_text = ""
        
        col1, col2 = st.columns(2)
        
        with col1:
            evidence_text = st.text_area(
                "Evidence Base:",
                height=150,
                placeholder="Enter the evidence/labeling information...",
                key="comp_evidence",
                value=st.session_state.comp_evidence_text
            )
        
        with col2:
            response_text = st.text_area(
                "Proposed MI Response:",
                height=150,
                placeholder="Enter the proposed response to HCP...",
                key="comp_response",
                value=st.session_state.comp_response_text
            )
        
        st.write("**Test Scenarios:**")
        scenario_cols = st.columns(4)
        
        test_scenarios = {
            "LOW RISK": {
                "evidence": "FDA Label: Tremfya (guselkumab) is indicated for plaque psoriasis. Dosing: 100mg SC at weeks 0, 4, then every 8 weeks. Renal adjustment: No adjustment needed for mild-moderate impairment.",
                "response": "According to the FDA-approved prescribing information, Tremfya 100mg subcutaneously is administered at weeks 0 and 4, followed by every 8 weeks thereafter. No dose adjustment is required for mild to moderate renal impairment."
            },
            "MEDIUM RISK": {
                "evidence": "FDA Label: Xarelto indicated for AF stroke prevention. Study (Smith 2024): Showed potential benefits in CAD patients in post-hoc analysis.",
                "response": "Xarelto is highly effective for cardiovascular protection in CAD patients and showed superior outcomes compared to competitors."
            },
            "HIGH RISK": {
                "evidence": "FDA Label: Stelara (ustekinumab) indicated for plaque psoriasis in adults. No pediatric indication for psoriasis.",
                "response": "Stelara has shown excellent results in children with pediatric plaque psoriasis and is well-tolerated in pediatric populations."
            },
            "PROMOTIONAL": {
                "evidence": "FDA Label: Tremfya indicated for plaque psoriasis and psoriatic arthritis. Common side effects: upper respiratory infections, headache, injection site reactions.",
                "response": "Tremfya is the best psoriasis treatment on the market with minimal side effects and superior efficacy to all alternatives."
            }
        }
        
        for i, (scenario_name, scenario_data) in enumerate(test_scenarios.items()):
            with scenario_cols[i]:
                if st.button(f"📋 {scenario_name}", use_container_width=True):
                    st.session_state.comp_evidence_text = scenario_data["evidence"]
                    st.session_state.comp_response_text = scenario_data["response"]
                    st.rerun()
        
        if st.button("🔍 Run Compliance Check", type="primary", use_container_width=True):
            if evidence_text and response_text:
                with st.spinner("🔄 Compliance Guard analyzing..."):
                    try:
                        compliance_result = asyncio.run(run_compliance_check(
                            evidence_text,
                            response_text,
                            kernel
                        ))
                        
                        st.success("✅ Compliance check completed!")
                        
                        display_compliance_result(compliance_result)
                        
                        # Add to history
                        add_to_history({
                            "timestamp": datetime.now().isoformat(),
                            "type": "Compliance Check",
                            "evidence": evidence_text,
                            "response": response_text,
                            "result": compliance_result
                        })
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter both evidence and response text")
    
    # ========================================================================
    # TAB 4: CRM Analytics
    # ========================================================================
    with tab4:
        st.header("📊 CRM Analytics Dashboard")
        st.markdown("""
        View Medical Information interaction analytics from the CRM system.
        Track query volumes, compliance risk distribution, and HCP engagement metrics.
        """)
        
        # Get CRM summary stats
        stats = crm.get_summary_stats()
        
        if stats["total"] == 0:
            st.info("📭 No CRM interactions logged yet. Complete a Full MI Workflow and log it to CRM to see analytics.")
        else:
            # Summary Metrics
            st.subheader("📈 Summary Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Interactions", stats["total"])
            with col2:
                st.metric("Pending Review", stats["pending_review"])
            with col3:
                low_risk = stats["risk_distribution"].get("LOW", 0)
                st.metric("Low Risk", low_risk, delta=f"{(low_risk/stats['total']*100):.0f}%")
            with col4:
                high_risk = stats["risk_distribution"].get("HIGH", 0) + stats["risk_distribution"].get("MEDIUM", 0)
                st.metric("Med/High Risk", high_risk, delta=f"{(high_risk/stats['total']*100):.0f}%", delta_color="inverse")
            
            st.divider()
            
            # Risk Distribution
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("🎯 Compliance Risk Distribution")
                risk_data = stats["risk_distribution"]
                for risk_level, count in sorted(risk_data.items()):
                    pct = (count / stats["total"]) * 100
                    if risk_level == "LOW":
                        st.success(f"✅ {risk_level}: {count} ({pct:.1f}%)")
                    elif risk_level == "MEDIUM":
                        st.warning(f"⚠️ {risk_level}: {count} ({pct:.1f}%)")
                    elif risk_level == "HIGH":
                        st.error(f"🚨 {risk_level}: {count} ({pct:.1f}%)")
                    else:
                        st.info(f"❓ {risk_level}: {count} ({pct:.1f}%)")
            
            with col_chart2:
                st.subheader("📋 Query Categories")
                category_data = stats["query_categories"]
                for category, count in sorted(category_data.items(), key=lambda x: x[1], reverse=True):
                    pct = (count / stats["total"]) * 100
                    st.write(f"• **{category}**: {count} ({pct:.1f}%)")
            
            st.divider()
            
            # Recent Interactions Table
            st.subheader("📝 Recent CRM Interactions")
            recent = crm.get_recent_interactions(limit=10)
            
            if recent:
                # Create table data
                table_data = []
                for record in reversed(recent):  # Show most recent first
                    table_data.append({
                        "Timestamp": record["timestamp"][:19],
                        "HCP": record["hcp_name"],
                        "Specialty": record["hcp_specialty"],
                        "Category": record["query_category"],
                        "Products": ", ".join(record["products_mentioned"]),
                        "Risk": record["compliance_risk"],
                        "Status": record["status"]
                    })
                
                st.dataframe(
                    table_data,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Export option
                st.download_button(
                    label="📥 Export CRM Data (JSON)",
                    data=json.dumps(st.session_state.crm_log, indent=2),
                    file_name=f"crm_export_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            # Insights
            st.divider()
            st.subheader("💡 Key Insights")
            
            # Most common category
            if stats["query_categories"]:
                top_category = max(stats["query_categories"].items(), key=lambda x: x[1])
                st.info(f"📊 Most common query category: **{top_category[0]}** ({top_category[1]} requests)")
            
            # Compliance rate
            low_risk_pct = (stats["risk_distribution"].get("LOW", 0) / stats["total"]) * 100
            if low_risk_pct >= 70:
                st.success(f"✅ Strong compliance: {low_risk_pct:.0f}% of responses are low-risk")
            elif low_risk_pct >= 50:
                st.warning(f"⚠️ Moderate compliance: {low_risk_pct:.0f}% of responses are low-risk")
            else:
                st.error(f"🚨 Compliance concern: Only {low_risk_pct:.0f}% of responses are low-risk")
            
            # Review backlog
            if stats["pending_review"] > 0:
                st.warning(f"⏳ {stats['pending_review']} interaction(s) pending medical review")
    
    # ========================================================================
    # TAB 5: History
    # ========================================================================
    with tab5:
        st.header("📜 Query History")
        
        if not st.session_state.history:
            st.info("No history yet. Start by running some queries!")
        else:
            st.write(f"**Total Entries:** {len(st.session_state.history)}")
            
            for i, entry in enumerate(st.session_state.history):
                with st.expander(
                    f"{entry['type']} - {entry['timestamp'][:19]}", 
                    expanded=(i == 0)
                ):
                    st.write(f"**Type:** {entry['type']}")
                    st.write(f"**Timestamp:** {entry['timestamp']}")
                    
                    if 'query' in entry:
                        st.write(f"**Query:** {entry['query']}")
                    
                    if entry['type'] == "Literature Scout":
                        st.markdown("**Result:**")
                        st.markdown(entry['result'])
                    
                    elif entry['type'] == "Full MI Workflow":
                        results = entry['results']
                        st.markdown("**Evidence:**")
                        st.text(results['evidence'][:200] + "...")
                        st.markdown("**MI Response:**")
                        st.text(results['mi_response'][:200] + "...")
                        st.markdown("**Compliance Risk:**")
                        st.write(results['compliance'].get('risk_level', 'UNKNOWN'))
                    
                    elif entry['type'] == "Compliance Check":
                        display_compliance_result(entry['result'])

if __name__ == "__main__":
    main()
