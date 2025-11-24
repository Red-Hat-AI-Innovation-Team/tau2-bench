# Tool Handbook: `send_certificate`

## Overview

**Tool Name:** `send_certificate`
**Purpose:** The send_certificate tool is used to issue a certificate as compensation to eligible users who explicitly request compensation for cancelled or delayed flights.

## API Signature

```
send_certificate(    user_id,    amount)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | Yes | The unique identifier of the user requesting compensation. | Must be the user id of the user explicitly requesting compensation; cannot be used for other users. |
| `amount` | integer | Yes | The dollar value of the certificate to be issued. | For cancelled flights: $100 x number of passengers. For delayed flights: $50 x number of passengers. Only these calculations are allowed. |

---

# When to Use

Use the send_certificate tool **only when** a user has **explicitly requested compensation** and has a confirmed complaint about a **cancelled or delayed flight** in their reservation, and all eligibility criteria are met.

* The user explicitly asks for compensation after a cancelled flight in their reservation, and the cancellation is confirmed.
* The user explicitly asks for compensation after a delayed flight in their reservation, and the delay is confirmed.
* The user is a silver or gold member, or has travel insurance, or is flying business class.
* All facts about the flight disruption and user eligibility have been verified.

---

# When NOT to Use

Do **not** use this tool when:

* The user does not explicitly request compensation, even if they mention a cancelled or delayed flight.
* The user is a regular member, has no travel insurance, and is flying (basic) economy.
* The complaint is about issues other than cancelled or delayed flights (e.g., baggage, seat assignment, etc.).
* You do not have the user's user_id or cannot confirm the facts of the complaint.
* You have already made a tool call and are attempting to respond to the user simultaneously.

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. User Identity

* The user's user_id.
### 2. Flight Disruption Details

* Confirmation of a cancelled or delayed flight in the user's reservation.
* Number of passengers in the reservation.
### 3. User Eligibility

* User's membership status (regular, silver, gold).
* Whether the user has travel insurance.
* Class of service (economy, business).
### 4. Explicit Request

* Clear evidence that the user has explicitly asked for compensation.

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before applying policy checks.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. User Request Verification

* The user has **explicitly requested compensation** for a cancelled or delayed flight.
## 2. Flight Disruption Confirmation

* The flight disruption (**cancelled** or **delayed**) is **confirmed** in the reservation and not based solely on user statements.
## 3. Eligibility Criteria

* The user is a **silver or gold member**, **has travel insurance**, or is **flying business class**.
* The user is **not** a regular member without insurance flying (basic) economy.
## 4. Parameter Calculation

* For a **cancelled flight**, set **amount** to **$100 x number of passengers**.
* For a **delayed flight**, set **amount** to **$50 x number of passengers**.

---

# Edge Cases & Special Considerations

* Do not offer compensation if the user is a regular member, has no travel insurance, and flies (basic) economy, even if they complain about a cancelled or delayed flight.
* Do not proactively offer compensation if the user does not explicitly ask for it, regardless of eligibility.
* Do not use the tool for compensation requests unrelated to cancelled or delayed flights.
* Do not rely solely on user statements; always confirm flight disruption facts.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A gold member user explicitly requests compensation after their flight was cancelled for a reservation with 2 passengers, and the cancellation is confirmed.

**Context:**
- User is a gold member
- Flight cancellation is confirmed in the reservation
- There are 2 passengers in the reservation
- User explicitly asks for compensation

**Tool Call:**
```json
{
  "arguments": {
    "amount": 200,
    "user_id": "user_12345"
  },
  "tool": "send_certificate"
}
```

**Why this is valid:** This is valid because the user is eligible (gold member), the cancellation is confirmed, the user explicitly requested compensation, and the amount is correctly calculated as $100 x 2 passengers (policy lines 155, 159, 161, 163).

---

### ❌ Invalid Usage Example 1

**Scenario:** A regular member with no travel insurance and flying economy requests compensation for a delayed flight with 1 passenger.

**Context:**
- User is a regular member
- No travel insurance
- Flying (basic) economy
- Flight delay is confirmed
- User explicitly asks for compensation

**Tool Call:**
```json
{
  "arguments": {
    "amount": 50,
    "user_id": "user_67890"
  },
  "tool": "send_certificate"
}
```

**Why this violates policy:** This is invalid because the user is not eligible for compensation (regular member, no insurance, economy class), even though the delay is confirmed and the user requested compensation (policy line 157).

---
