"""
GRADE Evidence Assessment Agent - Microsoft Agent Framework Version
====================================================================

Implements the GRADE (Grading of Recommendations, Assessment, Development and Evaluations)
methodology for assessing the quality of evidence in medical literature.

This version uses Microsoft Agent Framework with:
- AzureOpenAIChatClient for agent creation
- Custom function tools for GRADE assessment
- A2A protocol support
- MCP server capability

Reference: GRADE Working Group (https://www.gradeworkinggroup.org/)
"""

import asyncio
import json
from typing import Annotated, Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import ChatAgent
from azure.identity.aio import AzureCliCredential
from pydantic import Field


class EvidenceQuality(Enum):
    """GRADE evidence quality levels"""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"


class StudyDesign(Enum):
    """Study design types with initial GRADE quality"""
    RCT = ("Randomized Controlled Trial", EvidenceQuality.HIGH)
    OBSERVATIONAL = ("Observational Study", EvidenceQuality.LOW)
    CASE_SERIES = ("Case Series/Report", EvidenceQuality.VERY_LOW)


@dataclass
class GRADEAssessment:
    """Result of GRADE evidence assessment"""
    initial_quality: str
    final_quality: str
    downgrades: List[str]
    upgrades: List[str]
    certainty_rating: str
    evidence_summary: str
    recommendation_strength: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


# ============================================================================
# GRADE Assessment Functions (Exposed as Agent Tools)
# ============================================================================

def _quality_to_score(quality: str) -> int:
    """Convert quality level to numeric score"""
    mapping = {
        "HIGH": 4,
        "MODERATE": 3,
        "LOW": 2,
        "VERY_LOW": 1
    }
    return mapping.get(quality, 1)


def _score_to_quality(score: int) -> str:
    """Convert numeric score to quality level"""
    if score >= 4:
        return "HIGH"
    elif score == 3:
        return "MODERATE"
    elif score == 2:
        return "LOW"
    else:
        return "VERY_LOW"


def _get_initial_quality_rationale(design_type: str) -> str:
    """Explain why study design gets its initial quality"""
    rationales = {
        "Randomized Controlled Trial": "RCTs start at HIGH quality due to randomization reducing bias and confounding",
        "Observational Study": "Observational studies start at LOW quality due to potential confounding and selection bias",
        "Case Series/Report": "Case series start at VERY LOW quality due to lack of comparison group and high risk of bias"
    }
    return rationales.get(design_type, "Study design determines initial quality level per GRADE methodology")


def _generate_certainty_explanation(quality: str) -> str:
    """Generate explanation of certainty level"""
    explanations = {
        "HIGH": "High certainty: We are very confident that the true effect lies close to that of the estimate of the effect.",
        "MODERATE": "Moderate certainty: We are moderately confident in the effect estimate; the true effect is likely to be close to the estimate of the effect, but there is a possibility that it is substantially different.",
        "LOW": "Low certainty: Our confidence in the effect estimate is limited; the true effect may be substantially different from the estimate of the effect.",
        "VERY_LOW": "Very low certainty: We have very little confidence in the effect estimate; the true effect is likely to be substantially different from the estimate of effect."
    }
    return explanations.get(quality, "Unknown quality level")


def _generate_quality_interpretation(quality: str, downgrades: int, upgrades: int) -> str:
    """Generate plain-language interpretation of the GRADE rating"""
    
    interpretations = {
        "HIGH": (
            "The evidence is of HIGH quality. We can be very confident that the true effect "
            "is close to what the study found. Further research is very unlikely to change "
            "our confidence in the estimate of effect."
        ),
        "MODERATE": (
            "The evidence is of MODERATE quality. We are moderately confident in the effect estimate. "
            "The true effect is likely close to the estimate, but there is a possibility it could be "
            "substantially different. Further research may have an important impact on our confidence."
        ),
        "LOW": (
            "The evidence is of LOW quality. Our confidence in the effect estimate is limited. "
            "The true effect may be substantially different from the estimate. Further research is "
            "very likely to have an important impact on our confidence and may change the estimate."
        ),
        "VERY_LOW": (
            "The evidence is of VERY LOW quality. We have very little confidence in the effect estimate. "
            "The true effect is likely to be substantially different from the estimate. Any estimate "
            "of effect is very uncertain and should be interpreted with extreme caution."
        )
    }
    
    interpretation = interpretations.get(quality, "Unknown quality level")
    
    # Add context about adjustments
    if downgrades > 0 and upgrades > 0:
        interpretation += f"\n\nNote: Quality was downgraded {downgrades} level(s) due to study limitations, "
        interpretation += f"but upgraded {upgrades} level(s) due to strong supporting factors."
    elif downgrades > 0:
        interpretation += f"\n\nNote: Quality was downgraded {downgrades} level(s) from the initial assessment "
        interpretation += "due to identified limitations in the evidence."
    elif upgrades > 0:
        interpretation += f"\n\nNote: Quality was upgraded {upgrades} level(s) from the initial assessment "
        interpretation += "due to strong supporting factors (e.g., large effect size, dose-response gradient)."
    
    return interpretation


def _determine_recommendation_strength(quality: str, effect_size: Optional[float] = None) -> str:
    """Determine strength of recommendation based on GRADE"""
    
    if quality == "HIGH":
        if effect_size and effect_size >= 2.0:
            return "STRONG recommendation - High quality evidence, large effect"
        else:
            return "STRONG recommendation - High quality evidence"
    
    elif quality == "MODERATE":
        if effect_size and effect_size >= 2.0:
            return "STRONG recommendation - Moderate quality evidence, large effect"
        else:
            return "CONDITIONAL recommendation - Moderate quality evidence"
    
    elif quality == "LOW":
        return "CONDITIONAL recommendation - Low quality evidence"
    
    else:  # VERY_LOW
        return "WEAK recommendation - Very low quality evidence, consider expert opinion"


def assess_grade_evidence(
    study_design: Annotated[str, Field(description="Study design type: 'RCT', 'observational', or 'case_series'")],
    sample_size: Annotated[int, Field(description="Total number of participants in the study")],
    effect_size: Annotated[Optional[float], Field(description="Effect estimate (e.g., relative risk, odds ratio)")] = None,
    confidence_interval_lower: Annotated[Optional[float], Field(description="Lower bound of 95% confidence interval")] = None,
    confidence_interval_upper: Annotated[Optional[float], Field(description="Upper bound of 95% confidence interval")] = None,
    risk_of_bias: Annotated[str, Field(description="Risk of bias level: 'low', 'moderate', 'high', or 'very_high'")] = "low",
    consistency: Annotated[str, Field(description="Consistency of results: 'consistent' or 'inconsistent'")] = "consistent",
    directness: Annotated[str, Field(description="Directness of evidence: 'direct' or 'indirect'")] = "direct",
    precision: Annotated[str, Field(description="Precision of estimates: 'precise' or 'imprecise'")] = "precise",
    publication_bias_likely: Annotated[bool, Field(description="Whether publication bias is likely")] = False,
    dose_response: Annotated[bool, Field(description="Evidence of dose-response gradient")] = False,
    confounding_reduces_effect: Annotated[bool, Field(description="Plausible confounding would reduce demonstrated effect")] = False
) -> str:
    """
    Perform GRADE assessment of evidence quality for medical research.
    
    Returns a detailed JSON string with the GRADE assessment including quality rating,
    adjustments, and recommendations.
    """
    
    # Determine initial quality based on study design
    if "rct" in study_design.lower() or "randomized" in study_design.lower():
        initial_quality = "HIGH"
        design_type = "Randomized Controlled Trial"
    elif "observational" in study_design.lower() or "cohort" in study_design.lower() or "case-control" in study_design.lower():
        initial_quality = "LOW"
        design_type = "Observational Study"
    else:
        initial_quality = "VERY_LOW"
        design_type = "Case Series/Report"
    
    # Track downgrades and upgrades
    downgrades = []
    upgrades = []
    quality_score = _quality_to_score(initial_quality)
    
    # ====================================================================
    # FACTORS THAT LOWER QUALITY
    # ====================================================================
    
    # 1. Risk of Bias (study limitations)
    if risk_of_bias == "moderate":
        downgrades.append("Risk of bias: Moderate study limitations (-1)")
        quality_score -= 1
    elif risk_of_bias == "high":
        downgrades.append("Risk of bias: Serious study limitations (-1)")
        quality_score -= 1
    elif risk_of_bias == "very_high":
        downgrades.append("Risk of bias: Very serious study limitations (-2)")
        quality_score -= 2
    
    # 2. Inconsistency (heterogeneity across studies)
    if consistency == "inconsistent":
        downgrades.append("Inconsistency: Unexplained heterogeneity in results (-1)")
        quality_score -= 1
    
    # 3. Indirectness (PICO doesn't match question)
    if directness == "indirect":
        downgrades.append("Indirectness: Evidence from different population/intervention (-1)")
        quality_score -= 1
    
    # 4. Imprecision (wide CIs, small sample)
    if precision == "imprecise":
        downgrades.append("Imprecision: Wide confidence intervals or small sample size (-1)")
        quality_score -= 1
    elif sample_size < 100:
        downgrades.append(f"Imprecision: Very small sample size (n={sample_size}) (-1)")
        quality_score -= 1
    
    # 5. Publication Bias
    if publication_bias_likely:
        downgrades.append("Publication bias: Suspected selective reporting (-1)")
        quality_score -= 1
    
    # ====================================================================
    # FACTORS THAT RAISE QUALITY (only for observational studies)
    # ====================================================================
    
    if initial_quality in ["LOW", "VERY_LOW"]:
        
        # 1. Large magnitude of effect
        if effect_size is not None:
            if effect_size >= 2.0 or effect_size <= 0.5:
                upgrades.append(f"Large effect size (RR={effect_size:.2f}) (+1)")
                quality_score += 1
            if effect_size >= 5.0 or effect_size <= 0.2:
                upgrades.append(f"Very large effect size (RR={effect_size:.2f}) (+1 additional)")
                quality_score += 1
        
        # 2. Dose-response gradient
        if dose_response:
            upgrades.append("Dose-response gradient observed (+1)")
            quality_score += 1
        
        # 3. Plausible confounding would reduce effect
        if confounding_reduces_effect:
            upgrades.append("All plausible confounding would reduce demonstrated effect (+1)")
            quality_score += 1
    
    # Convert final score back to quality level
    final_quality = _score_to_quality(quality_score)
    
    # Generate evidence summary
    summary = "**GRADE EVIDENCE QUALITY ASSESSMENT**\n"
    summary += "=" * 60 + "\n\n"
    
    # Study characteristics
    summary += f"**Study Design:** {design_type}\n"
    summary += f"**Sample Size:** {sample_size} participants\n"
    
    ci = None
    if confidence_interval_lower is not None and confidence_interval_upper is not None:
        ci = (confidence_interval_lower, confidence_interval_upper)
        summary += f"**Effect Estimate:** RR = {effect_size:.2f} (95% CI: {ci[0]:.2f}-{ci[1]:.2f})\n"
    elif effect_size:
        summary += f"**Effect Estimate:** RR = {effect_size:.2f}\n"
    
    # Initial quality with explanation
    summary += f"\n**Initial GRADE Quality:** {initial_quality}\n"
    summary += f"*Rationale: {_get_initial_quality_rationale(design_type)}*\n"
    
    # Quality adjustments
    total_downgrades = len(downgrades)
    total_upgrades = len(upgrades)
    
    if downgrades or upgrades:
        summary += f"\n**Quality Adjustments:**\n"
        
        if downgrades:
            summary += f"\n  **Downgrades (↓{total_downgrades}):** Quality reduced due to:\n"
            for downgrade in downgrades:
                summary += f"    • {downgrade}\n"
        
        if upgrades:
            summary += f"\n  **Upgrades (↑{total_upgrades}):** Quality increased due to:\n"
            for upgrade in upgrades:
                summary += f"    • {upgrade}\n"
    else:
        summary += f"\n**No Quality Adjustments:** Evidence maintains initial quality level.\n"
    
    # Final quality with visual indicator
    quality_change = ""
    if final_quality != initial_quality:
        if _quality_to_score(final_quality) > _quality_to_score(initial_quality):
            quality_change = f" (↑ from {initial_quality})"
        else:
            quality_change = f" (↓ from {initial_quality})"
    else:
        quality_change = " (unchanged)"
    
    summary += f"\n**Final GRADE Quality:** {final_quality}{quality_change}\n"
    
    # Add interpretation
    summary += f"\n**What This Means:**\n"
    summary += f"{_generate_quality_interpretation(final_quality, total_downgrades, total_upgrades)}\n"
    
    # Create assessment object
    assessment = GRADEAssessment(
        initial_quality=initial_quality,
        final_quality=final_quality,
        downgrades=downgrades,
        upgrades=upgrades,
        certainty_rating=_generate_certainty_explanation(final_quality),
        evidence_summary=summary,
        recommendation_strength=_determine_recommendation_strength(final_quality, effect_size)
    )
    
    # Return as JSON string
    return json.dumps(assessment.to_dict(), indent=2)


# ============================================================================
# Agent Creation Function
# ============================================================================

async def create_grade_agent() -> ChatAgent:
    """
    Create a GRADE Evidence Assessment Agent using Microsoft Agent Framework.
    
    Returns:
        ChatAgent configured with GRADE assessment capabilities
    """
    
    # Instructions for the GRADE agent
    instructions = """You are a GRADE Evidence Assessment Agent specializing in evaluating the quality of medical research evidence.

Your role is to:
1. Assess the quality of medical evidence using the GRADE (Grading of Recommendations, Assessment, Development and Evaluations) methodology
2. Provide detailed explanations of quality ratings
3. Identify factors that raise or lower evidence quality
4. Generate recommendation strengths based on evidence quality

When assessing evidence, you should:
- Use the assess_grade_evidence function with appropriate parameters
- Explain the GRADE methodology to users when asked
- Be thorough in identifying study limitations and strengths
- Provide clear, actionable recommendations

GRADE Quality Levels:
- HIGH: Very confident that true effect lies close to estimate
- MODERATE: Moderately confident; true effect likely close to estimate
- LOW: Limited confidence; true effect may differ substantially
- VERY LOW: Very little confidence in effect estimate

Always provide detailed rationale for your assessments and help users understand the clinical implications."""
    
    # Create Azure OpenAI Chat Client
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())
    
    # Create agent with GRADE assessment tool
    agent = chat_client.create_agent(
        name="GRADE_Evidence_Agent",
        instructions=instructions,
        tools=assess_grade_evidence
    )
    
    return agent


# ============================================================================
# MCP Server Exposure
# ============================================================================

async def create_grade_mcp_server():
    """
    Create an MCP server that exposes the GRADE agent as a service.
    
    This allows other agents to call the GRADE agent via the MCP protocol.
    """
    agent = await create_grade_agent()
    mcp_server = agent.as_mcp_server()
    return mcp_server


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Example usage of the GRADE Evidence Assessment Agent"""
    
    print("=" * 80)
    print("GRADE Evidence Assessment Agent - Microsoft Agent Framework")
    print("=" * 80)
    
    # Create the agent
    agent = await create_grade_agent()
    
    # Example 1: Assess a high-quality RCT
    print("\n📊 Example 1: Assessing a High-Quality RCT\n")
    
    query1 = """Please assess the following study using GRADE methodology:
    - Study design: Randomized Controlled Trial
    - Sample size: 500 participants
    - Effect size (RR): 1.8
    - Confidence interval: 1.4 to 2.3
    - Risk of bias: Low
    - Consistency: Consistent across trials
    - Directness: Direct evidence
    - Precision: Precise estimates
    - Publication bias: Not suspected"""
    
    result1 = await agent.run(query1)
    print(result1.text)
    
    # Example 2: Assess observational study with large effect
    print("\n" + "=" * 80)
    print("\n📊 Example 2: Assessing Observational Study with Large Effect\n")
    
    query2 = """Please assess this observational study:
    - Study design: Cohort study (observational)
    - Sample size: 1200 participants
    - Effect size (RR): 3.5
    - Confidence interval: 2.8 to 4.4
    - Risk of bias: Moderate
    - Dose-response gradient: Yes, observed
    - Consistency: Consistent
    - Directness: Direct
    - Precision: Precise"""
    
    result2 = await agent.run(query2)
    print(result2.text)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
