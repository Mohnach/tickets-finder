import requests
import secrets

def get_iata_from_dict(iata_dict, target):
    if target in iata_dict:
        if 'iata' in iata_dict[target]:
            return iata_dict[target]['iata']
    raise ValueError(f'IATA of {target} not found')

def convert_city_name_to_iata(origin_name, dest_name):
    
    search = 'Из ' + origin_name + ' в ' + dest_name

    iata_url = 'https://www.travelpayouts.com/widgets_suggest_params'
    params = {
        'q' : search
    }
    
    try:
        result = requests.get(iata_url, params=params)
        result.raise_for_status()
        json_result = result.json()

        iatas = {}
        iatas['origin'] = get_iata_from_dict(json_result, 'origin')
        iatas['destination'] = get_iata_from_dict(json_result, 'destination')

        return iatas

    except (requests.RequestException, ValueError):
        print('Cities name conversion failed')
        raise ValueError


def avia_tickets_by_city(origin_city, destination_city, depart_date, return_date):

    iatas = convert_city_name_to_iata(origin_city, destination_city)

    try:
        destination_iata = iatas.get('destination')
        origin_iata = iatas.get('origin')
    except ValueError:
        print('Invalid city name')
        return None
    
    tickets_url = 'http://api.travelpayouts.com/v2/prices/week-matrix'
    params = {
        'currency' : 'rub',
        'origin' : origin_iata,
        'destination' : destination_iata,
        'show_to_affiliates' : 'false',
        'depart_date' : depart_date,
        'return_date' : return_date,
        'token' : secrets.travelpayouts_token
    }
    try:
        result = requests.get(tickets_url, params=params)
        result.raise_for_status()
        json_result = result.json()

        if 'success' in json_result:
            if json_result['success'] == True:
                return json_result.get('data')
    except (requests.RequestException, ValueError):
        print('')
    return None


def avia_tickets_by_city_cheap(origin_city, destination_city, depart_date, return_date):

    iatas = convert_city_name_to_iata(origin_city, destination_city)

    try:
        destination_iata = iatas.get('destination')
        origin_iata = iatas.get('origin')
    except ValueError:
        print('Invalid city name')
        return None
    
    tickets_url = 'http://api.travelpayouts.com/v1/prices/cheap'
    params = {
        'currency' : 'rub',
        'origin' : origin_iata,
        'destination' : destination_iata,
        'depart_date' : depart_date,
        'return_date' : return_date,
        'token' : secrets.travelpayouts_token
    }
    try:
        result = requests.get(tickets_url, params=params)
        result.raise_for_status()
        json_result = result.json()

        if 'success' in json_result:
            if json_result['success'] == True:
                return normalize_data(json_result.get('data'), destination_iata, origin_city, destination_city)
    except (requests.RequestException, ValueError):
        print('')
    return None

def normalize_data(data, destination_iata, origin_city, destination_city):
    tickets = []
    tickets_list = data.get(destination_iata)
    ticket = {}
    for ticket_key in tickets_list:
        ticket_value = tickets_list.get(ticket_key)
        ticket['type'] = 'plane'
        ticket['origin'] = origin_city
        ticket['destination'] = destination_city
        ticket['number'] = ticket_value.get('flight_number')
        ticket['airline'] = ticket_value.get('airline')
        ticket['price'] = ticket_value.get('price')
        ticket['departure_at'] = ticket_value.get('departure_at')
        ticket['return_at'] = ticket_value.get('return_at')

        tickets.append(ticket)

    return tickets

if __name__ == "__main__":
    #city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date='2020-03-21'
    return_date='2020-03-22'
    
    #print(avia_tickets_by_city(origin_city, destination_city, depart_date, return_date))
    print(avia_tickets_by_city_cheap(origin_city, destination_city, depart_date, return_date))
