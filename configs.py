import os


basedir = os.path.abspath(os.path.dirname(__file__))

DB_LOCATION = os.path.join(basedir, 'data/tickets_cache.db')
CSV_ROUTES_LOCATION = os.path.join(basedir, 'data/tutu_routes.csv')
FLIGHTS_ROUTES_LOCATION = os.path.join(basedir, 'data/openflights_routes.dat')
AIRPORTS_LOCATION = os.path.join(basedir, 'data/openflights_airports.dat')
CITIES_LOCATION = os.path.join(basedir, 'data/cities.json')
STATIONS_LOCATION = os.path.join(basedir, 'data/osm2esr.csv')
