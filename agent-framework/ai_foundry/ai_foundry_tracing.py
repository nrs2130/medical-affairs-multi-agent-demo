"""
Azure AI Foundry Tracing Integration

This module provides OpenTelemetry-based tracing for Medical Affairs agents,
enabling observability in Azure AI Foundry portal.

Features:
- Automatic instrumentation of OpenAI SDK calls
- Custom spans for multi-agent workflows
- Token usage and latency tracking
- Integration with Azure Application Insights

Usage:
    from ai_foundry_tracing import setup_tracing, trace_agent_call
    
    # Initialize tracing (once at startup)
    setup_tracing()
    
    # Use decorators for custom spans
    @trace_agent_call("literature_scout")
    async def call_literature_scout(query):
        # Your agent logic here
        pass
"""

import os
from typing import Optional
from functools import wraps
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter


class AIFoundryTracing:
    """Manages Azure AI Foundry tracing configuration"""
    
    def __init__(self):
        self.enabled = False
        self.tracer = None
        self.project_client = None
    
    def setup(self, 
              project_endpoint: Optional[str] = None,
              connection_string: Optional[str] = None,
              console_only: bool = False):
        """
        Initialize Azure AI Foundry tracing
        
        Args:
            project_endpoint: Azure AI Foundry project endpoint URL
            connection_string: Application Insights connection string
            console_only: If True, only traces to console (for testing)
        """
        try:
            if console_only:
                # Console-only tracing for testing/CI
                self._setup_console_tracing()
                print("✅ Tracing enabled: Console output only")
            else:
                # Azure AI Foundry tracing
                self._setup_azure_tracing(project_endpoint, connection_string)
                print("✅ Tracing enabled: Azure AI Foundry + Application Insights")
            
            self.enabled = True
            self.tracer = trace.get_tracer(__name__)
            
        except Exception as e:
            print(f"⚠️ Tracing setup failed: {e}")
            print("   Continuing without tracing...")
            self.enabled = False
    
    def _setup_console_tracing(self):
        """Setup console-only tracing for local development"""
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
        
        # Instrument OpenAI SDK
        OpenAIInstrumentor().instrument()
        
        # Configure console exporter
        span_exporter = ConsoleSpanExporter()
        tracer_provider = TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        trace.set_tracer_provider(tracer_provider)
    
    def _setup_azure_tracing(self, 
                            project_endpoint: Optional[str], 
                            connection_string: Optional[str]):
        """Setup Azure AI Foundry tracing with Application Insights"""
        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential
            from azure.monitor.opentelemetry import configure_azure_monitor
            from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
            
            # Get connection string from environment or project
            if not connection_string:
                # Try environment variable first (most reliable)
                connection_string = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
                
                if not connection_string and project_endpoint:
                    # Try to get from AI Foundry project (requires newer SDK)
                    try:
                        self.project_client = AIProjectClient(
                            credential=DefaultAzureCredential(),
                            endpoint=project_endpoint,
                        )
                        # This method may not exist in all SDK versions
                        if hasattr(self.project_client, 'telemetry') and hasattr(self.project_client.telemetry, 'get_application_insights_connection_string'):
                            connection_string = self.project_client.telemetry.get_application_insights_connection_string()
                    except Exception as e:
                        print(f"   Note: Could not retrieve connection string from project: {e}")
                
                if not connection_string:
                    raise ValueError(
                        "No connection string provided. Set APPLICATIONINSIGHTS_CONNECTION_STRING "
                        "environment variable or provide connection_string parameter."
                    )
            
            # Configure Azure Monitor
            configure_azure_monitor(connection_string=connection_string)
            
            # Instrument OpenAI SDK
            OpenAIInstrumentor().instrument()
            
        except ImportError as e:
            raise ImportError(
                f"Missing required packages for Azure tracing: {e}\n"
                "Install with: pip install azure-ai-projects azure-monitor-opentelemetry opentelemetry-instrumentation-openai-v2"
            )
    
    def create_span(self, name: str, attributes: Optional[dict] = None):
        """
        Create a custom span for tracing
        
        Args:
            name: Span name (e.g., "literature_scout_agent")
            attributes: Optional attributes to attach to span
        
        Returns:
            Span context manager
        """
        if not self.enabled or not self.tracer:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
        
        span = self.tracer.start_as_current_span(name)
        
        # Add custom attributes
        if attributes:
            current_span = trace.get_current_span()
            for key, value in attributes.items():
                current_span.set_attribute(key, value)
        
        return span
    
    def add_span_attribute(self, key: str, value):
        """Add attribute to current span"""
        if self.enabled:
            current_span = trace.get_current_span()
            current_span.set_attribute(key, value)
    
    def add_span_event(self, name: str, attributes: Optional[dict] = None):
        """Add event to current span"""
        if self.enabled:
            current_span = trace.get_current_span()
            current_span.add_event(name, attributes=attributes or {})


# Global tracing instance
_tracing = AIFoundryTracing()


def setup_tracing(project_endpoint: Optional[str] = None,
                 connection_string: Optional[str] = None,
                 console_only: bool = False,
                 capture_message_content: bool = True):
    """
    Initialize Azure AI Foundry tracing (call once at startup)
    
    Args:
        project_endpoint: Azure AI Foundry project endpoint (e.g., https://your-project.services.ai.azure.com/api/projects/your-project)
        connection_string: Application Insights connection string (optional if project_endpoint provided)
        console_only: If True, only output to console (useful for testing)
        capture_message_content: If True, capture full message content in traces
    
    Environment Variables:
        APPLICATIONINSIGHTS_CONNECTION_STRING: App Insights connection string
        AI_FOUNDRY_PROJECT_ENDPOINT: Project endpoint URL
        OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT: Capture message content (true/false)
    
    Example:
        # Option 1: Auto-configure from environment
        setup_tracing()
        
        # Option 2: Provide project endpoint
        setup_tracing(project_endpoint="https://your-project.services.ai.azure.com/api/projects/your-project")
        
        # Option 3: Console-only for testing
        setup_tracing(console_only=True)
    """
    # Set environment variable for message content capture
    if capture_message_content:
        os.environ['OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT'] = 'true'
    
    # Try to get from environment if not provided
    if not project_endpoint:
        project_endpoint = os.getenv('AI_FOUNDRY_PROJECT_ENDPOINT')
    
    _tracing.setup(project_endpoint, connection_string, console_only)


def trace_agent_call(agent_name: str):
    """
    Decorator to trace agent function calls
    
    Args:
        agent_name: Name of the agent (e.g., "literature_scout", "compliance_guard")
    
    Example:
        @trace_agent_call("literature_scout")
        async def call_literature_scout(query):
            result = await agent.run(query)
            return result
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with _tracing.create_span(f"{agent_name}_execution"):
                _tracing.add_span_attribute("agent.name", agent_name)
                _tracing.add_span_attribute("agent.function", func.__name__)
                
                # Add query if available
                if args:
                    _tracing.add_span_attribute("agent.query_length", len(str(args[0])))
                
                result = await func(*args, **kwargs)
                
                # Add result info
                if result:
                    _tracing.add_span_attribute("agent.result_length", len(str(result)))
                
                return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with _tracing.create_span(f"{agent_name}_execution"):
                _tracing.add_span_attribute("agent.name", agent_name)
                _tracing.add_span_attribute("agent.function", func.__name__)
                
                if args:
                    _tracing.add_span_attribute("agent.query_length", len(str(args[0])))
                
                result = func(*args, **kwargs)
                
                if result:
                    _tracing.add_span_attribute("agent.result_length", len(str(result)))
                
                return result
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def create_workflow_span(workflow_name: str, attributes: Optional[dict] = None):
    """
    Create a span for a multi-agent workflow
    
    Args:
        workflow_name: Name of workflow (e.g., "full_mi_workflow")
        attributes: Optional attributes like query, hcp_info, etc.
    
    Example:
        with create_workflow_span("full_mi_workflow", {"query": query}):
            evidence = await literature_scout(query)
            response = await mi_agent(evidence)
            validation = await compliance_guard(response)
    """
    return _tracing.create_span(workflow_name, attributes)


def add_workflow_metrics(metrics: dict):
    """
    Add metrics to current span
    
    Args:
        metrics: Dictionary of metrics (e.g., {"compliance_risk": "LOW", "tokens_used": 1234})
    
    Example:
        add_workflow_metrics({
            "compliance_risk": "LOW",
            "evidence_quality": "HIGH",
            "total_tokens": 1234,
            "latency_ms": 2500
        })
    """
    for key, value in metrics.items():
        _tracing.add_span_attribute(f"workflow.{key}", value)


def is_tracing_enabled() -> bool:
    """Check if tracing is enabled"""
    return _tracing.enabled


# Export key functions
__all__ = [
    'setup_tracing',
    'trace_agent_call',
    'create_workflow_span',
    'add_workflow_metrics',
    'is_tracing_enabled',
]
