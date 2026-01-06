# Tool Handbook: `search_onestop_flight`

## Overview

**Tool Name:** `search_onestop_flight`
**Purpose:** This tool searches for available flights between a specified origin and destination on a given date to support booking, modifying, or reviewing flight options.

## API Signature

```
search_onestop_flight(    origin,    destination,    date)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `origin` | string | Yes | The departure airport or city code. | Must be a valid airport or city code as recognized by the system; must not be the same as destination. (This is an operational constraint, not directly cited in policy.) |
| `destination` | string | Yes | The arrival airport or city code. | Must be a valid airport or city code as recognized by the system; must not be the same as origin. (This is an operational constraint, not directly cited in policy.) |
| `date` | string | Yes | The date of the desired flight (YYYY-MM-DD). | Must be a valid date in the future for which flights are available; cannot search for flights on dates in the past. (This is an operational constraint, not directly cited in policy, but aligns with only booking available flights.) |

---

# When to Use

Use this tool when a user requests to **search for available flights** between two locations on a **specific date**, especially as part of **booking**, **modifying**, or **reviewing** flight options. Ensure all required information is collected and policy constraints are met before proceeding.

* When the user wants to find flights for a new reservation between a specified origin and destination on a particular date.
* When the user is modifying an existing reservation and needs to select alternative flights (e.g., if they do not know their reservation ID or want to change flights).
* When the user requests to review available flight options for planning purposes, provided all required information is given.
* When supporting a booking workflow that requires presenting flight choices to the user.

---

# When NOT to Use

Do **not** use this tool when:

* When the user requests flights that cannot be booked (e.g., flights with status **'delayed'**, **'on time'**, or **'flying'**).
* When the user request is outside the scope of booking, modifying, or reviewing flights (e.g., asking for **subjective recommendations** or general travel advice). (Policy line 9)
* When the user requests to search for flights for **more than five passengers** (even though the tool does not take passenger count, this must be enforced at the agent level).
* When the user requests unsupported trip types (other than **'one way'** or **'round trip'**).
* When required parameters (**origin**, **destination**, **date**) are missing or invalid.
* When the agent has not obtained explicit user confirmation before taking any action that updates the booking database (Policy line 7).
* When another tool call is in progress or if responding to the user simultaneously with a tool call (Policy line 11).

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected from the user before any validation or tool call can occur. If any required information is missing (e.g., date, trip type, origin, destination), the agent must request it before proceeding.

Before calling the tool, the agent must have collected:

### 1. Trip Details

* Trip type (e.g., **one way** or **round trip**)
* Origin (departure airport or city code)
* Destination (arrival airport or city code)
### 2. Travel Date

* Specific date for the flight search (must be provided and valid)
### 3. Passenger Count

* Number of passengers (must be **five or fewer**; if more, deny the request even though the tool does not take this as a parameter)

Prerequisites ensure all required information is gathered before validation or tool use. They do not enforce policy compliance by themselves; policy checks must still be applied after prerequisites are collected.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Parameter Validity

* The **origin** and **destination** must be valid and recognized airport or city codes.
* The **origin** and **destination** must not be the same. (Operational constraint; not directly cited in policy.)
* The **date** must be a valid date in the future (no past dates). (Operational constraint; not directly cited in policy, but aligns with booking available flights.)
## 2. Flight Eligibility

* Only search for flights that can be booked (exclude flights with status **'delayed'**, **'on time'**, or **'flying'**).
## 3. Policy Compliance

* Do not search for flights for **more than five passengers** (deny request at agent level).
* Only support **one way** or **round trip** trip types; deny unsupported trip types.
* Obtain **explicit user confirmation** before taking any action that updates the booking database (Policy line 7).
* Only make **one tool call at a time** and do not respond to the user simultaneously when making a tool call (Policy line 11).
* Do not provide **subjective recommendations** or information beyond what is available from the user or the tool (Policy line 9).

---

# Edge Cases & Special Considerations

* If all flights on the requested date are **'delayed'**, **'on time'**, or **'flying'**, no bookable flights should be returned.
* Requests for **more than five passengers** must be denied, even if the tool does not take passenger count.
* Requests for unsupported trip types (other than **'one way'** or **'round trip'**) must be denied.
* If the user does not provide all required information (e.g., missing date, trip type, origin, or destination), the agent must ask for the missing details before proceeding.
* If the agent has not obtained explicit user confirmation for booking, modifying, or cancelling, no tool call should be made that updates the booking database.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user wants to book a one-way flight from New York (JFK) to Los Angeles (LAX) for June 20, 2024.

**Context:**
- User is planning a new trip.
- Trip type: one way.
- Passenger count: 2.
- All required information is provided.
- Agent has obtained explicit confirmation to proceed.

**Tool Call:**
```json
{
  "arguments": {
    "date": "2024-06-20",
    "destination": "LAX",
    "origin": "JFK"
  },
  "tool": "search_onestop_flight"
}
```

**Why this is valid:** This is valid because the user provided a valid origin and destination, a specific future date, the trip type and passenger count are within policy limits, and the agent has obtained explicit user confirmation (policy lines 5, 7, 34, 40, 41, 67).

---

### ❌ Invalid Usage Example 1

**Scenario:** A user requests to search for flights for 7 passengers from Paris (CDG) to Rome (FCO) for July 15, 2024.

**Context:**
- User is attempting to book a flight.
- Trip type: round trip.
- Passenger count: 7 (exceeds policy limit).
- All other required information is provided.

**Tool Call:**
```json
{
  "arguments": {
    "date": "2024-07-15",
    "destination": "FCO",
    "origin": "CDG"
  },
  "tool": "search_onestop_flight"
}
```

**Why this violates policy:** This is invalid because the request is for more than five passengers, which violates policy even though the tool does not take passenger count (policy line 73).

---
