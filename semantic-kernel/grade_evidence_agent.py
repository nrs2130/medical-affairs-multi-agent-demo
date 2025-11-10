"""
GRADE Evidence Assessment Agent
================================

Implements the GRADE (Grading of Recommendations, Assessment, Development and Evaluations)
methodology for assessing the quality of evidence in medical literature.

Reference: GRADE Working Group (https://www.gradeworkinggroup.org/)

Quality of Evidence Levels:
- HIGH: Very confident that true effect lies close to estimate
- MODERATE: Moderately confident; true effect likely close to estimate  
- LOW: Limited confidence; true effect may differ substantially
- VERY LOW: Very little confidence in effect estimate

Factors that LOWER quality:
1. Risk of bias (study limitations)
2. Inconsistency (heterogeneity)
3. Indirectness (applicability)
4. Imprecision (wide confidence intervals, small sample)
5. Publication bias

Factors that RAISE quality:
1. Large magnitude of effect (RR > 2 or < 0.5)
2. Dose-response gradient
3. All plausible confounding would reduce demonstrated effect
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


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
        from dataclasses import asdict
        return asdict(self)


class GRADEEvidenceAgent:
    """
    Agent that performs GRADE evidence quality assessment
    """
    
    def __init__(self):
        self.assessment_history = []
    
    def assess_evidence(self, 
                       study_design: str,
                       sample_size: int,
                       effect_size: float = None,
                       confidence_interval: tuple = None,
                       risk_of_bias: str = "low",
                       consistency: str = "consistent",
                       directness: str = "direct",
                       precision: str = "precise",
                       publication_bias_likely: bool = False,
                       dose_response: bool = False,
                       confounding_reduces_effect: bool = False) -> GRADEAssessment:
        """
        Perform GRADE assessment of evidence quality
        
        Args:
            study_design: "RCT", "observational", or "case_series"
            sample_size: Total number of participants
            effect_size: Effect estimate (e.g., relative risk, odds ratio)
            confidence_interval: Tuple of (lower, upper) CI bounds
            risk_of_bias: "low", "moderate", "high", "very_high"
            consistency: "consistent", "inconsistent"
            directness: "direct", "indirect"
            precision: "precise", "imprecise"
            publication_bias_likely: Boolean
            dose_response: Evidence of dose-response gradient
            confounding_reduces_effect: Plausible confounding would reduce effect
        
        Returns:
            GRADEAssessment object with quality rating
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
        quality_score = self._quality_to_score(initial_quality)
        
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
        final_quality = self._score_to_quality(quality_score)
        
        # Generate certainty rating explanation
        certainty_rating = self._generate_certainty_explanation(final_quality)
        
        # Generate evidence summary
        evidence_summary = self._generate_evidence_summary(
            design_type, sample_size, effect_size, confidence_interval,
            downgrades, upgrades, initial_quality, final_quality
        )
        
        # Determine recommendation strength
        recommendation_strength = self._determine_recommendation_strength(
            final_quality, effect_size
        )
        
        assessment = GRADEAssessment(
            initial_quality=initial_quality,
            final_quality=final_quality,
            downgrades=downgrades,
            upgrades=upgrades,
            certainty_rating=certainty_rating,
            evidence_summary=evidence_summary,
            recommendation_strength=recommendation_strength
        )
        
        self.assessment_history.append(assessment)
        return assessment
    
    def _quality_to_score(self, quality: str) -> int:
        """Convert quality level to numeric score"""
        mapping = {
            "HIGH": 4,
            "MODERATE": 3,
            "LOW": 2,
            "VERY_LOW": 1
        }
        return mapping.get(quality, 1)
    
    def _score_to_quality(self, score: int) -> str:
        """Convert numeric score to quality level"""
        if score >= 4:
            return "HIGH"
        elif score == 3:
            return "MODERATE"
        elif score == 2:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _generate_certainty_explanation(self, quality: str) -> str:
        """Generate explanation of certainty level"""
        explanations = {
            "HIGH": "High certainty: We are very confident that the true effect lies close to that of the estimate of the effect.",
            "MODERATE": "Moderate certainty: We are moderately confident in the effect estimate; the true effect is likely to be close to the estimate of the effect, but there is a possibility that it is substantially different.",
            "LOW": "Low certainty: Our confidence in the effect estimate is limited; the true effect may be substantially different from the estimate of the effect.",
            "VERY_LOW": "Very low certainty: We have very little confidence in the effect estimate; the true effect is likely to be substantially different from the estimate of effect."
        }
        return explanations.get(quality, explanations["VERY_LOW"])
    
    def _generate_evidence_summary(self, design_type: str, sample_size: int,
                                   effect_size: float, ci: tuple,
                                   downgrades: List[str], upgrades: List[str],
                                   initial: str, final: str) -> str:
        """Generate comprehensive evidence summary with detailed rationale"""
        
        summary = "**GRADE EVIDENCE QUALITY ASSESSMENT**\n"
        summary += "=" * 60 + "\n\n"
        
        # Study characteristics
        summary += f"**Study Design:** {design_type}\n"
        summary += f"**Sample Size:** {sample_size} participants\n"
        
        if effect_size and ci:
            summary += f"**Effect Estimate:** RR = {effect_size:.2f} (95% CI: {ci[0]:.2f}-{ci[1]:.2f})\n"
        elif effect_size:
            summary += f"**Effect Estimate:** RR = {effect_size:.2f}\n"
        
        # Initial quality with explanation
        summary += f"\n**Initial GRADE Quality:** {initial}\n"
        summary += f"*Rationale: {self._get_initial_quality_rationale(design_type)}*\n"
        
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
        if final != initial:
            if self._quality_to_score(final) > self._quality_to_score(initial):
                quality_change = f" (↑ from {initial})"
            else:
                quality_change = f" (↓ from {initial})"
        else:
            quality_change = " (unchanged)"
        
        summary += f"\n**Final GRADE Quality:** {final}{quality_change}\n"
        
        # Add interpretation
        summary += f"\n**What This Means:**\n"
        summary += f"{self._generate_quality_interpretation(final, total_downgrades, total_upgrades)}\n"
        
        return summary
    
    def _get_initial_quality_rationale(self, design_type: str) -> str:
        """Explain why study design gets its initial quality"""
        rationales = {
            "Randomized Controlled Trial": "RCTs start at HIGH quality due to randomization reducing bias and confounding",
            "Observational Study": "Observational studies start at LOW quality due to potential confounding and selection bias",
            "Case Series/Report": "Case series start at VERY LOW quality due to lack of comparison group and high risk of bias"
        }
        return rationales.get(design_type, "Study design determines initial quality level per GRADE methodology")
    
    def _generate_quality_interpretation(self, quality: str, downgrades: int, upgrades: int) -> str:
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
        
        interpretation = interpretations.get(quality, interpretations["VERY_LOW"])
        
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
    
    def _determine_recommendation_strength(self, quality: str, 
                                          effect_size: float = None) -> str:
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
    
    def format_grade_table(self, assessments: List[GRADEAssessment]) -> str:
        """Format multiple GRADE assessments as evidence table"""
        
        table = "| Quality | Certainty | Recommendation Strength |\n"
        table += "|---------|-----------|-------------------------|\n"
        
        for assessment in assessments:
            table += f"| {assessment.final_quality} | "
            table += f"{assessment.certainty_rating[:50]}... | "
            table += f"{assessment.recommendation_strength} |\n"
        
        return table


# ============================================================================
# Standalone Functions for Integration
# ============================================================================

def assess_study_grade(study_description: str, study_metadata: Dict[str, Any]) -> GRADEAssessment:
    """
    Convenience function to assess a single study
    
    Args:
        study_description: Text description of the study
        study_metadata: Dict with keys:
            - study_design: str
            - sample_size: int
            - effect_size: float (optional)
            - confidence_interval: tuple (optional)
            - risk_of_bias: str (optional)
            - consistency: str (optional)
            - directness: str (optional)
            - precision: str (optional)
            - publication_bias_likely: bool (optional)
    
    Returns:
        GRADEAssessment object
    """
    agent = GRADEEvidenceAgent()
    return agent.assess_evidence(**study_metadata)


def create_grade_summary(assessments: List[GRADEAssessment]) -> str:
    """Create summary of GRADE assessments across multiple studies"""
    
    if not assessments:
        return "No evidence to assess"
    
    # Count quality levels
    quality_counts = {}
    for assessment in assessments:
        quality = assessment.final_quality.value
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    # Determine overall quality (lowest among studies)
    overall_quality = min([a.final_quality for a in assessments], key=lambda q: q.value[0])
    
    summary = f"**Overall Evidence Quality: {overall_quality.value}**\n\n"
    summary += f"Based on {len(assessments)} studies:\n"
    for quality, count in sorted(quality_counts.items()):
        summary += f"  • {quality}: {count} study/studies\n"
    
    summary += f"\n{assessments[0]._generate_certainty_explanation(overall_quality)}\n"
    
    return summary


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Assess a randomized controlled trial
    agent = GRADEEvidenceAgent()
    
    print("=" * 80)
    print("GRADE Evidence Assessment - Example")
    print("=" * 80)
    
    # Example 1: High-quality RCT
    print("\n📊 Example 1: High-Quality RCT\n")
    assessment1 = agent.assess_evidence(
        study_design="RCT",
        sample_size=500,
        effect_size=1.8,
        confidence_interval=(1.4, 2.3),
        risk_of_bias="low",
        consistency="consistent",
        directness="direct",
        precision="precise",
        publication_bias_likely=False
    )
    
    print(assessment1.evidence_summary)
    print(f"\n{assessment1.certainty_rating}")
    print(f"\n{assessment1.recommendation_strength}\n")
    
    # Example 2: Observational study with large effect
    print("=" * 80)
    print("\n📊 Example 2: Observational Study with Large Effect\n")
    assessment2 = agent.assess_evidence(
        study_design="observational cohort",
        sample_size=1200,
        effect_size=3.5,
        confidence_interval=(2.8, 4.4),
        risk_of_bias="moderate",
        consistency="consistent",
        directness="direct",
        precision="precise",
        publication_bias_likely=False,
        dose_response=True
    )
    
    print(assessment2.evidence_summary)
    print(f"\n{assessment2.certainty_rating}")
    print(f"\n{assessment2.recommendation_strength}\n")
    
    # Example 3: Low-quality study
    print("=" * 80)
    print("\n📊 Example 3: Low-Quality Study with Serious Limitations\n")
    assessment3 = agent.assess_evidence(
        study_design="RCT",
        sample_size=80,
        effect_size=1.2,
        confidence_interval=(0.8, 1.8),
        risk_of_bias="high",
        consistency="inconsistent",
        directness="indirect",
        precision="imprecise",
        publication_bias_likely=True
    )
    
    print(assessment3.evidence_summary)
    print(f"\n{assessment3.certainty_rating}")
    print(f"\n{assessment3.recommendation_strength}\n")
    
    print("=" * 80)


# ============================================================================
# Standalone Function for Compatibility with medical_affairs_app.py
# ============================================================================

def assess_grade_evidence(
    study_design: str,
    sample_size: int,
    effect_size: float = None,
    confidence_interval_lower: float = None,
    confidence_interval_upper: float = None,
    risk_of_bias: str = "low",
    consistency: str = "consistent",
    directness: str = "direct",
    precision: str = "precise",
    publication_bias_likely: bool = False,
    dose_response: bool = False,
    confounding_reduces_effect: bool = False
) -> str:
    """
    Standalone function wrapper for GRADE assessment.
    Creates a GRADEEvidenceAgent instance and performs the assessment.
    
    Returns:
        JSON string representation of the GRADEAssessment
    """
    # Create agent instance
    agent = GRADEEvidenceAgent()
    
    # Convert confidence interval to tuple if bounds provided
    confidence_interval = None
    if confidence_interval_lower is not None and confidence_interval_upper is not None:
        confidence_interval = (confidence_interval_lower, confidence_interval_upper)
    
    # Perform assessment
    assessment = agent.assess_evidence(
        study_design=study_design,
        sample_size=sample_size,
        effect_size=effect_size,
        confidence_interval=confidence_interval,
        risk_of_bias=risk_of_bias,
        consistency=consistency,
        directness=directness,
        precision=precision,
        publication_bias_likely=publication_bias_likely,
        dose_response=dose_response,
        confounding_reduces_effect=confounding_reduces_effect
    )
    
    # Convert to JSON string
    return json.dumps(assessment.to_dict(), indent=2)
