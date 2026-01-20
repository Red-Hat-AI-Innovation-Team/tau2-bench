# Policy: list_all_airports

## Conditions for Use
- User explicitly requests a list of all airports
- Agent must provide the complete airport list to fulfill a specific booking, modification, cancellation, refund, or compensation action

## Refusal Conditions
- User request is outside booking, modifying, canceling, refund, or compensation scope
- User requests subjective recommendations, comments, or information not available via tools or user input
- The full airport list is not required for the current action
- Request is for information, knowledge, or procedures not provided by the user or available tools

## Critical Reminders
- Tool takes no parameters
- Do not provide information not available via tools or user input
- Do not make a tool call and respond to the user at the same time
- Transfer to a human agent if the request cannot be handled within agent scope
