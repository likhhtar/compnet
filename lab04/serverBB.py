import http.server
import socketserver
import requests
import os
import hashlib
import logging
from urllib.parse import urlparse

CACHE_DIR = "cache"
BLACKLIST_FILE = "blacklist.txt"
os.makedirs(CACHE_DIR, exist_ok=True)

logging.basicConfig(filename='proxy_requests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def get_cache_path(url):
    """Возвращает путь к файлу кэша для данного URL."""
    hashed_url = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, hashed_url)

def load_blacklist():
    """Загружает черный список доменов и URL из файла."""
    if not os.path.exists(BLACKLIST_FILE):
        return set()
    with open(BLACKLIST_FILE, 'r') as f:
        return set(line.strip() for line in f)

BLACKLIST = load_blacklist()

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        logging.info(f"URL: {self.path}, Response Code: {code}")

    def do_GET(self):
        url = self.path[1:]  
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url  
        
        if any(blacklisted in url for blacklisted in BLACKLIST):
            self.send_response(403)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Access to this page is blocked by the proxy server.")
            logging.info(f"Blocked access to {url}")
            return
        
        cache_path = get_cache_path(url)
        headers = {}
        
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                cached_data = f.read()
            
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(cached_data)
            logging.info(f"Cache hit for {url}")
            return
        
        try:
            response = requests.get(url, headers=headers)
            self.log_request(response.status_code)
            
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    f.write(response.content)
                logging.info(f"Cached response for {url}")
            
            self.send_response(response.status_code)
            self.send_header("Content-type", response.headers.get('Content-Type', 'application/octet-stream'))
            self.end_headers()
            self.wfile.write(response.content)
        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Error while proxying the request: {e}")

PORT = 8888
Handler = ProxyHTTPRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Proxy server is running on http://localhost:{PORT}")
    httpd.serve_forever()