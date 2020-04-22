import requests
from . import secrets
from decimal import Decimal
from datetime import datetime
from .TicketProvider import TicketProvider
from .RouteInfo import RouteInfo
from dataclasses import dataclass
from typing import List
from . import configs
from .cities import Cities
import csv


class Aviasales(TicketProvider):

    def __init__(self, db_session):
        super(Aviasales, self).__init__(db_session)
        self.load_flights_routes()

    def get_tickets(self, origin: str, destination: str, depart_date: datetime) -> List[RouteInfo]:
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

                    tickets += self.get_return_tickets(airport,
                                                       route['Destination airport'],
                                                       depart_date,
                                                       return_date,
                                                       convert_to_iata=False)
        return tickets

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
            result = requests.get(iata_url, params=params)
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
            result = requests.get(tickets_url, params=params)
            result.raise_for_status()
            json_result = result.json()

            if 'success' in json_result:
                if json_result['success'] is True:
                    return json_result.get('data')
        except (requests.RequestException, ValueError):
            print('')
        return None

    def get_return_tickets(self, origin_city: str, destination_city: str, depart_date: datetime,
                           return_date: datetime, convert_to_iata=True) -> List[RouteInfo]:
        iatas = {}
        if convert_to_iata is True:
            iatas = self.convert_city_name_to_iata(origin_city, destination_city)
        else:
            iatas['destination'] = destination_city
            iatas['origin'] = origin_city

        try:
            destination_iata = iatas.get('destination')
            origin_iata = iatas.get('origin')
        except ValueError:
            print('Invalid city name')
            return []

        tickets_url = 'http://api.travelpayouts.com/v1/prices/cheap'
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
            result = requests.get(tickets_url, params=params, headers=headers)
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

    def extract_tickets_from_json(self, data, destination_iata, origin_city, destination_city):
        tickets = []
        tickets_list = data.get(destination_iata)

        if tickets_list:
            for ticket_key in tickets_list:
                ticket_value = tickets_list.get(ticket_key)
                ticket = AviasalesInfo()
                ticket.route_type = 'plane'
                ticket.origin_city = origin_city
                ticket.destination_city = destination_city
                ticket.number = ticket_value.get('flight_number')
                ticket.airline = ticket_value.get('airline')
                ticket.price = Decimal(ticket_value.get('price'))
                depart_str = ticket_value.get('departure_at')
                ticket.depart_datetime = datetime.strptime(depart_str, '%Y-%m-%dT%H:%M:%SZ')

                return_str = ticket_value.get('return_at')
                ticket.return_datetime = datetime.strptime(return_str, '%Y-%m-%dT%H:%M:%SZ')

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


# информация о маршруте на самолете
@dataclass
class AviasalesInfo(RouteInfo):
    airline: str = ''


if __name__ == "__main__":
    # city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'

    depart_date = datetime.strptime('2020-04-10', '%Y-%m-%d')
    return_date = datetime.strptime('2020-04-12', '%Y-%m-%d')

    aviasales_parser = Aviasales()

    # print(avia_tickets_by_city(origin_city, destination_city, depart_date, return_date))
    print(aviasales_parser.get_return_tickets(origin_city, destination_city, depart_date, return_date))
