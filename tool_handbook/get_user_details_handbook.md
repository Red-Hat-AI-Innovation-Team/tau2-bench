# Tool Handbook: `get_user_details`

## Overview

**Tool Name:** `get_user_details`
**Purpose:** Retrieves comprehensive user profile information using a valid user_id to support booking, modification, or cancellation of flight reservations and related eligibility checks.

## API Signature

```
get_user_details(    user_id)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | Yes | The unique identifier for the user whose profile details are to be retrieved. | Must be a valid string corresponding to an existing user profile; required for all calls; cannot be omitted or null. |

---

# When to Use

Use this tool when **user profile information** is needed to perform or validate booking, modification, or cancellation actions, or to check **eligibility** for refunds, compensation, or membership-based benefits.

* To obtain or verify user profile details (user id, email, addresses, date of birth, payment methods, membership level, reservation numbers) required for booking, modifying, or cancelling flight reservations.
* When the user has not provided their user id and it is necessary to proceed with a reservation-related action.
* To confirm that a payment method is already present in the user profile before using it for booking or modification.
* To check the user's membership level for determining baggage allowance, compensation eligibility, or other membership-based rules.

---

# When NOT to Use

Do **not** use this tool when:

* If the user id and all required user profile information are already available to proceed with the action.
* To retrieve information not present in the user profile (e.g., data outside user id, email, addresses, date of birth, payment methods, membership level, reservation numbers).
* For actions outside the agent's permitted scope, such as providing subjective recommendations or information not supported by available tools.

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. User Identity

* A valid user_id provided by the user or collected through prompting if not initially available.
### 2. Single Tool Call Context

* No simultaneous tool calls or user responses; only one tool call should be made at a time.

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before attempting a tool call.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. User ID Validation

* The provided **user_id** must be a **string**.
* The **user_id** must correspond to an **existing user profile** in the system.
## 2. Scope of Information

* Requested information must be limited to **user profile fields**: user id, email, addresses, date of birth, payment methods (credit card, gift card, travel certificate), membership level (regular, silver, gold), and reservation numbers.
* Do **not** attempt to retrieve or infer information outside these fields using this tool.
## 3. Policy-Driven Usage

* Only use the tool when required for booking, modifying, cancelling reservations, or eligibility checks for refunds or compensation.
* Do **not** use the tool if all required user profile information is already available.

---

# Edge Cases & Special Considerations

* If the user does not know their user id, prompt the user to provide it before proceeding.
* If the provided user id does not match any user profile, handle the error gracefully and inform the user.
* Do not use the tool to retrieve information not present in the user profile, even if requested by the user.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** User wants to modify a flight reservation but has not provided their payment method information.

**Context:**
- User is a gold member.
- User provides their user_id.
- Agent needs to verify if the user's preferred payment method is on file before proceeding.

**Tool Call:**
```json
{
  "arguments": {
    "user_id": "USR123456"
  },
  "tool": "get_user_details"
}
```

**Why this is valid:** This is valid because the agent needs to confirm the user's payment methods (which must be present in the user profile) before modifying the reservation, and the user_id is provided and valid (policy lines 80, 131, 21, 65).

---

### ❌ Invalid Usage Example 1

**Scenario:** User asks for their frequent flyer points balance, and the agent calls get_user_details to retrieve it.

**Context:**
- User provides their user_id.
- Frequent flyer points are not part of the user profile fields defined by policy.

**Tool Call:**
```json
{
  "arguments": {
    "user_id": "USR987654"
  },
  "tool": "get_user_details"
}
```

**Why this violates policy:** This is invalid because the requested information (frequent flyer points) is not part of the user profile fields allowed by policy (policy lines 21, 9). The tool should not be used for data outside the defined user profile scope.

---
