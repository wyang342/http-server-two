class Request:
    def __init__(self, request_text):
      self.parse_request(request_text.recv(1024).decode('utf-8').split('\r\n'))

    def parse_request(self, request_as_list):
      self.parsed_request = {
        'method': request_as_list[0].split(' ')[0],
        'uri': request_as_list[0].split(' ')[1],
      }
      for row in request_as_list[1:-2]:
        split_list = row.split(': ')
        self.parsed_request[split_list[0]] = split_list[1]
