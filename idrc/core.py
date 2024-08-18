from flask import Flask, request, jsonify, abort
import inspect
import functools

class idrc:
    def __init__(self, debug=False):
        self.app = Flask(__name__)
        self.debug = debug

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
        
        # Wrap the function to handle requests
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'GET':
                # Extract query parameters and convert types based on annotations
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

            # Call the original function with converted arguments
            result = func(**args)

            # Return result as JSON from a regular function (not jsoned yet)
            if not isinstance(result, dict):
                return jsonify({"result": result})
            return jsonify(result)

        # Register the endpoint
        self.app.add_url_rule(f'/api/v{v}/{endpoint}', endpoint, wrapper, methods=methods)
    
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
    
    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs, debug=self.debug)
