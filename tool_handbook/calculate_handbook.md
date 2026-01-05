# Tool Handbook: `calculate`

## Overview

**Tool Name:** `calculate`
**Purpose:** Performs explicit arithmetic calculations for determining amounts such as fees, costs, compensation, or price differences as required by policy.

## API Signature

```
calculate(    expression)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `expression` | string | Yes | A valid mathematical expression representing the calculation to perform (e.g., 'number_of_extra_bags * 50'). | Must be a valid arithmetic expression; input values must be known, confirmed, and within policy limits (e.g., max 5 passengers per reservation, baggage limits by membership/cabin class); cannot include eligibility or policy logic. |

---

# When to Use

Use the calculate tool when an **explicit calculation** is required to determine amounts, such as fees, costs, or compensation, based on **confirmed user and reservation details**.

* Calculating extra baggage fees when the number of extra bags is known and within allowed limits.
* Determining the total travel insurance cost for a specified number of passengers.
* Computing compensation amounts for eligible users after eligibility has been verified.
* Calculating the price difference for cabin changes when both original and new prices are known.
* Summing up total fees for multiple passengers or services where the per-unit cost is fixed.

---

# When NOT to Use

Do **not** use this tool when:

* When booking, modifying, or cancelling flights—these are not calculation actions.
* To check user eligibility for compensation, cancellation, or policy compliance—these must be verified before any calculation.
* For subjective recommendations or non-numeric information requests.
* If required input values (e.g., number of bags, prices) are missing or unconfirmed.
* To perform calculations that would exceed policy limits, such as more than 5 passengers per reservation.

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. User and Reservation Details

* Number of passengers (must be known and within allowed limits)
* Membership level and/or cabin class (to determine applicable rates and limits)
* Number of extra bags (if calculating baggage fees)
* User's request for travel insurance (if calculating insurance cost)
### 2. Calculation-Specific Inputs

* Per-unit cost or rate (e.g., baggage fee per bag, insurance cost per passenger)
* Original and new prices (if calculating price differences for cabin changes)
* Eligibility confirmation for compensation (if compensation calculation is needed)

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before proceeding to validation and tool usage.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Input Value Limits

* The **number of passengers** must not exceed **5 per reservation**.
* The **number of extra bags** must not exceed the allowed limit for the user's **membership level or cabin class**.
## 2. Eligibility and Policy Compliance

* The user must be **eligible** for the calculation (e.g., compensation only if eligibility is confirmed).
* All values in the expression must be **confirmed and validated** with the user.
## 3. Expression Validity

* The **expression** must be a valid mathematical formula using only known, policy-compliant values.
* No policy logic or eligibility checks should be embedded in the expression.

---

# Edge Cases & Special Considerations

* If the number of extra bags is zero, no calculation for extra baggage fees is needed.
* If the user is not eligible for compensation, do not calculate compensation.
* If the price difference for a cabin change is zero, no payment or refund calculation is needed.
* If the user does not want travel insurance, do not calculate insurance cost.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** Calculating extra baggage fees for a Gold member traveling in Economy with 2 extra bags.

**Context:**
- User is a Gold member
- Traveling in Economy class
- Number of extra bags: 2
- Baggage fee per extra bag: $50
- All values confirmed and within policy limits

**Tool Call:**
```json
{
  "arguments": {
    "expression": "2 * 50"
  },
  "tool": "calculate"
}
```

**Why this is valid:** This is valid because all required inputs are known, the number of extra bags is within allowed limits, and the calculation is a straightforward arithmetic operation as required by policy.

---

### ❌ Invalid Usage Example 1

**Scenario:** Attempting to calculate compensation for a user before checking eligibility.

**Context:**
- User requests compensation for a delayed flight
- Agent has not yet verified if the user is eligible (e.g., membership level, insurance status not checked)

**Tool Call:**
```json
{
  "arguments": {
    "expression": "1 * 100"
  },
  "tool": "calculate"
}
```

**Why this violates policy:** This is invalid because the agent must confirm eligibility before performing any compensation calculation. Policy prohibits using the calculate tool for eligibility checks or before eligibility is established (see policy lines 113, 149, 159, 161).

---
