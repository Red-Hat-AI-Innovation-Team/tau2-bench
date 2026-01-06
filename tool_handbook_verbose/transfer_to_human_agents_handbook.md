# Tool Handbook: `transfer_to_human_agents`

## Overview

**Tool Name:** `transfer_to_human_agents`
**Purpose:** Transfers the user to a human agent when their request cannot be handled within the agent's scope of actions.

## API Signature

```
transfer_to_human_agents(    summary)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `summary` | string | Yes | A concise explanation of why the transfer to a human agent is necessary. | This is a handbook-imposed constraint for clarity and auditability; it is not explicitly required by policy but ensures every transfer is justified with a specific reason. |

---

# When to Use

Use the **transfer_to_human_agents** tool when a user's request is **outside the scope** of automated actions or **requires human intervention**. This ensures that complex or restricted scenarios are escalated appropriately and in compliance with policy.

* The user's request cannot be fulfilled by the agent due to policy or technical limitations.
* A user requests cancellation of a reservation where any portion of the flight has already been flown.
* The situation requires human judgment or access to resources unavailable to the agent.
* The user explicitly requests to speak with a human and their request cannot be resolved by the agent.

---

# When NOT to Use

Do **not** use this tool when:

* The user's request can be fully handled within the agent's capabilities.
* The request is against policy and must be denied (e.g., requests that are not permitted for any agent, human or automated).
* The user requests to modify the number of passengers in a reservation, as neither the agent nor a human agent can perform this action.
* Transferring solely for user preference when the agent can resolve the request within policy.

---

# Prerequisites

Prerequisites are the **required information and steps** that must be gathered and completed before making a tool call or validating eligibility for transfer.

Before calling the tool, the agent must have collected:

### 1. Request Assessment

* Full details of the user's request, including all relevant context.
* Verification that the request cannot be handled by the agent.
### 2. Transfer Justification

* A clear, policy-aligned summary explaining why transfer is necessary (handbook-imposed constraint).

Prerequisites ensure all necessary information is collected before proceeding, but do not themselves enforce policy validity. The requirement for a 'summary' parameter is imposed by this handbook for auditability, not by explicit policy.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Scope Validation

* The request is **outside the agent's scope** and cannot be fulfilled by automated actions.
* The agent has **verified** that no available tool or workflow can resolve the request.
## 2. Policy Compliance

* The request is **not explicitly denied by policy** (e.g., requests to modify passenger count must be denied, not transferred).
* The transfer is **not being used to circumvent policy restrictions**.
## 3. Parameter Requirements

* A **summary** parameter is provided, clearly stating the reason for transfer (handbook-imposed constraint for clarity and auditability).
## 4. Transfer Workflow Enforcement

* The agent must **not make a tool call and respond to the user simultaneously**; only one action at a time (per policy line 11).
* After making the transfer_to_human_agents tool call, the agent must send the message '**YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.**' to the user (per policy line 15).

---

# Edge Cases & Special Considerations

* If the user requests to modify the number of passengers in a reservation, deny the request—do not transfer.
* If any portion of a flight in a reservation has already been flown and the user requests cancellation, transfer to a human agent is required.
* Do not make a tool call and respond to the user simultaneously; only one action at a time.
* After making the transfer_to_human_agents tool call, always send the message 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user.
* If the agent can resolve the request, do not transfer even if the user requests a human.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user requests to cancel a reservation, but one leg of the flight has already been flown.

**Context:**
- User has a round-trip reservation.
- The outbound flight has been completed; the return flight is pending.
- User requests cancellation of the reservation.

**Tool Call:**
```json
{
  "arguments": {
    "summary": "User requests cancellation of a reservation where one flight segment has already been flown; this cannot be handled by the agent."
  },
  "tool": "transfer_to_human_agents"
}
```

**Why this is valid:** This is valid because policy requires transfer to a human agent when cancellation is requested for a reservation with any flown segment (policy line 141). After the tool call, the agent must send the message 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user.

---

### ❌ Invalid Usage Example 1

**Scenario:** A user requests to change the number of passengers in their reservation.

**Context:**
- User has a confirmed reservation for 2 passengers.
- User wants to add a third passenger to the reservation.

**Tool Call:**
```json
{
  "arguments": {
    "summary": "User requests to modify the number of passengers in a reservation, which cannot be handled by the agent."
  },
  "tool": "transfer_to_human_agents"
}
```

**Why this violates policy:** This is invalid because neither the agent nor a human agent can modify the number of passengers in a reservation; the request should be denied, not transferred (policy line 128).

---
