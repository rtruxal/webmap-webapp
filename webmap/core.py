import os
import re
import secrets
import socket
import requests


from webmap.local import TLD_LIST


#TODO: 2 things to make this application work.
# - stick a form in the html.
# - import the node/relationship objects & incorporate them

class ValidationError(BaseException):
    pass

def raise_validation_err(text=''):
    raise ValidationError(text)

class HandleInput:
    IP_REGEX = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    # operation_map = {
    #     'ip' : nslookup,
    #     'url' :
    # }

    @classmethod
    def _is_ip(cls, strang):
        """Checks if regex matches & if address numbers make sense."""
        is_ip = False
        if re.match(cls.IP_REGEX, strang):
            try:
                assert all([(int(i) <= 255) for i in strang.split('.')])
                is_ip = True
            except AssertionError:
                pass
        return True if is_ip else False

    @classmethod
    def _is_url(cls, strang):
        """Takes a big list of TLDs and compares the end of the user input to them.
        Finds the longest matching TLD.
        If there is a match, return True."""
        res = ''
        for tld in TLD_LIST:
            if strang.strip('/').endswith(tld) and len(tld) > len(res):
                res = tld
        return True if not res == '' else False

    @classmethod
    def url_or_ip(cls, strang):
        """I wish python had switch statements."""
        if cls._is_ip(strang):
            return 'ip'
        elif cls._is_url(strang):
            return 'url'
        else:
            return None

    @classmethod
    def handle(cls, strang):
        """eventually this will do more than return url_or_up()"""
        input_type = cls.url_or_ip(strang)
        return input_type


class Resolve:
    HYPERTEXT_PREFIX_STRIPPER = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
    
    @classmethod
    def get_simple_domainname(cls, url_string):
            """Uses regex grouping substitution."""    
            simple_dn = re.sub(cls.HYPERTEXT_PREFIX_STRIPPER, r'\3', url_string)
            return simple_dn
    @staticmethod
    def nslookup(url):
        return (i[-1][0] for i in socket.getaddrinfo(url, 80))

    @staticmethod
    def nslookups(urls):
        return dict((k, list(set(i[-1][0] for i in socket.getaddrinfo(k, 80)))) for k in urls)
    
    @classmethod
    def execute(cls, url_or_urls):
        """returns a dictionary of domain to IP addr mappings."""
        if isinstance(url_or_urls, str):
            domain = cls.get_simple_domainname(url_or_urls)
            ips = list(set(cls.nslookup(domain)))
            return {domain : ips}
        # if iterable and any type but str, we assume collection.
        elif hasattr(url_or_urls, '__iter__'): 
            domains = [cls.get_simple_domainname(i) for i in url_or_urls]
            return cls.nslookups(domains)



class Bing:
    ENDPOINT = 'https://api.cognitive.microsoft.com/bing/v7.0/search?'
    HEADERS = {
    'Ocp-Apim-Subscription-Key' : os.environ.get('BING_KEY', None),
    'X-MSEdge-ClientID' : '{}'.format(secrets.token_urlsafe(8)), #<<< Optional.
    }
    PARAMS = {
    "q" : '+ip:{}',
    "mkt" : "en-US",
    "offset" : "0",
    "count" : "50",
    }

    @classmethod
    def _call_api(cls, ip_addr, subscription_key=None):
        """inject an IP address into a query and call bing"""
        sesh = requests.Session()
        sesh.headers, sesh.params = cls.HEADERS.copy(), cls.PARAMS
        sesh.params['q'] = sesh.params['q'].format(ip_addr)
        if subscription_key:
            sesh.headers.update({'Ocp-Apim-Subscription-Key' : subscription_key})
        return sesh.get(cls.ENDPOINT)

    @staticmethod
    def _get_links_from_resp(response):
        """extracts a list of URLs from a bing JSON response"""
        try:
            return [i['url'] for i in response.json()['webPages']['value']]
        except Exception as err:
            #TODO: fix this.
            with open('fail.log', 'a', encoding='utf-8') as errfile:
                errfile.write('\n')
                errfile.write(str(err))
            return []

    @classmethod
    def execute(cls, ip_addr, subscription_key=None):
        """Only one url at a time because this part costs money.
        Executes previous 2 functions."""
        if not subscription_key:
            #TODO: create methods to limit call frequency.
            pass
        return {ip_addr : list(set(cls._get_links_from_resp(cls._call_api(ip_addr, subscription_key))))}
        
        
        # sites = dict()
        # for addr in ip_addrs:
        #     sites[addr] = set(cls._get_links_from_resp(cls._call_api(addr)))
        # return sites



OPERATION_MAP = {
    'ip' : Bing.execute,
    'url' : Resolve.execute,
    None: raise_validation_err
}


