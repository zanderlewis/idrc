import json, inspect
from http.server import BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = kwargs.pop('routes', {})
        self.verbose = kwargs.pop('verbose', None)
        self.requests_count = {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')

    def handle_request(self, method):
        from urllib.parse import urlparse, parse_qs
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None

        if path in self.routes:
            func, methods = self.routes[path]
            if method not in methods:
                self.send_response(405)
                self.end_headers()
                return

            try:
                if method == 'GET':
                    args = self._convert_types(func, query_params)
                elif method == 'DELETE':
                    args = self._convert_types(func, query_params)
                elif method == 'PUT':
                    data = json.loads(post_data) if post_data else {}
                    args = self._convert_types(func, data)
                else:
                    data = json.loads(post_data) if post_data else {}
                    args = self._convert_types(func, data)

                result = func(**args)
                if isinstance(result, str):
                    response = result
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                else:
                    response = json.dumps({"result": result}) if not isinstance(result, dict) else json.dumps(result)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response.encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _convert_types(self, func, data):
        signature = inspect.signature(func)
        converted = {}
        for key, value in data.items():
            param = signature.parameters.get(key)
            if param is None:
                continue

            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                converted[key] = value[0] if isinstance(value, list) else value
            else:
                try:
                    converted[key] = param_type(value[0] if isinstance(value, list) else value)
                except ValueError as e:
                    raise ValueError(f"Incorrect type for parameter '{key}': {e}")
        
        return converted