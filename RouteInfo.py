from dataclasses import dataclass
from datetime import date, time

@dataclass
class RouteInfo:
    origin_city: str
    destination_city: str
    depart_date: date
    depart_time: time
    arrival_date: date
    arrival_time: time
    route_type: str
    price: float
