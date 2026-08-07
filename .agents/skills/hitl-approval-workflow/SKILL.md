---
name: hitl-approval-workflow
description: Playbook for inspecting and resolving Human-in-the-Loop (HITL) approval states and risk assessment triggers.
---

# Human-in-the-Loop (HITL) Approval Playbook

This skill outlines how Human-in-the-Loop risk assessment and approval request workflows are evaluated and resolved across `agentic-ai-guardrails`, `travel-agent-service`, and `travel-agent-langgraph-service`.

## Risk Triggers & Approval Lifecycle

1. **Mandatory Approval Triggers**:
   - Financial bookings or payments exceeding `$250.00` auto-approval threshold.
   - Irreversible actions: `FLIGHT_BOOKING`, `HOTEL_BOOKING`, `PAYMENT`, `CANCEL_BOOKING`, `BUDGET_OVERRIDE`.

2. **Risk Categorization**:
   - **LOW**: Flight/hotel searches, weather forecast queries, itinerary generation.
   - **HIGH / CRITICAL**: Binding reservations or payments above threshold.

3. **Status Code**:
   When triggered, responses set `status="AWAITING_HUMAN_APPROVAL"`, `requires_human_approval=True`, and attach an `ApprovalRequestDTO`.
