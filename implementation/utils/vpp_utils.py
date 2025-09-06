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
from models.data_class import VPP, EventType, Site, Battery, Event
import csv
from datetime import datetime


class Utils(ABC):
    @abstractmethod
    def create_update_vpp(self,name: str, revenue_percentage: float, daily_fee_aud: float):
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

    # @abstractmethod
    # def create_report(self, vpp_name: str, month_yyyy_mm: str):
    #     pass

    @abstractmethod
    def exit(self,vpp_name: str, month_yyyy_mm: str):
        pass

# TODO: class implements the abstract class
class VPPUtils(Utils):

    def __init__(self):
        self.vpps: Dict[str, VPP] = {}
        self.sites: Dict[str, Site] = {}
        self.last_report: dict ={}

    
    def create_update_vpp(self, name: str, revenue_percentage: float, daily_fee_aud: float):
        #  update
        if name in self.vpps:
            vpp = self.vpps[name]
            vpp.revenue_percentage = revenue_percentage
            vpp.daily_fee_aud = daily_fee_aud
            print(f"Updated VPP '{name}'")
        #  create
        else:
            self.vpps[name] = VPP(name=name, revenue_percentage=revenue_percentage, daily_fee_aud=daily_fee_aud)
            print(f"Created VPP '{name}'")

    def create_update_site(self, vpp_name: str, nmi: str, address: str):
        # assert if site's vpp exists first if not raise an error
        if vpp_name not in self.vpps:
            raise ValueError(f"VPP '{vpp_name}' not found")
        # update the site if exists
        if nmi in self.sites:
            site = self.sites[nmi]
            site.address = address
            site.vpp_name = vpp_name
            print(f"Updated Site NMI={nmi}")
        # else create it
        else:
            site = Site(vpp_name=vpp_name, nmi=nmi, address=address)
            self.sites[nmi] = site
            self.vpps[vpp_name].sites.append(site)
            print(f"Created Site NMI={nmi}")

    def create_update_battery(self, site_nmi: str, manufacturer: str, serial: str, capacity_kwh: float):
        # assert if battery's site exist
        if site_nmi not in self.sites:
            raise ValueError(f"Site with NMI {site_nmi} not found")
        #  update or add the battery to the site
        site = self.sites[site_nmi]
        for bat in site.batteries:
            if bat.serial == serial:
                bat.manufacturer = manufacturer
                bat.capacity_kwh = capacity_kwh
                print(f"Updated Battery serial={serial} at site {site_nmi}")
                return
        bat = Battery(manufacturer=manufacturer, serial=serial, capacity_kwh=capacity_kwh)
        site.batteries.append(bat)
        print(f"Created Battery serial={serial} at site {site_nmi}")
    
    def import_events(self, file_path: str):
        imported, skipped = 0, 0
        try:
            with open(file_path, newline='', encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    try:
                        nmi = row['NMI'].strip()
                        if nmi not in self.sites:
                            skipped += 1
                            continue
                        dt = datetime.strptime(row['DATE'].strip(), "%Y-%m-%d").date()
                        ev_type_str = row['EVENT_TYPE'].strip().title()
                        
                        if ev_type_str not in [e.value for e in EventType]:
                            skipped += 1
                            continue
                        ev_type = EventType[ev_type_str.upper()]
                        energy = float(row['ENERGY'])
                        tariff = float(row['TARIFF'])
                        event = Event(nmi=nmi, date=dt, event_type=ev_type, energy_kwh=energy, tariff_cents_per_kwh=tariff)
                        self.sites[nmi].events.append(event)
                        imported += 1
                    except Exception as e:
                        skipped += 1
                        print(f"Skipping event, Error: {e}")
        except FileNotFoundError:
            raise
        print(f"Imported={imported}, Skipped={skipped}")
    
    
    def exit(self):
        if self.last_report:
            print(f"Report for VPP '{self.last_report['vpp']}' for month '{self.last_report['month']}' generated successfully. Exiting.")
        else:
            print("No report was generated. Exiting.")