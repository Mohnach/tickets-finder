from model import Base, TutuCache
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import Session, mapper
import os
from tutu import TutuInfo
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
base_file = os.path.join(basedir, 'data', 'test.db')
base_uri = 'sqlite:///' + base_file

engine = create_engine(base_uri)
#Base.metadata.create_all(engine)
if not os.path.exists(base_file):
    TutuCache.__table__.create(engine)


mapper(TutuInfo, TutuCache.__table__, properties={
    'seat_type': TutuCache.__table__.c.seat_type,
    'seats_count': TutuCache.__table__.c.seats_count,
    'top_seats_price': TutuCache.__table__.c.top_seats_price,
    'top_seats_count': TutuCache.__table__.c.top_seats_count,
    'bottom_seats_price': TutuCache.__table__.c.bottom_seats_price,
    'bottom_seats_count': TutuCache.__table__.c.bottom_seats_count,
    'url': TutuCache.__table__.c.url,
    'number': TutuCache.__table__.c.number,
    'travel_time': TutuCache.__table__.c.travel_time
})
session = Session(bind=engine)


test_ticket = TutuInfo(origin_city='Madrid',
    destination_city='Barcelona',
    route_type='catapult',
    depart_datetime=datetime.now(),
    arrival_datetime=datetime.now(),
    return_datetime=datetime.now(),
    price=0,
    seat_type='lux')
    
session.add(test_ticket)
session.commit()

# test_query = session.query(TutuCache).filter_by(origin_city='Madrid').first()
# print(test_query)