# Enterprise Agentic AI Travel Planner (`travel-agent-service`)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0%2B-red.svg)](https://docs.pydantic.dev/)
[![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI-Agents%20SDK-black.svg)](https://openai.com/)

**`travel-agent-service`** is the central orchestration microservice for the Enterprise AI Travel Platform. Designed using Clean Architecture, SOLID design principles, and enterprise design patterns, it coordinates memory retrieval, destination knowledge RAG, prompt management, security guardrails, execution planning, MCP tool execution, and observability without embedding domain business logic directly into the orchestrator.

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
                            OpenAI Agent SDK
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
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    ▼
                             HTTP Response
```

---

## Runtime Request Lifecycle

Every request follows a strict, deterministic 12-stage lifecycle:

1. **Client HTTP Request**: Received at `POST /api/v1/travel/plan` or `POST /api/v1/travel/plan/stream`.
2. **Session Initialization**: `SessionManager` instantiates `ExecutionContext` with session ID, conversation ID, request ID, and correlation trace ID.
3. **Input Guardrails**: `PlatformFacade` calls `agentic-ai-guardrails` to detect prompt injection, jailbreaks, and inbound PII.
4. **Prompt Template Loading**: `PlatformFacade` requests system prompt templates from `agentic-ai-prompt-management`.
5. **Memory Retrieval**: User travel profile, seat preferences, and past trip history fetched from `travel-memory-mcp-server`.
6. **Knowledge Retrieval**: Destination guides, advisories, visa requirements, and weather retrieved from `travel-knowledge-mcp-server`.
7. **Context Construction**: `ContextBuilder` sequences context following strictly ordered composition rules.
8. **Execution Planning**: `PlanningService` determines step-by-step tool dependencies without executing them directly.
9. **OpenAI Agent Reasoning**: OpenAI model reasons over prompt, context, and available MCP tools.
10. **Parallel Tool Execution**: `ToolExecutor` executes MCP tools concurrently via `asyncio.gather()` over `travel-mcp-server`.
11. **Response Processing & Output Guardrails**: `ResponseProcessor` validates DTOs and verifies output against safety policies.
12. **Observability Telemetry**: Execution metrics, token usage, latency, and costs published to `agentic-ai-observability`.

---

## Folder Structure

```
travel-agent-service/
├── app/
│   ├── agents/            # OpenAI Agent SDK integration
│   ├── builders/          # Prompt and Context Builder implementations
│   ├── config/            # Pydantic BaseSettings sectioned configuration
│   ├── context/           # Context pipeline engineering services
│   ├── controllers/       # FastAPI HTTP controllers (no business logic)
│   ├── dto/               # Strict Pydantic v2 Data Transfer Objects
│   ├── exceptions/        # Strongly-typed domain exception hierarchy
│   ├── factories/         # Strategy and Provider factories
│   ├── integrations/      # Platform clients (Memory, Knowledge, Tools, Guardrails, Observability, Prompt Mgmt)
│   ├── interfaces/        # Abstract contracts for pluggable components
│   ├── orchestrator/      # Central request lifecycle orchestrator
│   ├── planning/          # Execution plan generation service
│   ├── prompts/           # Prompt rendering services
│   ├── reasoning/         # Observability reasoning trace recorder
│   ├── services/          # Tool executor & Response processor services
│   ├── sessions/          # Session, conversation, and correlation ID manager
│   ├── strategies/        # Strategy pattern implementations (Planning, Context, Prompt, Response)
│   ├── utils/             # Structured JSON logger & utility helpers
│   └── main.py            # FastAPI entrypoint & exception handlers
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Technology Stack

- **Python 3.12+**
- **FastAPI**: Lightweight, high-performance async Web framework.
- **Pydantic v2**: Type validation and strict DTO schemas.
- **OpenAI Agents SDK / Async Client**: Model reasoning and tool selection.
- **httpx / asyncio**: Non-blocking async HTTP & parallel I/O execution.

---

## Platform Repositories Integration

| Component | Repository | Role |
| :--- | :--- | :--- |
| **Business Tools** | `travel-mcp-server` | Flight search, hotel search, weather, attractions, currency conversion |
| **Memory** | `travel-memory-mcp-server` | User profile, travel preferences, flight history, long-term memory |
| **Knowledge** | `travel-knowledge-mcp-server` | Destination RAG guides, visa policies, travel advisories, local customs |
| **Guardrails** | `agentic-ai-guardrails` | Input injection protection, PII masking, output toxicity & policy validation |
| **Prompt Mgmt** | `agentic-ai-prompt-management` | Centralized versioned prompt template rendering |
| **Observability** | `agentic-ai-observability` | Lifecycle telemetry, token tracking, latency & cost metrics |

---

## Quick Start & Local Execution

### 1. Requirements & Setup

Make sure Python 3.12+ is installed.

```bash
# Clone and navigate to repository
cd travel-agent-service

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 3. Run Service

```bash
# Start FastAPI application
python3 -m app.main
```
or via Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Sample Request & Response

### HTTP POST `/api/v1/travel/plan`

#### Request Payload:
```json
{
  "user_id": "usr_99812",
  "destination": "Japan",
  "duration_days": 5,
  "budget": 2500.0,
  "currency": "USD",
  "additional_notes": "Interested in historical temples and vegetarian dining."
}
```

#### Response Payload:
```json
{
  "session_id": "sess-a1b2c3d4",
  "conversation_id": "conv-e5f6g7h8",
  "request_id": "req-9i0j1k2l",
  "status": "SUCCESS",
  "destination": "Japan",
  "duration_days": 5,
  "summary": "Customized 5-day itinerary to Japan prepared based on your preferences.",
  "itinerary": [
    {
      "day": 1,
      "title": "Day 1: Exploring Japan",
      "activities": ["Visit top cultural attraction in Japan", "Guided city tour", "Evening relaxation"],
      "dining_recommendations": ["Local specialty restaurant", "Recommended Cafe"]
    }
  ],
  "flights": [
    {
      "airline": "Air Travel Express",
      "flight_number": "AT-101",
      "origin": "SFO",
      "destination": "Japan",
      "departure_time": "09:00 AM",
      "price": 750.0,
      "currency": "USD"
    }
  ],
  "hotels": [
    {
      "name": "The Royal Japan Hotel",
      "rating": 4.9,
      "price_per_night": 240.0,
      "location": "Downtown",
      "amenities": ["Spa", "Pool", "Free WiFi"]
    }
  ],
  "estimated_total_cost": 1950.0,
  "currency": "USD",
  "warnings": [],
  "applied_preferences": ["seat: Window", "diet: Vegetarian"],
  "execution_time_ms": 124.5
}
```

---

## Extending the Platform

To register a new MCP server:
1. Define a client implementing the appropriate provider interface under `app/integrations/`.
2. Add instantiation logic in the corresponding factory under `app/factories/`.
3. Update `McpConfig` in `app/config/settings.py`.
4. Register the new tool definition in `TravelToolsMcpClient.get_available_tools()`.