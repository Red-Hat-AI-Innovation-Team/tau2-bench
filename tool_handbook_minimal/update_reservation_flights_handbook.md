# Policy: update_reservation_flights

## Conditions for Use
- User id must be provided; if reservation id is unknown, agent helps locate it
- Modify flights in a non-basic economy reservation with unchanged origin, destination, and trip type; some flight segments can be kept but their prices will not be updated
- Change cabin class for all flights in a reservation (not just one segment) if no flight has been flown; cabin class must remain the same across all flights
- Payment/refund for changes must use a single gift card or credit card already in user profile
- User has explicitly confirmed the action

## Refusal Conditions
- Reservation is basic economy
- User requests to change origin, destination, or trip type
- User wants to change number of passengers (not permitted, even by human agent)
- Any flight in reservation has already been flown (for cabin changes)
- User wants to change cabin for only one segment
- Payment method for changes is not in user profile or not a single gift card or credit card
- User wants to add travel insurance after booking
- User wants to remove checked bags after booking
- User has not explicitly confirmed the action
- Request is against policy

## Critical Reminders
- Agent must validate all policy rules before calling the API
- Obtain user id and reservation id before proceeding; help locate reservation id if needed
- List action details and get explicit user confirmation before use
- Cabin class must remain the same across all flights; cannot change for only one segment
- Agent cannot modify number of passengers, even a human agent cannot
- Cannot add insurance after booking
- Can only add, not remove, checked bags after booking
- Ensure origin, destination, and trip type remain unchanged when modifying flights
- Payment/refund must use a single gift card or credit card already in user profile
- API does not enforce policy; agent is responsible for all checks
- Only one tool call at a time; do not respond to user simultaneously
