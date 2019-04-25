import os
import re
import secrets
import socket
import requests
from typing import Generator, Dict, List, Set

from webmap.local import TLD_LIST


def get_simple_domainname(url_string) -> str:
        """Uses regex grouping substitution."""
        hypertext_prefix_stripper = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
        simple_dn = re.sub(hypertext_prefix_stripper, r'\3', url_string)
        return simple_dn

def nslookup(url) -> Generator[str]:
    return (i[-1][0] for i in socket.getaddrinfo(url, 80))


def nslookups(urls) -> Dict[str, Generator[str]]:
    return dict((k, (i[-1][0] for i in socket.getaddrinfo(k, 80))) for k in urls)

class HandleInput:
    ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    # operation_map = {
    #     'ip' : nslookup,
    #     'url' :
    # }

    @classmethod
    def _is_ip(cls, strang) -> bool:
        """Checks if regex matches & if address numbers make sense."""
        is_ip = False
        if re.match(cls.ip_regex, strang):
            try:
                assert all([(int(i) <= 255) for i in strang.split('.')])
                is_ip = True
            except AssertionError:
                pass
        return True if is_ip else False

    @classmethod
    def _is_url(cls, strang) -> bool:
        """Takes a big list of TLDs and compares the end of the user input to them.
        Finds the longest matching TLD.
        If there is a match, return True."""
        res = ''
        for tld in TLD_LIST:
            if strang.strip('/').endswith(tld) and len(tld) > len(res):
                res = tld
        return True if not res == '' else False

    @classmethod
    def url_or_ip(cls, strang) -> (str, None):
        """I wish python had switch statements."""
        if cls._is_ip(strang):
            return 'ip'
        elif cls._is_url(strang):
            return 'url'
        else:
            return None

    @classmethod
    def handle(cls, strang) -> (str, None):
        """eventually this will do more than return url_or_up()"""
        input_type = cls.url_or_ip(strang)
        return input_type


class ValidationError:
    pass


class Bing:
    ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0/search?'
    HEADERS = {
    'Ocp-Apim-Subscription-Key' : os.environ('BING_KEY', None),
    'X-MSEdge-ClientID' : '{}'.format(secrets.token_urlsafe(8)), #<<< Optional.
    }
    PARAMS = {
    "q" : '+ip:{}',
    "mkt" : "en-US",
    "offset" : "0",
    "count" : "50",
    }

    @classmethod
    def _call_api(cls, ip_addr) -> requests.Response:
        """inject an IP address into a query and call bing"""
        sesh = requests.Session()
        sesh.headers, sesh.params = cls.HEADERS, cls.PARAMS
        sesh.params['q'] = sesh.params['q'].format(ip_addr)
        return sesh.get(cls.ENDPOINT)

    @staticmethod
    def _get_links_from_resp(response) -> List[str]:
        """extracts a list of URLs from a bing JSON response"""
        try:
            return [i['url'] for i in response.json()['webPages']['value']]
        except Exception as err:
            with open('fail.log', 'a', encoding='utf-8') as errfile:
                errfile.write('\n')
                errfile.write(str(err))
            return []

    @classmethod
    def get_websites(cls, ip_addrs) -> Dict[str, Set[str]]:
        """executes previous 2 functions."""
        sites = dict()
        for addr in ip_addrs:
            sites[addr] = set(cls._get_links_from_resp(cls._call_api(addr)))
        return sites


