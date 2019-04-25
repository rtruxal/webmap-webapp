# import pyquery
from flask import Blueprint, render_template, request
from .core import HandleInput, Bing, nslookups, get_simple_domainname
bp = Blueprint('/webmap', __name__, 'webmap')




@bp.route('/', methods=('GET', 'POST'))
def webmap():
    if request.method == 'POST':
        #TODO: Create either a click-interface, or a form-interface to allow users to interact with the graph visualization. 
        #TODO: By default, use my Free-tier Bing API key & limit queries based on user-session & absolute frequency.
        #TODO: Provide a form through which a user can specify their own API key & remove afformentioned query limits.
        pass
    return render_template('viz.html')


if __name__ == "__main__":
    # x = [
    #     'https://google.com',
    #     '123.0.0.1',
    #     'https://google.com/',
    #     '999.999.999.999',
    # ]
    # for i in x:
    #     print(HandleInput.handle(i))
    pass