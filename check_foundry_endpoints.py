"""
Check Azure AI Foundry API endpoints to find where Agents should be registered
"""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_AI_PROJECT_KEY", "")

print("=" * 80)
print("🔍 Exploring Azure AI Foundry API Endpoints")
print("=" * 80)
print(f"\n📍 Base Endpoint: {ENDPOINT}\n")

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

# Try different API versions and endpoints
api_versions = [
    "2024-07-01-preview",
    "2024-05-01-preview", 
    "2024-02-15-preview",
    "2023-12-01-preview"
]

endpoints_to_try = [
    "/agents",
    "/openai/agents",
    "/openai/assistants",
    "/projects/agents",
    "/ai/agents"
]

print("Testing available endpoints:\n")

for api_version in api_versions:
    print(f"\n{'='*80}")
    print(f"API Version: {api_version}")
    print('='*80)
    
    for endpoint_path in endpoints_to_try:
        url = f"{ENDPOINT}{endpoint_path}?api-version={api_version}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint_path:30} - SUCCESS (200)")
                    data = response.json()
                    if isinstance(data, dict):
                        if 'data' in data:
                            print(f"   └─ Found {len(data['data'])} items in 'data' field")
                        elif 'value' in data:
                            print(f"   └─ Found {len(data['value'])} items in 'value' field")
                        else:
                            print(f"   └─ Response keys: {list(data.keys())}")
                elif response.status_code == 404:
                    print(f"❌ {endpoint_path:30} - Not Found (404)")
                elif response.status_code == 401:
                    print(f"🔐 {endpoint_path:30} - Unauthorized (401)")
                else:
                    print(f"⚠️  {endpoint_path:30} - HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {endpoint_path:30} - Error: {str(e)[:50]}")
    
    # Only try first working version
    break

print("\n" + "=" * 80)
print("\n📝 Recommendation:")
print("   Based on the results above, use the endpoint that returned SUCCESS (200)")
print("   Current script uses: /openai/assistants")
print("\n🌐 Azure AI Foundry Portal:")
print("   https://ai.azure.com/")
print("   Look for: Build > Assistants OR Agents section\n")
