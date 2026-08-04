"""
Integration Client for agentic-ai-prompt-management.

Uses the PromptSdk from agentic-ai-prompt-management to fetch and render
versioned prompts over the REST API using official DTO contracts.
"""

import importlib.util
import os
import sys
from typing import Any
from app.interfaces.prompt import PromptProvider
from app.dto.context import PromptContext
from app.config.settings import settings
from app.prompts.prompt_cache import prompt_cache
from app.utils.logger import logger

# Dynamically load PromptSdk & PromptRequest from agentic-ai-prompt-management
_PROMPT_MGMT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "agentic-ai-prompt-management")
)


def _load_prompt_sdk():
    """Loads PromptSdk and PromptRequest without polluting the 'app' namespace."""
    sdk_path = os.path.join(_PROMPT_MGMT_ROOT, "app", "sdk", "sdk.py")
    dtos_path = os.path.join(_PROMPT_MGMT_ROOT, "app", "dto", "dtos.py")
    interfaces_path = os.path.join(_PROMPT_MGMT_ROOT, "app", "interfaces", "interfaces.py")
    exceptions_path = os.path.join(_PROMPT_MGMT_ROOT, "app", "exceptions", "exceptions.py")

    # Load exceptions
    spec_exc = importlib.util.spec_from_file_location("prompt_mgmt_lib.exceptions", exceptions_path)
    mod_exc = importlib.util.module_from_spec(spec_exc)
    sys.modules["prompt_mgmt_lib.exceptions"] = mod_exc
    spec_exc.loader.exec_module(mod_exc)

    # Load interfaces
    spec_iface = importlib.util.spec_from_file_location("prompt_mgmt_lib.interfaces", interfaces_path)
    mod_iface = importlib.util.module_from_spec(spec_iface)
    sys.modules["prompt_mgmt_lib.interfaces"] = mod_iface
    spec_iface.loader.exec_module(mod_iface)

    # Load DTOs
    spec_dto = importlib.util.spec_from_file_location("prompt_mgmt_lib.dtos", dtos_path)
    mod_dto = importlib.util.module_from_spec(spec_dto)
    sys.modules["prompt_mgmt_lib.dtos"] = mod_dto
    spec_dto.loader.exec_module(mod_dto)

    # Patch sys.modules so app.interfaces.interfaces and app.dto.dtos resolve for sdk.py
    sys.modules["app.interfaces.interfaces"] = mod_iface
    sys.modules["app.dto.dtos"] = mod_dto
    sys.modules["app.exceptions.exceptions"] = mod_exc

    spec_sdk = importlib.util.spec_from_file_location("prompt_mgmt_lib.sdk", sdk_path)
    mod_sdk = importlib.util.module_from_spec(spec_sdk)
    sys.modules["prompt_mgmt_lib.sdk"] = mod_sdk
    spec_sdk.loader.exec_module(mod_sdk)

    return mod_sdk.PromptSdk, mod_dto.PromptRequest


try:
    _PromptSdk, _PromptRequest = _load_prompt_sdk()
except Exception:
    _PromptSdk, _PromptRequest = None, None


class PromptManagementClient(PromptProvider):
    """Integration Client using PromptSdk for agentic-ai-prompt-management service."""

    def __init__(self, service_url: str | None = None):
        self.service_url = service_url or settings.mcp.prompt_management_url
        self.timeout = settings.timeouts.mcp_timeout
        base_api_url = f"{self.service_url.rstrip('/')}"
        self._sdk = _PromptSdk(base_url=base_api_url) if _PromptSdk else None

    async def load_prompt(
        self,
        template_name: str,
        version: str | None = None,
        variables: dict[str, Any] | None = None
    ) -> PromptContext:
        vars_dict = variables or {}
        version_str = version or settings.prompt.prompt_version
        cache_key = f"template:{template_name}:{version_str}:{sorted(vars_dict.items())}"

        # 1. Check Prompt Cache
        cached_template = prompt_cache.get(cache_key)
        if cached_template is not None:
            logger.info(f"Loaded prompt template '{template_name}' version {version_str} from PromptCache", component="PromptManagementClient")
            return PromptContext(
                template_name=template_name,
                rendered_prompt=cached_template,
                system_instruction=cached_template,
                variables=vars_dict
            )

        logger.info(f"Loading prompt template '{template_name}' version {version_str} via PromptSdk", component="PromptManagementClient")

        rendered_result = None

        if settings.features.enable_prompt_management and self._sdk:
            try:
                request = _PromptRequest(
                    prompt_name=template_name,
                    version=version_str,
                    variables=vars_dict
                )
                response = await self._sdk.get_prompt(request)
                rendered_result = response.rendered_prompt
            except Exception as e:
                logger.warning(f"Prompt Management SDK call failed ({str(e)}). Falling back to default system template.", component="PromptManagementClient")

        if rendered_result is None:
            rendered_result = (
                "You are an Enterprise AI Travel Planner orchestrator. "
                "Your role is to plan trips, coordinate flight and hotel searches, retrieve relevant travel advisories, "
                "and craft comprehensive, personalized travel itineraries using registered MCP tools."
            )

        # 2. Store in Prompt Cache
        prompt_cache.set(cache_key, rendered_result)

        return PromptContext(
            template_name=template_name,
            rendered_prompt=rendered_result,
            system_instruction=rendered_result,
            variables=vars_dict
        )
