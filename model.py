from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, DECIMAL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TutuCache(Base):
    __tablename__ = 'tutu_cache'

    id = Column(Integer, primary_key=True)
    route_type = Column(String)
    origin_city = Column(String)
    destination_city = Column(String)
    depart_datetime = Column(DateTime)
    arrival_datetime = Column(DateTime)
    return_datetime = Column(DateTime)
    price = Column(DECIMAL)
    obtained_datetime = Column(DateTime)

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
            return f'<id {self.id} name {self.origin_city}>'


if __name__ == "__main__":
    user1 = TutuCache(origin_city="Вася")
    #print("User1 columns: " + str(user1.__table__.c.items()))
    print(user1)
