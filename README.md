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

Let's break down what's happening here:
- A client makes a request to `/time`
- Our server parses the request and sees that they are making a request to `/time`
- We need to load the entire `time.html` file into `myfile`
- We read the contents of the file into `html_from_file`
- We pass the `html_from_file` to Jinja's  `Template()` class. `Template` will create aa new Jinja Template object. We are saving this as `template`
- We `render` the template with a dictionary of variables that the template needs. In our case, our HTML template we created earlier needs the `time` variable declared
  - We pass `time=datetime.datetime.now()` in the `.render` function. Finally, we send that fully built out HTML response to the user.

Run the server and test the `/time` routes:

```sh
$ curl http://localhost:9292/time
```

Ensure you've got a proper response coming back.

Next, try hitting http://localhost:9292/time in the browser. Are you finding that you can't hit it? Turns out that Chrome needs the correct HTTP headers in order to display things properly. A few things for you to do before moving into the next section:
- Utilize `build_html_response()` in the block of code we just wrote to get Chrome displaying our HTML
- Repeat the process we used for `/time` to account for the `/` route. We'll use an HTML template called `index` for this route.

#### Refactor!
As we build more routes, we're going to have more `Jinja2` files and will need to utilize helper methods:

```Python
# server.py 
def get_template(path):
    with open(f'./templates/{path}.html', 'r') as myfile:
        return myfile.read()

def build_html_response(text_body):
  # your code here

# ...

elif client_request.parsed_request['uri'] == '/time':
  view = Template(get_template('time'))
  body_response = build_html_response(view.render(time=datetime.datetime.now()))
  client_connection.send(body_response.encode())
```

Let's take a look at the current state of `server.py` and figure out what we need to do to make it follow the Single Responsibility Principle:
- `server.py` receives a request and passes it off to the `Request` class. `Request` will parse through it and gives `server.py` the ability to read it as a dictionary
- `server.py` is in charge of finding the correct template, building an HTTP response, and sending that response back to the client.

We should probably create a `Response` class to take some of the load off `server.py`. We should also create a `Router` class to handle reading each request and deciding how to respond (using the `Response` class).

By the end of today, we should get to this flow:
- `server.py` receives an HTTP request
- `server.py` passes the request to the `Request` class which parses/cleans the data so that we can use it more easily
- The `Request` gets passed to the `Router`, who decodes it and determines what kind of `Response` to send back
- `Response` will create an appropriate response with properly formated HTML to `server.py`
- `server.py` will send the client a proper HTML response

## Release 2 - The `Response` Class 
Create a new file `response.py` and a `Response` class. Here are a few pointers to get you started:
- `Response` should be initialized with the URI string from the `Request` and a dictionary of possible template variables (remember - we are going to be finding a template and inserting variables, so `Response` will need to know about them)
  - Be sure to account for the situation where there aren't any template variables
- `__str__` should be able to render a fully formatted Jinja HTML template using template variables (if applicable)
- You will be stripping `get_template` and `build_html_response` out from `server.py` and putting it in `Response`
  - Don't forget to remove code from `server.py` as you strip things out

By the end of your refactor, your `server.py` should just include this tiny bit of code:

```Python
# server.py 
...
if client_request.parsed_request['uri'] == '/':
    response = Response('index')
elif client_request.parsed_request['uri'] == '/time':
    response = Response('time', {'time': datetime.datetime.now()})

client_connection.send(str(response).encode())
client_connection.close()
```

**One final refactor**
We want to put all of our custom classes (Request/Response) in a `classes/` folder (at the same directory level as `templates/` and `server.py`) as part of the Single Responsibility principle, just like we have a `templates` folder to house the templates. From there, change the `import` statements on `server.py` to account for the new location of your `Response` and `Request`:

```python
# server.py
from classes.request import Request
from classes.response import Response
# ...
```

Ensure that everything works like it used to before moving forward.

## Release 3 - The Router Class
This release will introduce you to decorators in Python. These two articles are a great reference:
* [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/) 
* [Decorators In Python: What You Need To Know](https://timber.io/blog/decorators-in-python/)

Don't get discouraged if decorators don't make sense right away. Hopefully working with them here will help you get a handle on how they work. Their implementation in this challenge is based the way [Flask](http://flask.pocoo.org/docs/0.12/quickstart/) handles routing, though pared down quite a bit. You may not end up using decorators that much when you're just starting out, but you will certainly see them around. 

We'll write all of the code for you. Focus on trying to understand what's going on.

Create a file `classes/router.py` and add the following code: 

```Python
class Router:
  routes = [] # a class variable that will hold all of the routes on our application

  @classmethod # note that these methods are both class methods, meaning that we don't have instances of the Router class
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

The `route` class method is responsible for loading routes into our `routes` class variable. We will call this function every time we want to create a new route. Inside of `route` is another function, `add_to_routes`, which adds all the necessary route information (as a dictionary) to the `routes` class variable.

The `process` class method is in charge of figuring out what to do with a request. When `process` receives a request, it loops through the routes and sees if the request path matches any of the routes in the class variable. If it finds one, it runs the function saved under `route['function']`. If it doesn't find a match, it returns a `404` response.

Let's implement this router with the rest of our HTTP server application by first creating a file `controller.py` at the same level as `server.py`. This is where we will call the Router and handle incoming requests / write the code that tells our router how to handle each request:

```python
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

While it seems like a lot of work just to get the same functionality, we've set up our architecture to be able to scale this application to 5 or 5000 new routes. 