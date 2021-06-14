from classes.request import Request
from jinja2 import Template


class Response:
    def __init__(self, uri_string, template_vars_dict=None) -> None:
        self.uri_string = uri_string
        self.template_vars_dict = template_vars_dict
        self.template = Template(self.get_template(uri_string))

    def __str__(self) -> str:
        return self.build_html_response()

    def build_html_response(self) -> str:
        if self.uri_string == 'index':
            html_body = self.template.render(hello='Hello World!')
        elif self.template_vars_dict != None:
            html_body = self.template.render(**self.template_vars_dict)
        else:  # if there are no template variables
            html_body = self.template.render()

        return f"HTTP/1.1 200 OK\r\nContent-Type:text/html\r\nContent-Length:{len(html_body)}\r\n\r\n{html_body}"

    def get_template(self, path):
        with open(f'./templates/{path}.html', 'r') as myfile:
            return myfile.read()
