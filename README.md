# IDRC
I Don't Really Care: Auto APIs for lazy people

## Table of Contents
- [IRDC](#idrc)
  - [Installation](#installation)
  - [Usage](#usage)

## Installation

IDRC can be installed via `pip` like so:

`pip3 install idrc`

## Usage

IDRC can integrate with any function. For example:

```python
from idrc import idrc

# Initialize the idrc class
api = idrc(debug=True)

# Simulate a weather database
weather_data = {
    "New York": {"temperature": 25, "condition": "Sunny"},
    "Los Angeles": {"temperature": 30, "condition": "Cloudy"},
    "Chicago": {"temperature": 18, "condition": "Rainy"}
}

# Define a weather forecast function
def get_weather(city: str) -> dict:
    forecast = weather_data.get(city, None)
    if forecast:
        return forecast
    else:
        return {"error": "City not found"}

# Register the function as an API endpoint
api.define(get_weather, methods=['GET'])

# Run the idrc API
if __name__ == '__main__':
    api.run(host='0.0.0.0', port=5000)
```

The `define` function in the `idrc` library generated the api.

The Flask equivalent of the code above is:
```python
from flask import Flask, request, jsonify

# Initialize the Flask app
app = Flask(__name__)

# Simulate a weather database
weather_data = {
    "New York": {"temperature": 25, "condition": "Sunny"},
    "Los Angeles": {"temperature": 30, "condition": "Cloudy"},
    "Chicago": {"temperature": 18, "condition": "Rainy"}
}

# Define a weather forecast function
@app.route('/api/v1/get_weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    forecast = weather_data.get(city)
    if forecast:
        return jsonify(forecast)
    else:
        return jsonify({"error": "City not found"}), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
