# Tool Handbook: `update_reservation_flights`

## Overview

**Tool Name:** `update_reservation_flights`
**Purpose:** Allows modification of flights or cabin class in an existing reservation, subject to policy and eligibility constraints.

## API Signature

```
update_reservation_flights(    reservation_id,    cabin,    flights,    payment_id)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `reservation_id` | string | Yes | The unique identifier for the reservation to be updated. | Must be a valid reservation id belonging to the user; if unknown, must be located before proceeding. |
| `cabin` | string | Yes | The desired cabin class for all flights in the reservation. | Cabin class must be the same across all flights; cannot change cabin for only one segment; cannot change cabin if any flight has already been flown; if new price is higher, user must pay the difference; if lower, user should be refunded. |
| `flights` | string | Yes | The updated flight segments for the reservation. | Cannot change flights for basic economy reservations; origin, destination, and trip type must remain the same; some segments can be kept but their prices will not be updated. |
| `payment_id` | string | Conditional | The payment method to be used for any additional charges or refunds. | Required only if flights are being changed (not required for cabin-only changes); must be a single gift card or credit card already in the user profile. |

---

# When to Use

Use this tool when a user requests to **change flights or cabin class** in an existing reservation and all **policy constraints** are satisfied. **Explicit user confirmation** is required before proceeding.

* User wants to change flights (reservation must not be basic economy) or cabin class (no flights have been flown), and all policy constraints are met.
* User provides explicit confirmation to proceed with the requested changes.
* User requests to update all flight segments to the same cabin class.
* User requests to change flights while keeping the same origin, destination, and trip type.

---

# When NOT to Use

Do **not** use this tool when:

* Reservation is for basic economy and the user wants to change flights (flight changes not allowed for basic economy).
* User wants to change the origin, destination, or trip type (these cannot be modified).
* Any flight in the reservation has already been flown and the user wants to change cabin class.
* User wants to change cabin class for only one flight segment (must be the same for all flights).
* User wants to change the number of passengers in the reservation.
* User wants to change baggage or insurance (handled by separate tools).
* User has not provided explicit confirmation to proceed with the update.

---

# Prerequisites

Prerequisites are the information inputs that must be collected before any validation or tool call can occur.

Before calling the tool, the agent must have collected:

### 1. User and Reservation Identification

* User id (to confirm identity and ownership of reservation)
* Reservation id (must be obtained or located if unknown)
### 2. Action Confirmation

* Explicit user confirmation (yes) to proceed with the specified changes
* Detailed listing of requested changes (flights, cabin class, payment method)
### 3. Payment Method

* A single gift card or credit card already in the user's profile (required only if flights are being changed; not required for cabin-only changes)

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before policy checks and tool invocation.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. Reservation and Flight Eligibility

* Reservation is **not basic economy** if changing flights.
* Origin, destination, and trip type remain **unchanged**.
* No attempt to change the **number of passengers**.
## 2. Cabin Class Constraints

* Cabin class is **the same across all flights**.
* Cabin class is **not changed for only one segment**.
* Cabin class is **not changed if any flight has already been flown**.
* If changing cabin and the new price is higher, user must **pay the difference**; if lower, user should **be refunded**.
## 3. Flight Segment Rules

* Some flight segments may be kept, but their prices will **not be updated** to current prices.
* All policy rules for modifying flights or cabin class are **manually enforced** by the agent.
## 4. Payment Method Validation

* If flights are changed, **payment_id must be provided** and must be a **single gift card or credit card** already in the user profile.
* If only cabin is changed (no flight changes), payment_id is not required.
## 5. User Confirmation

* Agent has obtained **explicit user confirmation** to proceed with the update.

---

# Edge Cases & Special Considerations

* If any flight in the reservation has already been flown, cabin cannot be changed, but flights may still be modifiable if not basic economy.
* If the user wants to keep some flight segments, their prices will not be updated to current prices.
* The API does not enforce policy rules; the agent must manually ensure all constraints are satisfied before calling the tool.
* If the user wants to change both flights and cabin, all constraints for both must be satisfied.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A user with a standard (not basic economy) round-trip reservation wants to change both outbound and return flights and upgrade both segments from economy to business class.

**Context:**
- User has provided their reservation id and confirmed their identity.
- All flights in the reservation are upcoming (none have been flown).
- User explicitly confirms the action and has a credit card on file.
- Origin, destination, and trip type remain unchanged.

**Tool Call:**
```json
{
  "arguments": {
    "cabin": "business",
    "flights": "[{\"flight_number\": \"UA100\", \"date\": \"2024-08-01\"}, {\"flight_number\": \"UA101\", \"date\": \"2024-08-10\"}]",
    "payment_id": "CREDITCARD789",
    "reservation_id": "ABC12345"
  },
  "tool": "update_reservation_flights"
}
```

**Why this is valid:** This is valid because the reservation is not basic economy, all flight segments are being updated to the same cabin class, none have been flown, the user provided explicit confirmation, and a valid payment method is on file (policy lines: 5, 7, 105, 116, 118, 131).

---

### ❌ Invalid Usage Example 1

**Scenario:** A user with a basic economy reservation wants to change their outbound flight to a different date.

**Context:**
- User provides reservation id and confirms identity.
- User explicitly confirms the change.
- Reservation is basic economy.

**Tool Call:**
```json
{
  "arguments": {
    "cabin": "economy",
    "flights": "[{\"flight_number\": \"UA200\", \"date\": \"2024-09-05\"}]",
    "payment_id": "CREDITCARD123",
    "reservation_id": "BECO5678"
  },
  "tool": "update_reservation_flights"
}
```

**Why this violates policy:** This is invalid because flight changes are not allowed for basic economy reservations (policy line: 110). The agent must deny the request.

---
