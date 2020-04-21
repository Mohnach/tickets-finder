from datetime import datetime
from .tutu import Tutu
from .aviasales import Aviasales
from .cities import Cities
from .tickets_finder import prepare_db_session, get_return_tickets, get_tickets


origin_city = 'Москва'
destination_city = 'Сочи'
depart_date = datetime.strptime('2020-04-25', '%Y-%m-%d')
return_date = datetime.strptime('2020-04-27', '%Y-%m-%d')

session = prepare_db_session()

providers_list = []

aviasales_provider = Aviasales(db_session=session)
providers_list.append(aviasales_provider)

# содержит инфу о городах: переводы на разные языки, iata code, координаты
cities_info = Cities()
eng_name = cities_info.translate_from_russian_to_english(origin_city)

# поиск аэропортов для заданного города
airports = cities_info.find_airports_for_city(eng_name)
print(airports)

tickets = []
for airport in airports:
    # поиск всех возможных направлений для заданного аэропорта
    routes_list = aviasales_provider.find_routes_for_depart_point(airport)
    print('Число маршрутов из аэропорта {}: {}'.format(airport, len(routes_list)))

#     for route in routes_list:
#         # print('from {} to {}'.format(airport, route['Destination airport']))

#         # Если дистанция между аэропортами больше 5000км, то пропускаем это направление
#         distance = cities_info.calculate_distance(airport, route['Destination airport'])
#         if distance > 5000:
#             continue

#         tickets += aviasales_provider.get_return_tickets(airport,
#                                                          route['Destination airport'],
#                                                          depart_date,
#                                                          return_date,
#                                                          convert_to_iata=False)
# print(tickets)

tutu_provider = Tutu(db_session=session)
providers_list.append(tutu_provider)

# поиск аэропортов для заданного города
stations = tutu_provider.find_stations(origin_city)
print(stations)

tickets = []
for station in stations:
    # поиск всех возможных направлений для заданного аэропорта
    routes_list = tutu_provider.find_routes_for_depart_point(station)
#    routes_list = routes_list[1:5]
    print('Число маршрутов со станции {}: {}'.format(station, len(routes_list)))

    for route in routes_list:
       # print('from {} to {}'.format(station, route['arrival_station_name']))
       # print(cities_info.get_coordinates_from_stations_base(route['departure_station_name']))

        # Если дистанция между аэропортами больше 5000км, то пропускаем это направление
        distance = cities_info.calculate_distance(
            cities_info.get_coordinates_from_stations_base(route['departure_station_name']),
            cities_info.get_coordinates_from_stations_base(route['arrival_station_name']))
        if distance > 1000:
           # print('Не поедем - Далеко: {}km'.format(distance))
            continue

        tickets += tutu_provider.get_tickets(route['departure_station_name'],
                                             route['arrival_station_name'],
                                             depart_date)
print(tickets)

#print('One way tickets')
#print(get_tickets(origin_city, destination_city, depart_date, providers_list))

#print('Return tickets')
#print(get_return_tickets(origin_city, destination_city, depart_date, return_date, providers_list))
