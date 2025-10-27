# Launch script for Medical Affairs Streamlit App
# ================================================
# This script sets up the environment and launches the Streamlit application

Write-Host "Medical Affairs Multi-Agent Demo - Streamlit Launcher" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if required environment variables are set
$envVars = @{
    "AZURE_OPENAI_ENDPOINT" = $env:AZURE_OPENAI_ENDPOINT
    "AZURE_OPENAI_API_KEY" = $env:AZURE_OPENAI_API_KEY
    "AZURE_OPENAI_DEPLOYMENT_NAME" = $env:AZURE_OPENAI_DEPLOYMENT_NAME
}

$missingVars = @()
foreach ($var in $envVars.Keys) {
    if ([string]::IsNullOrEmpty($envVars[$var])) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "WARNING: The following environment variables are not set:" -ForegroundColor Yellow
    foreach ($var in $missingVars) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "You can set them using:" -ForegroundColor Yellow
    Write-Host '  $env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"' -ForegroundColor Gray
    Write-Host '  $env:AZURE_OPENAI_API_KEY="your-api-key-here"' -ForegroundColor Gray
    Write-Host '  $env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"' -ForegroundColor Gray
    Write-Host ""
    
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

Write-Host "Launching Streamlit app..." -ForegroundColor Green
Write-Host ""

# Launch Streamlit
streamlit run medical_affairs_app.py

# Note: Press Ctrl+C to stop the server
