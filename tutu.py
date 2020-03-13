import requests
import secrets
import csv
from requests_html import HTMLSession


def get_html(url, params=0, header=0):
    try:
        result = requests.get(url, params=params, headers=header)
        result.raise_for_status()
        return result.content
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
        finded_tickets = get_tickets(route, depart_date)
        if finded_tickets is not None:
            tickets += finded_tickets
    return tickets

def get_tickets(route, depart_date):

    origin_city_id = route.get('departure_station_id')
    destination_city_id = route.get('arrival_station_id')

    trains_url = 'https://www.tutu.ru/poezda/rasp_d.php'

    params = {
        'nnst1' : origin_city_id,
        'nnst2' : destination_city_id,
        'date' : depart_date
    }

    session = HTMLSession()
    r = session.get(trains_url, params=params)
    r.html.render()

    path_to_train_cards = "//div[contains(@class, 'b-train__schedule__train_card')]"
    train_number_path = ".//span[contains(@class, 'train_number_link')]"
    route_time_path = ".//span[contains(@class, 't-txt-s route_time')]"
    card_seats_path = ".//div/div/div/a/div/div/span[contains(@class, 'car-type') or contains(@class, 'car_type')]"
    price_path = ".//div/div/div/a/div/div/span[contains(@class, 't-ttl_third') or contains(@class, 'seats_price t-txt-s')]"
    tickets = []
    for train_card_element in r.html.xpath(path_to_train_cards):
        ticket = {}
        card_seats = train_card_element.xpath(card_seats_path)
        if len(card_seats) > 0:
            i = 0
            for card_seat in card_seats:
                print(card_seat.text)
                ticket['type'] = 'train'
                ticket['seat'] = card_seat.text
                price = train_card_element.xpath(price_path)[i]
                if price is not None:
                    print(price.text)
                    price_text = price.text.replace('\xa0', '')
                    price_text = price_text.replace('₽', '')
                    ticket['price'] = price_text
                else:
                    print(0)
                    ticket['price'] = None
                i += 1

                train_number = train_card_element.xpath(train_number_path, first=True)
                print(train_number.text)
                ticket['number'] = train_number.text
                route_time = train_card_element.xpath(route_time_path, first=True)
                print(route_time.text)
                ticket['time'] = route_time.text.replace('\xa0', '')

                ticket['origin'] = route.get('departure_station_name')
                ticket['destination'] = route.get('departure_station_name')

                tickets.append(ticket)   
   # print(tickets)
    return tickets
    
def write_file(result_file, text):
    with open(result_file, 'w', encoding='utf-8') as output:
        output.write(text)

def train_tickets_by_city_api(origin_city, destination_city, depart_date, return_date):

    origin_city = '2000000'
    destination_city = '2064130'
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
    depart_date='24.03.2020'
    return_date='2020.03.22'
    
    #print(get_cities_codes(origin_city, destination_city))
    print(train_tickets_by_city(origin_city, destination_city, depart_date))
