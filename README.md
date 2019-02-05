# HTTP Server Two


## Release 1 - Templates

Returning a hard-coded responses for every request isn't very useful, and generating HTML in Python is a bit of a chore. Fortunately, there's a Python library called Jinja2 that makes generating HTML much easier. Take a look at this introduction to [Jinja2](http://jinja.pocoo.org/docs/2.10/intro/) before continuing:

`Jinja` allows us to write `HTML` and run `Python` code in it before it gets rendered. Run `pip install Jinja2` in your terminal. 

We'll start off by creating a `templates` directory and then creating a `Jinja` template for our `/time` route: `templates/time.html`. Then we write some boilerplate `HTML` and add an `<h1>` tag to display our time. using brackets: `{{ time }}` The two brackets are special tags to let `Jinja2` know we want it to run/interpolate some Python code. Wrapping a variable in brackets, `{{ my_variable }}`, tells `Jinja2` to evaluate the variable and insert it into the final HTML string. 

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

Ok, we have some `HTML`. Now we need to use `Jinja2` to run the Python code and return a string that we can then send back to the client as our response body. Add `from jinja2 import Template` at the top of your `server.py` file. Then we can update our conditional statement to use `Jinja2`

```Python
# server.py 

 elif client_request.parsed_request['urn'] == '/time':
    with open(f'./templates/time.html', 'r') as myfile:
      html_from_file = myfile.read()
    template = Template(html_from_file)
    body_response = template.render(time=datetime.datetime.now())
    client_connection.send(body_response.encode())
```

Let's break down what's happening here. When a client makes a request to `/time`, the code inside our `elif` will run. First, we need to read out `time.html` file into a variable (`myfile`). After that, we pass the `html_from_file` to `Jinja2`'s  `Template()` function which makes a `Jinja` template for us. The Jinja template interpolates the `time` variable, so we need to pass it in the `.render` function (`time=datetime.datetime.now()`).

Run the server and test the `/time` route via `curl` to make sure you're getting the proper `HTML` response. Then, try going to `http://localhost:9292/time` in your browser - this should be broken. Can you modify/utilize the `build_html_response` to get a proper response via the browser and curl? Do this before going forward

#### Refactor
As we build more routes, we're going to have more `Jinja2` files, and ultimately we are going to have more Python helper methods. Let's make a new file, `utilities.py` to house our logic for getting a template and generating HTML code. This file will house our helper methods.

```Python
# utilities.py 
def get_template(path):
    with open(f'./views/{path}.html', 'r') as myfile:
        return myfile.read()

def build_html_response(text_body):
  # your code here
```

And then we can import these functions in `server.py`: 

```Python
# server.py
from utilities import *
...
elif request.path == '/time':
  view = Template(get_template('time'))
  body_response = build_html_response(view.render(date=datetime.datetime.now()))
  client_connection.send(body_response.encode())
```

We should be able to call `get_view` in any of our routes and pass it the file we want. Soon we are going to start adding the ability to read and save data from a database (we'll use a `csv` file for this) but before we do that, let's address two problems with how our code is organized. 

First, our responses are getting more elaborate, so we should create a class to handle creating responses. 

The second problem is that our conditional statement is going to become cumbersome to work with as it grows, so we'll need to create a `Router` class to handle reading the request and deciding how to respond. 

The flow we are working toward looks something like this: 

The server receives an HTTP request string. It passes the HTTP request string to the `Request` class which parses it and makes it easier for Python to deal with. After that, the request gets passed to the router. The router's job is to decide what to do with the request and create a response. The response is passed back to the server, which serves the response to the client. 

## Release 2 - Response Class 

Create a new file `response.py` and write the code for a class that will hold all the data for our response. Define be sure to define a `__str__()`. Remember, HTTP responses need to be strings. When your done, refactor your code in `server.py` to look something like this: 

```Python
# server.py 

if request.path == '/hello':
  view = Template(get_view('index'))
  body_response = view.render()

  response = Response()
  response.status = 200
  response.content_type = 'text/html'
  response.body = body_response
  
  client_connection.send(str(response).encode())
```

## Release 3 - Router 

This release will challenge you if you aren't comfortable with decorators in Python. These two articles are a great reference:[Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/) and [Decorators In Python: What You Need To Know](https://timber.io/blog/decorators-in-python/)

Don't get discouraged if decorators don't make sense right away. Hopefully working with them here will help you get a handle on how they work. They're implementation here is based the way [Flask](http://flask.pocoo.org/docs/0.12/quickstart/) handles routing, though pared down quite a bit. You may not end up using decorators that much when you're just starting out, but you will certainly see them around, and it will be good to have an idea how they work. 

Create a file `router.py` and add the following code. 

```Python
# router.py 
import re 

class Router:
 
  routes = []

  @classmethod 
  def route(self, path, method='get'):
    def add_to_routes(f):
      r = {'path': path, 'process': f, 'method': method}
      self.routes.append(r)
   
    return add_to_routes

  @classmethod
  def process(self, request):
    for route in self.routes:
      if re.search(route['path'], request.path)and route['method'].lower() == request.method.lower():
        return route['process']()
      else 
        return 'HTTP/1.1 404 Not Found \r\n'
```

First we have our class. Rather than creating instances of our class, we are going to have the class itself handle all the routes. We create a class variable `routes` that will hold all of the routes we want our server to accept. So instead of our if statement, `if '/'`, `if '/time'`, `if '/facts'`, we'll have a list of hashes. Each route will look something like this: `{ 'method': 'GET', 'path': '/', 'process': a function that knows how to create an appropriate response }`. 

Next we have our `route` function. This function is responsible for loading routes into our `routes` class variable. We will call this function every time we want to create a new route. Inside of route we define another function that creates a dictionary with the path and http method. You'll notice that `add_to_routes` takes in it's own argument. This variable will be replaced with whatever function we declare under our decorator. 

Here are two implementations of the same idea. The first is what we are doing, using decorators. The second will work just as well. 

```Python 
@Router.route('/')
def index():
  view = Template(get_view('index'))
  body_response = view.render()

  response = Response()
  response.status = 200
  response.body = body_response

  return response

# This is the same as saying: 

def index():
  view = Template(get_view('index'))
  body_response = view.render()

  response = Response()
  response.status = 200
  response.body = body_response

  return response

add_to_routes('/', 'get', index)

```

This might make more sense when we see the implementation in a little bit. First, let's quickly go over our last method in `Router`. 

`process` is in charge of figuring out what to do with a request. When it receives a request, it loops through the routes and uses regex to match the request path with one of the routes saved in our `routes` class variable. If it finds one it runs the function saved under `route['process']` (the code that needs to be run to generate the response). If it doesn't find a match, it returns a `404` not found response. 

That was a lot. If you're confused, don't worry. Read through the rest of the release and then feel free to go back and play with the code to get a better understanding of how it works. 

Let's look at the implementation of the router class. Create a file `controller.py`. This is where we will write the code that tells our router how to handle each request. 

```Python
# controller.py 

from router import Router
from jinja2 import Template
from utilities import get_view
from response import Response
import datetime

@Router.route('/hello')
def index():
  view = Template(get_view('index'))
  body_response = view.render()

  response = Response()
  response.status = 200
  response.body = body_response

  return response

@Router.route('/time')
def time():
  view = Template(get_view('time'))
  body_response = view.render(date=datetime.datetime.now())
  
  response = Response()
  response.status = 200
  response.body = body_response

  return response
  
```
Our controller will be where we store all the logic to process each request. Anytime we want to add a new route, we'll define it here. We can move our `import` statements for `jinja2`, `utilities`, `response`, and `datetime` here and delete them from `server.py`

Then, in `server.py`, we can `import` our controller and router and put them to good use for us. 


```Python
# server.py
from request import Request
from router import Router

import controller 
import socket

# create a server listening on port 8888
HOST, PORT = '', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)

while True:
  
    client_connection, client_address = listen_socket.accept()
    # we listen for a request. Then we need to convert it from bytes to a string with decode. 
    request_text = client_connection.recv(1024).decode('utf-8')
    request = Request(request_text)
 
    response = Router.process(request)
   
    client_connection.send( str(response).encode() )

    client_connection.close()

```
Our server is looking much cleaner now. All it does is take in a request and then serve back a response. You should still be able to run the server as before. 

Up to this point we've only been handling `GET` requests. In the next challenge we'll learn how to access parameters sent to us by the client, and save data based on the request. 


