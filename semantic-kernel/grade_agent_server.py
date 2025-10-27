"""
GRADE Evidence Assessment Agent - A2A Server
Standalone agent for GRADE (Grading of Recommendations Assessment, Development and Evaluation) methodology

This agent provides official GRADE Working Group methodology for systematic evidence quality assessment.
It can be called via the Agent-to-Agent (A2A) protocol for integration with multi-agent workflows.
"""

import asyncio
import json
from typing import Dict, Any
from a2a.server import A2AServer
from grade_evidence_agent import GRADEEvidenceAgent

# Create A2A server for GRADE assessment
server = A2AServer(
    name="GRADE Evidence Assessment Agent",
    description="""Official GRADE methodology for systematic evidence quality assessment.
    
Capabilities:
- Assigns evidence quality levels: HIGH ⊕⊕⊕⊕, MODERATE ⊕⊕⊕○, LOW ⊕⊕○○, VERY_LOW ⊕○○○
- Evaluates 5 downgrade factors (risk of bias, inconsistency, indirectness, imprecision, publication bias)
- Evaluates 3 upgrade factors (large effect, dose-response, confounding reduction)
- Generates certainty ratings and recommendation strength
- Based on GRADE Working Group standards

Input format (JSON):
{
  "study_design": "rct|observational|case_series|expert_opinion|unclear",
  "sample_size": <number or null>,
  "risk_of_bias": "low|moderate|high|very_high",
  "consistency": "consistent|inconsistent",
  "directness": "direct|indirect",
  "precision": "precise|imprecise",
  "publication_bias_likely": true/false,
  "dose_response": true/false,
  "confounding_reduces_effect": true/false
}

Output format (JSON):
{
  "final_quality": "HIGH|MODERATE|LOW|VERY_LOW",
  "certainty_rating": "description text",
  "recommendation_strength": "STRONG|CONDITIONAL",
  "evidence_summary": "detailed explanation"
}
""",
    host="127.0.0.1",
    port=9100,  # Different port from Literature Scout (9099)
    version="1.0.0"
)

# Initialize GRADE agent
grade_agent = GRADEEvidenceAgent()


def parse_grade_parameters(message_text: str) -> Dict[str, Any]:
    """
    Parse GRADE parameters from message text.
    Expects JSON format or attempts to extract parameters.
    """
    try:
        # Try direct JSON parsing
        params = json.loads(message_text)
        return params
    except json.JSONDecodeError:
        # If not JSON, return error message
        return {
            "error": "Invalid input format. Please provide parameters in JSON format.",
            "expected_format": {
                "study_design": "rct|observational|case_series|expert_opinion|unclear",
                "sample_size": "<number or null>",
                "risk_of_bias": "low|moderate|high|very_high",
                "consistency": "consistent|inconsistent",
                "directness": "direct|indirect",
                "precision": "precise|imprecise",
                "publication_bias_likely": "true/false",
                "dose_response": "true/false",
                "confounding_reduces_effect": "true/false"
            }
        }


@server.on_message()
async def handle_grade_assessment(message: dict) -> dict:
    """
    Handle incoming GRADE assessment requests.
    
    Args:
        message: A2A message containing GRADE parameters
        
    Returns:
        GRADE assessment results in A2A response format
    """
    try:
        # Extract message text
        parts = message.get('parts', [])
        if not parts or not parts[0].get('text'):
            return {
                "parts": [{
                    "text": json.dumps({
                        "error": "No message text provided",
                        "usage": "Send GRADE parameters as JSON in message text"
                    }, indent=2)
                }]
            }
        
        message_text = parts[0]['text']
        
        # Parse parameters
        params = parse_grade_parameters(message_text)
        
        # Check for parsing errors
        if "error" in params:
            return {
                "parts": [{
                    "text": json.dumps(params, indent=2)
                }]
            }
        
        # Extract parameters with defaults
        study_design = params.get("study_design", "unclear")
        sample_size = params.get("sample_size")
        risk_of_bias = params.get("risk_of_bias", "moderate")
        consistency = params.get("consistency", "consistent")
        directness = params.get("directness", "direct")
        precision = params.get("precision", "precise")
        publication_bias_likely = params.get("publication_bias_likely", False)
        dose_response = params.get("dose_response", False)
        confounding_reduces_effect = params.get("confounding_reduces_effect", False)
        
        # Perform GRADE assessment
        assessment = grade_agent.assess_evidence(
            study_design=study_design,
            sample_size=sample_size,
            risk_of_bias=risk_of_bias,
            consistency=consistency,
            directness=directness,
            precision=precision,
            publication_bias_likely=publication_bias_likely,
            dose_response=dose_response,
            confounding_reduces_effect=confounding_reduces_effect
        )
        
        # Format response
        grade_symbols = {
            "HIGH": "⊕⊕⊕⊕",
            "MODERATE": "⊕⊕⊕○",
            "LOW": "⊕⊕○○",
            "VERY_LOW": "⊕○○○"
        }
        
        result = {
            "final_quality": assessment.final_quality.value,
            "quality_symbol": grade_symbols.get(assessment.final_quality.value, "?"),
            "certainty_rating": assessment.certainty_rating,
            "recommendation_strength": assessment.recommendation_strength,
            "evidence_summary": assessment.evidence_summary,
            "input_parameters": {
                "study_design": study_design,
                "sample_size": sample_size,
                "risk_of_bias": risk_of_bias,
                "consistency": consistency,
                "directness": directness,
                "precision": precision,
                "publication_bias_likely": publication_bias_likely,
                "dose_response": dose_response,
                "confounding_reduces_effect": confounding_reduces_effect
            }
        }
        
        return {
            "parts": [{
                "text": json.dumps(result, indent=2)
            }]
        }
        
    except Exception as e:
        # Return error in A2A format
        return {
            "parts": [{
                "text": json.dumps({
                    "error": f"GRADE assessment failed: {str(e)}",
                    "type": type(e).__name__
                }, indent=2)
            }]
        }


if __name__ == "__main__":
    print("🔬 Starting GRADE Evidence Assessment Agent...")
    print(f"   Server: {server.name}")
    print(f"   Host: {server.host}")
    print(f"   Port: {server.port}")
    print(f"   URL: http://{server.host}:{server.port}")
    print("\n⊕⊕⊕⊕ GRADE Agent is ready to assess evidence quality!")
    print("\nExample request:")
    print(json.dumps({
        "study_design": "rct",
        "sample_size": 500,
        "risk_of_bias": "low",
        "consistency": "consistent",
        "directness": "direct",
        "precision": "precise",
        "publication_bias_likely": False,
        "dose_response": True,
        "confounding_reduces_effect": False
    }, indent=2))
    
    # Run the server
    asyncio.run(server.run())
