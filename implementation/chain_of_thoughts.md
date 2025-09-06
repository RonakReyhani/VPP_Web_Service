### Simple Program that receives the STDIN and calculates the distribution of revenues

- I go with a simple python handler without storing the data (CRUD action for VPP, Sites and batteries), to just process the STDIN
- From Part 1; I understand this behaviour/requirements:
    - Assumption: VPP can sell to the grid (discharge) when i.e. price is high and buy from grid(charge)
    - VPP takes a percentage cut and daily fee from each site
    - VPP first takes the monthly revenue. months have 28 days for consistency.
    - reminder is split: 80% to the site of origin of event (charge or discharge) and 20% to all sites according to their battery capacity
    - Discharge event with negative value is assigned to VPP
    - VPP takes a daily_fee * 28 days from site's monthly revenue if it doesn't make site revenue negative, if it's negative it only takes what site has and ignores the debts. in this case site's revenue will be 0.


#### Input  event of each site is within the csv:

```
- NMI: Site NMI
- DATE: ISO 8601 format date
- EVENT_TYPE: either “Charge” or “Discharge”
- ENERGY: the amount of energy charged or discharged in kWh (decimal)
- TARIFF: the cost of charging the battery or the feed-in tariff for discharging in cents/kWh
(decimal)

```

#### the program will receive the STDIN as bellow:
It has the date for the report: 2024-02, I have to calculate the revenue from the csv event report for the given month for each site and VPP.

```
1 Create VPP: Test VPP One, 20, 0.30
2 Create Site: Test VPP One, 9876543210, 426 King St Newcastle West NSW 2302
3 Create Battery: 9876543210, Tesla, 38764527113388, 13.5
4 Import Events: events_file.csv
5 Create Report: Test VPP One, 2024-02
6 Exit

```

#### example for event (charge/discharge) calculation:

```
** Discharge 6 kWh at daily_price 30 c/kWh =  6 * 30 / 100 = $1.80 revenue.
** Charge 10 kWh at daily_price 12 c/kWh= - (10 * 12 / 100) = -$1.20 cost.
** Discharge 5 kWh at daily_price -5 c/kWh= 5 * -5 / 100 = -$0.25 → this entire -$0.25 is assigned to VPP only.

```

#### example for capped revenue:

```
Scenario 1:
Given VPP has daily_fee of 0.3/day
And Monthly fee per site is 0.3*28
And Site earned $10
Then Site revenue is $10-(0.3*28)


Scenario 2: when Site monthly fee is more than what it earns, VPP only takes what Site earned, no negative revenue (site doesn't owe money).

Given VPP has daily_fee of 0.3/day
And Monthly fee per site is 0.3*28
And Site earned $2
Then Site revenue is $0

```





