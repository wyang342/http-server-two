# controller.py
from classes.router import Router
from classes.response import Response
import datetime


@Router.route('/')
def index():
    response = Response('index')
    return response


@Router.route('/time')
def time():
    response = Response('time', {'time': datetime.datetime.now()})
    return response
