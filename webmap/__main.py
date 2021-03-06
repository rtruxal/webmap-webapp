# import pyquery
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .core import HandleInput, OPERATION_MAP
from .graph.flask_interface_v2 import Dispatcher
from .util import ValidationError
bp = Blueprint('/webmap', __name__, 'webmap')


#TODO: Format dashboard HTML page layout.

@bp.route('/', methods=('GET', 'POST'))
def webmap():
    if request.method == 'POST':
        #TODO: Create either a click-interface, or a form-interface to allow users to interact with the graph visualization. 
        #TODO: By default, use my Free-tier Bing API key & limit queries based on user-session & absolute frequency.
        #TODO: Provide a form through which a user can specify their own API key & remove afformentioned query limits.
        try:
            user_input = request.form['domainOrIP']
            input_type = HandleInput.url_or_ip(user_input)
            new_data = OPERATION_MAP[input_type](user_input)
            if new_data:
                #TODO: logging and checks.
                Dispatcher.submit_data(input_type, new_data)
                return render_template('viz.html', new_data=new_data, input_type=input_type)
        except ValidationError:
            flash('Input validation failed. Please enter a public url or ip address.')
            return render_template('viz.html')
        # except:
        #     flash('Your input was successfully validated, but something else went wrong. Please try again.')
        #     return render_template('viz.html')

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