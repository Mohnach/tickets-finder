import requests
from . import secrets
from decimal import Decimal
from datetime import datetime
from .TicketProvider import TicketProvider
from .RouteInfo import RouteInfo
from dataclasses import dataclass
from typing import List


class Aviasales(TicketProvider):

    def get_tickets(self, origin: str, destination: str, depart_date: datetime) -> List[RouteInfo]:
        return []

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
                           return_date: datetime) -> List[RouteInfo]:
        iatas = self.convert_city_name_to_iata(origin_city, destination_city)

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
        try:
            result = requests.get(tickets_url, params=params)
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
