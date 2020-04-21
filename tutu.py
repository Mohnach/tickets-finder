import requests
import csv
import json
import os
from . import configs
from decimal import Decimal
from datetime import datetime, timedelta
from .TicketProvider import TicketProvider
from .RouteInfo import RouteInfo
from dataclasses import dataclass
from bs4 import BeautifulSoup
from typing import List
from .model import TutuCache
from sqlalchemy import exc
from sqlalchemy.orm import mapper


class Tutu(TicketProvider):

    def __init__(self, db_session):
        super(Tutu, self).__init__(db_session)
        self.read_csv_to_dict()
        self.my_mapper = mapper(TutuInfo, TutuCache.__table__, properties={
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

    def get_tickets(self, origin_city: str, destination_city: str, depart_date: datetime) -> List[RouteInfo]:
        routes = self.find_routes(origin_city, destination_city)

        tickets = []
        for route in routes:
            print(route)
            found_tickets = self.get_tickets_for_two_cities(route, depart_date)
            if found_tickets is not None:
                tickets += found_tickets
        return tickets

    def get_return_tickets(self, origin: str, destination: str, depart_date: datetime,
                           return_date: datetime) -> List[RouteInfo]:
        return []

    def use_cache(func):
        def wrapped(self, route, depart_date, use_cache=True):
            if use_cache is False:
                return func(self, route, depart_date)
            else:
                # ищем билеты в базе
                #  если нашли, возвращаем,
                #  если не нашли - идем на сайт
                tickets = self.get_from_cache(route, depart_date)
                if tickets is not None:
                    return tickets

                print('В кэше ничего не нашлось. Погнали на сайт')
                tickets = func(self, route, depart_date)

                if tickets:
                    self.store_to_cache(tickets)

                return tickets
        return wrapped

    def get_from_cache(self, route, depart_date):
        try:
            origin_city_id = route['departure_station_id']
            destination_city_id = route['arrival_station_id']

            next_day = depart_date + timedelta(days=1)

            tickets = self.session.query(self.my_mapper).filter(
                    TutuCache.destination_city == destination_city_id,
                    TutuCache.origin_city == origin_city_id,
                    TutuCache.depart_datetime.between(depart_date, next_day)
                )

            tutu_info_list = list(tickets)
            for ticket in tutu_info_list:
                print('Роемся в выдаче из кэша')
                if (datetime.now() - ticket.obtained_datetime).days > 1:
                    print('Удаляем старье')
                    self.session.delete(ticket)
                    tutu_info_list.remove(ticket)
            self.session.commit()

            if tutu_info_list:
                print('В кэше есть что-то актуальное! Берем')
                return tutu_info_list
        except exc.SQLAlchemyError:
            print('ошибка при работе с кэшем')
            return None

    def store_to_cache(self, tickets):
        try:
            for ticket in tickets:
                self.session.add(ticket)
            self.session.commit()
        except exc.SQLAlchemyError:
            print('ошибка записи в кэш')

    # читаем csv в переменную routes_dict
    # ключ - id станции. value - лист со строками csv для этого города (в формате ordered dict)
    def read_csv_to_dict(self):
        self.routes_dict = {}
        try:
            basedir = os.path.abspath(os.path.dirname(__file__))
            csv_file = os.path.join(basedir, configs.CSV_ROUTES_LOCATION)
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    for name in ['departure_station_name', 'arrival_station_name']:
                        if '-' in row[name]:
                            row[name] = row[name].replace('-', ' ')
                        if '.' in row[name]:
                            row[name] = row[name].replace('.', ' ')
                        if 'Пасс' in row[name]:
                            row[name] = row[name].replace('Пасс', '')
                        row[name] = row[name].strip()
                    if row['departure_station_name'] not in self.routes_dict:
                        self.routes_dict[row['departure_station_name']] = []

                    self.routes_dict[row['departure_station_name']].append(row)
        except OSError as e:
            print(f'не удалось открыть csv файл. {repr(e)}')
        except (ValueError, KeyError) as e:
            print(repr(e))
            self.routes_dict = {}

    def find_routes(self, origin_city, destination_city):
        routes = []
        # if origin_city in self.routes_dict:
        try:
            for key in self.routes_dict:
                if origin_city in key:
                    for route_for_city in self.routes_dict[key]:
                        # print(route_for_city['arrival_station_name'])
                        if route_for_city['arrival_station_name'] == destination_city:
                            routes.append(route_for_city)
        except (ValueError, KeyError) as e:
            print(f'error in routes_dict. {repr(e)}')
        return routes

    def find_stations(self, origin_city):
        routes = []
        # if origin_city in self.routes_dict:
        try:
            for key in self.routes_dict:
                if origin_city in key:
                    routes.append(key)
        except (ValueError, KeyError) as e:
            print(f'error in routes_dict. {repr(e)}')
        return routes

    # deprecated
    def find_routes_from_file(self, origin_city, destination_city):
        with open('data/tutu_routes.csv', 'r', encoding='utf-8') as f:
            fields = ['departure_station_id',
                      'departure_station_name',
                      'arrival_station_id',
                      'arrival_station_name']
            reader = csv.DictReader(f, fields, delimiter=';')

            routes = []
            for row in reader:
                if (origin_city in row.get('departure_station_name')) and\
                   (destination_city in row.get('arrival_station_name')):
                    route = {}
                    route['departure_station_name'] = row.get('departure_station_name')
                    route['departure_station_id'] = row.get('departure_station_id')
                    route['arrival_station_name'] = row.get('arrival_station_name')
                    route['arrival_station_id'] = row.get('arrival_station_id')
                    routes.append(route)
            return routes

    @use_cache
    def get_tickets_for_two_cities(self, route, depart_date):

        origin_city_id = route['departure_station_id']
        destination_city_id = route['arrival_station_id']

        params = {
            'nnst1': origin_city_id,
            'nnst2': destination_city_id,
            'date': depart_date.strftime('%d.%m.%Y')
        }

        trains_url = 'https://www.tutu.ru/poezda/rasp_d.php'
        user_agent = self.get_random_user_agent()
        headers = {
            "Accept-Language": "en-US,en;q=0.5",
            'User-Agent': user_agent
            }
        html = self.get_html(trains_url, params=params, header=headers)
        # write_file('data/new_test.html', html)

        routes_in_json = self.get_routes_in_json(html)
        tickets = self.get_tickets_from_json(routes_in_json)

        return tickets

    def get_html(self, url, params=None, header=None):
        try:
            result = requests.get(url, params=params, headers=header)
            result.raise_for_status()
            return result.text
        except(requests.RequestException, ValueError):
            print('Сетевая ошибка')
            return None

    def get_routes_in_json(self, html):
        try:
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                # self.write_file('test.html', soup.prettify())
                scripts_list = soup.findAll('script')
                for script in scripts_list:
                    # print(script.text)
                    script_text = script.text
                    script_text = script_text.strip()
                    if script_text.startswith('window.params = {'):
                        script_text = script_text.lstrip('window.params = ')

                        script_text = script_text[0:script_text.find('window.langLabels')]
                        script_text = script_text.strip()
                        script_text = script_text.rstrip(';')

                        # write_file('data/test.json', script_text)
                        json_result = json.loads(script_text)

                        return json_result
        except ValueError as e:
            print(f'ошибка при парсинге html. {repr(e)}')
        return None

    def get_tickets_from_json(self, data):
        tickets = []

        try:
            componentData = data['componentData']
            resultsList = componentData['searchResultList']
            for result in resultsList:
                trains = result['trains']
                for train in trains:

                    # run = train['params']['run']
                    trip = train['params']['trip']
                    seats = train['params']['withSeats']
                    for seat in seats['categories']:
                        if seat['type'] == 'prices':
                            params = seat['params']
                            ticket = TutuInfo()
                            ticket.route_type = 'train'

                            ticket.seat_type = params['name']
                            ticket.seats_count = params['seatsCount']
                            ticket.price = params['price']['RUB']
                            ticket.top_seats_price = params['topSeatsPrice']
                            ticket.top_seats_count = params['topSeatsCount']
                            ticket.bottom_seats_price = params['bottomSeatsPrice']
                            ticket.bottom_seats_count = params['bottomSeatsCount']

                            ticket.url = seats['buyAbsUrl']

                            ticket.number = trip['trainNumber']
                            ticket.origin_city = trip['departureStation']
                            ticket.destination_city = trip['arrivalStation']
                            depart_date_str = trip['departureDate'] + ' ' + trip['departureTime']
                            ticket.depart_datetime = datetime.strptime(depart_date_str, '%Y-%m-%d %H:%M:%S')
                            arrival_date_str = trip['arrivalDate'] + ' ' + trip['arrivalTime']
                            ticket.arrival_datetime = datetime.strptime(arrival_date_str, '%Y-%m-%d %H:%M:%S')
                            ticket.travel_time = trip['travelTimeSeconds']

                            tickets.append(ticket)
        except (ValueError, KeyError, TypeError) as e:
            print(f'ошибка при парсинге json. {repr(e)}')

        return tickets

    def write_file(self, result_file, text):
        try:
            with open(result_file, 'w', encoding='utf-8') as output:
                output.write(text)
        except OSError as e:
            print(f'не удалось открыть файл. {repr(e)}')

    # Deprecated
    def train_tickets_by_api(self, origin_city, destination_city, depart_date, return_date):

        trains_url = 'https://suggest.travelpayouts.com/search'

        params = {
            'service': 'tutu_trains',
            'term': origin_city,
            'term2': destination_city,
            'callback': 'plazcard'
        }

        user_agent = self.get_random_user_agent()

        headers = {
            "Accept-Language": "en-US,en;q=0.5",
            'User-Agent': user_agent
            }
        try:
            result = requests.get(trains_url, params=params, headers=headers)
            result.raise_for_status()
            text_result = result.text

            return text_result
        except (requests.RequestException, ValueError):
            print('exception')
        return None


# информация о маршруте на поезде
@dataclass
class TutuInfo(RouteInfo):
    seat_type: str = ''
    seats_count: int = 0
    top_seats_price: Decimal = Decimal(0)
    top_seats_count: int = 0
    bottom_seats_price: Decimal = Decimal(0)
    bottom_seats_count: int = 0
    url: str = ''
    number: str = ''
    travel_time: int = 0


if __name__ == "__main__":
    # city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date = datetime.strptime('10.04.2020', '%d.%m.%Y')
    tutu_parser = Tutu()

    tutu_parser.get_tickets(origin_city, destination_city, depart_date)
    tutu_parser.get_tickets(origin_city, destination_city, depart_date)
