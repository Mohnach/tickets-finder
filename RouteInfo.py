from dataclasses import dataclass
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional

@dataclass
class RouteInfo:
    origin_city: str = ''
    destination_city: str = ''
    route_type: str = ''
    depart_datetime: Optional[datetime] = None
    arrival_datetime: Optional[datetime] = None
    return_datetime: Optional[datetime] = None
    price: Decimal = Decimal('0')

    @property
    def depart_date(self) -> Optional[date]:
        if self.depart_datetime is not None:
            return self.depart_datetime.date()
        return None

    @property
    def depart_time(self) -> Optional[time]:
        if self.depart_datetime is not None:
            return self.depart_datetime.time()
        return None

    @property
    def arrival_date(self) -> Optional[date]:
        if self.arrival_datetime is not None:
            return self.arrival_datetime.date()
        return None

    @property
    def arrival_time(self) -> Optional[time]:
        if self.arrival_datetime is not None:
            return self.arrival_datetime.time()
        return None

    @property
    def return_date(self) -> Optional[date]:
        if self.return_datetime is not None:
            return self.return_datetime.date()
        return None

    @property
    def return_time(self) -> Optional[time]:
        if self.return_datetime is not None:
            return self.return_datetime.time()
        return None

if __name__ == "__main__":
    test = RouteInfo('Moscow','London', 'peshkom')
    print(test)
    print(test.arrival_time)
    print(test.depart_date)
    test2 = datetime(1970,4,11)
    print(test2)
