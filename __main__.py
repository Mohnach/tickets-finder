from datetime import datetime
from .tutu import Tutu
from .aviasales import Aviasales
from .tickets_finder import prepare_db_session, get_return_tickets, get_tickets

origin_city = 'Москва'
destination_city = 'Сочи'
depart_date = datetime.strptime('2020-04-25', '%Y-%m-%d')
return_date = datetime.strptime('2020-04-27', '%Y-%m-%d')

session = prepare_db_session()

providers_list = []

aviasales_provider = Aviasales(db_session=session)
providers_list.append(aviasales_provider)

aviasales_provider.load_airports_data()
airports = aviasales_provider.find_airports_for_city('Moscow')
print(airports)

aviasales_provider.load_flights_routes()

tickets = []
for airport in airports:
    routes_list = aviasales_provider.find_routes_for_airport(airport)
    #routes_list = routes_list[1:10]
    #print(routes_list)

    for route in routes_list:
         #print('from {} to {}'.format(airport, route['Destination airport']))
         tickets += aviasales_provider.get_return_tickets(airport, route['Destination airport'],
               depart_date, return_date, convert_to_iata=False)
print(tickets)

#tutu_provider = Tutu(db_session=session)
#providers_list.append(tutu_provider)

#print('One way tickets')
#print(get_tickets(origin_city, destination_city, depart_date, providers_list))

#print('Return tickets')
#print(get_return_tickets(origin_city, destination_city, depart_date, return_date, providers_list))
