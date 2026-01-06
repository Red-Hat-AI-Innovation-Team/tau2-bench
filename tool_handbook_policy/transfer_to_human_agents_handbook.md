# Policy: transfer_to_human_agents

You should transfer the user to a human agent if and only if the request cannot be handled within the scope of your actions.

To transfer, first make a tool call to transfer_to_human_agents, and then send the message 'YOU ARE BEING TRANSFERRED TO A HUMAN AGENT. PLEASE HOLD ON.' to the user.

If any portion of the flight has already been flown, the agent cannot help and transfer is needed.
