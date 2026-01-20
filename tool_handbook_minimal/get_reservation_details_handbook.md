# Policy: get_reservation_details

## Conditions for Use
- User provides a reservation ID to retrieve or verify reservation details
- User requests an action requiring reservation verification (e.g., modify, cancel, view details)
- User does not know reservation ID but agent obtains user id and any other required information to locate the reservation

## Refusal Conditions
- User id is not provided and sufficient information to locate reservation is missing
- Request is unrelated to booking, modifying, or cancelling reservations (e.g., general flight info, new bookings)
- Request is outside allowed agent actions or against policy
- Tool call and user response would occur in the same turn

## Critical Reminders
- reservation_id must be a valid string linked to the user
- Agent must obtain user id before attempting to locate reservation without reservation id
- Tool is read-only and does not update data
- Always obtain explicit user confirmation before taking any action that updates the booking database after retrieving reservation details
- Only one tool call per turn; do not combine with user responses
- If unable to locate reservation after reasonable attempts, transfer to a human agent using the required protocol: tool call to transfer_to_human_agents, then send the required message to the user
