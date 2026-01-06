# Tool Handbook: `get_reservation_details`

## Overview

**Tool Name:** `get_reservation_details`
**Purpose:** Retrieves detailed information about a specific reservation using a reservation ID, with strict association to the user's identity.

## API Signature

```
get_reservation_details(    reservation_id)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `reservation_id` | string | Yes | The unique identifier for the reservation to be retrieved. | Must be a valid reservation ID explicitly associated with the provided user ID; required for the tool call. If not known, the agent should attempt to locate it using available tools before proceeding. The agent must not provide information not available from the user or tools. |

---

# When to Use

Use this tool whenever you need to **retrieve, verify, or confirm reservation details** for actions such as booking, modifying, or cancelling flights, or when assisting users in locating their reservation information. Always ensure the **user ID** is obtained and the reservation is associated with that user.

* When the user provides a reservation ID and user ID and requests details about their reservation.
* When verifying reservation details before modifying, cancelling, or confirming a booking, ensuring the reservation is linked to the provided user ID.
* When validating reservation status, passenger information, payment methods, baggage, or insurance prior to further actions.
* When the user does not know their reservation ID and needs assistance in locating it, provided sufficient identifying information (such as user ID or email) is available.

---

# When NOT to Use

Do **not** use this tool when:

* When the user's request is unrelated to booking, modifying, or cancelling reservations, or does not pertain to refunds or compensation.
* When the user has not provided enough information to identify the reservation and no available tools can help locate it.
* When responding to the user directly in the same turn—do not call the tool and respond simultaneously.
* When the reservation ID is not associated with the provided user ID.
* When information requested is not available from the user or accessible tools.

---

# Prerequisites

Prerequisites are the **required information inputs** that must be collected before any validation or tool call can occur. These ensure the agent has sufficient data to comply with policy and maintain user privacy.

Before calling the tool, the agent must have collected:

### 1. User Identity

* A valid user ID must be obtained before using or searching for a reservation ID.
* If user ID is not directly provided, sufficient identifying information (e.g., email, login credentials) must be collected to establish user identity.
### 2. Reservation Identification

* A valid reservation ID associated with the user ID must be provided or located.
* If reservation ID is unknown, use available tools to help the user locate it using their user ID or other identifying details.
### 3. Action Scope Confirmation

* Confirmation that the intended action is within the allowed scope (**booking, modifying, cancelling, refunds, or compensation**).

Prerequisites ensure the agent has gathered all required information before proceeding to policy checks. They do not, by themselves, guarantee policy compliance.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. User and Reservation Association

* The **user ID** must be obtained and verified before using the **reservation_id**.
* The **reservation_id** must be valid and explicitly associated with the provided **user ID**.
## 2. Scope of Action

* The intended action must be within the allowed scope (**booking, modifying, cancelling, refunding, or compensating** a reservation).
## 3. Single Action per Turn

* Do **not** call this tool and respond to the user in the same turn; only one action is allowed at a time.
## 4. Information Availability

* Do **not** provide information that is not available from the user or accessible tools.

---

# Edge Cases & Special Considerations

* If the user does not know their reservation ID, the agent should use available tools to help locate it using the user ID or other identifying information before proceeding.
* If the provided reservation ID does not match any reservation associated with the user ID, inform the user and request more information or escalate as needed.
* If multiple reservations are found for the user with similar details, clarify with the user to determine the correct reservation before proceeding.
* If the reservation contains flights that have already been flown, certain actions (like modification or cancellation) may not be allowed; check flight status before proceeding.
* If the reservation ID format is invalid or malformed, inform the user and request a valid reservation ID or additional identifying information.
* If the agent cannot fulfill the user's request after retrieving reservation details due to policy restrictions, escalate to a human agent.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user wants to confirm the details of their upcoming flight before requesting a seat change.

**Context:**
- User is logged in and provides both a valid user ID and reservation ID.
- The action (seat change) requires confirmation of reservation and passenger details.
- The reservation ID is verified to be associated with the provided user ID.

**Tool Call:**
```json
{
  "arguments": {
    "reservation_id": "ABC123456"
  },
  "tool": "get_reservation_details"
}
```

**Why this is valid:** This is valid because the user provided both user ID and a valid reservation ID associated with that user, the action is within the allowed scope (modification), and all prerequisites and policy checks are satisfied.

---

### ❌ Invalid Usage Example 1

**Scenario:** A user provides a reservation ID but no user ID, and requests details about the reservation.

**Context:**
- User has not provided a user ID or any identifying information.
- The agent cannot verify if the reservation ID is associated with the user.
- Policy requires user ID to be obtained before using reservation ID.

**Tool Call:**
```json
{
  "arguments": {
    "reservation_id": "XYZ987654"
  },
  "tool": "get_reservation_details"
}
```

**Why this violates policy:** This is invalid because the agent did not obtain or verify the user ID before using the reservation ID, violating policy lines 65, 105, and 135. The association between the user and the reservation cannot be confirmed.

---
