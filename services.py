# Copyright 2026 Google LLC
# Service registry custom services for recipe-concierge agent

import os
from google.adk.cli.service_registry import get_service_registry
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService

def memory_bank_factory(uri: str, **kwargs):
    project = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-02-4d1e13b696da")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east1")
    agent_engine_id = "3778931304712634368"
    
    return VertexAiMemoryBankService(
        project=project,
        location=location,
        agent_engine_id=agent_engine_id
    )

get_service_registry().register_memory_service("agentengine", memory_bank_factory)
