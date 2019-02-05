# HTTP Server Two

## Release 1 - Templates
Returning a hard-coded responses for every request isn't very useful, and generating HTML in Python is a bit of a chore. Fortunately, there's a Python library called Jinja2 that makes generating HTML much easier. Take a look at this introduction to [Jinja2](http://jinja.pocoo.org/docs/2.10/intro/) before continuing:

`Jinja` allows us to write `HTML` and run `Python` code in it before it gets rendered. Run `pip install Jinja2` in your terminal. 

We'll start off by creating a `templates` directory and then creating a `Jinja` template for our `/time` route: `templates/time.html`. Then we write some boilerplate `HTML` and add an `<h1>` tag to display our time using brackets: `{{ time }}` The two brackets are special tags to let `Jinja2` know we want it to run/interpolate some Python code into the final HTML string. 

```HTML
<!-- templates/time.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>What Time Is It?</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" media="screen" href="main.css" />
    <script src="main.js"></script>
</head>
<body>
    <h1>The time is now: {{ time }} </h1>
</body>
</html>
```

Ok, we have an HTML file. We need to pass that HTML into Jinja and pass in our `time` value to be interpolated and ultimately shown to the screen. Add `from jinja2 import Template` at the top of your `server.py` file and update the conditional statement to use `Jinja2`

```Python
# server.py 
...
 elif client_request.parsed_request['urn'] == '/time':
    with open(f'./templates/time.html', 'r') as myfile:
      html_from_file = myfile.read()
    template = Template(html_from_file)
    body_response = template.render(time=datetime.datetime.now())
    client_connection.send(body_response.encode())
```

Let's break down what's happening here. When a client makes a request to `/time`, the code inside our `elif` will run. First, we need to read out `time.html` file into a variable (`myfile`). After that, we pass the `html_from_file` to `Jinja2`'s  `Template()` function which makes a `Jinja` template for us. The Jinja template needs to interpolate the `time` variable, so we pass it in the `.render` function (`time=datetime.datetime.now()`). Finally, we send that fully built out HTML response to the user.

Run the server and test the `/time` route via `curl` to make sure you're getting the proper `HTML` response. Then, try going to `http://localhost:9292/time` in your browser - this should be broken. Can you modify/utilize the `build_html_response` to get a proper response via the browser and curl? Do this before going forward!

#### Refactor
As we build more routes, we're going to have more `Jinja2` files and need to utilize helper methods. Let's make a new file, `utilities.py` to house our helper methods:

```Python
# utilities.py 
def get_template(path):
    with open(f'./templates/{path}.html', 'r') as myfile:
        return myfile.read()

def build_html_response(text_body):
  # your code here
```

Import these functions into `server.py`: 

```Python
# server.py
from utilities import *
...
elif client_request.parsed_request['urn'] == '/time':
  view = Template(get_template('time'))
  body_response = build_html_response(view.render(time=datetime.datetime.now()))
  client_connection.send(body_response.encode())
```

As we pause for a second to look at our code, we have to address 2 things regarding its future organization:
* First, we want to create a `Response` class because our responses are going to get more elaborate
* Second, our if/elif statement for URNs is going to become cumbersome to work with as it grows. We need to create a `Router` class to handle reading each request and deciding how to respond (using the `Response` class)

The flow we are working toward looks something like this:
* `server.py` receives an HTTP request (a string)
* It passes the request to the `Request` class which parses/cleans the data so that we can use it more easily.
* The `Request` gets passed to the `Router`, who's job is to decide decode it and determine what kind of `Response` to send back
* `Response` will creates an appropriate response with properly formated HTML to `server.py`
* You get to see the response as usual

## Release 2 - `Response` Class 
Create a new file `response.py` and create a `Response` class. Some suggestions/pointers for your `Response` class:
- It should be initialized with the URN string and a dictionary of possible template variables
- Based off the URN string, it should be able to render a fully formatted Jinja HTML template using (if applicable) template variables
- You will probably end up stripping the methods you wrote in `utilities.py` to put into this class and deleting `utilities.py` altogether
    - Don't forget to remove unnecessary libraries from `server.py` when you strip out code

By the end of your refactor, your `server.py` should just include this tiny bit of code:

```Python
# server.py 
...

if client_request.parsed_request['urn'] == '/hello':
    response = Response('hello')
elif client_request.parsed_request['urn'] == '/time':
    response = Response('time', {'time': datetime.datetime.now()})

client_connection.send(str(response).encode()) # the __str__ method you wrote in the Response class
```

Let's refactor again before moving forward to the next section. Our `Response` and `Request` class is at the same level as our `server.py`, despite being custom classes that we need. Let's create a `classes` folder to house our two classes like the `templates` folder houses the templates. From there, change the `import` statements on `server.py` to account for the new location of your `Response` and `Request`.

## Release 3 - Router
This release will introduce you to decorators in Python. These two articles are a great reference: [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/) and [Decorators In Python: What You Need To Know](https://timber.io/blog/decorators-in-python/)

Don't get discouraged if decorators don't make sense right away. Hopefully working with them here will help you get a handle on how they work. Their implementation in this challenge is based the way [Flask](http://flask.pocoo.org/docs/0.12/quickstart/) handles routing, though pared down quite a bit. You may not end up using decorators that much when you're just starting out, but you will certainly see them around.

Create a file `classes/router.py` and add the following code: 

```Python
import re

class Router:
  routes = []

  @classmethod 
  def route(self, path, method='get'):
    def add_to_routes(function):
      route = {'path': path, 'function': function, 'method': method}
      self.routes.append(route)
    return add_to_routes

  @classmethod
  def process(self, request):
    for route in self.routes:
      if re.search(route['path'], request.path)and route['method'].lower() == request.method.lower():
        return route['function']()
      else 
        return 'HTTP/1.1 404 Not Found \r\n'
```

First, we have our class which will handle all the routes at the class level instead of at the instance level. Then, we create a class variable `routes` that will hold all of the routes we want our server to accept. 

Next we have our `route` function. This function is responsible for loading routes into our `routes` class variable. We will call this function every time we want to **create** a new route. Inside of `route`, we define another function `add_to_routes` which adds all the necessary route information (as a dictionary) to the class variable `routes`.

Thoroughly confused yet? Don't worry, this will make more sense when we see the implementation in just a bit. Let's go over our last method in `Router`. 

The `process` method is in charge of figuring out what to do with a request. When `process` receives a request, it loops through the routes and uses regex to match the request path with one of the routes saved in our `routes` class variable. If it finds one it runs the function saved under `route['function']` (the code that needs to be run to generate the response). If it doesn't find a match, it returns a `404` response. 

Let's implement this router with the rest of our HTTP server application by first creating a file `controller.py` at the same level as `server.py`. This is where we will call the Router and handle incoming requestswrite the code that tells our router how to handle each request:

```Python
# controller.py 

from router import Router
from classes.response import Response
import datetime

@Router.route('/hello')
def index():
    response = Response('hello')
    return response

@Router.route('/time')
def time():
    response = Response('time', {'time': datetime.datetime.now()})
    return response
```

Our controller will be where we store all the logic to process each request. Anytime we want to add a new route, we'll define it here. 

Then, in `server.py`, remove all the unnecessary libraries and `import` our new controller / router:

```Python
# server.py
from classes.request import Request
from classes.router import Router
import controller
import socket

# create a server listening on port 8888
HOST, PORT = 'localhost', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print(f'Serving HTTP on http://{HOST}:{PORT}')

while True:
    client_connection, client_address = listen_socket.accept()
    request = Request(request_text)
    response = Router.process(request)
    client_connection.send(str(response).encode())
    client_connection.close()
```

Our server is looking much cleaner now. All it does is take in a request and then serve back a response. You should still be able to run the server as before.
