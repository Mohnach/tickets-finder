import json
import csv
import os
import geopy.distance
from . import configs


class Cities:
    cities = None
    airports = None
    airports_dict = None

    def __init__(self):
        self.load_cities_info()
        self.load_airports_data()

    def load_cities_info(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        cities_file = os.path.join(basedir, configs.CITIES_LOCATION)
        with open(cities_file, "r") as read_file:
            data = json.load(read_file)
        self.cities = data

    def translate_from_russian_to_english(self, russian_name):
        for row in self.cities:
            if row['name'] == russian_name:
                eng_name = row['name_translations']['en']
        return eng_name

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

    def calculate_distance(self, origin_iata, destination_iata):
        origin_coords = self.get_coordinates_from_airports_base(origin_iata)
        if origin_coords is None:
            origin_coords = self.get_coordinates_from_cities_base(origin_iata)

        destination_coords = self.get_coordinates_from_airports_base(destination_iata)
        if destination_coords is None:
            destination_coords = self.get_coordinates_from_cities_base(destination_iata)

        coords_1 = (origin_coords['lat'], origin_coords['lon'])
        coords_2 = (destination_coords['lat'], destination_coords['lon'])

        distance = geopy.distance.distance(coords_1, coords_2).km
        return distance

    def load_airports_data(self):
        self.airports = []
        self.airports_dict = {}
        try:
            basedir = os.path.abspath(os.path.dirname(__file__))
            dat_file = os.path.join(basedir, configs.AIRPORTS_LOCATION)
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
        airports = []
        if city in self.airports_dict:
            try:
                for airport_info in self.airports_dict[city]:
                    airports.append(airport_info['IATA'])
            except (ValueError, KeyError) as e:
                print(f'error in airports_dict. {repr(e)}')
        return airports


if __name__ == "__main__":
    test = Cities()
    rus_name = 'Тверь'
    name = test.translate_from_russian_to_english(rus_name)
    print(test.get_iata(rus_name=rus_name))
    print(test.get_iata(eng_name=name))
