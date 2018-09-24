from request import Request
import socket
import datetime

# create a server listening on port 8888
HOST, PORT = '', 9292

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.bind((HOST, PORT))
print('Waiting For Connection...')
listen_socket.listen(1)

while True:

    client_connection, client_address = listen_socket.accept()
    # we listen for a request. Then we need to convert it from bytes to a string with decode.
    request_text = client_connection.recv(1024).decode('utf-8')
    request = Request(request_text)

    if request.path == '/':
        protocol = 'HTTP/1.1 200 OK\r\n'
        body_response = '<html><body><h1>Hello World!</h1></body></html>'
        content_type = 'Content Type: text/html\r\n'
        content_length = f'Content Length: {len(body_response)}\r\n'

        client_connection.send(protocol.encode())
        client_connection.send(content_type.encode())
        client_connection.send(content_length.encode())
        client_connection.send('\r\n'.encode())
        client_connection.send(body_response.encode())

    elif request.path == '/time':
        protocol = 'HTTP/1.1 200 OK\r\n'
        body_response = f'<html><body><h1>{ datetime.datetime.now() }</h1></body></html>'
        content_type = 'Content Type: text/html\r\n'
        content_length = f'Content Length: {len(body_response)}\r\n'

        client_connection.send(protocol.encode())
        client_connection.send(content_type.encode())
        client_connection.send(content_length.encode())
        client_connection.send('\r\n'.encode())
        client_connection.send(body_response.encode())

    client_connection.close()
