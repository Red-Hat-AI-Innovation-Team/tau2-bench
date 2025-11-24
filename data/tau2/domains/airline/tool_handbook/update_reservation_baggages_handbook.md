# Tool Handbook: `update_reservation_baggages`

## Overview

**Tool Name:** `update_reservation_baggages`
**Purpose:** Allows updating the number of checked bags on an existing reservation, including adding paid (nonfree) baggage items.

## API Signature

```
update_reservation_baggages(    reservation_id,    total_baggages,    nonfree_baggages,    payment_id)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `reservation_id` | string | Yes | Unique identifier for the reservation to be updated. | Must correspond to an existing reservation belonging to the user. |
| `total_baggages` | integer | Yes | Total number of checked bags after the update. | Must be greater than or equal to the current number of checked bags (cannot decrease); should not include bags the user does not need. |
| `nonfree_baggages` | integer | Yes | Number of checked bags exceeding the user's free allowance. | Must be the number of bags above the free allowance based on membership level and cabin class; each nonfree bag costs $50; cannot exceed airline/system-imposed limits. |
| `payment_id` | string | Yes | Payment method identifier for nonfree baggages. | Required if nonfree_baggages > 0; must be a payment method already in the user's profile. |

---

# When to Use

Use this tool **only when the user explicitly requests to add checked bags** to an existing reservation and has confirmed the action after being presented with all details.

* When the user requests to add checked bags to an existing reservation.
* When modifying baggage information after obtaining explicit user confirmation.
* When the user has provided a valid payment method for any nonfree (paid) baggage.
* When the reservation is not for a basic economy flight where only baggage changes are allowed.

---

# When NOT to Use

Do **not** use this tool when:

* To remove checked bags from a reservation (decreasing the total is not allowed).
* If the user has not provided explicit confirmation after being shown action details.
* If the reservation is for a basic economy flight and the user is attempting to modify the flight itself (only baggage changes are allowed).
* If the payment method for nonfree baggage is not in the user's profile.
* If the request violates any stated policy (e.g., exceeding baggage limits, removing bags).
* If the scenario requires actions outside the tool's scope (e.g., canceling a reservation, changing flights).

---

# Prerequisites

Prerequisites are the information inputs that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. Reservation Details

* The reservation_id of the reservation to be updated.
### 2. User Confirmation

* Explicit user confirmation after listing the action details (number of bags, costs, payment method, etc.).
### 3. Payment Information

* A valid payment_id for any nonfree baggages (if nonfree_baggages > 0).

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before proceeding to policy checks.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Reservation and User Eligibility

* The **reservation_id** must belong to the user and refer to an existing reservation.
* The reservation must not be for a basic economy flight if the user is attempting to change the flight itself (baggage changes are allowed).
## 2. Baggage Policy Compliance

* The **total_baggages** must be **greater than or equal to** the current number of checked bags (no removals allowed).
* The **total_baggages** must not exceed the airline/system-imposed maximum for the user's membership level and cabin class.
* The **nonfree_baggages** must be calculated as the number of bags exceeding the user's free allowance.
## 3. Payment Validation

* If **nonfree_baggages > 0**, the **payment_id** must be a payment method already saved in the user's profile.
* Each nonfree baggage must be charged at **$50** per bag.
## 4. User Confirmation

* Explicit user confirmation must be obtained after listing all action details (including costs and payment method).

---

# Edge Cases & Special Considerations

* If the user tries to remove checked bags (set total_baggages lower than current), the request must be denied.
* If the user requests more checked bags than allowed by their membership level or airline policy, the request must be denied.
* If the payment method provided for nonfree baggages is not in the user's profile, the request must be denied.
* If the user attempts to change the flight on a basic economy reservation, the request must be denied (only baggage changes allowed).

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A Gold member wants to add one extra checked bag to their reservation after being shown the cost and confirming the action.

**Context:**
- User is a Gold member with a reservation (ID: RES123) that currently has 1 checked bag.
- Gold members have a free allowance of 1 checked bag.
- User requests to add 1 more checked bag (total will be 2).
- Agent lists the action details: 1 extra bag at $50, payment method ending in 1234.
- User provides explicit confirmation.

**Tool Call:**
```json
{
  "arguments": {
    "nonfree_baggages": 1,
    "payment_id": "pm_1234",
    "reservation_id": "RES123",
    "total_baggages": 2
  },
  "tool": "update_reservation_baggages"
}
```

**Why this is valid:** This is valid because the user is only adding bags (not removing), the number of bags does not exceed policy limits, the nonfree bag is correctly calculated, the payment method is on file, and explicit confirmation was obtained.

---

### ❌ Invalid Usage Example 1

**Scenario:** A user tries to reduce their checked bags from 2 to 1 on an existing reservation.

**Context:**
- User has a reservation (ID: RES456) with 2 checked bags.
- User requests to reduce to 1 checked bag.
- Agent prepares to call the tool with total_baggages: 1.

**Tool Call:**
```json
{
  "arguments": {
    "nonfree_baggages": 0,
    "payment_id": "",
    "reservation_id": "RES456",
    "total_baggages": 1
  },
  "tool": "update_reservation_baggages"
}
```

**Why this violates policy:** This is invalid because policy prohibits removing checked bags (total_baggages cannot be set lower than the current number). The request must be denied and the user should be transferred to a human agent if needed.

---
