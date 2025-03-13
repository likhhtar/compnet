import http.server
import socketserver
import requests
from urllib.parse import urlparse
import logging
import json

logging.basicConfig(filename='proxy_requests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        """Запись запроса в журнал"""
        logging.info(f"URL: {self.path}, Response Code: {code}")

    def do_GET(self):
        """Обработка GET-запроса"""
        url = self.path[1:]  
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url  

        try:
            response = requests.get(url)
            self.log_request(response.status_code)

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['Content-Type'])
            self.end_headers()
            self.wfile.write(response.content)
        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Error while proxying the request: {e}")

    def do_POST(self):
        """Обработка POST-запроса"""
        url = self.path[1:]  
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url  

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            response = requests.post(url, data=post_data)
            self.log_request(response.status_code)

            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['Content-Type'])
            self.end_headers()
            self.wfile.write(response.content)
        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Error while proxying the request: {e}")

PORT = 8888
Handler = ProxyHTTPRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Proxy server is running on http://localhost:{PORT}")
    httpd.serve_forever()
