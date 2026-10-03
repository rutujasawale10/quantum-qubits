import sys
import os
import json
import asyncio

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from api import app

async def test_app():
    # Construct mock ASGI request for POST /api/verify
    scope = {
        'type': 'http',
        'method': 'POST',
        'path': '/api/verify',
        'headers': [(b'content-type', b'application/json')],
        'query_string': b''
    }

    body_bytes = json.dumps({
        "state": "0",
        "attack": "NONE",
        "verifier": "Bob",
        "shots": 1000
    }).encode('utf-8')

    async def receive():
        return {
            'type': 'http.request',
            'body': body_bytes,
            'more_body': False
        }

    response_status = None
    response_headers = []
    response_body = []

    async def send(message):
        nonlocal response_status, response_headers
        if message['type'] == 'http.response.start':
            response_status = message['status']
            response_headers = message['headers']
        elif message['type'] == 'http.response.body':
            response_body.append(message.get('body', b''))

    await app(scope, receive, send)

    full_body = b''.join(response_body).decode('utf-8')
    print("STATUS CODE:", response_status)
    print("RESPONSE BODY:", full_body)

if __name__ == "__main__":
    asyncio.run(test_app())
