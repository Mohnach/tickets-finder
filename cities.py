import json
import csv
import geopy.distance
from . import configs


class Cities:
    cities = None
    airports = None
    airports_dict = None
    stations = None
    russian_popular_cities = None
    international_popular_cities = None

    def __init__(self):
        self.load_cities_info()
        self.load_airports_data()
        self.load_esr_data()
        self.load_russian_popular_cities()
        self.load_int_popular_cities()

    def load_cities_info(self):
        cities_file = configs.CITIES_LOCATION
        with open(cities_file, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)
        self.cities = data

    def translate_from_russian_to_english(self, russian_name):
        for row in self.cities:
            if row['name'] == russian_name:
                return row['name_translations'].get('en')

    def translate_from_iata_to_english(self, iata):
        for row in self.cities:
            if row['code'] == iata:
                return row['name_translations']['en']

    def get_iata(self, eng_name=None, rus_name=None):
        if eng_name is not None:
            for row in self.cities:
                if row['name_translations']['en'] == eng_name:
                    return row['code']
        if rus_name is not None:
            for row in self.cities:
                if row['name'] and rus_name in row['name']:
                    return row['code']

    def get_coordinates_from_cities_base(self, iata=None):
        for row in self.cities:
            if row['code'] == iata:
                return row['coordinates']

    def get_coordinates_from_airports_base(self, iata=None):
        for row in self.airports:
            if row['IATA'] == iata:
                coords = {}
                coords['lat'] = float(row['Latitude'])
                coords['lon'] = float(row['Longitude'])
                return coords

    def get_coordinates_from_stations_base(self, name=''):
        for row in self.stations:
            if row['name'] == name or row['alt_name'] == name or row['old_name'] == name or row['official_name'] == name:
                coords = {}
                coords['lat'] = float(row['lat'])
                coords['lon'] = float(row['lon'])
                return coords

    def get_airport_coordinates(self, iata):
        coords = self.get_coordinates_from_airports_base(iata)
        if coords is None:
            coords = self.get_coordinates_from_cities_base(iata)
        return coords

    def calculate_distance(self, origin_coords, destination_coords):
        if not origin_coords or not destination_coords:
            return 9999999

        coords_1 = (origin_coords['lat'], origin_coords['lon'])
        coords_2 = (destination_coords['lat'], destination_coords['lon'])

        distance = geopy.distance.distance(coords_1, coords_2).km
        return distance

    def load_airports_data(self):
        self.airports = []
        self.airports_dict = {}
        try:
            dat_file = configs.AIRPORTS_LOCATION
            with open(dat_file, 'r', encoding='utf-8') as f:
                fields = ['Airport ID',
                          'Name',
                          'City',
                          'Country',
                          'IATA',
                          'ICAO',
                          'Latitude',
                          'Longitude',
                          'Altitude',
                          'Timezone',
                          'DST',
                          'tz',
                          'Type',
                          'Source']
                reader = csv.DictReader(f, fields, delimiter=',')
                for row in reader:
                    self.airports.append(row)
                    if row['IATA'] == '\\N':
                        continue
                    if row['City'] not in self.airports_dict:
                        self.airports_dict[row['City']] = []
                    self.airports_dict[row['City']].append(row)
        except OSError as e:
            print(f'не удалось открыть csv файл. {repr(e)}')
        except (ValueError, KeyError) as e:
            print(e.text)
            self.airports = []
        return self.airports

    def find_airports_for_city(self, city):
        city = city.replace('Saint', 'St.')
        airports = []
        if city in self.airports_dict:
            try:
                for airport_info in self.airports_dict[city]:
                    airports.append(airport_info['IATA'])
            except (ValueError, KeyError) as e:
                print(f'error in airports_dict. {repr(e)}')
        return airports

    def load_esr_data(self):
        self.stations = []
        rows_with_names = ["name", "alt_name", "old_name", "official_name"]
        try:
            csv_file = configs.STATIONS_LOCATION
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    if row['railway'] != 'station':
                        continue
                    for name in rows_with_names:
                        if '-Пассажирская-' in row[name]:
                            row[name] = row[name].replace('-Пассажирская-', ' ')
                        if '-' in row[name]:
                            row[name] = row[name].replace('-', ' ')
                        if '-Пассажирская' in row[name]:
                            row[name] = row[name].replace('-Пассажирская', '')
                        if '-Пассажирский' in row[name]:
                            row[name] = row[name].replace('-Пассажирский', '')
                        if 'I' in row[name]:
                            row[name] = row[name].replace('I', '1')
                        if 'II' in row[name]:
                            row[name] = row[name].replace('II', '2')
                        if 'III' in row[name]:
                            row[name] = row[name].replace('III', '3')
                        row[name] = row[name].strip()

                    self.stations.append(row)
        except OSError as e:
            print(f'не удалось открыть csv файл. {repr(e)}')
        except (ValueError, KeyError) as e:
            print(e.text)
            self.stations = []
        return self.stations

    def load_russian_popular_cities(self):
        self.russian_popular_cities = []
        try:
            csv_file = configs.RUSSIAN_POPULAR_CITIES_LOCATION
            with open(csv_file, 'r', encoding='utf-8') as f:
                fields = [
                    'number',
                    'name',
                    'rating'
                ]
                reader = csv.DictReader(f, fields, delimiter=';')
                for row in reader:
                    row['name'] = row['name'].replace('-', ' ')
                    self.russian_popular_cities.append(row['name'].strip())
        except OSError as e:
            print(f'не удалось открыть csv файл. {repr(e)}')
        except (ValueError, KeyError) as e:
            print(e.text)
            self.russian_popular_cities = []
        return self.russian_popular_cities

    def load_int_popular_cities(self):
        self.international_popular_cities = []
        try:
            csv_file = configs.POPULAR_CITIES_LOCATION
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    self.international_popular_cities.append(row['City'].strip())
        except OSError as e:
            print(f'не удалось открыть csv файл. {repr(e)}')
        except (ValueError, KeyError) as e:
            print(e.text)
            self.international_popular_cities = []
        return self.international_popular_cities


if __name__ == "__main__":
    test = Cities()
    rus_name = 'Тверь'
    name = test.translate_from_russian_to_english(rus_name)
    print(test.get_iata(rus_name=rus_name))
    print(test.get_iata(eng_name=name))
