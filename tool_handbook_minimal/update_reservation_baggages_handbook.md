# Policy: update_reservation_baggages

## Conditions for Use
- User requests to add checked bags to an existing reservation after initial booking
- User provides both user id and reservation id
- Reservation is modifiable (not basic economy if modifications are not allowed)
- No flight segment in the reservation has already been flown

## Refusal Conditions
- User requests to remove checked bags
- User requests to add checked bags to a reservation or flight segment that has already been flown
- User requests to add checked bags to a basic economy reservation if modifications are not allowed
- User does not provide user id or reservation id
- User requests to add more checked bags than needed

## Critical Reminders
- Always verify user id and reservation id belong to the user
- List action details and obtain explicit user confirmation before proceeding
- Do not add checked bags the user does not need
- Checked bag allowance depends on membership level and cabin class; calculate free vs. paid bags
- Each extra checked bag beyond free allowance costs $50
- Payment method for baggage fees must already be in user's profile
- API does not enforce policy; agent must validate all constraints
- Only one tool call at a time; do not respond to user simultaneously with tool call
- Transfer to human agent if request is outside allowed actions
