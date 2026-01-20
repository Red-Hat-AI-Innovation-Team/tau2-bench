# Policy: search_onestop_flight

## Conditions for Use
- User requests to search for available flights between specified origin and destination on a specific date as part of booking or modification
- User ID is obtained before searching as part of booking or modification
- Origin and destination are valid and identifiable locations (airport or city)
- Date is provided and valid for booking
- Cabin class is collected or clarified if relevant
- Number of passengers does not exceed five
- All passengers fly the same flights in the same cabin

## Refusal Conditions
- Request is not related to booking, modifying, or canceling flight reservations
- User ID is not provided (for booking/modification)
- Origin, destination, or date is missing or cannot be obtained
- Flights for the requested date are not available for booking (status not 'available')
- Number of passengers exceeds five
- Request includes different cabin classes within the same reservation

## Critical Reminders
- Obtain user ID, trip type, origin, destination, date, and cabin class (if relevant) from user before use
- Always obtain explicit user confirmation before proceeding with booking or modification after presenting search results
- Only call the tool once at a time and do not respond to user simultaneously
- Do not provide or infer information not explicitly provided by user or available tools
- Do not make subjective recommendations or comments about flight options
- Transfer to human agent if request is outside agent's scope
