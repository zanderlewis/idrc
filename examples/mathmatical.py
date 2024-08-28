from idrc import idrc

api = idrc(verbose=True)

def add(a: int, b: int):
    return a + b

def subtract(a: int, b: int):
    return a - b

def error():
    return api.ecode(404, 'Not found')

api.define(add, methods=['GET'])
api.define(subtract)
api.define(error, endpoint='error', methods=['GET'])

api.run(port=5001)
