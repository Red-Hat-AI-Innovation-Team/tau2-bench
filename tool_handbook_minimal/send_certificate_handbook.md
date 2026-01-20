# Policy: send_certificate

## Conditions for Use
- User explicitly requests compensation for a cancelled flight in a reservation AND facts are confirmed
- User explicitly requests compensation for a delayed flight in a reservation AND facts are confirmed
- User is a silver or gold member OR has travel insurance OR flies business class
- User_id is available

## Refusal Conditions
- User does not explicitly request compensation for a cancelled or delayed flight
- User is a regular member with no travel insurance and flies (basic) economy
- Compensation is requested for any reason other than cancelled or delayed flights
- Proactive compensation offer (user did not explicitly request it)

## Critical Reminders
- Always confirm complaint facts before offering compensation
- Never proactively offer compensation; only respond to explicit user requests
- Never offer compensation for reasons other than cancelled or delayed flights
- Set amount: $100 x passengers for cancelled, $50 x passengers for delayed
- Only make one tool call at a time; do not respond and call simultaneously
