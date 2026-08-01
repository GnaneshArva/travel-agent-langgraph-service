"""
Integration Client for agentic-ai-guardrails.

Makes HTTP calls to the guardrails microservice (server.py in agentic-ai-guardrails)
which wraps the GuardrailService facade and runs the full Input/Output pipelines
(prompt injection, jailbreak, PII, toxicity, hallucination, etc.).
"""

import httpx
from typing import Any
from app.interfaces.guardrail import GuardrailProvider
from app.config.settings import settings
from app.utils.logger import logger


class GuardrailClient(GuardrailProvider):
    """Integration Client for agentic-ai-guardrails microservice."""

    def __init__(self, service_url: str | None = None):
        self.service_url = service_url or settings.mcp.guardrails_service_url
        self.timeout = settings.timeouts.mcp_timeout

    async def validate_input(self, text: str, session_id: str | None = None) -> tuple[bool, str, dict[str, Any]]:
        if not settings.features.enable_guardrails:
            return True, text, {}

        logger.info("Evaluating input guardrails", component="GuardrailClient", session_id=session_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.service_url}/guardrails/input/validate",
                    json={"text": text, "session_id": session_id},
                )
                resp.raise_for_status()
                data = resp.json()
                return (
                    data["is_allowed"],
                    data["sanitized_text"],
                    data.get("metadata", {}),
                )
        except httpx.ConnectError:
            logger.warning(
                f"Guardrails service unreachable at {self.service_url}. Falling back to local check.",
                component="GuardrailClient",
            )
        except Exception as exc:
            logger.error(f"Input guardrail call failed: {exc}", component="GuardrailClient")

        # Fallback: basic prompt injection check when service is unavailable
        return self._local_input_fallback(text)

    async def validate_output(self, text: str, session_id: str | None = None) -> tuple[bool, str, dict[str, Any]]:
        if not settings.features.enable_guardrails:
            return True, text, {}

        logger.info("Evaluating output guardrails", component="GuardrailClient", session_id=session_id)
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.service_url}/guardrails/output/validate",
                    json={"text": text, "session_id": session_id},
                )
                resp.raise_for_status()
                data = resp.json()
                return (
                    data["is_allowed"],
                    data["sanitized_text"],
                    data.get("metadata", {}),
                )
        except httpx.ConnectError:
            logger.warning(
                f"Guardrails service unreachable at {self.service_url}. Falling back to pass-through.",
                component="GuardrailClient",
            )
        except Exception as exc:
            logger.error(f"Output guardrail call failed: {exc}", component="GuardrailClient")

        return True, text, {"mode": "local_fallback"}

    # ── Local fallback (used only when the guardrails service is down) ──────

    @staticmethod
    def _local_input_fallback(text: str) -> tuple[bool, str, dict[str, Any]]:
        """Minimal safety net when the guardrails microservice is unavailable."""
        forbidden_patterns = [
            "ignore previous instructions",
            "ignore all instructions",
            "disregard previous",
            "system prompt leak",
            "reveal your prompt",
            "forget your instructions",
        ]
        lower = text.lower()
        for pattern in forbidden_patterns:
            if pattern in lower:
                return False, f"Input blocked due to policy term: {pattern}", {"reason": "prompt_injection", "mode": "local_fallback"}

        return True, text, {"mode": "local_fallback"}
