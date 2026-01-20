# Policy: cancel_reservation

## Conditions for Use
- User requests cancellation
- User provides user id
- User provides reservation id (or agent assists in locating it)
- User provides reason for cancellation
- At least one of: booking made within last 24 hours, flight cancelled by airline, business flight, or user has travel insurance and reason is covered by insurance

## Refusal Conditions
- User does not provide user id
- User does not provide reservation id and cannot be assisted in locating it
- Cancellation eligibility rules are not met

## Critical Reminders
- Obtain and record user id, reservation id, and reason for cancellation before proceeding
- List action details and obtain explicit user confirmation (yes) before calling tool
- If any portion of the flight has already been flown, transfer user to human agent
- If request cannot be handled within agent's allowed actions, transfer to human agent
- If user has travel insurance, ensure reason is covered by insurance
- Refund will go to original payment method within 5 to 7 business days
- Agent must verify all policy conditions; API does not enforce them
- Only one tool call at a time; do not respond to user while making tool call
