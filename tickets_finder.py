from tutu import Tutu
from aviasales import Aviasales
from datetime import datetime

def get_tickets(origin_city, destination_city, departure_date, return_date, sources):
    tickets = []
    if 'aviasales' in sources:
        aviasales_provider = Aviasales()
        tickets += aviasales_provider.get_return_tickets(origin_city, destination_city, departure_date, return_date)
    if 'tutu' in sources:
        tutu_provider = Tutu()
        tickets += tutu_provider.get_tickets(origin_city, destination_city, departure_date)
    return tickets

if __name__ == "__main__":
    #city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date = datetime.strptime('2020-04-21', '%Y-%m-%d')
    return_date = datetime.strptime('2020-04-22', '%Y-%m-%d')

    print(get_tickets(origin_city, destination_city, depart_date, return_date, ['aviasales', 'tutu']))
