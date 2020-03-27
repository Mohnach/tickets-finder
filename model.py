from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, DECIMAL
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.declarative import declared_attr

@as_declarative()
class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

class TutuCache(Base):
    # fields from RouteInfo
    route_type = Column(String)
    origin_city = Column(String)
    destination_city = Column(String)
    depart_datetime = Column(DateTime)
    arrival_datetime = Column(DateTime)
    return_datetime = Column(DateTime)
    price = Column(DECIMAL)
    obtained_datetime = Column(DateTime)

    # fields from TutuInfo
    seat_type = Column(String)
    seats_count = Column(Integer)
    top_seats_price = Column(DECIMAL)
    top_seats_count = Column(Integer)
    bottom_seats_price = Column(DECIMAL)
    bottom_seats_count = Column(Integer)
    url = Column(String)
    number = Column(String)
    travel_time = Column(Integer)

    def __repr__(self):
        return f'<{self.__class__}. id: {self.id}. Origin city: {self.origin_city}. Destination city: {self.destination_city}>'


if __name__ == "__main__":
    test = TutuCache(origin_city="Default")
    print(test)