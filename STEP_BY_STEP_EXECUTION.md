# Step-by-Step Execution Architecture (`travel-agent-langgraph-service`)

## Purpose
`travel-agent-langgraph-service` is an enterprise central orchestration microservice cloned from `travel-agent-service`. Built with Clean Architecture and SOLID principles, it coordinates session state, memory retrieval, knowledge RAG, prompt management, security guardrails, execution planning, and observability telemetry. 

Instead of using the OpenAI Agents SDK, it orchestrates multi-agent workflows using a stateful **LangGraph** `StateGraph` mesh.

---

## Step-by-Step Request Execution Flow

```
Client / Evals Request
      │
      ▼
FastAPI TravelController / EvalController
      │
      ▼
AgentOrchestrator
      │
 ┌────┴───────────────────────────┬───────────────────────────┬───────────────────────────┐
 ▼                                ▼                           ▼                           ▼
1. Session Init          2. Input Guardrails        3. Memory & Knowledge       4. Build Context
 (SessionManager)        (agentic-ai-guardrails)     (MCP Servers)               (ContextBuilder)
                                                                                          │
 ┌────────────────────────────────────────────────────────────────────────────────────────┘
 ▼
5. Execution Plan        6. Render Prompt           7. LangGraph StateGraph      8. Tool Executor
 (PlanningService)       (agentic-ai-prompt-mgmt)    (LangGraphAgent)            (travel-mcp-server)
                                                     ├── Triage Node
                                                     ├── Flight Node
                                                     ├── Hotel Node
                                                     ├── Weather Node
                                                     └── Synthesizer Node
                                                                                          │
 ┌────────────────────────────────────────────────────────────────────────────────────────┘
 ▼
9. Output Guardrails     10. Automated Remediation  11. Response Processor      12. Telemetry & Output
 (agentic-ai-guardrails)  (Multi-Violation Loop)     (Structured Strategy)       (agentic-ai-obs / Client)
```

### Execution Lifecycle:
1. **Client HTTP Request**: Request received at `POST /api/v1/travel/plan`, `POST /api/v1/travel/plan/stream`, or `POST /api/v1/travel/evaluate` (from `agentic-ai-evals`).
2. **Session Initialization**: `SessionManager` instantiates `ExecutionContext` with session ID, conversation ID, request ID, and correlation trace ID.
3. **Input Guardrails**: `PlatformFacade` calls `agentic-ai-guardrails` (`POST /guardrails/input/validate`) to validate prompt safety.
4. **Prompt Template Loading**: `PlatformFacade` requests versioned system prompt templates from `agentic-ai-prompt-management` via official `PromptSdk`.
5. **Memory Retrieval**: User travel profile, seat preferences, and past trip history fetched from `travel-memory-mcp-server`.
6. **Knowledge Retrieval**: Destination guides, advisories, visa requirements, and weather retrieved from `travel-knowledge-mcp-server`.
7. **Context Construction**: `ContextBuilder` sequences context following strictly ordered composition rules.
8. **Execution Planning**: `PlanningService` determines step-by-step tool dependencies without executing them directly.
9. **LangGraph StateGraph Multi-Agent Execution**: `LangGraphAgent` compiles and runs `TravelAgentState` across discrete nodes:
   - **`triage_node`**: Entry router analyzing user intent and budget constraints.
   - **`flight_node`**: Invokes `search_flights` MCP tool.
   - **`hotel_node`**: Invokes `search_hotels` MCP tool and enforces budget bounds.
   - **`weather_node`**: Invokes `get_weather` MCP tool.
   - **`synthesizer_node`**: Consolidates state data into a structured travel itinerary synthesis.
10. **Response Processing & Output Guardrails**: `ResponseProcessor` calls `agentic-ai-guardrails` (`POST /guardrails/output/validate`) to perform RAG grounding checks, citation verification, and business rule enforcement.
11. **Automated Multi-Violation Remediation**: Performs multi-violation self-correction feedback loop (max 2 retries) or triggers circuit breaker fallback ($\ge 3$ violations).
12. **Observability Telemetry**: Execution metrics, token usage, latency, and costs published to `agentic-ai-observability`.
