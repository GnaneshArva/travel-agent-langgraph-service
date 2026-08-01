# Enterprise Agentic AI Travel Planner (`travel-agent-langgraph-service`)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0%2B-red.svg)](https://docs.pydantic.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0%2B-orange.svg)](https://python.langchain.com/docs/langgraph)

**`travel-agent-langgraph-service`** is the central orchestration microservice for the Enterprise AI Travel Platform utilizing **LangGraph** (`StateGraph`) for stateful multi-agent orchestration. 

Designed using Clean Architecture, SOLID design principles, and enterprise design patterns, it coordinates memory retrieval, destination knowledge RAG, prompt management, security guardrails, execution planning, stateful graph node execution, MCP tool execution, and observability.

---

## High-Level Architecture Diagram

```
                              Client Request
                                    │
                                    ▼
                         FastAPI TravelController
                                    │
                                    ▼
                            AgentOrchestrator
                                    │
    ┌───────────────────────┬───────┴───────┬──────────────────────┐
    ▼                       ▼               ▼                      ▼
Input Guardrails    Prompt Management  Memory MCP           Knowledge MCP
(agentic-ai-gdr)    (agentic-ai-pm)    (travel-mem-mcp)     (travel-know-mcp)
    │                       │               │                      │
    └───────────────────────┴───────┬───────┴──────────────────────┘
                                    ▼
                              ContextBuilder
                                    │
                                    ▼
                             PlanningService
                                    │
                                    ▼
                           LangGraph StateGraph
                             (LangGraphAgent)
                           ├── Triage Node
                           ├── Flight Node
                           ├── Hotel Node
                           ├── Weather Node
                           └── Synthesizer Node
                                    │
                                    ▼
                              ToolExecutor
                                    │
                                    ▼
                            Travel MCP Server
                                    │
                                    ▼
                            ResponseProcessor
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
          Output Guardrails                     Observability
           (agentic-ai-gdr)                    (agentic-ai-obs)
```

---

## Key Features & Highlights

- **LangGraph Multi-Agent Orchestration**: Uses stateful `StateGraph(TravelAgentState)` to coordinate execution across `triage_node`, `flight_node`, `hotel_node`, `weather_node`, and `synthesizer_node`.
- **Clean Architecture & SOLID**: Fully decoupled layers (Controllers, Orchestrator, Services, BaseAgent Abstraction, Interfaces, DTOs).
- **Prompt Management Integration**: Resolves versioned prompts from `agentic-ai-prompt-management` via `PromptSdk`.
- **Enterprise Guardrails & Self-Correction**: Enforces perimeter/application input validation and RAG output grounding checks with automated multi-violation re-prompting loops.
- **Model Context Protocol (MCP) Integration**: Connects seamlessly with `travel-memory-mcp-server`, `travel-knowledge-mcp-server`, and `travel-mcp-server`.