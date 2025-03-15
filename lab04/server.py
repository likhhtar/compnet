import http.server
import socketserver
import requests
from urllib.parse import urlparse

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = self.path[1:]  
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url  
        
        try:
            response = requests.get(url)
            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers['Content-Type'])
            self.end_headers()
            self.wfile.write(response.content)
        except Exception as e:
            self.send_error(500, f"Error while proxying the request: {e}")

PORT = 8888
Handler = ProxyHTTPRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Proxy server is running on http://localhost:{PORT}")
    httpd.serve_forever()
