# Tool Handbook: `list_all_airports`

## Overview

**Tool Name:** `list_all_airports`
**Purpose:** Provides a comprehensive list of all available airports to support flight-related actions.

## API Signature

```
list_all_airports(    none)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `none` | N/A | No | This tool does not accept any parameters. | No parameters are allowed; any attempt to provide parameters is invalid. |

---

# When to Use

**Use this tool** when the user needs to view or select from a list of airports, especially in the context of booking, modifying, or canceling flights. **It is essential** for presenting airport options to assist with flight-related actions.

* The user requests information about available airports.
* The user needs to select or specify an origin or destination airport for a booking.
* The agent must present a list of airports to facilitate booking, modifying, or canceling a flight.
* The user asks for airport codes or names to complete a flight-related transaction.
* The agent needs to verify available airports before proceeding with a flight-related process.

---

# When NOT to Use

Do **not** use this tool when:

* The user request is unrelated to booking, modifying, or canceling flights, or does not require airport information.
* The agent is being asked for information or recommendations not available via tools or user input.
* The user is being transferred to a human agent due to an unsupported request.
* The agent is already responding to the user or making another tool call (only one action at a time is allowed).
* The agent needs to provide subjective advice or information not explicitly supported by the tool.

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. Tool-Specific Requirements

* No explicit prerequisites are required, as the tool takes no parameters and is used for informational purposes.

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Scope Validation

* The user request must be **directly related to booking, modifying, canceling, or managing flights**.
* The request must **require airport information** to proceed.
## 2. Tool Usage Exclusivity

* The agent must **not make a tool call and respond to the user simultaneously**; only one action at a time is allowed.
## 3. Information Boundaries

* The agent must **not provide information beyond what is available via tools or user input**.

---

# Edge Cases & Special Considerations

* If the user is being transferred to a human agent because their request cannot be handled, do not use this tool.
* Do not use the tool for requests that do not pertain to flight booking, modification, or cancellation.
* Do not attempt to pass parameters to the tool, as it does not accept any.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user is booking a new flight and asks for a list of available airports to choose their departure location.

**Context:**
- User is logged in and initiating a flight booking.
- No airport has been selected yet.

**Tool Call:**
```json
{
  "arguments": {},
  "tool": "list_all_airports"
}
```

**Why this is valid:** This is valid because the user needs airport information to proceed with booking, which is within the tool's allowed scope (policy lines 67, 9, 11).

---

### ❌ Invalid Usage Example 1

**Scenario:** A user asks for tourist recommendations in a city, and the agent attempts to call list_all_airports to provide airport options.

**Context:**
- User is not engaged in any flight-related process.
- Request is about tourism, not flights.

**Tool Call:**
```json
{
  "arguments": {},
  "tool": "list_all_airports"
}
```

**Why this violates policy:** This is invalid because the request is outside the scope of booking, modifying, or canceling flights and does not require airport information (policy lines 13, 15).

---
