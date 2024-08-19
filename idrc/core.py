from flask import Flask, request, jsonify, abort
import inspect
import functools
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import warnings
from .api_key import APIKeyGenerator
from .colors import printc

logging.getLogger('werkzeug').setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

class Verbose:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def debug(self, msg, color='blue'):
        if self.verbose:
            printc(f'[DEBUG] {msg}', color)

class idrc:
    def __init__(self, verbose=False):
        self.app = Flask(__name__)
        self.is_verbose = verbose
        self.verbose = Verbose(self.is_verbose).debug
        self.landing_html = ''
        self.landing_registered = False  # Flag to check if landing is registered
        self.api_keys = []
        self.limit = None

    def define(self, func, v=1, endpoint=None, methods=['POST']):
        """
        Defines an API endpoint for the given function.
        Parameters:
            func (function): The function to be wrapped and registered as an API endpoint.
            v (int, optional): The version of the API. Defaults to 1.
            endpoint (str, optional): The endpoint URL. If not provided, the function name will be used as the endpoint. Defaults to None.
            methods (list, optional): The HTTP methods allowed for this endpoint. Defaults to ['POST'].
        Returns:
            None
        """
        if endpoint is None:
            endpoint = func.__name__
            self.verbose(f'No endpoint specified. Defaulting to function name: {endpoint}')
        
        # Wrap the function to handle requests
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'GET':
                # Extract query parameters and convert types based on annotations
                self.verbose('Converting types...')
                args = self._convert_types(func, request.args)

                # Handle missing required parameters
                signature = inspect.signature(func)
                missing = [param.name for param in signature.parameters.values() if param.default == inspect.Parameter.empty and param.name not in args]
                if missing:
                    abort(400, description=f"Missing required parameters: {', '.join(missing)}")    
            else:
                # Handle JSON payloads for POST, PUT, etc.
                if request.is_json:
                    data = request.get_json()
                else:
                    abort(400, description="Request payload must be in JSON format")
                args = self._convert_types(func, data)

            # Check if the function accepts _method as an argument
            if '_method' in inspect.signature(func).parameters:
                args['_method'] = request.method

            # Call the original function with converted arguments
            result = func(**args)

            # Return result as JSON from a regular function (not jsoned yet)
            if not isinstance(result, dict):
                return jsonify({"result": result})
            return jsonify(result)

        # Register the endpoint
        self.verbose('Registering function...')
        self.app.add_url_rule(f'/api/v{v}/{endpoint}', endpoint, wrapper, methods=methods)
        string = f'API endpoint registered for function `{func.__name__}`: /api/v{v}/{endpoint}'
        self.verbose(string)
        if self.is_verbose:
            s = len(string) + 10
            printc('='*s, 'yellow')
    
    def _convert_types(self, func, data):
        """
        Convert the types of the values in the given data dictionary based on the parameter annotations of the provided function.
        Parameters:
        - func (callable): The function whose parameter annotations will be used for type conversion.
        - data (dict): The dictionary containing the data to be converted.
        Returns:
        - converted (dict): The dictionary with the converted values.
        Raises:
        - ValueError: If the value of a parameter cannot be converted to the specified type.
        """
        signature = inspect.signature(func)
        converted = {}
        for key, value in data.items():
            param = signature.parameters.get(key)
            if param is None:
                continue

            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                converted[key] = value
            else:
                try:
                    converted[key] = param_type(value)
                except ValueError as e:
                    abort(400, description=f"Incorrect type for parameter '{key}': {e}")
        
        return converted
    
    def keygen(self, multiplier=1):
        """
        Generate a custom API key using the given multiplier.
        Parameters:
            multiplier (int, optional): The multiplier to use for generating the key. Defaults to 1.
        Returns:
            key (str): The generated API key.
        """
        keygen = APIKeyGenerator()
        key = keygen.generate(multiplier)
        key = f'{__name__}-{key}'
        self.api_keys.append(key)
        return key
    
    def protect(self, key):
        """
        Protect an API endpoint using the given key.
        Parameters:
            key (str): The API key to protect the endpoint.
        Returns:
            None
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if (request.headers.get('X-API-Key') or request.args.get('key')) == key:
                    return func(*args, **kwargs)
                else:
                    abort(401, description='Unauthorized')
            return wrapper
        return decorator
    
    def list_keys(self):
        """
        List all the generated API keys.
        Parameters:
            None
        Returns:
            keys (list): The list of generated API keys.
        """
        return self.api_keys
    
    def remove_key(self, key):
        """
        Remove the given API key from the list of generated keys.
        Parameters:
            key (str): The API key to be removed.
        Returns:
            None
        """
        if key in self.api_keys:
            self.api_keys.remove(key)
            return True
        return False
    
    def clear_keys(self):
        """
        Clear all the generated API keys.
        Parameters:
            None
        Returns:
            None
        """
        self.api_keys = []

    def rate_limit(self, limit=5):
        """
        Rate limit the API endpoints to the given number of requests per minute.
        Parameters:
            limit (int, optional): The number of requests allowed per minute. Defaults to 5.
        Returns:
            None
        """
        self.limit = limit
        self.verbose(f'Rate limit set to {limit} requests per minute')

        # Initialize the Limiter with the Flask app and key function
        self.limiter = Limiter(
            get_remote_address,
            app=self.app,
            default_limits=[f"{limit} per minute"]
        )
    
    def landing(self, html=None):
        """
        Set the landing page for the Flask app.
        Parameters:
            html (str, optional): The HTML content to be displayed on the landing page. Defaults to '<h1>Welcome to idrc!</h1>'.
        Returns:
            None
        """
        if html is None:
            html = '<h1>My IDRC API</h1><br><p>Available endpoints:</p><ul>'
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    html += f'<li><a href="{rule.rule}">{rule.rule}</a></li>'
            html += '</ul>'

        self.landing_html = html
        if not self.landing_registered:
            def landing_page():
                return html
            
            self.app.add_url_rule('/', 'landing', landing_page)
            self.landing_registered = True
        
    def ecode(self, code, message=''):
        """
        Return a JSON response with the given status code and message.
        Parameters:
            code (int): The HTTP status code.
            message (str, optional): The message to include in the response. Defaults to ''.
        Returns:
            response (flask.Response): The JSON response object.
        """
        self.verbose(f'Returning status code {code} with message: {message}')
        self.app.make_response(({"message": message}, code))

        abort(code, message)

    def run(self, *args, **kwargs):
        import threading
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 5001)
        debug = kwargs.get('debug', False)
        error = [False]  # Use a list to track error state

        if debug:
            printc('[WARNING] Debug mode is currently not supported. Please disable debug mode.', 'yellow')
            sys.exit(1)

        import os
        import sys

        # stdout and stderr are redirected to /dev/null
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

        def start_app():
            try:
                self.landing()
                self.app.run(host=host, port=port, *args, **kwargs)
            except Exception as e:
                error[0] = True  # Set error state to True
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                printc(f'[ERROR] {e}', 'red')
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

        # Start the Flask app in a separate thread
        app_thread = threading.Thread(target=start_app)
        app_thread.start()

        # Wait for the Flask app thread to start
        app_thread.join(1)

        # Print success message after the app starts
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if not error[0]:  # Check error state
            m = f'[SUCCESS] Flask app running on http://{host}:{port}'
            printc(m, 'green')
            printc('[SUCCESS] Press Ctrl+C to stop the server', 'green')
            printc('='*(len(m)+10), 'yellow')

        # Wait for the Flask app thread to finish
        app_thread.join()

