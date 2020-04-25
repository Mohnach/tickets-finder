from datetime import datetime
from .tutu import Tutu
from .aviasales import Aviasales
from .tickets_finder import prepare_db_session, get_return_tickets_for_all_directions, get_tickets_for_all_directions


origin_city = 'Москва'
depart_date = datetime.strptime('2020-05-02', '%Y-%m-%d')
return_date = datetime.strptime('2020-05-03', '%Y-%m-%d')

session = prepare_db_session()

providers_list = []

aviasales_provider = Aviasales(db_session=session)
providers_list.append(aviasales_provider)

tutu_provider = Tutu(db_session=session)
providers_list.append(tutu_provider)

print('One way tickets')
print(get_tickets_for_all_directions(origin_city, depart_date, providers_list))

print('Return tickets')
print(get_return_tickets_for_all_directions(origin_city, depart_date, return_date, providers_list))
