from datetime import datetime
from .RouteInfo import RouteInfo
from .cities import Cities
from typing import List
import random
import requests
from bs4 import BeautifulSoup


class TicketProvider:
    engine = None
    session = None

    def __init__(self, db_session=None):
        self.session = db_session

    def get_tickets(self, origin: str, destination: str, depart_date: datetime) -> List[RouteInfo]:
        raise NotImplementedError()

    def get_return_tickets(self, origin: str, destination: str, depart_date: datetime,
                           return_date: datetime) -> List[RouteInfo]:
        raise NotImplementedError()

    def get_tickets_for_all_directions(self, origin_city: str, depart_date: datetime,
                                       cities_info: Cities) -> List[RouteInfo]:
        raise NotImplementedError()

    def get_return_tickets_for_all_directions(self, origin_city: str, depart_date: datetime,
                                              return_date: datetime, cities_info: Cities) -> List[RouteInfo]:
        raise NotImplementedError()

    def find_routes_for_depart_point(self, depart_point):
        routes = []
        if depart_point in self.routes_dict:
            try:
                for route_for_place in self.routes_dict[depart_point]:
                    routes.append(route_for_place)
            except (ValueError, KeyError) as e:
                print(f'error in routes_dict. {repr(e)}')
        return routes

    def get_random_user_agent(self):
        user_agent_list = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            # Firefox
            'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
        ]

        return random.choice(user_agent_list)

    def init_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url, timeout=5)
        proxies = list()
        soup = BeautifulSoup(response.text, 'html.parser')
        proxies_list = soup.find('tbody').findAll('tr')
        for proxy in proxies_list:
            # https only
            if 'yes' in proxy.findAll('td')[6].text:
                # print(proxy.findAll('td')[0].text + ':' + proxy.findAll('td')[1].text)
                proxy_string = proxy.findAll('td')[0].text + ':' + proxy.findAll('td')[1].text
                proxies.append(proxy_string)
        self.proxies = proxies

    def get_random_proxy(self):
        proxy = dict()
        proxy['https'] = random.choice(self.proxies)
        return proxy


if __name__ == "__main__":
    test = TicketProvider()
    test.init_proxies()
    print(test.get_random_proxy())
    print(test.get_random_user_agent())
