"""Toolkit for the airline reservation system."""

from copy import deepcopy
from typing import List, Optional

from loguru import logger

from tau2.domains.airline.data_model import (
    AirportCode,
    AirportInfo,
    CabinClass,
    Certificate,
    DirectFlight,
    Flight,
    FlightDateStatus,
    FlightDateStatusAvailable,
    FlightDB,
    FlightInfo,
    FlightType,
    Insurance,
    Passenger,
    Payment,
    Reservation,
    ReservationFlight,
    User,
)
from tau2.environment.toolkit import ToolKitBase, ToolType, is_tool

# TODO: Add an abstract base class for the tools


class AirlineTools(ToolKitBase):  # Tools
    """All the tools for the airline domain."""

    db: FlightDB

    def __init__(self, db: FlightDB) -> None:
        super().__init__(db)

    def _get_user(self, user_id: str) -> User:
        """Get user from database."""
        if user_id not in self.db.users:
            raise ValueError(f"User {user_id} not found")
        return self.db.users[user_id]

    def _get_reservation(self, reservation_id: str) -> Reservation:
        """Get reservation from database."""
        if reservation_id not in self.db.reservations:
            raise ValueError(f"Reservation {reservation_id} not found")
        return self.db.reservations[reservation_id]

    def _get_flight(self, flight_number: str) -> Flight:
        """Get flight from database."""
        if flight_number not in self.db.flights:
            raise ValueError(f"Flight {flight_number} not found")
        return self.db.flights[flight_number]

    def _get_flight_instance(self, flight_number: str, date: str) -> FlightDateStatus:
        """Get flight instance from database."""
        flight = self._get_flight(flight_number)
        if date not in flight.dates:
            raise ValueError(f"Flight {flight_number} not found on date {date}")
        return flight.dates[date]

    def _get_flights_from_flight_infos(
        self, flight_infos: List[FlightInfo]
    ) -> list[FlightDateStatus]:
        """Get the flight from the reservation."""
        flights = []
        for flight_info in flight_infos:
            flights.append(
                self._get_flight_instance(flight_info.flight_number, flight_info.date)
            )
        return flights

    def _get_new_reservation_id(self) -> str:
        """Get a new reservation id.
        Assume each task makes at most 3 reservations

        Returns:
            A new reservation id.

        Raises:
            ValueError: If too many reservations are made.
        """
        for reservation_id in ["HATHAT", "HATHAU", "HATHAV"]:
            if reservation_id not in self.db.reservations:
                return reservation_id
        raise ValueError("Too many reservations")

    def _get_new_payment_id(self) -> str:
        """Get a new payment id.
        Assume each task makes at most 3 payments

        Returns:
            A new payment id.
        """
        return [3221322, 3221323, 3221324]

    def _get_datetime(self) -> str:
        """Get the current datetime."""
        return "2024-05-15T15:00:00"

    def _search_direct_flight(
        self,
        date: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        leave_after: Optional[str] = None,
    ) -> list[DirectFlight]:
        """Search for direct flights

        Args:
            date: The date of the flight in the format 'YYYY-MM-DD', such as '2024-01-01'.
            origin: The origin city airport in three letters, such as 'JFK'.
            destination: The destination city airport in three letters, such as 'LAX'.
            leave_after: The time to leave after the flight, such as '15:00:00'.
        """
        results = []
        for flight in self.db.flights.values():
            check = (
                (origin is None or flight.origin == origin)
                and (destination is None or flight.destination == destination)
                and (date in flight.dates)
                and (flight.dates[date].status == "available")
                and (
                    leave_after is None
                    or flight.scheduled_departure_time_est >= leave_after
                )
            )
            if check:
                direct_flight = DirectFlight(
                    flight_number=flight.flight_number,
                    origin=flight.origin,
                    destination=flight.destination,
                    status="available",
                    scheduled_departure_time_est=flight.scheduled_departure_time_est,
                    scheduled_arrival_time_est=flight.scheduled_arrival_time_est,
                    available_seats=flight.dates[date].available_seats,
                    prices=flight.dates[date].prices,
                )
                results.append(direct_flight)
        return results

    def _payment_for_update(
        self, user: User, payment_id: str, total_price: int
    ) -> Optional[Payment]:
        """
        Process payment for update reservation

        Args:
            user: The user to process payment for.
            payment_id: The payment id to process.
            total_price: The total price to process.
            reservation: The reservation to process payment for.

        Raises:
            ValueError: If the payment method is not found.
            ValueError: If the certificate is used to update reservation.
            ValueError: If the gift card balance is not enough.
        """
        # Check payment
        if payment_id not in user.payment_methods:
            raise ValueError("Payment method not found")
        payment_method = user.payment_methods[payment_id]
        if payment_method.source == "certificate":
            raise ValueError("Certificate cannot be used to update reservation")
        elif (
            payment_method.source == "gift_card" and payment_method.amount < total_price
        ):
            raise ValueError("Gift card balance is not enough")

        # Deduct payment
        if payment_method.source == "gift_card":
            payment_method.amount -= total_price

        payment = None
        # Create payment if total price is not 0
        if total_price != 0:
            payment = Payment(
                payment_id=payment_id,
                amount=total_price,
            )
        return payment

    @is_tool(ToolType.WRITE)
    def book_reservation(
        self,
        user_id: str,
        origin: str,
        destination: str,
        flight_type: FlightType,
        cabin: CabinClass,
        flights: List[FlightInfo | dict],
        passengers: List[Passenger | dict],
        payment_methods: List[Payment | dict],
        total_baggages: int,
        nonfree_baggages: int,
        insurance: Insurance,
    ) -> Reservation:
        """
        Book a reservation.

        Args:
            user_id: The ID of the user to book the reservation such as 'sara_doe_496'`.
            origin: The IATA code for the origin city such as 'SFO'.
            destination: The IATA code for the destination city such as 'JFK'.
            flight_type: The type of flight such as 'one_way' or 'round_trip'.
            cabin: The cabin class such as 'basic_economy', 'economy', or 'business'.
            flights: An array of objects containing details about each piece of flight.
            passengers: An array of objects containing details about each passenger.
            payment_methods: An array of objects containing details about each payment method.
            total_baggages: The total number of baggage items to book the reservation.
            nonfree_baggages: The number of non-free baggage items to book the reservation.
            insurance: Whether the reservation has insurance.

        Tool Guideline:
            ## Overview

            **Tool Name:** `book_reservation`
            **Purpose:** This tool is used to create a new flight reservation for a user, including passenger details, flight selection, baggage, payment, and optional insurance.

            ## API Signature

            ```
            book_reservation(user_id, origin, destination, flight_type, cabin, flights, passengers, payment_methods, total_baggages, nonfree_baggages, insurance)
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
        """
        if all(isinstance(flight, dict) for flight in flights):
            flights = [FlightInfo(**flight) for flight in flights]
        if all(isinstance(passenger, dict) for passenger in passengers):
            passengers = [Passenger(**passenger) for passenger in passengers]
        if all(isinstance(payment_method, dict) for payment_method in payment_methods):
            payment_methods = [
                Payment(**payment_method) for payment_method in payment_methods
            ]
        user = self._get_user(user_id)
        reservation_id = self._get_new_reservation_id()

        reservation = Reservation(
            reservation_id=reservation_id,
            user_id=user_id,
            origin=origin,
            destination=destination,
            flight_type=flight_type,
            cabin=cabin,
            flights=[],
            passengers=deepcopy(passengers),
            payment_history=deepcopy(payment_methods),
            created_at=self._get_datetime(),
            total_baggages=total_baggages,
            nonfree_baggages=nonfree_baggages,
            insurance=insurance,
        )

        # Update flights and calculate price
        total_price = 0
        all_flights_date_data: list[FlightDateStatusAvailable] = []

        for flight_info in flights:
            flight_number = flight_info.flight_number
            flight = self._get_flight(flight_number)
            flight_date_data = self._get_flight_instance(
                flight_number=flight_number, date=flight_info.date
            )
            # Checking flight availability
            if not isinstance(flight_date_data, FlightDateStatusAvailable):
                raise ValueError(
                    f"Flight {flight_number} not available on date {flight_info.date}"
                )
            # Checking seat availability
            if flight_date_data.available_seats[cabin] < len(passengers):
                raise ValueError(f"Not enough seats on flight {flight_number}")
            # Calculate price
            price = flight_date_data.prices[cabin]
            # Update reservation
            reservation.flights.append(
                ReservationFlight(
                    origin=flight.origin,
                    destination=flight.destination,
                    flight_number=flight_number,
                    date=flight_info.date,
                    price=price,
                )
            )
            all_flights_date_data.append(flight_date_data)
            total_price += price * len(passengers)

        # Add insurance fee
        if insurance == "yes":
            total_price += 30 * len(passengers)

        # Add baggage fee
        total_price += 50 * nonfree_baggages

        for payment_method in payment_methods:
            payment_id = payment_method.payment_id
            amount = payment_method.amount
            if payment_id not in user.payment_methods:
                raise ValueError(f"Payment method {payment_id} not found")

            user_payment_method = user.payment_methods[payment_id]
            if user_payment_method.source in {"gift_card", "certificate"}:
                if user_payment_method.amount < amount:
                    raise ValueError(
                        f"Not enough balance in payment method {payment_id}"
                    )

        total_payment = sum(payment.amount for payment in payment_methods)
        if total_payment != total_price:
            raise ValueError(
                f"Payment amount does not add up, total price is {total_price}, but paid {total_payment}"
            )

        # if checks pass, deduct payment
        for payment_method in payment_methods:
            payment_id = payment_method.payment_id
            amount = payment_method.amount
            user_payment_method = user.payment_methods[payment_id]
            if user_payment_method.source == "gift_card":
                user_payment_method.amount -= amount
            elif user_payment_method.source == "certificate":
                user.payment_methods.pop(payment_id)

        # Update DB
        for flight_date_data in all_flights_date_data:
            flight_date_data.available_seats[cabin] -= len(passengers)
        self.db.reservations[reservation_id] = reservation
        self.db.users[user_id].reservations.append(reservation_id)
        return reservation

    @is_tool(ToolType.GENERIC)
    def calculate(self, expression: str) -> str:
        """
        Calculate the result of a mathematical expression.

        Args:
            expression: The mathematical expression to calculate, such as '2 + 2'. The expression can contain numbers, operators (+, -, *, /), parentheses, and spaces.

        Returns:
            The result of the mathematical expression.

        Raises:
            ValueError: If the expression is invalid.

        Tool Guideline:
            ## Overview

            **Tool Name:** `calculate`
            **Purpose:** Performs explicit arithmetic calculations for determining amounts such as fees, costs, compensation, or price differences as required by policy.

            ## API Signature

            ```
            calculate(expression)
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
        """
        if not all(char in "0123456789+-*/(). " for char in expression):
            raise ValueError("Invalid characters in expression")
        return str(round(float(eval(expression, {"__builtins__": None}, {})), 2))

    @is_tool(ToolType.WRITE)
    def cancel_reservation(self, reservation_id: str) -> Reservation:
        """
        Cancel the whole reservation.

        Args:
            reservation_id: The reservation ID, such as 'ZFA04Y'.

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.

        Tool Guideline:
            ## Overview

            **Tool Name:** `cancel_reservation`
            **Purpose:** This tool allows an agent to cancel a user's flight reservation when specific policy and eligibility conditions are met.

            ## API Signature

            ```
            cancel_reservation(reservation_id)
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
        """
        reservation = self._get_reservation(reservation_id)
        logger.debug(reservation.model_dump_json(indent=4))
        # reverse the payment
        refunds = []
        for payment in reservation.payment_history:
            refunds.append(
                Payment(
                    payment_id=payment.payment_id,
                    amount=-payment.amount,
                )
            )
        reservation.payment_history.extend(refunds)
        reservation.status = "cancelled"
        logger.debug(self._get_reservation(reservation_id).model_dump_json(indent=4))
        # Release seats
        logger.warning("Seats release not implemented for cancellation!!!")
        return reservation

    @is_tool(ToolType.READ)
    def get_reservation_details(self, reservation_id: str) -> Reservation:
        """
        Get the details of a reservation.

        Args:
            reservation_id: The reservation ID, such as '8JX2WO'.

        Returns:
            The reservation details.

        Raises:
            ValueError: If the reservation is not found.

        Tool Guideline:
            ## Overview

            **Tool Name:** `get_reservation_details`
            **Purpose:** Retrieves detailed information about a specific reservation using a reservation ID, with strict association to the user's identity.

            ## API Signature

            ```
            get_reservation_details(reservation_id)
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
        """
        return self._get_reservation(reservation_id)

    @is_tool(ToolType.READ)
    def get_user_details(self, user_id: str) -> User:
        """
        Get the details of a user, including their reservations.

        Args:
            user_id: The user ID, such as 'sara_doe_496'.

        Returns:
            The user details.

        Raises:
            ValueError: If the user is not found.

        Tool Guideline:
            ## Overview

            **Tool Name:** `get_user_details`
            **Purpose:** Retrieves comprehensive user profile information using a valid user_id to support booking, modification, or cancellation of flight reservations and related eligibility checks.

            ## API Signature

            ```
            get_user_details(user_id)
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
        """
        return self._get_user(user_id)

    @is_tool(ToolType.READ)
    def list_all_airports(self) -> AirportInfo:  # DONE
        """Returns a list of all available airports.

        Returns:
            A dictionary mapping IATA codes to AirportInfo objects.

        Tool Guideline:
            ## Overview

            **Tool Name:** `list_all_airports`
            **Purpose:** Provides a comprehensive list of all available airports to support flight-related actions.

            ## API Signature

            ```
            list_all_airports(none)
            ```

            ## Arguments

            | Parameter | Type | Required | Description | Constraints |
            |-----------|------|----------|-------------|-------------|
            | `none` | N/A | No | This tool does not accept any parameters. | No parameters are allowed; any attempt to provide parameters is invalid. |

            ---

            # When to Use

            **Use this tool** when the user needs to view or select from a list of airports, especially in the context of booking, modifying, or canceling flights. **It is essential** for presenting airport options to assist with flight-related actions.

            * The user requests information about available airports.
            * The user needs to select or specify an origin or destination airport for a booking.
            * The agent must present a list of airports to facilitate booking, modifying, or canceling a flight.
            * The user asks for airport codes or names to complete a flight-related transaction.
            * The agent needs to verify available airports before proceeding with a flight-related process.

            ---

            # When NOT to Use

            Do **not** use this tool when:

            * The user request is unrelated to booking, modifying, or canceling flights, or does not require airport information.
            * The agent is being asked for information or recommendations not available via tools or user input.
            * The user is being transferred to a human agent due to an unsupported request.
            * The agent is already responding to the user or making another tool call (only one action at a time is allowed).
            * The agent needs to provide subjective advice or information not explicitly supported by the tool.

            ---

            # Prerequisites

            Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

            Before calling the tool, the agent must have collected:

            ### 1. Tool-Specific Requirements

            * No explicit prerequisites are required, as the tool takes no parameters and is used for informational purposes.

            Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered.

            ---

            # Conditional Checks

            Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

            The agent must verify:

            ## 1. Scope Validation

            * The user request must be **directly related to booking, modifying, canceling, or managing flights**.
            * The request must **require airport information** to proceed.
            ## 2. Tool Usage Exclusivity

            * The agent must **not make a tool call and respond to the user simultaneously**; only one action at a time is allowed.
            ## 3. Information Boundaries

            * The agent must **not provide information beyond what is available via tools or user input**.

            ---

            # Edge Cases & Special Considerations

            * If the user is being transferred to a human agent because their request cannot be handled, do not use this tool.
            * Do not use the tool for requests that do not pertain to flight booking, modification, or cancellation.
            * Do not attempt to pass parameters to the tool, as it does not accept any.

            ---

            # Usage Examples

            ### ✅ Valid Usage Example 1

            **Scenario:** A user is booking a new flight and asks for a list of available airports to choose their departure location.

            **Context:**
            - User is logged in and initiating a flight booking.
            - No airport has been selected yet.

            **Tool Call:**
            ```json
            {
              "arguments": {},
              "tool": "list_all_airports"
            }
            ```

            **Why this is valid:** This is valid because the user needs airport information to proceed with booking, which is within the tool's allowed scope (policy lines 67, 9, 11).

            ---

            ### ❌ Invalid Usage Example 1

            **Scenario:** A user asks for tourist recommendations in a city, and the agent attempts to call list_all_airports to provide airport options.

            **Context:**
            - User is not engaged in any flight-related process.
            - Request is about tourism, not flights.

            **Tool Call:**
            ```json
            {
              "arguments": {},
              "tool": "list_all_airports"
            }
            ```

            **Why this violates policy:** This is invalid because the request is outside the scope of booking, modifying, or canceling flights and does not require airport information (policy lines 13, 15).
        """
        return [
            AirportCode(iata="SFO", city="San Francisco"),
            AirportCode(iata="JFK", city="New York"),
            AirportCode(iata="LAX", city="Los Angeles"),
            AirportCode(iata="ORD", city="Chicago"),
            AirportCode(iata="DFW", city="Dallas"),
            AirportCode(iata="DEN", city="Denver"),
            AirportCode(iata="SEA", city="Seattle"),
            AirportCode(iata="ATL", city="Atlanta"),
            AirportCode(iata="MIA", city="Miami"),
            AirportCode(iata="BOS", city="Boston"),
            AirportCode(iata="PHX", city="Phoenix"),
            AirportCode(iata="IAH", city="Houston"),
            AirportCode(iata="LAS", city="Las Vegas"),
            AirportCode(iata="MCO", city="Orlando"),
            AirportCode(iata="EWR", city="Newark"),
            AirportCode(iata="CLT", city="Charlotte"),
            AirportCode(iata="MSP", city="Minneapolis"),
            AirportCode(iata="DTW", city="Detroit"),
            AirportCode(iata="PHL", city="Philadelphia"),
            AirportCode(iata="LGA", city="LaGuardia"),
        ]

    @is_tool(ToolType.READ)
    def search_direct_flight(
        self, origin: str, destination: str, date: str
    ) -> list[DirectFlight]:
        """
        Search for direct flights between two cities on a specific date.

        Args:
            origin: The origin city airport in three letters, such as 'JFK'.
            destination: The destination city airport in three letters, such as 'LAX'.
            date: The date of the flight in the format 'YYYY-MM-DD', such as '2024-01-01'.

        Returns:
            The direct flights between the two cities on the specific date.

        Tool Guideline:
            ## Overview

            **Tool Name:** `search_direct_flight`
            **Purpose:** This tool allows agents to search for available direct flights between a specified origin and destination on a given date.

            ## API Signature

            ```
            search_direct_flight(origin, destination, date)
            ```

            ## Arguments

            | Parameter | Type | Required | Description | Constraints |
            |-----------|------|----------|-------------|-------------|
            | `origin` | string | Yes | The departure airport or city code. | Must be a valid airport or city code as specified by the user; required parameter. |
            | `destination` | string | Yes | The arrival airport or city code. | Must be a valid airport or city code as specified by the user; required parameter. |
            | `date` | string | Yes | The date of the desired flight (YYYY-MM-DD). | Must be a valid date in the future (relative to current time 2024-05-15 15:00:00 EST); required parameter. |

            ---

            # When to Use

            Use the **search_direct_flight** tool when a user requests to find **available direct flights** between a specific origin and destination on a particular date, especially as part of the **booking** or **flight modification** process. The tool is limited to direct flights only by its design.

            * When the user wants to search for direct flights between two locations on a specific date.
            * When the user provides both **origin** and **destination** information and a **date** for travel.
            * When assisting the user in locating flights before proceeding with booking or modifying a reservation.
            * When verifying availability of direct flights as part of pre-booking checks.

            ---

            # When NOT to Use

            Do **not** use this tool when:

            * If the user does not provide both **origin** and **destination** information.
            * If the user requests information about indirect flights, baggage, payment, or unrelated topics. (The tool is limited to direct flights only; it cannot process indirect flight searches.)
            * If the user requests actions not supported by this tool, such as booking, modification, or cancellation.
            * If the agent is responding to the user in the same turn as making the tool call (tool calls and user responses must not be simultaneous).
            * If the requested date is in the past or the flight has already taken off.
            * If the agent is asked to provide subjective recommendations, opinions, or information not provided by the user or available tools (per general agent conduct rules).

            ---

            # Prerequisites

            Prerequisites are the information inputs that must be collected before any validation or tool call can occur. Agents must ensure all required details are gathered and that tool usage complies with general conduct rules.

            Before calling the tool, the agent must have collected:

            ### 1. Flight Search Details

            * User's intended **origin** (valid airport or city code).
            * User's intended **destination** (valid airport or city code).
            * User's intended **date of travel** (must be a valid future date).
            ### 2. Tool Call Sequencing and Conduct

            * Ensure only one tool call is made at a time.
            * Do not respond to the user simultaneously with making a tool call.
            * Do not provide subjective recommendations, opinions, or information not provided by the user or available tools.

            Prerequisites ensure all required information is collected and that general agent conduct rules are followed before proceeding to policy checks. They do not enforce policy validity themselves.

            ---

            # Conditional Checks

            Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

            The agent must verify:

            ## 1. Parameter Validity

            * The **origin** and **destination** must be valid airport or city codes provided by the user.
            * The **date** must be a valid date in the future (**after 2024-05-15 15:00:00 EST**).
            ## 2. Scope of Tool and Request

            * The request must be for a **direct flight** search only (this is a tool limitation, not a policy rule).
            * No simultaneous tool call and user response in the same turn.
            * Do not provide information or procedures not available from the user or the tool.
            ## 3. Flight Status

            * Do not search for flights that are already **flying** (departed) or for dates in the past.
            * If the flight status is **delayed** or **on time**, results may be returned but booking is not possible.
            * If the flight status is **available**, the tool can return available seats and prices.

            ---

            # Edge Cases & Special Considerations

            * If the user requests a search for a date in the past or for a flight that has already taken off, the tool must not be used.
            * If the user requests a flight with status 'delayed' or 'on time', results may be shown but booking cannot proceed.
            * If the user requests a flight with status 'available', the tool can return seats and prices.
            * If any required parameter (**origin**, **destination**, **date**) is missing, the tool must not be called.
            * If the user asks for indirect flights, the tool is not applicable due to tool limitations (not a policy rule); the agent should not attempt to search for indirect flights.
            * If the user requests information not available from the tool or not provided by the user, the agent must not provide it.

            ---

            # Usage Examples

            ### ✅ Valid Usage Example 1

            **Scenario:** A user wants to find direct flights from JFK (New York) to LAX (Los Angeles) on 2024-06-01.

            **Context:**
            - User has provided both origin and destination airport codes.
            - User has specified a future date.
            - No simultaneous tool call and user response.
            - Agent does not provide any subjective recommendations or information not available from the tool.

            **Tool Call:**
            ```json
            {
              "arguments": {
                "date": "2024-06-01",
                "destination": "LAX",
                "origin": "JFK"
              },
              "tool": "search_direct_flight"
            }
            ```

            **Why this is valid:** This is valid because all required parameters are provided, the date is in the future, the request is within the tool's scope (searching for direct flights), and the agent follows all conduct rules. (Policy lines: 3, 5, 9, 36, 37, 40, 41, 67)

            ---

            ### ❌ Invalid Usage Example 1

            **Scenario:** A user asks to search for direct flights from ORD (Chicago) to SFO (San Francisco) on 2024-05-10.

            **Context:**
            - User has provided both origin and destination airport codes.
            - User has specified a date in the past (before current time 2024-05-15 15:00:00 EST).

            **Tool Call:**
            ```json
            {
              "arguments": {
                "date": "2024-05-10",
                "destination": "SFO",
                "origin": "ORD"
              },
              "tool": "search_direct_flight"
            }
            ```

            **Why this violates policy:** This is invalid because the requested date is in the past, violating the policy that the date must be in the future. The tool must not be used for past dates. (Policy lines: 3, 41, 43)
        """
        return self._search_direct_flight(
            date=date, origin=origin, destination=destination
        )

    @is_tool(ToolType.READ)
    def search_onestop_flight(
        self, origin: str, destination: str, date: str
    ) -> list[tuple[DirectFlight, DirectFlight]]:
        """
        Search for one-stop flights between two cities on a specific date.

        Args:
            origin: The origin city airport in three letters, such as 'JFK'.
            destination: The destination city airport in three letters, such as 'LAX'.
            date: The date of the flight in the format 'YYYY-MM-DD', such as '2024-05-01'.

        Returns:
            A list of pairs of DirectFlight objects.

        Tool Guideline:
            ## Overview

            **Tool Name:** `search_onestop_flight`
            **Purpose:** This tool searches for available flights between a specified origin and destination on a given date to support booking, modifying, or reviewing flight options.

            ## API Signature

            ```
            search_onestop_flight(origin, destination, date)
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
        """
        results = []
        for result1 in self._search_direct_flight(
            date=date, origin=origin, destination=None
        ):
            result1.date = date
            date2 = (
                f"2024-05-{int(date[-2:]) + 1}"
                if "+1" in result1.scheduled_arrival_time_est
                else date
            )
            # TODO: flight1.scheduled_arrival_time_est could have a +1?
            for result2 in self._search_direct_flight(
                date=date2,
                origin=result1.destination,
                destination=destination,
                leave_after=result1.scheduled_arrival_time_est,
            ):
                result2.date = date2
                results.append([result1, result2])
        return results

    @is_tool(ToolType.WRITE)
    def send_certificate(self, user_id: str, amount: int) -> str:
        """
        Send a certificate to a user. Be careful!

        Args:
            user_id: The ID of the user to book the reservation, such as 'sara_doe_496'.
            amount: The amount of the certificate to send.

        Returns:
            A message indicating the certificate was sent.

        Raises:
            ValueError: If the user is not found.

        Tool Guideline:
            ## Overview

            **Tool Name:** `send_certificate`
            **Purpose:** The send_certificate tool is used to issue a certificate as compensation to eligible users who explicitly request compensation for cancelled or delayed flights.

            ## API Signature

            ```
            send_certificate(user_id, amount)
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
        """
        user = self._get_user(user_id)

        # add a certificate, assume at most 3 cases per task
        for payment_id in [f"certificate_{id}" for id in self._get_new_payment_id()]:
            if payment_id not in user.payment_methods:
                new_payment = Certificate(
                    id=payment_id,
                    amount=amount,
                    source="certificate",
                )
                user.payment_methods[payment_id] = new_payment
                return f"Certificate {payment_id} added to user {user_id} with amount {amount}."
        raise ValueError("Too many certificates")

    # @is_tool(ToolType.THINK)
    # def think(self, thought: str) -> str:
    #     """
    #     Use the tool to think about something.
    #     It will not obtain new information or change the database, but just append the thought to the log.
    #     Use it when complex reasoning or some cache memory is needed.

    #     Args:
    #         thought: A thought to think about.

    #     Returns:
    #         Empty string
    #     """
    #     return ""

    @is_tool(ToolType.GENERIC)
    def transfer_to_human_agents(self, summary: str) -> str:
        """
        Transfer the user to a human agent, with a summary of the user's issue.
        Only transfer if
         -  the user explicitly asks for a human agent
         -  given the policy and the available tools, you cannot solve the user's issue.

        Args:
            summary: A summary of the user's issue.

        Returns:
            A message indicating the user has been transferred to a human agent.

        Tool Guideline:
            ## Overview

            **Tool Name:** `transfer_to_human_agents`
            **Purpose:** Transfers the user to a human agent when their request cannot be handled within the agent's scope of actions.

            ## API Signature

            ```
            transfer_to_human_agents(summary)
            ```

            ## Arguments

            | Parameter | Type | Required | Description | Constraints |
            |-----------|------|----------|-------------|-------------|
            | `summary` | string | Yes | A concise explanation of why the transfer to a human agent is necessary. | This is a handbook-imposed constraint for clarity and auditability; it is not explicitly required by policy but ensures every transfer is justified with a specific reason. |

            ---

            # When to Use

            Use the **transfer_to_human_agents** tool when a user's request is **outside the scope** of automated actions or **requires human intervention**. This ensures that complex or restricted scenarios are escalated appropriately and in compliance with policy.

            * The user's request cannot be fulfilled by the agent due to policy or technical limitations.
            * A user requests cancellation of a reservation where any portion of the flight has already been flown.
            * The situation requires human judgment or access to resources unavailable to the agent.
            * The user explicitly requests to speak with a human and their request cannot be resolved by the agent.

            ---

            # When NOT to Use

            Do **not** use this tool when:

            * The user's request can be fully handled within the agent's capabilities.
            * The request is against policy and must be denied (e.g., requests that are not permitted for any agent, human or automated).
            * The user requests to modify the number of passengers in a reservation, as neither the agent nor a human agent can perform this action.
            * Transferring solely for user preference when the agent can resolve the request within policy.

            ---

            # Prerequisites

            Prerequisites are the **required information and steps** that must be gathered and completed before making a tool call or validating eligibility for transfer.

            Before calling the tool, the agent must have collected:

            ### 1. Request Assessment

            * Full details of the user's request, including all relevant context.
            * Verification that the request cannot be handled by the agent.
            ### 2. Transfer Justification

            * A clear, policy-aligned summary explaining why transfer is necessary (handbook-imposed constraint).

            Prerequisites ensure all necessary information is collected before proceeding, but do not themselves enforce policy validity. The requirement for a 'summary' parameter is imposed by this handbook for auditability, not by explicit policy.

            ---

            # Conditional Checks

            Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

            The agent must verify:

            ## 1. Scope Validation

            * The request is **outside the agent's scope** and cannot be fulfilled by automated actions.
            * The agent has **verified** that no available tool or workflow can resolve the request.
            ## 2. Policy Compliance

            * The request is **not explicitly denied by policy** (e.g., requests to modify passenger count must be denied, not transferred).
            * The transfer is **not being used to circumvent policy restrictions**.
            ## 3. Parameter Requirements

            * A **summary** parameter is provided, clearly stating the reason for transfer (handbook-imposed constraint for clarity and auditability).
            ## 4. Transfer Workflow Enforcement

            * The agent must **not make a tool call and respond to the user simultaneously**; only one action at a time (per policy line 11).
            * After making the transfer_to_human_agents tool call, the agent must send the message '**YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.**' to the user (per policy line 15).

            ---

            # Edge Cases & Special Considerations

            * If the user requests to modify the number of passengers in a reservation, deny the request—do not transfer.
            * If any portion of a flight in a reservation has already been flown and the user requests cancellation, transfer to a human agent is required.
            * Do not make a tool call and respond to the user simultaneously; only one action at a time.
            * After making the transfer_to_human_agents tool call, always send the message 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user.
            * If the agent can resolve the request, do not transfer even if the user requests a human.

            ---

            # Usage Examples

            ### ✅ Valid Usage Example 1

            **Scenario:** A user requests to cancel a reservation, but one leg of the flight has already been flown.

            **Context:**
            - User has a round-trip reservation.
            - The outbound flight has been completed; the return flight is pending.
            - User requests cancellation of the reservation.

            **Tool Call:**
            ```json
            {
              "arguments": {
                "summary": "User requests cancellation of a reservation where one flight segment has already been flown; this cannot be handled by the agent."
              },
              "tool": "transfer_to_human_agents"
            }
            ```

            **Why this is valid:** This is valid because policy requires transfer to a human agent when cancellation is requested for a reservation with any flown segment (policy line 141). After the tool call, the agent must send the message 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user.

            ---

            ### ❌ Invalid Usage Example 1

            **Scenario:** A user requests to change the number of passengers in their reservation.

            **Context:**
            - User has a confirmed reservation for 2 passengers.
            - User wants to add a third passenger to the reservation.

            **Tool Call:**
            ```json
            {
              "arguments": {
                "summary": "User requests to modify the number of passengers in a reservation, which cannot be handled by the agent."
              },
              "tool": "transfer_to_human_agents"
            }
            ```

            **Why this violates policy:** This is invalid because neither the agent nor a human agent can modify the number of passengers in a reservation; the request should be denied, not transferred (policy line 128).
        """
        return "Transfer successful"

    @is_tool(ToolType.WRITE)
    def update_reservation_baggages(
        self,
        reservation_id: str,
        total_baggages: int,
        nonfree_baggages: int,
        payment_id: str,
    ) -> Reservation:
        """
        Update the baggage information of a reservation.

        Args:
            reservation_id: The reservation ID, such as 'ZFA04Y'
            total_baggages: The updated total number of baggage items included in the reservation.
            nonfree_baggages: The updated number of non-free baggage items included in the reservation.
            payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
            ValueError: If the user is not found.
            ValueError: If the payment method is not found.
            ValueError: If the certificate cannot be used to update reservation.
            ValueError: If the gift card balance is not enough.

        Tool Guideline:
            ## Overview

            **Tool Name:** `update_reservation_baggages`
            **Purpose:** Allows updating the number of checked bags on an existing reservation, including adding paid (nonfree) baggage items.

            ## API Signature

            ```
            update_reservation_baggages(reservation_id, total_baggages, nonfree_baggages, payment_id)
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
            * The **nonfree_baggages** must be calculated as the number of bags exceeding the user's free allowance based on the table below:

            **Free Checked Bag Allowance Table:**
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

            **Scenario:** A Regular member with an economy cabin reservation wants to add one extra checked bag to their reservation after being shown the cost and confirming the action.

            **Context:**
            - User is a Regular member with economy cabin reservation (ID: RES123) that currently has 1 checked bag.
            - Regular members in economy have a free allowance of 1 checked bag.
            - User requests to add 1 more checked bag (total will be 2).
            - Calculation: 2 total bags - 1 free bag = 1 nonfree bag at $50.
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

            **Why this is valid:** This is valid because the user is only adding bags (not removing), the number of bags does not exceed policy limits, the nonfree bag is correctly calculated (2 total - 1 free = 1 nonfree), the payment method is on file, and explicit confirmation was obtained.

            ---

            ### ✅ Valid Usage Example 2

            **Scenario:** A Gold member with an economy cabin reservation wants to add one checked bag, which is within their free allowance.

            **Context:**
            - User is a Gold member with economy cabin reservation (ID: RES789) that currently has 2 checked bags.
            - Gold members in economy have a free allowance of 3 checked bags.
            - User requests to add 1 more checked bag (total will be 3).
            - Calculation: 3 total bags - 3 free bags = 0 nonfree bags. No charge.
            - Agent lists the action details: 1 extra bag, no charge (within free allowance).
            - User provides explicit confirmation.

            **Tool Call:**
            ```json
            {
              "arguments": {
                "nonfree_baggages": 0,
                "payment_id": "",
                "reservation_id": "RES789",
                "total_baggages": 3
              },
              "tool": "update_reservation_baggages"
            }
            ```

            **Why this is valid:** This is valid because the user is adding a bag within their free allowance (Gold member in economy gets 3 free bags), so nonfree_baggages is correctly set to 0, no payment is required, and explicit confirmation was obtained.

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
        """
        reservation = self._get_reservation(reservation_id)
        user = self._get_user(reservation.user_id)

        # Calculate price
        total_price = 50 * max(0, nonfree_baggages - reservation.nonfree_baggages)

        # Create payment
        payment = self._payment_for_update(user, payment_id, total_price)
        if payment is not None:
            reservation.payment_history.append(payment)

        # Update reservation
        reservation.total_baggages = total_baggages
        reservation.nonfree_baggages = nonfree_baggages

        return reservation

    @is_tool(ToolType.WRITE)
    def update_reservation_flights(
        self,
        reservation_id: str,
        cabin: CabinClass,
        flights: List[FlightInfo | dict],
        payment_id: str,
    ) -> Reservation:
        """
        Update the flight information of a reservation.


        Args:
            reservation_id: The reservation ID, such as 'ZFA04Y'.
            cabin: The cabin class of the reservation
            flights: An array of objects containing details about each piece of flight in the ENTIRE new reservation. Even if the a flight segment is not changed, it should still be included in the array.
            payment_id: The payment id stored in user profile, such as 'credit_card_7815826', 'gift_card_7815826', 'certificate_7815826'.

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
            ValueError: If the user is not found.
            ValueError: If the payment method is not found.
            ValueError: If the certificate cannot be used to update reservation.
            ValueError: If the gift card balance is not enough.

        Tool Guideline:
            ## Overview

            **Tool Name:** `update_reservation_flights`
            **Purpose:** Allows modification of flights or cabin class in an existing reservation, subject to policy and eligibility constraints.

            ## API Signature

            ```
            update_reservation_flights(reservation_id, cabin, flights, payment_id)
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
        """
        if all(isinstance(flight, dict) for flight in flights):
            flights = [FlightInfo(**flight) for flight in flights]
        reservation = self._get_reservation(reservation_id)
        user = self._get_user(reservation.user_id)

        # update flights and calculate price
        total_price = 0
        reservation_flights = []
        for flight_info in flights:
            # if existing flight, keep it
            matching_reservation_flight = next(
                (
                    reservation_flight
                    for reservation_flight in reservation.flights
                    if reservation_flight.flight_number == flight_info.flight_number
                    and reservation_flight.date == flight_info.date
                    and cabin == reservation.cabin
                ),
                None,
            )
            if matching_reservation_flight:
                total_price += matching_reservation_flight.price * len(
                    reservation.passengers
                )
                reservation_flights.append(matching_reservation_flight)
                continue

            # If new flight:
            flight = self._get_flight(flight_info.flight_number)
            # Check flight availability
            flight_date_data = self._get_flight_instance(
                flight_number=flight_info.flight_number,
                date=flight_info.date,
            )
            if not isinstance(flight_date_data, FlightDateStatusAvailable):
                raise ValueError(
                    f"Flight {flight_info.flight_number} not available on date {flight_info.date}"
                )

            # Check seat availability
            if flight_date_data.available_seats[cabin] < len(reservation.passengers):
                raise ValueError(
                    f"Not enough seats on flight {flight_info.flight_number}"
                )

            # Calculate price and add to reservation
            reservation_flight = ReservationFlight(
                flight_number=flight_info.flight_number,
                date=flight_info.date,
                price=flight_date_data.prices[cabin],
                origin=flight.origin,
                destination=flight.destination,
            )
            total_price += reservation_flight.price * len(reservation.passengers)
            reservation_flights.append(reservation_flight)

        # Deduct amount already paid for reservation
        total_price -= sum(flight.price for flight in reservation.flights) * len(
            reservation.passengers
        )

        # Create payment
        payment = self._payment_for_update(user, payment_id, total_price)
        if payment is not None:
            reservation.payment_history.append(payment)

        # Update reservation
        reservation.flights = reservation_flights
        reservation.cabin = cabin  # This was missing from original TauBench

        # Do not make flight database update here, assume it takes time to be updated # TODO: So this means that we don't update the seats here. What about in cancel_reservation?
        return reservation

    @is_tool(ToolType.WRITE)
    def update_reservation_passengers(
        self, reservation_id: str, passengers: List[Passenger | dict]
    ) -> Reservation:
        """
        Update the passenger information of a reservation.

        Args:
            reservation_id: The reservation ID, such as 'ZFA04Y'.
            passengers: An array of objects containing details about each passenger.

        Returns:
            The updated reservation.

        Raises:
            ValueError: If the reservation is not found.
            ValueError: If the number of passengers does not match.

        Tool Guideline:
            ## Overview

            **Tool Name:** `update_reservation_passengers`
            **Purpose:** Allows modification of passenger details (such as name or date of birth) for an existing reservation, without changing the number of passengers.

            ## API Signature

            ```
            update_reservation_passengers(reservation_id, passengers)
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
        """
        if all(isinstance(passenger, dict) for passenger in passengers):
            passengers = [Passenger(**passenger) for passenger in passengers]
        reservation = self._get_reservation(reservation_id)
        logger.info(len(passengers))
        logger.info(len(reservation.passengers))
        if len(passengers) != len(reservation.passengers):
            raise ValueError("Number of passengers does not match")
        reservation.passengers = deepcopy(passengers)
        return reservation

    @is_tool(ToolType.READ)
    def get_flight_status(self, flight_number: str, date: str) -> str:
        """
        Get the status of a flight.

        Args:
            flight_number: The flight number.
            date: The date of the flight.

        Returns:
            The status of the flight.

        Raises:
            ValueError: If the flight is not found.

        Tool Guideline:
            ## Overview

            **Tool Name:** `get_flight_status`
            **Purpose:** Retrieves the current status of a specific flight based on its flight number and scheduled departure date.

            ## API Signature

            ```
            get_flight_status(flight_number, date)
            ```

            ## Arguments

            | Parameter | Type | Required | Description | Constraints |
            |-----------|------|----------|-------------|-------------|
            | `flight_number` | string | Yes | The unique identifier for the flight whose status is being queried. | Must be a valid flight number corresponding to the flight of interest; cannot be empty or malformed. |
            | `date` | string | Yes | The scheduled departure date of the flight (in local time). | Must be the scheduled departure date (local time) for the flight being queried; must be provided and formatted correctly. |

            ---

            # When to Use

            Use this tool when you need to **determine the current status** of a specific flight, especially in scenarios involving **booking, modification, cancellation, or compensation** decisions.

            * To check if a flight is available, delayed, on time, flying, or cancelled as part of booking, modifying, or cancelling a reservation.
            * To verify if a flight has already taken off or landed, which affects eligibility for booking, modification, or cancellation.
            * To confirm flight status when a user complains about a cancelled or delayed flight and requests compensation.
            * To validate facts about a flight before proceeding with actions dependent on its status.

            ---

            # When NOT to Use

            Do **not** use this tool when:

            * If the user request is unrelated to booking, modifying, cancelling, or compensation (e.g., general flight information or unrelated inquiries).
            * If either the flight_number or date is missing, unavailable, or cannot be reliably determined.
            * If the required parameters are incomplete or do not correspond to a real flight.
            * If another tool is more appropriate for the user's request (e.g., searching for available flights rather than checking status).

            ---

            # Prerequisites

            Prerequisites are the **information inputs** that must be collected before any validation or tool call can occur.

            Before calling the tool, the agent must have collected:

            ### 1. Flight Identification

            * A valid flight_number for the flight of interest.
            * The scheduled departure date (local time) for the flight.
            ### 2. Operational Independence

            * Ensure the tool call is made independently, without simultaneously responding to the user.

            Prerequisites do *not* enforce policy validity—they simply ensure required information has been gathered before proceeding with validation or tool execution.

            ---

            # Conditional Checks

            Conditional checks are **policy-driven validations** that must all pass before the tool is executed.

            The agent must verify:

            ## 1. Parameter Validity

            * The **flight_number** must be a valid, recognized identifier for the flight.
            * The **date** must be the correct scheduled departure date (local time) for the flight.
            ## 2. Use Case Alignment

            * The request must relate to **booking, modification, cancellation, or compensation** actions.
            * The tool must not be used for unrelated or out-of-scope requests.

            ---

            # Edge Cases & Special Considerations

            * A flight may have different statuses on different dates; always use the correct date to get the relevant status.
            * If a flight is 'flying', it has taken off but not landed, which may affect eligibility for booking, modification, or cancellation.
            * If the flight status is 'delayed' or 'on time', the flight has not taken off but cannot be booked.
            * If the flight status is 'available', the flight has not taken off and can be booked.

            ---

            # Usage Examples

            ### ✅ Valid Usage Example 1

            **Scenario:** A user requests compensation for a delayed flight and provides the flight number and date.

            **Context:**
            - User is a frequent flyer member.
            - User claims their flight (AB123) on 2024-07-01 was delayed and requests compensation.

            **Tool Call:**
            ```json
            {
              "arguments": {
                "date": "2024-07-01",
                "flight_number": "AB123"
              },
              "tool": "get_flight_status"
            }
            ```

            **Why this is valid:** This is valid because the agent has both required parameters (flight_number and date), the request concerns compensation for a delayed flight, and the tool is used to confirm the flight status before proceeding, as required by policy (policy lines 41, 42, 159, 163, 165).

            ---

            ### ❌ Invalid Usage Example 1

            **Scenario:** A user asks for the status of a flight but only provides the airline name and destination, not the flight number or date.

            **Context:**
            - User is not logged in.
            - User says: 'What's the status of the flight to Paris with AirBlue?'

            **Tool Call:**
            ```json
            {
              "arguments": {
                "date": "",
                "flight_number": ""
              },
              "tool": "get_flight_status"
            }
            ```

            **Why this violates policy:** This is invalid because the required parameters (flight_number and date) are missing, violating the prerequisite and parameter constraints (policy lines 11, 35, 38, 40). The tool cannot be used without these inputs.
        """
        return self._get_flight_instance(flight_number, date).status


if __name__ == "__main__":
    from tau2.domains.airline.utils import AIRLINE_DB_PATH

    airline = AirlineTools(FlightDB.load(AIRLINE_DB_PATH))
    print(airline.get_statistics())
