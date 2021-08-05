from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

host_name = "localhost"
server_port = 4000

# This is just a dict, but we'll drop-in replace this with a file system.
class InMemoryDB:
    def __init__(self):
        self.db = {}

    def __getitem__(self, key):
        return self.db[key]

    def __setitem__(self, key, val):
        self.db[key] = val

# This server is very low level, we might use something like flask to clean up
# a lot of this cruft, but let's stick to base Python for now.
class DBServer(BaseHTTPRequestHandler):
    def _send_headers(self, code):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def _send_text(self, text):
        self.wfile.write(text.encode("utf8"))

    def do_GET(self):
        qs = urlparse(self.path)
        params = parse_qs(qs.query)

        if qs.path.endswith('/get'):
            if 'key' not in params:
                self._send_headers(400)
                self._send_text("Missing key")
                return

            try:
                val = db[params['key'][0]]
            except KeyError:
                self._send_headers(404)
                return

            self._send_headers(200)
            self._send_text(val)
        elif qs.path.endswith('/set'): 
            if 'key' not in params or 'value' not in params:
                self._send_headers(400)
                self._send_text("Missing key or value")
                return
            
            db[params['key'][0]] = params['value'][0]
            self._send_headers(200)
        else:
            self._send_headers(200)

if __name__ == "__main__":
    db = InMemoryDB()     
    ws = HTTPServer((host_name, server_port), DBServer)
    print("Server started http://%s:%s" % (host_name, server_port))

    try:
        ws.serve_forever()
    except KeyboardInterrupt:
        pass

    ws.server_close()
    print("Server stopped.")