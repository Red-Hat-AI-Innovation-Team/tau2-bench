# Policy: transfer_to_human_agents

## Conditions for Use
- Request cannot be handled within the agent's scope of actions: book, modify, cancel, refunds, compensation
- User requests to cancel a reservation where any flight segment has already been flown

## Refusal Conditions
- Request can be handled within the agent's scope of actions (book, modify, cancel, refunds, compensation) and all policy conditions are met
- Request is a policy violation (e.g., modifying number of passengers in a reservation); must be denied, not transferred

## Critical Reminders
- Transfer is only for requests outside the agent's scope of actions, never for policy violations
- Always deny requests that violate policy; do not transfer
- When transferring, first make the tool call, then send: 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user
- Do not provide a summary to the user; only send the required transfer message
