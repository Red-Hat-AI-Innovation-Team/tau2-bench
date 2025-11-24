# Tool Handbook: `search_direct_flight`

## Overview

**Tool Name:** `search_direct_flight`
**Purpose:** This tool allows agents to search for available direct flights between a specified origin and destination on a given date.

## API Signature

```
search_direct_flight(    origin,    destination,    date)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `origin` | string | Yes | The departure airport or city code. | Must be a valid airport or city code as specified by the user; required parameter. |
| `destination` | string | Yes | The arrival airport or city code. | Must be a valid airport or city code as specified by the user; required parameter. |
| `date` | string | Yes | The date of the desired flight (YYYY-MM-DD). | Must be a valid date in the future (relative to current time 2024-05-15 15:00:00 EST); required parameter. |

---

# When to Use

Use the **search_direct_flight** tool when a user requests to find **available direct flights** between a specific origin and destination on a particular date, especially as part of the **booking** or **flight modification** process. The tool is limited to direct flights only by its design.

* When the user wants to search for direct flights between two locations on a specific date.
* When the user provides both **origin** and **destination** information and a **date** for travel.
* When assisting the user in locating flights before proceeding with booking or modifying a reservation.
* When verifying availability of direct flights as part of pre-booking checks.

---

# When NOT to Use

Do **not** use this tool when:

* If the user does not provide both **origin** and **destination** information.
* If the user requests information about indirect flights, baggage, payment, or unrelated topics. (The tool is limited to direct flights only; it cannot process indirect flight searches.)
* If the user requests actions not supported by this tool, such as booking, modification, or cancellation.
* If the agent is responding to the user in the same turn as making the tool call (tool calls and user responses must not be simultaneous).
* If the requested date is in the past or the flight has already taken off.
* If the agent is asked to provide subjective recommendations, opinions, or information not provided by the user or available tools (per general agent conduct rules).

---

# Prerequisites

Prerequisites are the information inputs that must be collected before any validation or tool call can occur. Agents must ensure all required details are gathered and that tool usage complies with general conduct rules.

Before calling the tool, the agent must have collected:

### 1. Flight Search Details

* User's intended **origin** (valid airport or city code).
* User's intended **destination** (valid airport or city code).
* User's intended **date of travel** (must be a valid future date).
### 2. Tool Call Sequencing and Conduct

* Ensure only one tool call is made at a time.
* Do not respond to the user simultaneously with making a tool call.
* Do not provide subjective recommendations, opinions, or information not provided by the user or available tools.

Prerequisites ensure all required information is collected and that general agent conduct rules are followed before proceeding to policy checks. They do not enforce policy validity themselves.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Parameter Validity

* The **origin** and **destination** must be valid airport or city codes provided by the user.
* The **date** must be a valid date in the future (**after 2024-05-15 15:00:00 EST**).
## 2. Scope of Tool and Request

* The request must be for a **direct flight** search only (this is a tool limitation, not a policy rule).
* No simultaneous tool call and user response in the same turn.
* Do not provide information or procedures not available from the user or the tool.
## 3. Flight Status

* Do not search for flights that are already **flying** (departed) or for dates in the past.
* If the flight status is **delayed** or **on time**, results may be returned but booking is not possible.
* If the flight status is **available**, the tool can return available seats and prices.

---

# Edge Cases & Special Considerations

* If the user requests a search for a date in the past or for a flight that has already taken off, the tool must not be used.
* If the user requests a flight with status 'delayed' or 'on time', results may be shown but booking cannot proceed.
* If the user requests a flight with status 'available', the tool can return seats and prices.
* If any required parameter (**origin**, **destination**, **date**) is missing, the tool must not be called.
* If the user asks for indirect flights, the tool is not applicable due to tool limitations (not a policy rule); the agent should not attempt to search for indirect flights.
* If the user requests information not available from the tool or not provided by the user, the agent must not provide it.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user wants to find direct flights from JFK (New York) to LAX (Los Angeles) on 2024-06-01.

**Context:**
- User has provided both origin and destination airport codes.
- User has specified a future date.
- No simultaneous tool call and user response.
- Agent does not provide any subjective recommendations or information not available from the tool.

**Tool Call:**
```json
{
  "arguments": {
    "date": "2024-06-01",
    "destination": "LAX",
    "origin": "JFK"
  },
  "tool": "search_direct_flight"
}
```

**Why this is valid:** This is valid because all required parameters are provided, the date is in the future, the request is within the tool's scope (searching for direct flights), and the agent follows all conduct rules. (Policy lines: 3, 5, 9, 36, 37, 40, 41, 67)

---

### ❌ Invalid Usage Example 1

**Scenario:** A user asks to search for direct flights from ORD (Chicago) to SFO (San Francisco) on 2024-05-10.

**Context:**
- User has provided both origin and destination airport codes.
- User has specified a date in the past (before current time 2024-05-15 15:00:00 EST).

**Tool Call:**
```json
{
  "arguments": {
    "date": "2024-05-10",
    "destination": "SFO",
    "origin": "ORD"
  },
  "tool": "search_direct_flight"
}
```

**Why this violates policy:** This is invalid because the requested date is in the past, violating the policy that the date must be in the future. The tool must not be used for past dates. (Policy lines: 3, 41, 43)

---
