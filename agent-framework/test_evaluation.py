"""Test Azure AI Foundry Evaluation Setup"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_evaluation():
    """Test evaluation setup and basic functionality"""
    print("\n" + "="*60)
    print("TESTING AZURE AI FOUNDRY EVALUATION")
    print("="*60 + "\n")
    
    # Step 1: Import
    print("Step 1: Importing evaluation module...")
    try:
        from ai_foundry.ai_foundry_evaluation import setup_evaluation, evaluate_response
        print("SUCCESS: Module imported\n")
    except ImportError as e:
        print(f"ERROR: Failed to import - {e}")
        print("Install with: pip install azure-ai-evaluation")
        return
    
    # Step 2: Setup
    print("Step 2: Setting up evaluation...")
    try:
        setup_evaluation()
        print("SUCCESS: Evaluation setup complete\n")
    except Exception as e:
        print(f"ERROR: Setup failed - {e}\n")
        return
    
    # Step 3: Test evaluation
    print("Step 3: Testing evaluation with sample data...")
    try:
        result = await evaluate_response(
            query="What is the recommended dose of Drug X?",
            response="The recommended dose is 10mg once daily, as per FDA labeling.",
            context="FDA Label: Drug X should be administered at 10mg once daily for adults."
        )
        
        print(f"SUCCESS: Evaluation completed")
        print(f"\nResults keys: {list(result.keys())}")
        
        if result.get("error"):
            print(f"ERROR in results: {result['error']}")
        else:
            print("\nEvaluation Scores:")
            for metric, data in result.items():
                if isinstance(data, dict) and "score" in data:
                    print(f"  {metric}: {data.get('score', 'N/A')}")
        
    except Exception as e:
        print(f"ERROR: Evaluation failed - {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_evaluation())
