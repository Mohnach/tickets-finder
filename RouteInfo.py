from dataclasses import dataclass
from datetime import date, time, datetime
from decimal import Decimal

@dataclass
class RouteInfo:
    origin_city: str = ''
    destination_city: str = ''
    route_type: str = ''
    depart_datetime: datetime = datetime.now()
    arrival_datetime: datetime = datetime.now()
    price: Decimal = Decimal('0')

    @property
    def depart_date(self) -> date:
        return self.depart_datetime.date()

    @property
    def depart_time(self) -> time:
        return self.depart_datetime.time()

    @property
    def arrival_date(self) -> date:
        return self.arrival_datetime.date()

    @property
    def arrival_time(self) -> time:
        return self.arrival_datetime.time()

if __name__ == "__main__":
    test = RouteInfo('Moscow','London', 'peshkom')
    print(test)
    print(test.arrival_time)
    print(test.depart_date)
    test2 = datetime(1970,4,11)
    print(test2)