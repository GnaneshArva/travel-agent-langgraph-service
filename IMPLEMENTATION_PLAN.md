# Final Implementation Plan - `travel-agent-langgraph-service`

## Overview
`travel-agent-langgraph-service` is a standalone central orchestration microservice for the Enterprise AI Travel Platform. Cloned from `travel-agent-service`, it maintains identical Clean Architecture, SOLID principles, 12-stage request processing lifecycles, and external integrations (Guardrails, Prompt SDK, Memory/Knowledge MCP servers, Observability).

However, it replaces the OpenAI Agents SDK with **LangGraph** (`StateGraph`) for stateful multi-agent execution and dynamic node routing.

---

## Technical Architecture & Components

### 1. Dependencies & Manifests
- `pyproject.toml` & `requirements.txt`: Depend on `langgraph`, `langchain-core`, and `langchain-openai`. `openai-agents` dependency completely removed.

### 2. State Management (`app/agents/state.py`)
- Defines `TravelAgentState(TypedDict)` tracking:
  - `user_request` & `system_prompt`
  - `destination`, `budget`, `duration_days`
  - `messages` (Annotated message history list)
  - `flight_results`, `hotel_results`, `weather_results`, `final_itinerary`
  - `tool_calls_executed` & execution telemetry

### 3. Domain Execution Nodes (`app/agents/nodes.py`)
Implemented `LangGraphNodes` containing 5 discrete node functions:
- **`triage_node`**: Analyzes user intent & budget, initializing state.
- **`flight_node`**: Invokes `search_flights` MCP tool via `ToolExecutor`.
- **`hotel_node`**: Invokes `search_hotels` MCP tool via `ToolExecutor` and validates budget constraints.
- **`weather_node`**: Invokes `get_weather` MCP tool.
- **`synthesizer_node`**: Consolidates state data into a structured travel itinerary synthesis.

### 4. Graph Topology Builder (`app/agents/graph_builder.py`)
- Constructs `StateGraph(TravelAgentState)`:
  - Entry node: `triage`
  - Edges: `triage` $\rightarrow$ `flight` $\rightarrow$ `hotel` $\rightarrow$ `weather` $\rightarrow$ `synthesizer` $\rightarrow$ `END`

### 5. BaseAgent Implementation (`app/agents/langgraph_agent.py`)
- `LangGraphAgent` implements `BaseAgent` interface (`async def run(...)`), invoking `compiled_graph.ainvoke(initial_state)` and returning typed `AgentResponse`.

### 6. Orchestrator Integration (`app/orchestrator/agent_orchestrator.py`)
- Injects `LangGraphAgent` into `AgentOrchestrator` to seamlessly run within the 12-stage enterprise execution pipeline.

---

## 12-Stage Request Lifecycle
1. **Client Request Ingestion**: FastAPI controllers (`TravelController` / `EvalController`).
2. **Session Initialization**: `SessionManager` instantiates `ExecutionContext`.
3. **Application Input Guardrails**: `agentic-ai-guardrails` (`POST /guardrails/input/validate`).
4. **Prompt Template Loading**: `agentic-ai-prompt-management` via `PromptSdk`.
5. **Traveler Memory Retrieval**: `travel-memory-mcp-server`.
6. **Knowledge RAG Retrieval**: `travel-knowledge-mcp-server`.
7. **Context Construction**: `ContextBuilder`.
8. **Execution Planning**: `PlanningService`.
9. **LangGraph Multi-Agent Execution**: `LangGraphAgent` (`StateGraph`).
10. **MCP Tool Execution**: `ToolExecutor` over `travel-mcp-server`.
11. **Output Guardrails & Self-Correction**: `agentic-ai-guardrails` (`POST /guardrails/output/validate`).
12. **Telemetry & Output**: `agentic-ai-observability`.

---

## Verification & Testing
- Automated pytest test suite passes (`tests/test_travel_agent.py`).
- Runtime build and application startup verified cleanly.
