# Policy: get_flight_status

## Conditions for Use
- User requests current status of a specific flight (by flight number and date)
- Need to verify if a flight can be booked, modified, or cancelled
- Need to confirm if a flight is delayed or cancelled for compensation or complaint
- User requests flight status for information retrieval (including helping locate reservation id)

## Refusal Conditions
- Flight number or date is missing or cannot be reliably determined
- User request is outside booking, modification, cancellation, refund, compensation, or information retrieval
- Do not provide information not available from user or tools
- Do not use tool and respond to user simultaneously; only one tool call or user response at a time

## Critical Reminders
- You must ensure flight number and date are provided and appear valid before calling
- Obtain missing flight number or date from user if not provided
- Do not provide subjective recommendations or comments about flight status
- Only make one tool call at a time and do not respond to user simultaneously
- API does not enforce policy rules—agent is responsible
- Always confirm flight status before offering compensation
- Current time is 2024-05-15T15:00:00 for time-based checks
