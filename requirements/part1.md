## Skills Test: VPP Web Service
### Exercise
Homeowners with batteries and commercial battery owners join Virtual Power Plants (VPPs),which automatically charge and discharge batteries in response to network demand in order to maximise revenues. The profits are shared between the VPP and its members.
You should spend 2-3 hours working on the problem in total.
You may not finish all of the functionality, so prioritise the parts that you think would be most important for us to review, and let us know about any things that you would have liked to have done but didn’t get around to.
We’d love to see a Git repository showing commits you made as you developed your solution.
Respond by email with your source code and Git repo in a ZIP file within 24 hours.

### Part 1
Your task is to build a simple program using Python that can calculate the distribution of revenues for (fictional) VPPs based off (fictional) charge & discharge data.
The program will support multiple VPPs, each VPP can have multiple Sites, and each site can have multiple batteries.
A VPP has a name, and a price schedule that has a percentage of revenue share taken by theVPP, and an optional fixed daily fee in AUD.
A Site has an address and a NMI: a 10- or 11-digit code identifying the site meter point.
A battery has a manufacturer, serial number, and capacity.
The profit-sharing for the VPP works like this:
The VPP is assigned its margin of the revenue first.
- Of the remainder of the revenue:
    - 80% is assigned to the Site that had an event
    - 20% is distributed across all Sites, proportionally according to their batteries' capacity
- Daily fees are taken from a Site’s revenue and given to the VPP, assuming 28 days every month
- Daily fees cannot make a Site’s total revenue for the month go negative
- Discharge events that incurred a cost are 100% assigned to the VPP
Your program should accept the following instructions from STDIN (all values after the colons
are variables):
- Create VPP: NAME, REVENUE_PERCENTAGE, DAILY_FEE
- Create Site: VPP_NAME, NMI, ADDRESS
- Create Battery: SITE_NMI, MANUFACTURER, SERIAL, CAPACITY
- Import Events: FILE_NAME
- Create Report: VPP, MONTH
- Exit

Here is an example set of instructions:
```
1 Create VPP: Test VPP One, 20, 0.30
2 Create Site: Test VPP One, 9876543210, 426 King St Newcastle West NSW 2302
3 Create Battery: 9876543210, Tesla, 38764527113388, 13.5
4 Import Events: events_file.csv
5 Create Report: Test VPP One, 2024-02
6 Exit
```

The ‘Import Events’ instruction will import the named CSV file of charge/discharge events with
the following columns:
- NMI: Site NMI
- DATE: ISO 8601 format date
- EVENT_TYPE: either “Charge” or “Discharge”
- ENERGY: the amount of energy charged or discharged in kWh (decimal)
- TARIFF: the cost of charging the battery or the feed-in tariff for discharging in cents/kWh
(decimal)

The ‘Create Report’ instruction will produce a revenue-sharing report for a specified VPP and
month, using JSON, with daily fees and ad valorem fees as separate items.