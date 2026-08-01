from typing import Any
from app.interfaces.memory import MemoryProvider
from app.interfaces.knowledge import KnowledgeProvider
from app.interfaces.guardrail import GuardrailProvider
from app.interfaces.prompt import PromptProvider
from app.interfaces.observability import ObservabilityProvider
from app.integrations.memory.memory_client import MemoryMcpClient
from app.integrations.knowledge.knowledge_client import KnowledgeMcpClient
from app.integrations.guardrails.guardrail_client import GuardrailClient
from app.integrations.prompt_management.prompt_management_client import PromptManagementClient
from app.integrations.observability.observability_client import ObservabilityClient
from app.dto.requests import MemoryRequest, KnowledgeRequest
from app.dto.context import MemoryContext, KnowledgeContext, PromptContext
from app.utils.logger import logger

class PlatformFacade:
    """
    Facade Pattern encapsulating platform subsystem interactions:
    Memory, Knowledge, Guardrails, Prompt Management, and Observability.
    """

    def __init__(
        self,
        memory_provider: MemoryProvider | None = None,
        knowledge_provider: KnowledgeProvider | None = None,
        guardrail_provider: GuardrailProvider | None = None,
        prompt_provider: PromptProvider | None = None,
        observability_provider: ObservabilityProvider | None = None
    ):
        self.memory = memory_provider or MemoryMcpClient()
        self.knowledge = knowledge_provider or KnowledgeMcpClient()
        self.guardrails = guardrail_provider or GuardrailClient()
        self.prompt_mgmt = prompt_provider or PromptManagementClient()
        self.observability = observability_provider or ObservabilityClient()

    async def validate_input_guardrails(self, text: str, session_id: str) -> tuple[bool, str, dict[str, Any]]:
        return await self.guardrails.validate_input(text=text, session_id=session_id)

    async def validate_output_guardrails(self, text: str, session_id: str) -> tuple[bool, str, dict[str, Any]]:
        return await self.guardrails.validate_output(text=text, session_id=session_id)

    async def load_prompt_template(self, template_name: str, variables: dict[str, Any]) -> PromptContext:
        return await self.prompt_mgmt.load_prompt(template_name=template_name, variables=variables)

    async def retrieve_memory(self, user_id: str) -> MemoryContext:
        return await self.memory.retrieve(MemoryRequest(user_id=user_id))

    async def retrieve_knowledge(self, destination: str) -> KnowledgeContext:
        return await self.knowledge.retrieve(KnowledgeRequest(destination=destination))

    async def publish_telemetry(self, event_type: str, session_id: str, request_id: str, trace_id: str, payload: dict[str, Any]) -> bool:
        return await self.observability.publish_event(
            event_type=event_type,
            session_id=session_id,
            request_id=request_id,
            trace_id=trace_id,
            payload=payload
        )
