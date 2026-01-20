# Policy: get_user_details

## Conditions for Use
- Agent needs to obtain or verify user profile info (user id, email, address, date of birth, payment methods, membership level, reservation numbers)
- Agent must use this tool to verify user id before any booking, modification, cancellation, or refund
- Agent needs to check if a payment method exists in the user profile before booking, modifying, or refunding a reservation
- Agent needs to determine membership level for baggage allowance at booking or for compensation eligibility
- Agent must use this tool to help locate reservation numbers if user does not know their reservation id for modify or cancel actions

## Refusal Conditions
- User id cannot be verified or obtained
- Requested information is not present in the user profile (e.g., flight details, baggage details, or any info outside profile fields)
- Agent attempts to retrieve or infer information not in user profile or available tools

## Critical Reminders
- User id must be a valid string corresponding to an existing user
- Never proceed with booking, modification, cancellation, or refund without confirming user id and required profile info
- All payment methods for booking, modification, or refund must already exist in user profile
- Membership level affects baggage and compensation eligibility
- Do not use or infer information not present in user profile or available tools
- Always confirm request is within allowed policy scope before calling
