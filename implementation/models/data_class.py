from dataclasses import dataclass, field
from typing import List
from datetime import datetime


class EventType(Enum):
    CHARGE = "Charge"
    DISCHARGE = "Discharge"


@dataclass
class Event:
    nmi: str
    date: datetime
    event_type: EventType
    energy_kwh: float
    tariff_cents_per_kwh: float


@dataclass
class Battery:
    manufacturer: str
    serial: str
    capacity_kwh: float


@dataclass
class Site:
    vpp_name: str
    nmi: str
    address: str
    batteries: List[Battery] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)


@dataclass
class VPP:
    name: str
    revenue_percentage: float
    daily_fee_aud: float
    sites: List[Site] = field(default_factory=list)
