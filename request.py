class Request:

  def __init__(self, request_text):
    self.request = request_text.split('\r\n')
    self.request_line = self.request.pop(0).split(' ')
    self.headers = self.parse_headers()
    self.method = self.request_line[0]
    self.path = self.request_line[1]
    self.url = self.headers['host']

  def parse_headers(self):
    request = self.request
    headers = {}

    for header in request:
      seperated_header_value = header.split(': ')
      if len(seperated_header_value) > 1:
        headers[seperated_header_value[0].lower()] = seperated_header_value[1]
    return headers


