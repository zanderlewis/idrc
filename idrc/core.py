import logging, warnings, os, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from http.server import HTTPServer
from .request_handler import RequestHandler
from .colors import printc

logging.getLogger('werkzeug').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

class RestartHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_any_event(self, event):
        # Clear terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        self.restart_callback()

class Verbose:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def debug(self, msg, color='blue'):
        if self.verbose:
            printc(f'[DEBUG] {msg}', color)

class idrc:
    def __init__(self, verbose=False):
        self.routes = {}
        self.is_verbose = verbose
        self.verbose = Verbose(self.is_verbose).debug

    def define(self, func, v=1, endpoint=None, methods=['POST']):
        if endpoint is None:
            endpoint = func.__name__
            self.verbose(f'No endpoint specified. Defaulting to function name: {endpoint}')
        
        path = f'/api/v{v}/{endpoint}'
        self.routes[path] = (func, methods)
        self.verbose(f'API endpoint registered for function `{func.__name__}`: {path}')
    
    def landing(self, html=None):
        if html is None:
            html = '<h1>My IDRC API</h1><br><p>Available endpoints:</p><ul>'
            for path in self.routes:
                html += f'<li><a href="{path}">{path}</a></li>'
            html += '</ul>'

        self.routes['/'] = (lambda: html, ['GET'])
    
    def ecode(self, code, message=''):
        self.verbose(f'Returning status code {code} with message: {message}')
        raise Exception(message)

    def run(self, *args, **kwargs):
        debug = kwargs.get('debug', False)

        if debug:
            self._run_with_reloader(*args, **kwargs)
        else:
            self._run_without_reloader(*args, **kwargs)

    def _run_with_reloader(self, *args, **kwargs):
        kwargs.pop('debug', None)

        def restart():
            printc('[INFO] Detected file change. Restarting...', 'yellow')
            os.execv(sys.executable, ['python'] + sys.argv)
        
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 5000)

        event_handler = RestartHandler(restart)
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()
        printc(f'[SUCCESS] API is running on http://{host}:{port}', 'green')
 
        try:
            self._run_without_reloader(*args, **kwargs)
        finally:
            observer.stop()
            observer.join()
            self.verbose('[INFO] Observer stopped.', 'yellow')
    
    def _run_without_reloader(self, *args, **kwargs):
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 5000)
        available = self.port_available(host, port)
        if not available:
            printc(f'[ERROR] Port {port} is not available. Please use a different port.', 'red')
            sys.exit(1)

        error = [False]

        def start_app():
            try:
                self.landing()
                server = HTTPServer((host, port), lambda *args, **kwargs: RequestHandler(*args, routes=self.routes, verbose=self.verbose, **kwargs))
                server.serve_forever()
            except Exception as e:
                error[0] = True
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                printc(f'[ERROR] {e}', 'red')
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

        start_app()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if not error[0]:
            m = f'[SUCCESS] HTTP server running on http://{host}:{port}'
            printc(m, 'green')
            printc('[SUCCESS] Press Ctrl+C to stop the server', 'green')
            printc('='*(len(m)+10), 'yellow')

    def port_available(self, host, port):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) != 0
        