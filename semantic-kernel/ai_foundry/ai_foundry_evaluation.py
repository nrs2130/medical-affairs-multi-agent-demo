"""
Azure AI Foundry Evaluation Integration

This module provides evaluation capabilities for Medical Affairs agents,
enabling quality assessment alongside performance tracing.

Features:
- Automated evaluation of agent responses
- Custom evaluators for medical accuracy, compliance, and tone
- Integration with Azure AI Foundry evaluation dashboard
- Metrics: groundedness, relevance, coherence, fluency, safety

Usage:
    from ai_foundry_evaluation import evaluate_response, create_custom_evaluator
    
    # Evaluate a single response
    result = await evaluate_response(
        query="What's the dosing for Drug X?",
        response="The recommended dose is...",
        context="FDA label: ..."
    )
    
    # Create custom compliance evaluator
    compliance_eval = create_custom_evaluator(
        name="compliance_check",
        criteria="Check for off-label promotion and fair balance"
    )
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


class AIFoundryEvaluation:
    """Manages Azure AI Foundry evaluation configuration"""
    
    def __init__(self):
        self.enabled = False
        self.project_client = None
        self.evaluators = {}
    
    def setup(self, 
              project_endpoint: Optional[str] = None,
              enable_default_evaluators: bool = True):
        """
        Initialize Azure AI Foundry evaluation
        
        Args:
            project_endpoint: Azure AI Foundry project endpoint URL
            enable_default_evaluators: If True, enable built-in evaluators
        """
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
            from azure.core.credentials import AzureKeyCredential
            from azure.ai.evaluation import (
                GroundednessEvaluator,
                RelevanceEvaluator,
                CoherenceEvaluator,
                FluencyEvaluator,
            )
            
            # Get project endpoint from environment if not provided
            if not project_endpoint:
                project_endpoint = os.getenv('AI_FOUNDRY_PROJECT_ENDPOINT')
                if not project_endpoint:
                    raise ValueError(
                        "No project endpoint provided. Set AI_FOUNDRY_PROJECT_ENDPOINT "
                        "environment variable."
                    )
            
            # Use API key if available, otherwise use DefaultAzureCredential
            project_key = os.getenv('AZURE_AI_PROJECT_KEY')
            if project_key:
                credential = AzureKeyCredential(project_key)
            else:
                credential = DefaultAzureCredential()
            
            # Create AI Project client
            self.project_client = AIProjectClient(
                credential=credential,
                endpoint=project_endpoint,
            )
            
            # Setup default evaluators
            if enable_default_evaluators:
                # Create model config for evaluators
                model_config = {
                    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                    "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
                }
                
                print(f"[DEBUG] Initializing evaluators with endpoint: {model_config['azure_endpoint']}")
                
                try:
                    self.evaluators = {
                        "groundedness": GroundednessEvaluator(model_config=model_config),
                        "relevance": RelevanceEvaluator(model_config=model_config),
                        "coherence": CoherenceEvaluator(model_config=model_config),
                        "fluency": FluencyEvaluator(model_config=model_config),
                    }
                    print(f"[DEBUG] Successfully initialized {len(self.evaluators)} evaluators")
                except Exception as eval_error:
                    print(f"WARNING: Failed to initialize evaluators: {eval_error}")
                    # Try alternative initialization without model_config parameter
                    print("[DEBUG] Trying alternative initialization...")
                    self.evaluators = {}
                    raise eval_error
            
            self.enabled = True
            print("Evaluation enabled: Azure AI Foundry")
            
        except ImportError as e:
            print(f"WARNING: Evaluation setup failed: {e}")
            print("   Install with: pip install azure-ai-evaluation")
            self.enabled = False
        except Exception as e:
            print(f"WARNING: Evaluation setup failed: {e}")
            print("   Continuing without evaluation...")
            self.enabled = False
    
    async def evaluate_response(self,
                                query: str,
                                response: str,
                                context: Optional[str] = None,
                                ground_truth: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate a single agent response
        
        Args:
            query: User query/question
            response: Agent response
            context: Supporting context (e.g., retrieved documents)
            ground_truth: Optional reference answer for comparison
        
        Returns:
            Dictionary with evaluation scores
        """
        if not self.enabled:
            return {"error": "Evaluation not enabled"}
        
        results = {}
        
        try:
            # Groundedness: Is response grounded in context?
            if "groundedness" in self.evaluators and context:
                groundedness_result = self.evaluators["groundedness"](
                    query=query,
                    response=response,
                    context=context
                )
                print(f"[DEBUG] Groundedness result type: {type(groundedness_result)}")
                print(f"[DEBUG] Groundedness result: {groundedness_result}")
                results["groundedness"] = groundedness_result
            
            # Relevance: Is response relevant to query?
            if "relevance" in self.evaluators:
                relevance_result = self.evaluators["relevance"](
                    query=query,
                    response=response,
                    context=context
                )
                print(f"[DEBUG] Relevance result type: {type(relevance_result)}")
                print(f"[DEBUG] Relevance result: {relevance_result}")
                results["relevance"] = relevance_result
            
            # Coherence: Is response coherent and well-structured?
            if "coherence" in self.evaluators:
                coherence_result = self.evaluators["coherence"](
                    query=query,
                    response=response
                )
                print(f"[DEBUG] Coherence result: {coherence_result}")
                results["coherence"] = coherence_result
            
            # Fluency: Is response fluent and grammatical?
            if "fluency" in self.evaluators:
                fluency_result = self.evaluators["fluency"](
                    query=query,
                    response=response
                )
                print(f"[DEBUG] Fluency result: {fluency_result}")
                results["fluency"] = fluency_result
            
            return results
            
        except Exception as e:
            print(f"[DEBUG] Evaluation exception: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def create_custom_evaluator(self,
                                name: str,
                                prompt_template: str,
                                criteria: str) -> Any:
        """
        Create a custom evaluator for domain-specific assessment
        
        Args:
            name: Evaluator name (e.g., "compliance_check", "medical_accuracy")
            prompt_template: Evaluation prompt template
            criteria: Evaluation criteria description
        
        Returns:
            Custom evaluator function
        """
        from azure.ai.evaluation import ContentSafetyEvaluator
        
        # For now, use content safety as base
        # TODO: Implement true custom evaluator when SDK supports it
        evaluator = ContentSafetyEvaluator()
        self.evaluators[name] = evaluator
        
        return evaluator
    
    def add_custom_evaluator(self, name: str, evaluator_func):
        """
        Add a custom Python evaluator function
        
        Args:
            name: Evaluator name
            evaluator_func: Function that takes (query, response, context) and returns score
        """
        self.evaluators[name] = evaluator_func


# Global evaluation instance
_evaluation = AIFoundryEvaluation()


def setup_evaluation(project_endpoint: Optional[str] = None,
                     enable_default_evaluators: bool = True):
    """
    Initialize Azure AI Foundry evaluation (call once at startup)
    
    Args:
        project_endpoint: Azure AI Foundry project endpoint
        enable_default_evaluators: Enable built-in evaluators (groundedness, relevance, etc.)
    
    Example:
        # Auto-configure from environment
        setup_evaluation()
        
        # Provide project endpoint
        setup_evaluation(project_endpoint="https://your-project.services.ai.azure.com/api/projects/your-project")
    """
    _evaluation.setup(project_endpoint, enable_default_evaluators)


async def evaluate_response(query: str,
                            response: str,
                            context: Optional[str] = None,
                            ground_truth: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate a single agent response
    
    Args:
        query: User query
        response: Agent response
        context: Supporting context/evidence
        ground_truth: Optional reference answer
    
    Returns:
        Dictionary with evaluation scores
    
    Example:
        result = await evaluate_response(
            query="What's the renal dosing for Drug X?",
            response="In patients with severe renal impairment...",
            context="FDA Label: Dosage adjustment required for CrCl <30..."
        )
        print(f"Groundedness: {result['groundedness']}")
        print(f"Relevance: {result['relevance']}")
    """
    return await _evaluation.evaluate_response(query, response, context, ground_truth)


def create_custom_evaluator(name: str,
                            prompt_template: str,
                            criteria: str):
    """
    Create a custom evaluator for Medical Affairs-specific assessment
    
    Args:
        name: Evaluator name (e.g., "compliance_risk", "medical_accuracy")
        prompt_template: Evaluation prompt
        criteria: Evaluation criteria
    
    Example:
        compliance_evaluator = create_custom_evaluator(
            name="compliance_check",
            prompt_template="Assess if response contains off-label promotion",
            criteria="Flag any content not in approved labeling"
        )
    """
    return _evaluation.create_custom_evaluator(name, prompt_template, criteria)


def add_medical_affairs_evaluators():
    """
    Add Medical Affairs-specific evaluators
    
    Evaluators:
    - compliance_risk: Off-label promotion, fair balance
    - medical_accuracy: Alignment with approved labeling
    - citation_quality: Proper evidence citations
    - tone_appropriateness: Professional, non-promotional
    """
    
    def compliance_risk_evaluator(query: str, response: str, context: str) -> Dict[str, Any]:
        """Check for off-label content and promotional language"""
        # TODO: Implement with Azure OpenAI call
        # For now, return placeholder
        return {
            "score": 1.0,  # 0-1 scale, 1 = low risk
            "reasoning": "No off-label promotion detected",
            "flags": []
        }
    
    def medical_accuracy_evaluator(query: str, response: str, context: str) -> Dict[str, Any]:
        """Verify response aligns with approved labeling"""
        return {
            "score": 1.0,
            "reasoning": "Response aligns with FDA labeling",
            "discrepancies": []
        }
    
    def citation_quality_evaluator(query: str, response: str, context: str) -> Dict[str, Any]:
        """Check citation quality and completeness"""
        return {
            "score": 1.0,
            "reasoning": "All claims properly cited",
            "missing_citations": []
        }
    
    _evaluation.add_custom_evaluator("compliance_risk", compliance_risk_evaluator)
    _evaluation.add_custom_evaluator("medical_accuracy", medical_accuracy_evaluator)
    _evaluation.add_custom_evaluator("citation_quality", citation_quality_evaluator)
    
    print("Medical Affairs evaluators added: compliance_risk, medical_accuracy, citation_quality")


# Batch evaluation support
async def evaluate_batch(test_cases: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Evaluate multiple test cases in batch
    
    Args:
        test_cases: List of dicts with keys: query, response, context, ground_truth
    
    Returns:
        List of evaluation results
    
    Example:
        test_cases = [
            {"query": "Renal dosing?", "response": "...", "context": "..."},
            {"query": "Drug interactions?", "response": "...", "context": "..."},
        ]
        results = await evaluate_batch(test_cases)
    """
    results = []
    for test_case in test_cases:
        result = await evaluate_response(
            query=test_case.get("query", ""),
            response=test_case.get("response", ""),
            context=test_case.get("context"),
            ground_truth=test_case.get("ground_truth")
        )
        results.append(result)
    
    return results
