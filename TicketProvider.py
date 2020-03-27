from datetime import datetime
from RouteInfo import RouteInfo
from typing import List

class TicketProvider:
    def __init__(self, use_cache=True):
        self._use_cache = use_cache
        self.engine = None

    def get_tickets(self, origin : str, destination : str, depart_date : datetime) -> List[RouteInfo]:
        pass

    def get_return_tickets(self, origin : str, destination : str, depart_date : datetime, return_date : datetime) -> List[RouteInfo]:
        pass
