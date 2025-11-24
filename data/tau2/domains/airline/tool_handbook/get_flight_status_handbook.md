# Tool Handbook: `get_flight_status`

## Overview

**Tool Name:** `get_flight_status`
**Purpose:** Retrieves the current status of a specific flight based on its flight number and scheduled departure date.

## API Signature

```
get_flight_status(    flight_number,    date)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `flight_number` | string | Yes | The unique identifier for the flight whose status is being queried. | Must be a valid flight number corresponding to the flight of interest; cannot be empty or malformed. |
| `date` | string | Yes | The scheduled departure date of the flight (in local time). | Must be the scheduled departure date (local time) for the flight being queried; must be provided and formatted correctly. |

---

# When to Use

Use this tool when you need to **determine the current status** of a specific flight, especially in scenarios involving **booking, modification, cancellation, or compensation** decisions.

* To check if a flight is available, delayed, on time, flying, or cancelled as part of booking, modifying, or cancelling a reservation.
* To verify if a flight has already taken off or landed, which affects eligibility for booking, modification, or cancellation.
* To confirm flight status when a user complains about a cancelled or delayed flight and requests compensation.
* To validate facts about a flight before proceeding with actions dependent on its status.

---

# When NOT to Use

Do **not** use this tool when:

* If the user request is unrelated to booking, modifying, cancelling, or compensation (e.g., general flight information or unrelated inquiries).
* If either the flight_number or date is missing, unavailable, or cannot be reliably determined.
* If the required parameters are incomplete or do not correspond to a real flight.
* If another tool is more appropriate for the user's request (e.g., searching for available flights rather than checking status).

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. Flight Identification

* A valid flight_number for the flight of interest.
* The scheduled departure date (local time) for the flight.
### 2. Operational Independence

* Ensure the tool call is made independently, without simultaneously responding to the user.

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before proceeding with validation or tool execution.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Parameter Validity

* The **flight_number** must be a valid, recognized identifier for the flight.
* The **date** must be the correct scheduled departure date (local time) for the flight.
## 2. Use Case Alignment

* The request must relate to **booking, modification, cancellation, or compensation** actions.
* The tool must not be used for unrelated or out-of-scope requests.

---

# Edge Cases & Special Considerations

* A flight may have different statuses on different dates; always use the correct date to get the relevant status.
* If a flight is 'flying', it has taken off but not landed, which may affect eligibility for booking, modification, or cancellation.
* If the flight status is 'delayed' or 'on time', the flight has not taken off but cannot be booked.
* If the flight status is 'available', the flight has not taken off and can be booked.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user requests compensation for a delayed flight and provides the flight number and date.

**Context:**
- User is a frequent flyer member.
- User claims their flight (AB123) on 2024-07-01 was delayed and requests compensation.

**Tool Call:**
```json
{
  "arguments": {
    "date": "2024-07-01",
    "flight_number": "AB123"
  },
  "tool": "get_flight_status"
}
```

**Why this is valid:** This is valid because the agent has both required parameters (flight_number and date), the request concerns compensation for a delayed flight, and the tool is used to confirm the flight status before proceeding, as required by policy (policy lines 41, 42, 159, 163, 165).

---

### ❌ Invalid Usage Example 1

**Scenario:** A user asks for the status of a flight but only provides the airline name and destination, not the flight number or date.

**Context:**
- User is not logged in.
- User says: 'What's the status of the flight to Paris with AirBlue?'

**Tool Call:**
```json
{
  "arguments": {
    "date": "",
    "flight_number": ""
  },
  "tool": "get_flight_status"
}
```

**Why this violates policy:** This is invalid because the required parameters (flight_number and date) are missing, violating the prerequisite and parameter constraints (policy lines 11, 35, 38, 40). The tool cannot be used without these inputs.

---
