from model import Base, TutuCache
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import Session, Mapper
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


Mapper(TutuInfo, TutuCache.__table__)
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