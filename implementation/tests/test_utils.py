import pytest
from models.data_class import VPP, Site, Battery
from utils.vpp_utils import VPPUtils

@pytest.fixture
def utils():
    return VPPUtils()

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
