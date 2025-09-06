How to run the report generator service:

- Setup
    - Cd ./implementation
    - Create env environment: python3 -m venv env
    - Activate the virtual env: source env/bin/activate
    - Install requirements: pip install -r requirements.txt
- Project Structure:
```
        implementation/
        ├─ service/
        │  ├─ report_generator.py       # Main CLI service
        │─ utils/
        │  └─ vpp_utils.py           # Core VPP logic and helper methods
        ├─ tests/
        │  └─ unit_test_utils.py        # Pytest unit tests
        ├─ events_file.csv               # Sample events file
        └─ requirements.txt
```
- Run handler: 
    - python -m service.report_generator
    - use the sample from **STDIN.txt**
    - generated report would be like and will be saved to **vpp_report.json** file:
        ```
            {
                "vpp": "Test VPP One",
                "month": "2025-09",
                "totals": {
                    "total_revenue": 1.75,
                    "vpp_ad_valorem_fee": 0.35,
                    "vpp_cost_only": 0.0,
                    "vpp_total_revenue": 1.75,
                    "site_total_revenue_after_fees": 0.0
                },
                "sites": {
                    "9876543210": {
                    "nmi": "9876543210",
                    "address": "426 King St Newcastle West NSW 2302",
                    "site_capacity_kwh": 13.5,
                    "site_revenue_before_fees": 1.4,
                    "site_daily_fee": 1.4,
                    "site_revenue_after_fees": 0.0
                    }
                }
                }

        ```

- run tests
    - pytests -v -s
