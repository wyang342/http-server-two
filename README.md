# HTTP Server Two

## Release 1 - Templates
Returning hard-coded responses for every request isn't very useful and generating HTML in Python is a bit of a chore. Fortunately, there's a Python library called [Jinja2](http://jinja.pocoo.org/docs/2.10/intro/) that makes generating HTML much easier.

Jinja allows us to write HTML and interpolate Python code inside. To get started today, run the following commands after cloning this repo:

```sh
$ python -m venv venv
$ source venv/bin/activate
$ pip install Jinja2
```

As our applications get larger and larger, we need to organize our files within folders. In Django, all HTML files are nested within a `templates` directory. Let create that:

```sh
$ mkdir templates
$ cd templates
$ touch time.html
```

We should have an HTML file for our `/time` route: `templates/time.html`:

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

We've got an HTML file with a twist: `{{ time }}`. The two curly braces are to interpolate a `time` variable that we pass in using Python/Jinja.

`server.py` should now read:
```python
# at the top
from jinja2 import Template
#...
elif client_request.parsed_request['uri'] == '/time':
    with open(f'./templates/time.html', 'r') as myfile:
        html_from_file = myfile.read()
    template = Template(html_from_file)
    body_response = template.render(time=datetime.datetime.now())
    client_connection.send(body_response.encode())
```

**start here**

Let's break down what's happening here. When a client makes a request to `/time`, the code inside our `elif` will run. First, we need to read the `time.html` file into a variable (`myfile`). After that, we pass the `html_from_file` to `Jinja2`'s  `Template()` function which makes a `Jinja` template for us. The Jinja template needs to interpolate the `time` variable, so we pass it in the `.render` function (`time=datetime.datetime.now()`). Finally, we send that fully built out HTML response to the user.

Run the server and test the `/time` route via `curl` to make sure you're getting the proper `HTML` response. Then, try going to `http://localhost:9292/time` in your browser - this should be broken. Can you modify/utilize the `build_html_response` to get a proper response via the browser and curl? Do this before going forward!

Repeat this process for the `/` route - call this the `index` template.

#### Refactor!
As we build more routes, we're going to have more `Jinja2` files and will need to utilize helper methods. Let's make a new file, `utilities.py` to house these helper methods:

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
...
from utilities import *
...
elif client_request.parsed_request['uri'] == '/time':
  view = Template(get_template('time'))
  body_response = build_html_response(view.render(time=datetime.datetime.now()))
  client_connection.send(body_response.encode())
```

Ah, a bit more breathing room. Let's pause for a second to look at our code and plan its future:
* `server.py` passed off the `Request` responsibility to another class but it's doing everything with the `Response` right now. We want to create a `Response` class soon to keep to the single responsibility principle.
* Our `if/elif` statement for URIs is going to become cumbersome to work with as it grows. We need to create a `Router` class to handle reading each request and deciding how to respond (using the `Response` class)

The flow we are working toward looks something like this:
* `server.py` receives an HTTP request (a string)
* It passes the request to the `Request` class which parses/cleans the data so that we can use it more easily
* The `Request` gets passed to the `Router`, who's job is to decide decode it and determine what kind of `Response` to send back
* `Response` will creates an appropriate response with properly formated HTML to `server.py`
* You see the response as HTML on your browser

## Release 2 - The `Response` Class 
Create a new file `response.py` and create the `Response` class. Some suggestions/pointers for your `Response` class:
- It should be initialized with the URI string and a dictionary of possible template variables. Be sure to account for the situation where there aren't any template variables in `Response`
- Write a method `__str__` where, based off the URN string, it should be able to render a fully formatted Jinja HTML template using template variables (if applicable)
- You will probably end up stripping the methods you wrote in `utilities.py` to put into this class and deleting `utilities.py` altogether
    - Don't forget to remove unnecessary libraries from `server.py` when you strip out code

By the end of your refactor, your `server.py` should just include this tiny bit of code:

```Python
# server.py 
...
if client_request.parsed_request['uri'] == '/':
    response = Response('index')
elif client_request.parsed_request['uri'] == '/time':
    response = Response('time', {'time': datetime.datetime.now()})

client_connection.send(str(response).encode()) # the __str__ method you wrote in the Response class
client_connection.close()
```

Let's refactor again before moving forward to the next section. Our `Response` and `Request` class is at the same level as our `server.py`, despite being custom classes that we need. Let's create a `classes` folder to house our two classes like the `templates` folder houses the templates. From there, change the `import` statements on `server.py` to account for the new location of your `Response` and `Request`.

**Ensure that everything works like it used to before moving forward**

## Release 3 - The Router Class
This release will introduce you to decorators in Python. These two articles are a great reference: [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/) and [Decorators In Python: What You Need To Know](https://timber.io/blog/decorators-in-python/)

Don't get discouraged if decorators don't make sense right away. Hopefully working with them here will help you get a handle on how they work. Their implementation in this challenge is based the way [Flask](http://flask.pocoo.org/docs/0.12/quickstart/) handles routing, though pared down quite a bit. You may not end up using decorators that much when you're just starting out, but you will certainly see them around.

Create a file `classes/router.py` and add the following code: 

```Python
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
    parsed_request = request.parsed_request
    for route in self.routes:
      if route['path'] == parsed_request['uri'] and route['method'].lower() == parsed_request['method'].lower():
        return route['function']()
    return 'HTTP/1.1 404 Not Found \r\n'
```

First, we have our class which will handle all the routes at the class level instead of at the instance level. Then, we create a class variable `routes` that will hold all of the routes we want our server to accept. 

Next we have our `route` class method. This is responsible for loading routes into our `routes` class variable. We will call this function every time we want to **create** a new route. Inside of `route` is another function, `add_to_routes`, which adds all the necessary route information (as a dictionary) to the `routes` class variable. Don't worry if this doesn't make sense yet - we'll see it in action soon.

The `process` class method is in charge of figuring out what to do with a request. When `process` receives a request, it loops through the routes and sees if the request path matches any of the routes in the class variable. If it finds one, it runs the function saved under `route['function']` (the code that needs to be run to generate the response). If it doesn't find a match, it returns a `404` response.

Let's implement this router with the rest of our HTTP server application by first creating a file `controller.py` at the same level as `server.py`. This is where we will call the Router and handle incoming requests / write the code that tells our router how to handle each request:

```Python
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
    request = Request(client_connection)
    response = Router.process(request)
    client_connection.send(str(response).encode())
    client_connection.close()
```

Our server is looking much cleaner now. All it does is take in a request and then serve back a response. You should still be able to run the server as before.
