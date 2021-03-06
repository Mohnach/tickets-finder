from .tutu import Tutu
from .aviasales import Aviasales
from .cities import Cities
from datetime import datetime
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import Session
import os
from . import configs


def get_tickets(origin_city, destination_city, departure_date, providers_list):
    tickets = []

    for provider in providers_list:
        tickets += provider.get_tickets(origin_city, destination_city, departure_date)

    return tickets


def get_return_tickets(origin_city, destination_city, departure_date, return_date, providers_list):
    tickets = []

    for provider in providers_list:
        tickets += provider.get_return_tickets(origin_city, destination_city, departure_date, return_date)

    return tickets


def get_tickets_for_all_directions(origin_city, departure_date, providers_list):
    # содержит инфу о городах: переводы на разные языки, iata code, координаты
    cities_info = Cities()

    tickets = []
    for provider in providers_list:
        tickets += provider.get_tickets_for_all_directions(origin_city, departure_date, cities_info)

    return tickets


def get_return_tickets_for_all_directions(origin_city, departure_date, return_date, providers_list):
    # содержит инфу о городах: переводы на разные языки, iata code, координаты
    cities_info = Cities()

    tickets = []

    for provider in providers_list:
        tickets += provider.get_return_tickets_for_all_directions(origin_city, departure_date, return_date, cities_info)

    return tickets


def prepare_db_session():
    session = None
    try:
        print('Создаем новую сессию...')
        base_file = configs.DB_LOCATION
        base_uri = 'sqlite:///' + base_file

        engine = create_engine(base_uri)
        if os.path.exists(base_file):
            session = Session(bind=engine)
    except exc.SQLAlchemyError:
        print('Не удалось инициализировать кэш')

    return session


if __name__ == "__main__":
    # Debug
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date = datetime.strptime('2020-04-21', '%Y-%m-%d')
    return_date = datetime.strptime('2020-04-22', '%Y-%m-%d')

    session = prepare_db_session()

    providers_list = []

    aviasales_provider = Aviasales(db_session=session)
    providers_list.append(aviasales_provider)

    tutu_provider = Tutu(db_session=session)
    providers_list.append(tutu_provider)

    print('One way tickets')
    print(get_tickets(origin_city, destination_city, depart_date, providers_list))

    print('Return tickets')
    print(get_return_tickets(origin_city, destination_city, depart_date, return_date, providers_list))
