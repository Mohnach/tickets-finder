import os


basedir = os.path.abspath(os.path.dirname(__file__))
 
DB_LOCATION = os.path.join(basedir, 'data/tickets_cache.db')
# https://support.travelpayouts.com/hc/ru/articles/115001440551-%D0%94%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5-%D0%BE%D1%82-Tutu-ru
CSV_ROUTES_LOCATION = os.path.join(basedir, 'data/tutu_routes.csv')
# https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
FLIGHTS_ROUTES_LOCATION = os.path.join(basedir, 'data/openflights_routes.dat')
# https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat
AIRPORTS_LOCATION = os.path.join(basedir, 'data/openflights_airports.dat')
# http://api.travelpayouts.com/data/ru/cities.json
CITIES_LOCATION = os.path.join(basedir, 'data/cities.json')
# http://osm.sbin.ru/esr/osm2esr.csv
STATIONS_LOCATION = os.path.join(basedir, 'data/osm2esr.csv')
# https://en.wikipedia.org/wiki/List_of_cities_by_international_visitors
POPULAR_CITIES_LOCATION = os.path.join(basedir, 'data/popular_cities.csv')
# http://towntravel.ru/interesnie-fakti-o-gorodah-rossyi/samye-populyarnye-goroda-rossii-top-50-za-2018-2019-god.html
RUSSIAN_POPULAR_CITIES_LOCATION = os.path.join(basedir, 'data/russian_cities_rating.csv')
