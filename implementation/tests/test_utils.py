from datetime import date
import pytest
from models.data_class import Event, EventType, Battery
from utils.vpp_utils import VPPUtils
import uuid

@pytest.fixture
def utils():
    return VPPUtils()

def setup_for_create_report(utils, vpp_name, nmi, cap, addr="Test Addr"):
    utils.create_update_vpp(vpp_name, revenue_percentage=10.0, daily_fee_aud=0.5)
    utils.create_update_site(vpp_name, nmi, addr)
    utils.sites[nmi].batteries.append(Battery(capacity_kwh=cap, manufacturer="man 001", serial=uuid.uuid4()))
    return utils.sites[nmi]

def test_create_update_vpp(utils, capsys):

    utils.create_update_vpp("VPP1", 20.0, 0.5)
    captured = capsys.readouterr()
    assert "Created VPP 'VPP1'" in captured.out
    assert "VPP1" in utils.vpps
    assert utils.vpps["VPP1"].revenue_percentage == 20.0
    assert utils.vpps["VPP1"].daily_fee_aud == 0.5


    utils.create_update_vpp("VPP1", 25.0, 0.8)
    captured = capsys.readouterr()
    assert "Updated VPP 'VPP1'" in captured.out
    assert utils.vpps["VPP1"].revenue_percentage == 25.0
    assert utils.vpps["VPP1"].daily_fee_aud == 0.8

def test_create_update_site_raises_error_for_missing_vpp(utils):

    with pytest.raises(ValueError) as excinfo:
        utils.create_update_site("NonExistentVPP","1234567890","Test Address")
    
    assert "VPP 'NonExistentVPP' not found" in str(excinfo.value)

def test_create_update_site(utils, capsys):
    utils.create_update_vpp("VPP1", 20.0, 0.5)


    utils.create_update_site("VPP1", "1234567890", "Test Address")
    captured = capsys.readouterr()
    assert "Created Site NMI=1234567890" in captured.out
    site = utils.sites["1234567890"]
    assert site.address == "Test Address"
    assert site.vpp_name == "VPP1"


    utils.create_update_site("VPP1", "1234567890", "New Address")
    captured = capsys.readouterr()
    assert "Updated Site NMI=1234567890" in captured.out
    assert utils.sites["1234567890"].address == "New Address"

def test_create_update_battery_raises_error_for_missing_site(utils):

    with pytest.raises(ValueError) as excinfo:
        utils.create_update_battery("9999999999", "TestManu", "BAT123", 5.0)
    
    assert "Site with NMI 9999999999 not found" in str(excinfo.value)

def test_create_update_battery(utils, capsys):
    utils.create_update_vpp("VPP1", 20.0, 0.5)
    utils.create_update_site("VPP1", "1234567890", "Test Address")


    utils.create_update_battery("1234567890", "Tesla", "BAT123", 10.0)
    captured = capsys.readouterr()
    site = utils.sites["1234567890"]
    assert "Created Battery serial=BAT123 at site 1234567890" in captured.out
    assert len(site.batteries) == 1
    assert site.batteries[0].serial == "BAT123"


    utils.create_update_battery("1234567890", "TeslaX", "BAT123", 12.0)
    captured = capsys.readouterr()
    bat = site.batteries[0]
    assert "Updated Battery serial=BAT123 at site 1234567890" in captured.out
    assert bat.manufacturer == "TeslaX"
    assert bat.capacity_kwh == 12.0

def test_exit(utils, capsys):

    utils.exit()
    captured = capsys.readouterr()
    assert "No report was generated. Exiting." in captured.out


    utils.last_report = {"vpp": "VPP1", "month": "2025-09"}
    utils.exit()
    captured = capsys.readouterr()
    assert "Report for VPP 'VPP1' for month '2025-09' generated successfully. Exiting." in captured.out

def test_import_events(utils, capsys):

    utils.create_update_vpp("VPP1", revenue_percentage=10.0, daily_fee_aud=0.5)
    utils.create_update_site("VPP1", "1234567890", "Test Address")


    csv_content = """NMI,DATE,EVENT_TYPE,ENERGY,TARIFF
1234567890,2025-09-01,Charge,5.0,20
1234567890,2025-09-02,Discharge,3.0,25
9999999999,2025-09-03,Charge,2.0,15
1234567890,2025-09-04,InvalidType,1.0,10
"""
    csv_file = "events.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(csv_content)

    utils.import_events(str(csv_file))

    captured = capsys.readouterr()
    print(captured.out)
    assert "Imported=2, Skipped=2" in captured.out

    site = utils.sites["1234567890"]
    assert len(site.events) == 2
    assert site.events[0].event_type.value == "Charge"
    assert site.events[0].energy_kwh == 5.0
    assert site.events[1].event_type.value == "Discharge"
    assert site.events[1].tariff_cents_per_kwh == 25

def test_create_report_no_sites_in_vpp(utils, capsys):
    utils.create_update_vpp("EMPTY", 5, 1.0)
    utils.create_report("EMPTY", "2025-09")
    captured = capsys.readouterr().out
    assert "has not sites" in captured

def test_create_report_event_outside_month_is_skipped(utils):
    site = setup_for_create_report(utils, "VPP1", "333", 10)
    site.events.append(Event("333", date(2025, 8, 1), EventType.DISCHARGE, 10, 20))
    utils.create_report("VPP1", "2025-09")
    report = utils.last_report
    assert report["totals"]["total_revenue"] == 0

def test_create_report_daily_fees_cannot_exceed_revenue(utils):
    site = setup_for_create_report(utils, "VPP1", "444", 10)
    site.events.append(Event("444", date(2025, 9, 1), EventType.CHARGE, 0.01, 1))
    utils.create_report("VPP1", "2025-09")
    report = utils.last_report
    assert report["sites"]["444"]["site_revenue_after_fees"] == 0

def test_create_report_zero_capacity_distribution(utils):
    s1 = setup_for_create_report(utils, "VPP1", "S1", 0)
    setup_for_create_report(utils, "VPP1", "S2", 0)
    s1.events.append(Event("S1", date(2025, 9, 1), EventType.CHARGE, 5, 10))
    utils.create_report("VPP1", "2025-09")
    report = utils.last_report

    assert report["totals"]["total_revenue"] > 0
    assert report["totals"]["total_revenue"] == 0.5
    assert all(sid in report["sites"] for sid in ["S1", "S2"])

def test_create_report_multiple_sites_with_capacity_split_0_revenue(utils):
    s1 = setup_for_create_report(utils, "VPP1", "A", 5)
    s2 = setup_for_create_report(utils, "VPP1", "B", 15)

    s1.events.append(Event("A", date(2025, 9, 1), EventType.DISCHARGE, 10, 20)) 
    s2.events.append(Event("B", date(2025, 9, 1), EventType.CHARGE, 5, 20))

    utils.create_report("VPP1", "2025-09")
    report = utils.last_report

    assert report["sites"]["A"]["site_revenue_after_fees"] == 0
    assert report["sites"]["B"]["site_revenue_after_fees"] == 0
    assert report["totals"]["vpp_total_revenue"] == 3.0

def test_create_report_single_discharge_cost_event(utils, capsys):
    site = setup_for_create_report(utils, "VPP1", "222", 10)

    site.events.append(Event("222", date(2025, 9, 1), EventType.DISCHARGE, 10, -20))

    utils.create_report("VPP1", "2025-09")
    report = utils.last_report
    print(report)
    assert report["totals"]["total_revenue"] == 0
    assert report["totals"]["vpp_cost_only"] < 0
    assert report["totals"]["vpp_total_revenue"] < 0

def test_create_report_single_charge_event(utils, capsys):
    site = setup_for_create_report(utils, "VPP1", "111", 10)
    site.events.append(Event("111", date(2025, 9, 1), EventType.CHARGE, 10, 20))
    
    utils.create_report("VPP1", "2025-09")

    report = utils.last_report
    print(report)

    assert report["totals"]["total_revenue"] > 0
    assert report["totals"]["vpp_total_revenue"] > 0
    assert report["sites"]["111"]["site_revenue_after_fees"] == 0

def test_create_report_site_has_positive_revenue_after_fees(utils):
    site = setup_for_create_report(utils, "VPP1", "111", 10)

    # Discharge earns enough to cover VPP margin + site daily fee
    site.events.append(Event("111", date(2025, 9, 1), EventType.DISCHARGE, 10, 500))  
    # → revenue = 10 * 500 / 1000 = 5.0

    utils.create_report("VPP1", "2025-09")
    report = utils.last_report
    print(report)

    assert report["totals"]["total_revenue"] == 50
    assert report["totals"]["vpp_total_revenue"] == 19
    assert report["sites"]["111"]["site_revenue_after_fees"] == 31