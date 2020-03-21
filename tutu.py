import requests
import csv
import json
from decimal import Decimal
from datetime import datetime
from TicketProvider import TicketProvider
from RouteInfo import RouteInfo
from dataclasses import dataclass
from bs4 import BeautifulSoup
from typing import List

class Tutu(TicketProvider):

    trains_url = 'https://www.tutu.ru/poezda/rasp_d.php'

    def get_tickets(self, origin : str, destination : str, depart_date : datetime) -> List[RouteInfo]:
        routes = self.find_routes(origin_city, destination_city)

        tickets = []
        for route in routes:
            print(route)
            found_tickets = self.get_tickets_for_two_cities(route, depart_date)
            if found_tickets is not None:
                tickets += found_tickets
        return tickets 

    def get_return_tickets(self, origin : str, destination : str, depart_date : datetime,
                            return_date : datetime) -> List[RouteInfo]:
        pass

    def find_routes(self, origin_city, destination_city):
        with open('data/tutu_routes.csv', 'r', encoding='utf-8') as f:
            fields = ['departure_station_id','departure_station_name','arrival_station_id','arrival_station_name']
            reader = csv.DictReader(f, fields, delimiter=';')

            routes = []
            for row in reader:
                if (origin_city in row.get('departure_station_name')) and (destination_city in row.get('arrival_station_name')):
                    route = {}
                    route['departure_station_name'] = row.get('departure_station_name')
                    route['departure_station_id'] = row.get('departure_station_id')
                    route['arrival_station_name'] = row.get('arrival_station_name')
                    route['arrival_station_id'] = row.get('arrival_station_id')
                    routes.append(route)
            return routes

    def get_tickets_for_two_cities(self, route, depart_date):

        origin_city_id = route['departure_station_id']
        destination_city_id = route['arrival_station_id']

        params = {
            'nnst1' : origin_city_id,
            'nnst2' : destination_city_id,
            'date' : depart_date.strftime('%d.%m.%Y')
        }

        headers = {"Accept-Language": "en-US,en;q=0.5"}
        html = self.get_html(self.trains_url, params = params, header = headers)
        #write_file('data/new_test.html', html)

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
            return False

    def get_routes_in_json(self, html):
        if html:
            soup = BeautifulSoup(html, 'html.parser')
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

                    #write_file('data/test.json', script_text)
                    json_result = json.loads(script_text)
                
                    return json_result
        else:
            return None

    def get_tickets_from_json(self, data):
        tickets = []

        componentData = data['componentData']
        resultsList = componentData['searchResultList']
        for result in resultsList:
            trains = result['trains']
            for train in trains:
                
                run = train['params']['run']
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
                        ticket.depart_datetime = datetime.strptime( depart_date_str, '%Y-%m-%d %H:%M:%S' )
                        arrival_date_str = trip['arrivalDate'] + ' ' + trip['arrivalTime']
                        ticket.arrival_datetime = datetime.strptime( arrival_date_str, '%Y-%m-%d %H:%M:%S' )
                        ticket.travel_time = trip['travelTimeSeconds']

                        tickets.append(ticket) 
        return tickets

    def write_file(self, result_file, text):
        with open(result_file, 'w', encoding='utf-8') as output:
            output.write(text)

    # Deprecated
    def train_tickets_by_api(self, origin_city, destination_city, depart_date, return_date):

        trains_url = 'https://suggest.travelpayouts.com/search'

        params = {
            'service' : 'tutu_trains',
            'term' : origin_city,
            'term2' : destination_city,
            'callback' : 'plazcard'
        }

        headers = {"Accept-Language": "en-US,en;q=0.5"}
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
    #city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date = datetime.strptime('30.03.2020', '%d.%m.%Y')
    tutu_parser = Tutu()

 #   t = TutuInfo()
 #   print(t)

    #print(get_cities_codes(origin_city, destination_city))
    print(tutu_parser.get_tickets(origin_city, destination_city, depart_date))
