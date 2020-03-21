from datetime import datetime
from RouteInfo import RouteInfo
from typing import List

class TicketProvider:
    def get_tickets(self, origin : str, destination : str, depart_date : datetime) -> List[RouteInfo]:
        pass

    def get_return_tickets(self, origin : str, destination : str, depart_date : datetime, return_date : datetime) -> List[RouteInfo]:
        pass
