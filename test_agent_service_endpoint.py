"""
Test Azure AI Foundry Agent Service endpoint
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_AI_PROJECT_KEY", "")
PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")
API_VERSION = "2025-05-01"  # GA version for Agent Service

print("=" * 80)
print("🧪 Testing Azure AI Foundry Agent Service Endpoint")
print("=" * 80)
print(f"\nBase Endpoint: {ENDPOINT}")
print(f"Project Name: {PROJECT_NAME}")
print(f"API Version: {API_VERSION}\n")

# Test both endpoint formats
endpoints_to_test = [
    {
        "name": "Old OpenAI Assistants Endpoint",
        "url": f"{ENDPOINT}/openai/assistants?api-version=2024-07-01-preview",
        "description": "Legacy endpoint (current implementation)"
    },
    {
        "name": "New Agent Service Endpoint",
        "url": f"{ENDPOINT}/api/projects/{PROJECT_NAME}/assistants?api-version={API_VERSION}",
        "description": "New Azure AI Foundry Agent Service (should show in portal)"
    }
]

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

for endpoint_test in endpoints_to_test:
    print(f"Testing: {endpoint_test['name']}")
    print(f"Description: {endpoint_test['description']}")
    print(f"URL: {endpoint_test['url']}")
    print("-" * 80)
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(endpoint_test['url'], headers=headers)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS (HTTP 200)")
                data = response.json()
                agents = data.get("data", [])
                print(f"   Found {len(agents)} agents")
                if agents:
                    for agent in agents[:3]:  # Show first 3
                        print(f"   - {agent.get('name')} (ID: {agent.get('id')})")
            else:
                print(f"❌ FAILED (HTTP {response.status_code})")
                print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:100]}")
    
    print("\n")

print("=" * 80)
print("📝 Conclusion:")
print("   The endpoint that returns HTTP 200 is the correct one to use.")
print("   Agents registered via the NEW endpoint should appear in the portal.")
print("=" * 80)
