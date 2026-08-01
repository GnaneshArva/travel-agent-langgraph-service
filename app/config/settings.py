from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AgentConfig(BaseSettings):
    model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    temperature: float = Field(default=0.7, alias="AGENT_TEMPERATURE")
    max_tokens: int = Field(default=4096, alias="AGENT_MAX_TOKENS")
    retry_count: int = Field(default=3, alias="AGENT_RETRY_COUNT")
    openai_api_key: str = Field(default="mock-key", alias="OPENAI_API_KEY")

    model_config = SettingsConfigDict(extra="ignore")

class McpConfig(BaseSettings):
    travel_mcp_url: str = Field(default="http://localhost:8001", alias="TRAVEL_MCP_URL")
    memory_mcp_url: str = Field(default="http://localhost:8002", alias="MEMORY_MCP_URL")
    knowledge_mcp_url: str = Field(default="http://localhost:8003", alias="KNOWLEDGE_MCP_URL")
    guardrails_service_url: str = Field(default="http://localhost:8004", alias="GUARDRAILS_SERVICE_URL")
    prompt_management_url: str = Field(default="http://localhost:8005", alias="PROMPT_MANAGEMENT_URL")
    observability_service_url: str = Field(default="http://localhost:8006", alias="OBSERVABILITY_SERVICE_URL")

    model_config = SettingsConfigDict(extra="ignore")

class TimeoutConfig(BaseSettings):
    tool_timeout: float = Field(default=15.0, alias="TOOL_TIMEOUT")
    mcp_timeout: float = Field(default=10.0, alias="MCP_TIMEOUT")
    agent_timeout: float = Field(default=60.0, alias="AGENT_TIMEOUT")
    default_retry_attempts: int = Field(default=3, alias="DEFAULT_RETRY_ATTEMPTS")

    model_config = SettingsConfigDict(extra="ignore")

class PromptConfig(BaseSettings):
    prompt_version: str = Field(default="1.0.0", alias="PROMPT_VERSION")
    prompt_name: str = Field(default="travel_agent_system", alias="PROMPT_NAME")
    environment: str = Field(default="development", alias="APP_ENV")

    model_config = SettingsConfigDict(extra="ignore")

class FeatureFlags(BaseSettings):
    enable_memory: bool = Field(default=True, alias="ENABLE_MEMORY")
    enable_knowledge: bool = Field(default=True, alias="ENABLE_KNOWLEDGE")
    enable_guardrails: bool = Field(default=True, alias="ENABLE_GUARDRAILS")
    enable_observability: bool = Field(default=True, alias="ENABLE_OBSERVABILITY")
    enable_prompt_management: bool = Field(default=True, alias="ENABLE_PROMPT_MANAGEMENT")
    enable_streaming: bool = Field(default=True, alias="ENABLE_STREAMING")
    enable_planning: bool = Field(default=True, alias="ENABLE_PLANNING")

    model_config = SettingsConfigDict(extra="ignore")

class ApplicationConfig(BaseSettings):
    app_name: str = Field(default="travel-agent-service", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    agent: AgentConfig = Field(default_factory=AgentConfig)
    mcp: McpConfig = Field(default_factory=McpConfig)
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)
    prompt: PromptConfig = Field(default_factory=PromptConfig)
    features: FeatureFlags = Field(default_factory=FeatureFlags)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = ApplicationConfig()
