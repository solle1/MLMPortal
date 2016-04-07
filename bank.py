import json

import requests

API_ENDPOINT = 'https://www.routingnumbers.info/api/data.json'
API_ENDPOINT = 'http://www.routingnumbers.info/api/data.json'

def bank_data(routing_num):
    payload = {
        'rn': routing_num,
    }

    resp = json.loads(requests.get(API_ENDPOINT, params=payload).content)
    return resp
