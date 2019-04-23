import socket
import pyquery
import re
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .local import TLDs

bp = Blueprint('/webmap', __name__, 'webmap')



@bp.route('/', methods=('GET', 'POST'))
def webmap():
    if request.method == 'POST':
        pass
    return render_template('webmapp/index.html')


def get_simple_domainname(url_string) -> str:
    """Uses regex grouping substitution."""
    hypertext_prefix_stripper = r'(^https?:\/\/)(www\.)?([^\/]*)(.*)$'
    simple_dn = re.sub(hypertext_prefix_stripper, r'\3', url_string)
    return simple_dn

class HandleInput:
    ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    
    # operation_map = {
    #     'ip' : nslookup,
    #     'url' : 
    # }
    
    @classmethod
    def _is_ip(cls, strang):
        is_ip = False
        if re.match(cls.ip_regex, strang):
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
        for tld in TLDs:
            if strang.strip('/').endswith(tld) and len(tld) > len(res):
                res = tld
        return True if not res == '' else False

    @classmethod
    def url_or_ip(cls, strang):
        if cls._is_ip(strang):
            return 'ip'
        elif cls._is_url(strang):
            return 'url'
        else:
            return None
    
    @classmethod
    def handle(cls, strang):
        input_type = cls.url_or_ip(strang)
        return input_type



class ValidationError:
    pass


def nslookup(url):
    return (i[-1][0] for i in socket.getaddrinfo(url, 80))

def nslookups(urls):
    return {(k, (i[-1][0] for i in socket.getaddrinfo(k, 80))) for k in urls}


if __name__ == "__main__":
    x = [
        'https://google.com',
        '123.0.0.1',
        'https://google.com/',
        '999.999.999.999',
    ]
    for i in x:
        print(HandleInput.handle(i))
