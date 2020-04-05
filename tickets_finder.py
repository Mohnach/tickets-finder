from tutu import Tutu
from aviasales import Aviasales
from datetime import datetime
from model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os


def get_tickets(origin_city, destination_city, departure_date, return_date, sources):
    tickets = []

    print('База не инициализирована!')
    print('Создаем новую сессию...')
    basedir = os.path.abspath(os.path.dirname(__file__))
    base_file = os.path.join(basedir, 'data', 'test.db')
    base_uri = 'sqlite:///' + base_file

    engine = create_engine(base_uri)
    # Base.metadata.create_all(engine)
    if not os.path.exists(base_file):
        print('Создаем новую базу!')
        Base.metadata.create_all(engine)
        # TutuCache.__table__.create(engine)

    session = Session(bind=engine)

    if 'aviasales' in sources:
        aviasales_provider = Aviasales(db_session=session)
        tickets += aviasales_provider.get_return_tickets(origin_city, destination_city, departure_date, return_date)
    if 'tutu' in sources:
        tutu_provider = Tutu(db_session=session)
        tickets += tutu_provider.get_tickets(origin_city, destination_city, departure_date)
    return tickets


if __name__ == "__main__":
    # city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date = datetime.strptime('2020-04-21', '%Y-%m-%d')
    return_date = datetime.strptime('2020-04-22', '%Y-%m-%d')

    print(get_tickets(origin_city, destination_city, depart_date, return_date, ['aviasales', 'tutu']))
