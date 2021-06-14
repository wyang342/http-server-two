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
