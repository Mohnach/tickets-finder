# Tickets Finder

This project is backend for [WeekendTrips service](https://myweekendtrip.ru/).

You can find frontend [here](https://github.com/Mesoru13/WeekendTrips)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Firstly install python 3.7 or newer

### Installing

1. clone this repo
2. prepare virtual environment

``python3 -m venv env
source ./env/bin/activate``

3. install all reqs

``pip install -r ./requirements.txt``

4. prepare databases

``alembic upgrade head``

### Launching

Just launch the module:

``python -m tickets_finder``

This sample should collect tickets using 1 tickets provider: tutu.ru

Using aviasales provider requires developer's token from [travel payouts service](https://travelpayouts.com). You can send it as env argument:

``TRAVEL_PAYOUTS_TOKEN='<token>' python -m tickets_finder``

You can search tickets for given direction:

```
origin_city = 'Москва'
destination_city = 'Сочи'
depart_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
return_date = datetime.strptime('2020-01-02', '%Y-%m-%d')

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
```

Or You can search tickets to all directions from one city:

```
origin_city = 'Москва'
depart_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
return_date = datetime.strptime('2020-01-02', '%Y-%m-%d')

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
```
