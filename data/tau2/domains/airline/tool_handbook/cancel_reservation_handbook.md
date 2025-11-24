# Tool Handbook: `cancel_reservation`

## Overview

**Tool Name:** `cancel_reservation`
**Purpose:** This tool allows an agent to cancel a user's flight reservation when specific policy and eligibility conditions are met.

## API Signature

```
cancel_reservation(    reservation_id)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `reservation_id` | string | Yes | The unique identifier for the reservation to be cancelled. | Must be provided and correspond to the reservation the user wishes to cancel; agent must assist in locating it if unknown. |

---

# When to Use

Use the **cancel_reservation** tool when a user explicitly requests to cancel a flight reservation and at least one **policy-approved condition** is satisfied.

* The user requests cancellation and the booking was made within the last 24 hours.
* The user requests cancellation and the flight has been cancelled by the airline.
* The user requests cancellation and the reservation is for a business flight.
* The user requests cancellation, has travel insurance, and the reason for cancellation is covered by their insurance (e.g., health or weather reasons).

---

# When NOT to Use

Do **not** use this tool when:

* Any portion of the flight in the reservation has already been flown; instead, transfer the user to a human agent.
* The user request is against policy or does not meet any allowed cancellation condition.
* The required information (user id, reservation id, reason for cancellation) has not been obtained.
* The user does not provide explicit confirmation to proceed with cancellation.
* The cancellation is not covered by the user's travel insurance (if insurance is cited as the reason).

---

# Prerequisites

Prerequisites are the information inputs that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. User Identity

* User id must be obtained from the user.
### 2. Reservation Details

* Reservation id must be obtained from the user.
* If the user does not know their reservation id, the agent should assist in locating it using available tools.
### 3. Cancellation Reason

* The reason for cancellation (e.g., change of plan, airline cancelled flight, or other) must be collected.
### 4. User Confirmation

* The agent must list the action details and obtain explicit user confirmation (yes) before proceeding.

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before proceeding to policy checks.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Flight Eligibility

* Verify that **no portion of the flight has already been flown**.
## 2. Cancellation Conditions

* At least one of the following must be true: **booking was made within the last 24 hours**, **flight is cancelled by the airline**, **it is a business flight**, or **user has travel insurance and the reason is covered by insurance**.
## 3. Parameter Validation

* The **reservation_id** provided must correspond to the reservation the user wishes to cancel.
## 4. User Confirmation

* Explicit user confirmation (e.g., 'yes') to proceed with cancellation must be obtained.

---

# Edge Cases & Special Considerations

* If the user does not know their reservation id, the agent must assist in locating it before proceeding.
* If any portion of the flight has already been flown, the agent cannot process the cancellation and must transfer the user to a human agent.
* If the user has travel insurance, cancellation is only allowed if the reason is covered by the insurance policy (e.g., health or weather).
* The API does not enforce cancellation rules; the agent must manually verify all policy conditions before calling the tool.
* Refunds for cancellations will be processed to the original payment method within 5 to 7 business days.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user requests to cancel a business flight reservation that was booked 3 days ago.

**Context:**
- User provides user id and reservation id.
- The reservation is for a business flight.
- No portion of the flight has been flown.
- The agent lists the cancellation details and receives explicit confirmation from the user.

**Tool Call:**
```json
{
  "arguments": {
    "reservation_id": "ABC123456"
  },
  "tool": "cancel_reservation"
}
```

**Why this is valid:** This is valid because the user requested cancellation, provided all required information, the reservation is for a business flight (an allowed condition), no flight segments have been flown, and explicit confirmation was obtained (policy lines 143, 145, 7, 135, 141).

---

### ❌ Invalid Usage Example 1

**Scenario:** A user requests to cancel a reservation after completing the first leg of a multi-leg flight.

**Context:**
- User provides user id and reservation id.
- The agent verifies that the outbound flight has already been flown.
- The user requests cancellation and provides a valid reason.

**Tool Call:**
```json
{
  "arguments": {
    "reservation_id": "DEF987654"
  },
  "tool": "cancel_reservation"
}
```

**Why this violates policy:** This is invalid because a portion of the flight has already been flown; per policy, the agent must transfer the user to a human agent and cannot process the cancellation (policy lines 141, 15).

---
