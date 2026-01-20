# Policy: book_reservation

## Conditions for Use
- User requests to book a new flight reservation
- User provides user id corresponding to an existing profile
- User provides trip type (one way or round trip), origin, and destination
- User provides first name, last name, and date of birth for each passenger (max five)
- All flights are available and in the same cabin class
- All passengers fly the same flights in the same cabin
- Payment methods (max one travel certificate, one credit card, three gift cards) are in user profile
- Action details are listed and explicit user confirmation is obtained before booking

## Refusal Conditions
- User id not provided or does not match an existing profile
- Trip type, origin, or destination not specified
- Missing passenger details (first name, last name, date of birth)
- Number of passengers exceeds five
- Any flight segment is not available or cabin classes differ
- Passengers do not fly the same flights in the same cabin
- Payment methods exceed allowed limits or are not in user profile
- No explicit user confirmation after listing action details
- User requests checked bags not needed
- User requests information or recommendations not provided by user or tools

## Critical Reminders
- Collect user id, trip type, origin, destination, and passenger details before booking
- Collect first name, last name, and date of birth for each passenger
- List all action details and obtain explicit user confirmation before proceeding
- Do not provide subjective recommendations or comments
- Only one tool call at a time; do not respond and call simultaneously
- Checked bag allowance depends on membership level and cabin class; extra bags are $50 each
- Do not add checked bags unless user requests them
- Travel insurance is $30 per passenger and covers full refund for health/weather cancellations
- Reservation can be one way or round trip
- Check seat availability and prices for selected cabin before booking
