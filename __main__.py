from datetime import datetime
from .tutu import Tutu
from .aviasales import Aviasales
from .tickets_finder import prepare_db_session, get_return_tickets, get_tickets

origin_city = 'Москва'
destination_city = 'Сочи'
depart_date = datetime.strptime('2020-04-21', '%Y-%m-%d')
return_date = datetime.strptime('2020-04-22', '%Y-%m-%d')

session = prepare_db_session()

providers_list = []

aviasales_provider = Aviasales(db_session=session)
providers_list.append(aviasales_provider)

tutu_provider = Tutu(db_session=session)
providers_list.append(tutu_provider)

print('One way tickets')
print(get_tickets(origin_city, destination_city, depart_date, providers_list))

print('Return tickets')
print(get_return_tickets(origin_city, destination_city, depart_date, return_date, providers_list))
