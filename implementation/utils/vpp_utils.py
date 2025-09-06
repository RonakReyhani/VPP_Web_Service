# This file contains Utils for report generator
# Methods:
# create/update vpp method
# create/update site method
# create/update battery method
# import event method
# create report method
# exit method: just logs the report generated successfully message
from abc import ABC, abstractmethod
from typing import Dict
from models.data_class import VPP, Site

class Utils(ABC):
    @abstractmethod
    def create_update_vpp(self,name: str, revenue_percentage: float, daily_fee_aud: float)
        pass

    @abstractmethod
    def create_update_site(self, vpp_name: str, nmi: str, address: str):
        pass

    @abstractmethod
    def create_update_battery(self, site_nmi: str, manufacturer: str, serial: str, capacity_kwh: float):
        pass

    @abstractmethod
    def import_events(self, file_path: str):
        pass

    @abstractmethod
    def create_report(self, vpp_name: str, month_yyyy_mm: str):
        pass

    @abstractmethod
    def exit(self):
        pass

# TODO: class implements the abstract class
class VPPUtils:

    def __init__(self):
        self.vpps: Dict[str, VPP] = {}
        self.sites: Dict[str, Site] = {}