# Tool Handbook: `book_reservation`

## Overview

**Tool Name:** `book_reservation`
**Purpose:** This tool is used to create a new flight reservation for a user, including passenger details, flight selection, baggage, payment, and optional insurance.

## API Signature

```
book_reservation(    user_id,    origin,    destination,    flight_type,    cabin,    flights,    passengers,    payment_methods,    total_baggages,    nonfree_baggages,    insurance)
```

## Arguments

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `user_id` | string | Yes | Unique identifier for the user making the reservation. | Must be provided by the user and correspond to an existing user profile. |
| `origin` | string | Yes | Airport or city of departure. | Must be specified by the user. |
| `destination` | string | Yes | Airport or city of arrival. | Must be specified by the user. |
| `flight_type` | string | Yes | Type of trip: one way or round trip. | Must be specified as either 'one way' or 'round trip'. |
| `cabin` | string | Yes | Cabin class for all flights in the reservation. | Cabin class must be the same across all flights; valid values are 'basic economy', 'economy', or 'business'. |
| `flights` | string | Yes | Flight(s) to be booked. | All passengers must fly the same flights in the same cabin. |
| `passengers` | string | Yes | Passenger details for the reservation. | Maximum of five passengers; must include first name, last name, and date of birth for each. |
| `payment_methods` | string | Yes | Payment methods to be used for the reservation. | At most one travel certificate, one credit card, and three gift cards; all must be in the user profile. |
| `total_baggages` | integer | Yes | Total number of checked bags for the reservation. | Do not add checked bags the user does not need; per-passenger limits depend on membership level and cabin class. |
| `nonfree_baggages` | integer | Yes | Number of checked bags that are not free. | Each extra baggage beyond free allowance is $50; must be calculated based on membership level and cabin class. |
| `insurance` | string | Yes | Whether travel insurance is included. | Must ask the user if they want travel insurance; if selected, it is $30 per passenger and enables full refund for health or weather cancellations. |

---

# When to Use

Use the book_reservation tool when a user requests to **book a new flight reservation** and all required information has been gathered and confirmed. This tool is appropriate for **initiating new bookings** with specified details.

* A user explicitly asks to book a flight or create a new reservation.
* All required booking details (user ID, trip type, origin, destination, passengers, payment, etc.) have been collected.
* The user has reviewed and confirmed the booking details.
* The booking request does not violate any policy constraints (e.g., passenger or payment limits).

---

# When NOT to Use

Do **not** use this tool when:

* The user request exceeds passenger or payment method limits, or violates other policy constraints.
* The user has not provided explicit confirmation after reviewing booking details.
* The user is requesting information, advice, or procedures not directly related to booking a reservation.
* The request is to modify or cancel an existing reservation, or is unrelated to booking.
* Required details (such as user ID, passenger info, or payment method) are missing or incomplete.
* The payment methods specified are not present in the user profile.
* The request cannot be handled within the scope of booking and should be transferred to a human agent.

---

# Prerequisites

Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur. Before calling the tool, the agent must have collected:

Before calling the tool, the agent must have collected:

### 1. User Identity

* User ID (must correspond to an existing user profile)
### 2. Trip Details

* Trip type (one way or round trip)
* Origin and destination locations
### 3. Passenger Information

* First name, last name, and date of birth for each passenger (up to five passengers)
### 4. Baggage and Insurance

* Number of checked bags needed (per passenger)
* Whether the user wants to purchase travel insurance
### 5. Payment Methods

* Payment methods to be used (must be present in the user profile)
### 6. User Confirmation

* Explicit user confirmation (yes) after listing all booking details

Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered.

---

# Conditional Checks

Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

The agent must verify:

## 1. User and Passenger Eligibility

* The **user_id** must correspond to an existing user profile.
* There must be **no more than five passengers** in the reservation.
* Each passenger must have **first name, last name, and date of birth** provided.
## 2. Flight and Cabin Constraints

* The **origin** and **destination** must be specified.
* The **flight_type** must be either **'one way'** or **'round trip'**.
* The **cabin** class must be the same across all flights and be one of: **'basic economy'**, **'economy'**, or **'business'**.
* All passengers must fly the **same flights in the same cabin**.
## 3. Payment Method Limits

* At most **one travel certificate**, **one credit card**, and **three gift cards** may be used.
* All payment methods must be present in the **user profile**.
* The remaining amount of a travel certificate is **not refundable**.
## 4. Baggage Allowance

* Do **not** add checked bags the user does not need.
* Total checked bags per passenger are limited by **membership level** and **cabin class** based on the table below:

**Free Checked Bag Allowance (per passenger):**
- **Regular member:**
  - 0 free checked bags for basic economy
  - 1 free checked bag for economy
  - 2 free checked bags for business
- **Silver member:**
  - 1 free checked bag for basic economy
  - 2 free checked bags for economy
  - 3 free checked bags for business
- **Gold member:**
  - 2 free checked bags for basic economy
  - 3 free checked bags for economy
  - 4 free checked bags for business

* Each extra baggage (beyond free allowance) is **$50**.
* **Calculation:** `nonfree_baggages = max(0, total_baggages - (free_allowance_per_passenger × number_of_passengers))`
## 5. Insurance Offer

* The user must be **asked** if they want travel insurance.
* If selected, insurance is **$30 per passenger** and enables full refund for health or weather cancellations.
## 6. Explicit User Confirmation

* The agent must obtain **explicit user confirmation** (yes) after listing all action details before executing the tool call.

---

# Edge Cases & Special Considerations

* The remaining amount of a travel certificate is not refundable (cannot get back unused portion).
* Only one tool call should be made at a time; do not respond to the user and call the tool simultaneously.
* Baggage allowances are calculated per passenger, so multiply the per-passenger free allowance by the number of passengers.
* All passengers must fly the same flights in the same cabin, so baggage calculations apply uniformly.

---

# Usage Examples

### ✅ Valid Usage Example 1

**Scenario:** A regular member wants to book a round trip from New York to Los Angeles for themselves and one companion, both in economy class, with one checked bag each, paying with a credit card on file, and opts for travel insurance.

**Context:**
- User ID: user123 (regular member, profile exists)
- Trip type: round trip
- Origin: JFK
- Destination: LAX
- Cabin: economy
- Passengers: John Doe (01-01-1980), Jane Doe (02-02-1985)
- Checked bags: 2 (1 per passenger, within free allowance for regular member in economy)
- Payment: credit card on file
- Insurance: yes (user confirmed)
- User has reviewed and confirmed all details

**Tool Call:**
```json
{
  "arguments": {
    "cabin": "economy",
    "destination": "LAX",
    "flight_type": "round trip",
    "flights": "JFK-LAX-JFK",
    "insurance": "yes",
    "nonfree_baggages": 0,
    "origin": "JFK",
    "passengers": "[{\"first_name\":\"John\",\"last_name\":\"Doe\",\"dob\":\"1980-01-01\"},{\"first_name\":\"Jane\",\"last_name\":\"Doe\",\"dob\":\"1985-02-02\"}]",
    "payment_methods": "[{\"type\":\"credit_card\",\"id\":\"cc001\"}]",
    "total_baggages": 2,
    "user_id": "user123"
  },
  "tool": "book_reservation"
}
```

**Why this is valid:** This booking is valid because all required information is provided, policy constraints are met (passenger and baggage limits, payment method, insurance offer), and the user has explicitly confirmed the booking details.

---

### ❌ Invalid Usage Example 1

**Scenario:** A user tries to book a flight for themselves and five friends (six passengers total) in business class, using two travel certificates and four gift cards, without confirming the booking details.

**Context:**
- User ID: user456 (silver member, profile exists)
- Trip type: one way
- Origin: ORD
- Destination: MIA
- Cabin: business
- Passengers: six total (exceeds limit)
- Payment: two travel certificates and four gift cards (exceeds limits)
- Insurance: not offered/confirmed
- User has not confirmed the booking details

**Tool Call:**
```json
{
  "arguments": {
    "cabin": "business",
    "destination": "MIA",
    "flight_type": "one way",
    "flights": "ORD-MIA",
    "insurance": "no",
    "nonfree_baggages": 3,
    "origin": "ORD",
    "passengers": "[{\"first_name\":\"Alice\",\"last_name\":\"Smith\",\"dob\":\"1990-03-03\"},{\"first_name\":\"Bob\",\"last_name\":\"Jones\",\"dob\":\"1991-04-04\"},{\"first_name\":\"Carol\",\"last_name\":\"Lee\",\"dob\":\"1992-05-05\"},{\"first_name\":\"Dan\",\"last_name\":\"Kim\",\"dob\":\"1993-06-06\"},{\"first_name\":\"Eve\",\"last_name\":\"Nguyen\",\"dob\":\"1994-07-07\"},{\"first_name\":\"Frank\",\"last_name\":\"Wong\",\"dob\":\"1995-08-08\"}]",
    "payment_methods": "[{\"type\":\"travel_certificate\",\"id\":\"tc001\"},{\"type\":\"travel_certificate\",\"id\":\"tc002\"},{\"type\":\"gift_card\",\"id\":\"gc001\"},{\"type\":\"gift_card\",\"id\":\"gc002\"},{\"type\":\"gift_card\",\"id\":\"gc003\"},{\"type\":\"gift_card\",\"id\":\"gc004\"}]",
    "total_baggages": 6,
    "user_id": "user456"
  },
  "tool": "book_reservation"
}
```

**Why this violates policy:** This booking is invalid because it violates several policy constraints: more than five passengers, more than one travel certificate and three gift cards used, and no explicit user confirmation after listing booking details. (Policy lines: 73, 78, 80, 7)

---
