import requests
import secrets
import csv
import json
from bs4 import BeautifulSoup

def get_html(url, params=None, header=None):
    try:
        result = requests.get(url, params=params, headers=header)
        result.raise_for_status()
        return result.text
    except(requests.RequestException, ValueError):
        print('Сетевая ошибка')
        return False

def get_cities_codes(origin_city, destination_city):
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

def train_tickets_by_city(origin_city, destination_city, depart_date):

    cities_codes = get_cities_codes(origin_city, destination_city)

    tickets = []
    for route in cities_codes:
        print(route)
        #### debug
        #found_tickets = get_route('')
        found_tickets = get_tickets(route, depart_date)
        if found_tickets is not None:
            tickets += found_tickets
    return tickets

def get_routes_in_json(html):
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

def get_route(data):
    tickets = []

    #data = None
    #with open("data/test.json", "r") as read_file:
    #    data = json.load(read_file)

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
                    ticket = {}
                    ticket['seat_type'] = params['name']
                    ticket['seats_count'] = params['seatsCount']
                    ticket['price'] = params['price']['RUB']
                    ticket['top_seats_price'] = params['topSeatsPrice']
                    ticket['top_seats_count'] = params['topSeatsCount']
                    ticket['bottom_seats_price'] = params['bottomSeatsPrice']
                    ticket['bottom_seats_count'] = params['bottomSeatsCount']
                    
                    ticket['url'] = seats['buyAbsUrl']

                    ticket['number'] = trip['trainNumber']
                    ticket['origin'] = trip['departureStation']
                    ticket['destination'] = trip['arrivalStation']
                    ticket['departure_at'] = trip['departureDate'] + ' ' + trip['departureTime']
                    ticket['return_at'] = trip['arrivalDate'] + ' ' + trip['arrivalTime']
                    ticket['travel_time'] = trip['travelTimeSeconds']


                tickets.append(ticket) 
    return tickets

def get_tickets(route, depart_date):

    origin_city_id = route['departure_station_id']
    destination_city_id = route['arrival_station_id']

    trains_url = 'https://www.tutu.ru/poezda/rasp_d.php'

    params = {
        'nnst1' : origin_city_id,
        'nnst2' : destination_city_id,
        'date' : depart_date
    }

    headers = {"Accept-Language": "en-US,en;q=0.5"}
    html = get_html(trains_url, params = params, header = headers)
    #write_file('data/new_test.html', html)

    routes_in_json = get_routes_in_json(html)
    tickets = get_route(routes_in_json)

    return tickets
    
def write_file(result_file, text):
    with open(result_file, 'w', encoding='utf-8') as output:
        output.write(text)


def train_tickets_by_city_api(origin_city, destination_city, depart_date, return_date):

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

if __name__ == "__main__":
    #city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date='28.03.2020'
    
    #print(get_cities_codes(origin_city, destination_city))
    print(train_tickets_by_city(origin_city, destination_city, depart_date))
