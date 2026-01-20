# Policy: update_reservation_passengers

## Conditions for Use
- User requests to update passenger information (e.g., name, date of birth) for an existing reservation
- Both user id and reservation id are provided before proceeding
- If user does not know reservation id, agent assists in locating it using available tools
- Action details are listed to the user and explicit confirmation is obtained before proceeding

## Refusal Conditions
- User requests to add or remove passengers (change in passenger count), even if requested by a human agent
- Required user id or reservation id is missing and cannot be obtained
- Action violates any policy rule
- Any flight in the reservation has already been flown

## Critical Reminders
- Number of passengers in the update must exactly match the original reservation; no addition or removal allowed
- Each passenger entry must include first name, last name, and date of birth
- Obtain explicit user confirmation before updating the booking database; do not update without confirmation
- Only one tool call at a time; do not respond to user while calling the tool
- Do not provide information or procedures not supplied by user or available tools
- All passenger modifications must comply with the original reservation's constraints
