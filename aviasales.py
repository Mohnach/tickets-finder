import requests
from . import secrets
from decimal import Decimal
from datetime import datetime, timedelta
from .ticket_provider import TicketProvider
from .route_info import RouteInfo
from dataclasses import dataclass
from typing import List
from . import configs
from .cities import Cities
import csv
from .model import AviasalesCache
from sqlalchemy import exc
from sqlalchemy.orm import mapper


# информация о маршруте на самолете
@dataclass
class AviasalesInfo(RouteInfo):
    airline: str = ''
    number: str = ''
    origin_city: str = ''
    destination_city: str = ''
    travel_time: int = 0
    url: str = ''


class Aviasales(TicketProvider):

    my_mapper = mapper(AviasalesInfo, AviasalesCache.__table__, properties={
            'airline': AviasalesCache.__table__.c.airline,
            'number': AviasalesCache.__table__.c.number
        })

    def __init__(self, db_session):
        super(Aviasales, self).__init__(db_session)
        self.load_flights_routes()

    def use_cache(func):
        def wrapped(self, origin_city, destination_city, departure_date, return_date, use_cache=True):
            if use_cache is False:
                return func(self, origin_city, destination_city, departure_date, return_date)
            else:
                # ищем билеты в базе
                #  если нашли, возвращаем,
                #  если не нашли - идем на сайт
                tickets = self.get_from_cache(origin_city, destination_city, departure_date, return_date)

                if tickets is not None:
                    for ticket in tickets:
                        if ticket.is_empty is True:
                            print('В кэше пишут, что искать по этому направлению бесполезно')
                            return []
                    return tickets

                print('В кэше ничего не нашлось. Погнали на сайт')
                tickets = func(self, origin_city, destination_city, departure_date, return_date)

                if not tickets:
                    print('Там ничего нет. Так и запишем')
                    empty_ticket = self.create_empty_ticket(origin_city=origin_city,
                                                            destination_city=destination_city,
                                                            depart_date=departure_date,
                                                            return_date=return_date,
                                                            ticket_type='plain',
                                                            ticket_class=AviasalesInfo)
                    tickets.append(empty_ticket)
                    self.store_to_cache(tickets)
                    return []

                self.store_to_cache(tickets)

                return tickets
        return wrapped

    def get_tickets(self, origin: str, destination: str, depart_date: datetime) -> List[RouteInfo]:
        return []

    @use_cache
    def get_return_tickets(self, origin_city: str, destination_city: str, depart_date: datetime,
                           return_date: datetime) -> List[RouteInfo]:
        iatas = {}
        iatas['destination'] = destination_city
        iatas['origin'] = origin_city

        try:
            destination_iata = iatas.get('destination')
            origin_iata = iatas.get('origin')
        except ValueError:
            print('Invalid city name')
            return []

        # tickets_url = 'http://api.travelpayouts.com/v1/prices/cheap'
        tickets_url = 'https://api.travelpayouts.com/v1/prices/direct'
        params = {
            'currency': 'rub',
            'origin': origin_iata,
            'destination': destination_iata,
            'depart_date': depart_date,
            'return_date': return_date,
            'token': secrets.travelpayouts_token
        }
        headers = {
            'Accept-Encoding': 'gzip, deflate'
        }
        try:
            result = requests.get(tickets_url, params=params, headers=headers, timeout=5)
            result.raise_for_status()
            json_result = result.json()

            if 'success' in json_result:
                if json_result['success'] is True:
                    return self.extract_tickets_from_json(
                        json_result.get('data'),
                        destination_iata,
                        origin_city,
                        destination_city)
        except (requests.RequestException, ValueError):
            pass
        return []

    def get_tickets_for_all_directions(self, origin_city: str, depart_date: datetime,
                                       cities_info: Cities) -> List[RouteInfo]:
        return []

    def get_return_tickets_for_all_directions(self, origin_city: str, depart_date: datetime,
                                              return_date: datetime, cities_info: Cities) -> List[RouteInfo]:
        eng_name = cities_info.translate_from_russian_to_english(origin_city)

        # поиск аэропортов для заданного города
        airports = cities_info.find_airports_for_city(eng_name)
        print(airports)

        tickets = []
        for airport in airports:
            # поиск всех возможных направлений для заданного аэропорта
            routes_list = self.find_routes_for_depart_point(airport)
            print('Число маршрутов из аэропорта {}: {}'.format(airport, len(routes_list)))

            for route in routes_list:
                if cities_info.translate_from_iata_to_english(route['Destination airport']) \
                        in cities_info.international_popular_cities:
                    print('from {} to {}'.format(airport, route['Destination airport']))
                    # Если дистанция между аэропортами больше 5000км, то пропускаем это направление
                    distance = cities_info.calculate_distance(
                        cities_info.get_airport_coordinates(route['Source airport']),
                        cities_info.get_airport_coordinates(route['Destination airport']))
                    if distance > 5000:
                        print(f'Далеко: {distance}km')
                        continue

                    new_tickets = self.get_return_tickets(airport,
                                                          route['Destination airport'],
                                                          depart_date,
                                                          return_date)
                    new_tickets = self.add_estimated_travel_time(new_tickets, distance)
                    tickets += new_tickets

            tickets = self.add_readable_names_for_airports(tickets, cities_info)
            tickets = self.add_mock_url_to_aviatickets(tickets)
            tickets = self.add_attractions_link(tickets, 'destination_city')
        return tickets

    def get_from_cache(self, origin_city, destination_city, depart_date, return_date):
        try:
            next_day_after_departure = depart_date + timedelta(days=1)
            next_day_after_return = return_date + timedelta(days=1)

            tickets = self.session.query(self.my_mapper).filter(
                    AviasalesCache.destination_point == destination_city,
                    AviasalesCache.origin_point == origin_city,
                    AviasalesCache.depart_datetime.between(depart_date, next_day_after_departure),
                    AviasalesCache.return_datetime.between(return_date, next_day_after_return)
                )

            cached_tickets = list(tickets)
            for ticket in cached_tickets:
                print('Роемся в выдаче из кэша')
                if (datetime.now() - ticket.obtained_datetime).days > 1:
                    print('Удаляем старье')
                    self.session.delete(ticket)
                    cached_tickets.remove(ticket)
            self.session.commit()

            if cached_tickets:
                print('В кэше есть что-то актуальное! Берем')
                return cached_tickets
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

    def get_iata_from_dict(self, iata_dict, target):
        if target in iata_dict:
            if 'iata' in iata_dict[target]:
                return iata_dict[target]['iata']
        raise ValueError(f'IATA of {target} not found')

    def convert_city_name_to_iata(self, origin_name, dest_name):

        search = 'Из ' + origin_name + ' в ' + dest_name

        iata_url = 'https://www.travelpayouts.com/widgets_suggest_params'
        params = {
            'q': search
        }

        try:
            result = requests.get(iata_url, params=params, timeout=5)
            result.raise_for_status()
            json_result = result.json()

            iatas = {}
            iatas['origin'] = self.get_iata_from_dict(json_result, 'origin')
            iatas['destination'] = self.get_iata_from_dict(json_result, 'destination')

            return iatas

        except (requests.RequestException, ValueError):
            print('Cities name conversion failed')
            raise ValueError

    def avia_tickets_by_city_week_matrix(self, origin_city, destination_city, depart_date, return_date):

        iatas = self.convert_city_name_to_iata(origin_city, destination_city)

        try:
            destination_iata = iatas.get('destination')
            origin_iata = iatas.get('origin')
        except ValueError:
            print('Invalid city name')
            return None

        tickets_url = 'http://api.travelpayouts.com/v2/prices/week-matrix'
        params = {
            'currency': 'rub',
            'origin': origin_iata,
            'destination': destination_iata,
            'show_to_affiliates': 'false',
            'depart_date': depart_date,
            'return_date': return_date,
            'token': secrets.travelpayouts_token
        }
        try:
            result = requests.get(tickets_url, params=params, timeout=5)
            result.raise_for_status()
            json_result = result.json()

            if 'success' in json_result:
                if json_result['success'] is True:
                    return json_result.get('data')
        except (requests.RequestException, ValueError):
            print('')
        return None

    def extract_tickets_from_json(self, data, destination_iata, origin_city, destination_city):
        tickets = []
        tickets_list = data.get(destination_iata)

        if tickets_list:
            for ticket_key in tickets_list:
                ticket_value = tickets_list.get(ticket_key)
                ticket = AviasalesInfo()
                ticket.route_type = 'plane'
                ticket.origin_point = origin_city
                ticket.destination_point = destination_city
                ticket.number = ticket_value.get('flight_number')
                ticket.airline = ticket_value.get('airline')
                ticket.price = Decimal(ticket_value.get('price'))
                depart_str = ticket_value.get('departure_at')
                ticket.depart_datetime = datetime.strptime(depart_str, '%Y-%m-%dT%H:%M:%SZ')

                return_str = ticket_value.get('return_at')
                ticket.return_datetime = datetime.strptime(return_str, '%Y-%m-%dT%H:%M:%SZ')

                ticket.is_empty = False

                tickets.append(ticket)

        return tickets

    def load_flights_routes(self):
        self.routes_dict = {}
        try:
            dat_file = configs.FLIGHTS_ROUTES_LOCATION
            with open(dat_file, 'r', encoding='utf-8') as f:
                fields = ['Airline',
                          'Airline ID',
                          'Source airport',
                          'Source airport ID',
                          'Destination airport',
                          'Destination airport ID',
                          'Codeshare',
                          'Stops',
                          'Equipment']
                reader = csv.DictReader(f, fields, delimiter=',')
                for row in reader:
                    if row['Source airport'] not in self.routes_dict:
                        self.routes_dict[row['Source airport']] = []
                    self.routes_dict[row['Source airport']].append(row)
        except OSError as e:
            print(f'не удалось открыть csv файл. {repr(e)}')
        except (ValueError, KeyError) as e:
            print(e.text)
            self.routes_dict = {}
        return self.routes_dict

    def add_readable_names_for_airports(self, tickets: List[AviasalesInfo], cities_info: Cities):
        for ticket in tickets:
            ticket.origin_city = cities_info.convert_iata_to_russian_city_name(ticket.origin_point)
            ticket.destination_city = cities_info.convert_iata_to_russian_city_name(ticket.destination_point)
        return tickets

    def add_estimated_travel_time(self, tickets: List[AviasalesInfo], distance: int):
        AVERAGE_AIRCRAFTS_SPEED = 600  # км/ч
        TIME_FOR_AIRPORTS_ROUTINE = 2  # часа
        estimate_travel_time = distance / AVERAGE_AIRCRAFTS_SPEED + TIME_FOR_AIRPORTS_ROUTINE
        for ticket in tickets:
            ticket.travel_time = timedelta(hours=estimate_travel_time).seconds
        return tickets

    def add_mock_url_to_aviatickets(self, tickets: List[AviasalesInfo]):
        for ticket in tickets:
            url_template = 'https://www.google.com/search?q='
            ticket.url = url_template + ticket.airline + '+' + ticket.number + '+flight+' +\
                ticket.depart_date.strftime('%d+%B+%Y')
        return tickets


if __name__ == "__main__":
    # city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'

    depart_date = datetime.strptime('2020-04-10', '%Y-%m-%d')
    return_date = datetime.strptime('2020-04-12', '%Y-%m-%d')

    aviasales_parser = Aviasales()

    # print(avia_tickets_by_city(origin_city, destination_city, depart_date, return_date))
    print(aviasales_parser.get_return_tickets(origin_city, destination_city, depart_date, return_date))
