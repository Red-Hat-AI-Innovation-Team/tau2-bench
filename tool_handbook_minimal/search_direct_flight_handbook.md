# Policy: search_direct_flight

## Conditions for Use
- User requests to search for available direct flights between specified origin and destination on a specific date
- Agent needs to locate direct flights for booking or modifying a reservation with all required details provided
- Searching for flights is allowed as a precursor to booking or modifying a reservation
- Agent must obtain user id before proceeding with booking or modification flows
- Agent must obtain explicit user confirmation before taking any booking or modification action that updates the booking database

## Refusal Conditions
- Required parameters (origin, destination, date) are missing or incomplete
- User is being transferred to a human agent
- Request is outside policy scope
- Do not provide information, knowledge, or procedures not provided by the user or available tools
- Do not give subjective recommendations or comments

## Critical Reminders
- Origin and destination must be specified by the user
- Date must be valid and not in the past
- Only direct flights are supported; connecting flights are excluded
- Do not show flights with status 'delayed', 'on time', or 'flying' as available for booking
- Agent must not respond to the user and make a tool call at the same time (strict separation)
- Agent must list action details and obtain explicit user confirmation before proceeding with booking or modification
- Seat availability and prices are returned by the tool but are not input parameters
