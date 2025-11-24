# Tool Handbook: `update_reservation_passengers`

## Overview

**Tool Name:** `update_reservation_passengers`
**Purpose:** Allows modification of passenger details (such as name or date of birth) for an existing reservation, without changing the number of passengers.

## API Signature

```
update_reservation_passengers(    reservation_id,    passengers)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `reservation_id` | string | Yes | The unique identifier for the reservation to be updated. | Must be a valid reservation id corresponding to the user's reservation. |
| `passengers` | string | Yes | A structured string (typically JSON) containing the updated details for all passengers in the reservation. | Number of passengers must remain the same as in the original reservation; each reservation can have at most five passengers; for each passenger, first name, last name, and date of birth must be provided. |

---

# When to Use

Use this tool when a user needs to **modify passenger information**—such as names or dates of birth—on an existing reservation, provided the **number of passengers remains unchanged**.

* The user requests to correct or update a passenger's name, date of birth, or other personal details for an existing reservation.
* All passengers in the reservation remain the same in number; only their details are being modified.
* The user has provided explicit confirmation to proceed with the listed changes.

---

# When NOT to Use

Do **not** use this tool when:

* The user wants to add or remove passengers, thereby changing the number of passengers in the reservation.
* The action details have not been listed or explicit user confirmation has not been obtained.
* The request violates any stated policy or exceeds the maximum allowed number of passengers.
* The user does not have or cannot provide a valid reservation ID.
* The user requests changes outside of passenger details (e.g., flight changes, seat upgrades).

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. Reservation Information

* A valid reservation_id for the reservation to be updated.
### 2. User Identity

* The user ID of the user making the request.
### 3. Action Confirmation

* A clear list of the specific passenger detail changes to be made.
* Explicit user confirmation (e.g., a 'yes' response) to proceed with the changes.

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before proceeding to validation.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Reservation and User Validation

* The provided reservation_id is a **valid reservation identifier** and belongs to the requesting user.
## 2. Passenger Count and Details

* The **number of passengers** in the update matches the original reservation (no additions or removals).
* Each reservation contains **no more than five passengers**.
* For each passenger, **first name, last name, and date of birth** are provided.
## 3. User Confirmation

* The agent has **listed all action details** and obtained **explicit user confirmation** before calling the tool.
## 4. Policy Compliance

* The request does **not violate any stated policy** (e.g., changing the number of passengers is not allowed).

---

# Edge Cases & Special Considerations

* If the user requests to add or remove passengers, deny the request and inform them that even a human agent cannot modify the number of passengers.
* If the user does not know their reservation id, assist in locating it using available tools before proceeding.
* If the user attempts to update details for more than five passengers, deny the request.
* If any passenger's required fields (first name, last name, date of birth) are missing, the request must not proceed.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user notices a typo in one passenger's last name and wants to correct it for an existing reservation with three passengers.

**Context:**
- User is logged in and has provided their user ID.
- User provides the reservation_id and lists the correction needed.
- Agent lists the action details and obtains explicit confirmation from the user.

**Tool Call:**
```json
{
  "arguments": {
    "passengers": "[{\"first_name\": \"John\", \"last_name\": \"Doe\", \"date_of_birth\": \"1980-01-01\"}, {\"first_name\": \"Jane\", \"last_name\": \"Smith\", \"date_of_birth\": \"1985-05-05\"}, {\"first_name\": \"Alice\", \"last_name\": \"Johnson\", \"date_of_birth\": \"1990-09-09\"}]",
    "reservation_id": "ABC123456"
  },
  "tool": "update_reservation_passengers"
}
```

**Why this is valid:** This is valid because the user is only correcting a passenger's last name, the number of passengers remains unchanged, all required details are provided, and explicit confirmation was obtained (policy lines 5, 74, 7).

---

### ❌ Invalid Usage Example 1

**Scenario:** A user wants to add a fourth passenger to a reservation that originally had three passengers.

**Context:**
- User provides their user ID and reservation_id.
- User requests to add a new passenger.
- Agent lists the action and obtains confirmation.

**Tool Call:**
```json
{
  "arguments": {
    "passengers": "[{\"first_name\": \"John\", \"last_name\": \"Doe\", \"date_of_birth\": \"1980-01-01\"}, {\"first_name\": \"Jane\", \"last_name\": \"Smith\", \"date_of_birth\": \"1985-05-05\"}, {\"first_name\": \"Alice\", \"last_name\": \"Johnson\", \"date_of_birth\": \"1990-09-09\"}, {\"first_name\": \"Bob\", \"last_name\": \"Brown\", \"date_of_birth\": \"1992-12-12\"}]",
    "reservation_id": "XYZ987654"
  },
  "tool": "update_reservation_passengers"
}
```

**Why this violates policy:** This is invalid because the user is attempting to change the number of passengers (from three to four), which is strictly prohibited by policy—even with confirmation. The tool must not be used for adding or removing passengers (policy lines 127, 128).

---
