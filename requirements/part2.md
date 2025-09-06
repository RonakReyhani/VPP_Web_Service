## Skills Test: VPP Web Service
### Exercise

### Part 2
Imagine the above program is to be made available as a backend web service.
Design a REST API for the service that would support the following capabilities:
Create and update a VPP
Create and update a Site
Assign a Site to a VPP
Add a battery to a Site
1 Create VPP: Test VPP One, 20, 0.30
2 Create Site: Test VPP One, 9876543210, 426 King St Newcastle West NSW 2302
3 Create Battery: 9876543210, Tesla, 38764527113388, 13.5
4 Import Events: events_file.csv
5 Create Report: Test VPP One, 2024-02
6 Exit
Update a battery
Remove a battery from a Site
Import a CSV file of charge/discharge events
Produce a revenue-sharing report for a specified VPP and month
Describe your API design using any method you think will make it easy for us as developers tounderstand how we would use it.
Do they realise the daily fee * 28 is actually a fixed monthly fee?
When a Site doesn’t have enough revenue to pay daily fees, the VPP doesn’t accrues feesfrom that Site
REST API
Do the REST endpoints make intuitive sense?
Has any business logic or data validation made its way into the REST API code?
Did they waste time building a UI when asked for a backend service?
Bonus points:
Streaming the Events file in rather than pulling it all into memory
Comments towards REST endpoint “productisation”, e.g. auth, rate limiting
Comments towards observability