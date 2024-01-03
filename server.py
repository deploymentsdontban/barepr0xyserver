# server.py
from fastapi import FastAPI, HTTPException
import httpx
from urllib import parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import asyncio

app = FastAPI()

@app.get("/")
async def proxy(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            return response.content
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

class ServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = parse.unquote(self.path[1:])
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        content = loop.run_until_complete(self.fetch_content(url))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content)

    async def fetch_content(self, url):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                return response.content
            except httpx.HTTPError as exc:
                return exc.response.text

def run(server_class=HTTPServer, handler_class=ServerHandler):
    server_address = ('0.0.0.0', int(os.environ.get('PORT', 8000)))
    httpd = server_class(server_address, handler_class)
    print('Starting server...')
    httpd.serve_forever()

run()