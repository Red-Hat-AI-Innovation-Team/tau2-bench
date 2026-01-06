# Policy: search_direct_flight

Each flight has the following attributes:
- flight number
- origin
- destination
- scheduled departure and arrival time (local time)

A flight can be available at multiple dates. For each date:
- If the status is available, the flight has not taken off, available seats and prices are listed.
- If the status is delayed or on time, the flight has not taken off, cannot be booked.
- If the status is flying, the flight has taken off but not landed, cannot be booked.

There are three cabin classes: basic economy, economy, business. basic economy is its own class, completely distinct from economy.

Seat availability and prices are listed for each cabin class.
