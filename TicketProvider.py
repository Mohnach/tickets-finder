from datetime import datetime
from RouteInfo import RouteInfo

class TicketProvider:
    def get_ticket(self, origin : str, destination : str, depart_date : datetime) -> RouteInfo:
        pass

    def get_return_ticket(self, origin : str, destination : str, depart_date : datetime, return_date : datetime) -> RouteInfo:
        pass
