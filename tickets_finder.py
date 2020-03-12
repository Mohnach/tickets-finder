
from aviasales import avia_tickets_by_city_cheap
from tutu import train_tickets_by_city

def get_tickets(origin_city, destination_city, departure_date, return_date, sources):
    tickets = []
    if 'aviasales' in sources:
        tickets += avia_tickets_by_city_cheap(origin_city, destination_city, departure_date, return_date)
    if 'tutu' in sources:
        tickets += train_tickets_by_city(origin_city, destination_city, departure_date)
    return tickets

if __name__ == "__main__":
    #city = input('Введите город: ')
    origin_city = 'Москва'
    destination_city = 'Сочи'
    depart_date='2020-03-21'
    return_date='2020-03-22'

    print(get_tickets(origin_city, destination_city, depart_date, return_date, ['aviasales', 'tutu']))
