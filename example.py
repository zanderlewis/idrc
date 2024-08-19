from idrc import idrc

api = idrc(verbose=True)

@api.protect(api.keygen(2))
def add(a: int, b: int):
    return a + b

def subtract(a: int, b: int):
    return a - b

def error():
    return api.ecode(404, 'Not found')

api.define(add, methods=['GET'])
api.define(subtract)
api.define(error, endpoint='error', methods=['GET'])

print(api.list_keys())

api.rate_limit(1)

api.run()
