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
from datetime import datetime, date
import calendar
import json

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

    @abstractmethod
    def create_report(self, vpp_name: str, month_yyyy_mm: str):
        pass

    @abstractmethod
    def exit(self,vpp_name: str, month_yyyy_mm: str):
        pass

# TODO: class implements the abstract class
class VPPUtils(Utils):

    def __init__(self):
        self.vpps: Dict[str, VPP] = {}
        self.sites: Dict[str, Site] = {}
        self.last_report: dict ={}

    @staticmethod
    def find_month_start_end(yyyymm: str):
        year, month = [int(x) for x in yyyymm.split("-", 1)]
        start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end = date(year, month, last_day)
        return start, end
    
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
    
    def create_report(self, vpp_name, month_yyyy_mm):
        # ===================== Assertion =====================
        # assert if vpp exist
        if vpp_name not in self.vpps:
            raise ValueError(f"VPP '{vpp_name}' not found")
        
        # get the sites for the vpp and if not sites then skip generating the report
        sites = [s for s in self.sites.values() if s.vpp_name == vpp_name]
        if not sites:
            print(f"VPP has not sites to generate reports")
            return
        
        # ===================== constraints =====================
        start, end = self.find_month_start_end(month_yyyy_mm)
        capacity_per_site= {s.nmi: sum(b.capacity_kwh for b in s.batteries) for s in sites}
        total_capacity= sum(capacity_per_site.values())
        vpp = self.vpps[vpp_name]
        contributed_sites = {s.nmi: 0.0 for s in sites}
        vpp_cost_only= 0.0
        total_revenue= 0.0
        days= 28

        # ===================== Core logic to calculate the revenue per site and for VPP =====================
        # total revenue for sites for the given month
        for s in sites:
            for ev in s.events:
                if not(start <= ev.date <= end):
                    print(f"event date {ev.date} is not valid for this report");
                    continue
                value = (ev.tariff_cents_per_kwh* ev.energy_kwh) / 100
                if(value <0 and ev.event_type == EventType.DISCHARGE):
                    # discharge negative values are 100% vpp only cost
                    vpp_cost_only +=value
                else:
                    total_revenue +=value
                    contributed_sites[ev.nmi] += value
        
        # The VPP is assigned its margin of the revenue first
        vpp_margin = total_revenue * (vpp.revenue_percentage / 100)
        # Of the remainder of the revenue
        revenue_reminder = total_revenue - vpp_margin
        share_per_site = {s.nmi: 0.0 for s in sites}
        if(revenue_reminder > 0 ):
            # 80% is assigned to the Site that had an event
            total_contributions = sum(contributed_sites.values())
            if total_contributions > 0:
                for sid, contrib in contributed_sites.items():
                    share_per_site[sid] = 0.8 * revenue_reminder * (contrib / total_contributions)

            # 20% is distributed across all Sites, proportionally according to their batteries' capacity
            if total_capacity > 0:
                for sid, cap in capacity_per_site.items():
                    share_per_site[sid] += 0.2 * revenue_reminder * (cap / total_capacity)

                        
        # Daily fees are taken from a Site’s revenue and given to the VPP, assuming 28 days every month
        # Daily fees cannot make a Site’s total revenue for the month go negative
        site_fees = {}
        for sid, amount in share_per_site.items():
            fee = vpp.daily_fee_aud * days
            actual_fee = min(max(amount, 0), fee)
            share_per_site[sid] -= actual_fee
            site_fees[sid] = actual_fee

        # construct the report:
        vpp_total_revenue = vpp_margin + sum(site_fees.values()) + vpp_cost_only
        report = {
            "vpp": vpp.name,
            "month": month_yyyy_mm,
            "totals": {
                "total_revenue": round(total_revenue, 2),
                "vpp_ad_valorem_fee": round(vpp_margin, 2),
                "vpp_cost_only": round(vpp_cost_only, 2),
                "vpp_total_revenue":round(vpp_total_revenue, 2),
                "site_total_revenue_after_fees": round(sum(share_per_site.values()), 2),
            },
            "sites": {
                s.nmi: {
                    "nmi": s.nmi,
                    "address": s.address,
                    "site_capacity_kwh": round(capacity_per_site[s.nmi], 2),
                    "site_revenue_before_fees": round(share_per_site[s.nmi] + site_fees[s.nmi], 2),
                    "site_daily_fee": round(site_fees[s.nmi], 2),
                    "site_revenue_after_fees": round(share_per_site[s.nmi], 2),
                }
                for s in sites
            }
        }
        self.last_report = report
        return(json.dumps(report, indent=2))


    def exit(self):
        if self.last_report:
            print(f"Report for VPP '{self.last_report['vpp']}' for month '{self.last_report['month']}' generated successfully. Exiting.")
        else:
            print("No report was generated. Exiting.")