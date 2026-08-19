import asyncio
import logging

from typing import Callable
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class App:
    def __init__(self):
        self.routes = {}
        self.route_names = {}
        self.static_dir = BASE_DIR / "static"
        self.media_dir = BASE_DIR / "media"
        self.logger = logging.getLogger(__name__)

    def get(self, path: str):
        def decorator(func):
            if ("GET", path) in self.routes:
                raise ValueError(f"Route already registered: GET {path}")
            if func.__name__ in self.route_names:
                raise ValueError(f"Route name already registered: {func.__name__}")
            self.routes[("GET", path)] = func
            self.route_names[func.__name__] = path
            self.logger.debug("Registered route: GET %s", path)
            return func
        return decorator

    def url_for(self, name: str, **kwargs):
        path = self.route_names[name]
        return path.format(**kwargs)

    async def handle_client(self, reader, writer):
        # PULL CLIENT ADDRESS
        address = writer.get_extra_info("peername")
        self.logger.info("Connection from %s", address)

        try:
            # PARSE REQUEST
            method, path, version, headers, body = await self._parse_request(reader)
            self.logger.info("%s %s %s", method, path, version)
            self.logger.info("Headers: %s", headers)
            content_type = "text/html"

            # STATIC FILES
            if path.startswith("/static/"):
                file_path = self.static_dir / path.removeprefix("/static/")
            elif path.startswith("/media/"):
                file_path = self.static_dir / path.removeprefix("/media/")
            else:
                file_path = None

            if file_path is not None:
                print("STATIC PATH:", file_path)
                print("EXISTS:", file_path.exists())
                print("FILE PATH:", file_path)
                print("EXISTS:", file_path.exists())
                if file_path.exists() and file_path.is_file():
                    body = file_path.read_bytes()
                    status = "200 OK"
                    if file_path.suffix == ".css":
                        content_type = "text/css"
                    elif file_path.suffix == ".svg":
                        content_type = "image/svg+xml"
                    elif file_path.suffix in (".jpg", ".jpeg", ".png"):
                        content_type = "image/png"
                    else:
                        content_type = "application/octet-stream"
                else:
                    body = b"404 Not Found"
                    status = "404 Not Found"
                    content_type = "text/plain"
                self.logger.info("%s -> %s %s", path, status, content_type)
            else:
                # HANDLE REQUEST
                handler, kwargs = self._get_handler(request_method=method, request_path=path)
                if handler is None:
                    body = b"404 Not Found"
                    status = "404 Not Found"
                    self.logger.info("%s %s -> 404", method, path)
                else:
                    try:
                        result = await handler(**kwargs)
                        body = result.encode()
                        status = "200 OK"
                    except Exception:
                        self.logger.exception("Handler failed")
                        body = b"500 Internal Server Error"
                        status = "500 Internal Server Error"

            # SEND RESPONSE
            response = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode() + body
            writer.write(response)
            await writer.drain()

        finally:
            # CLOSE CONNECTION
            writer.close()
            await writer.wait_closed()
            self.logger.info("Connection closed: %s", address)

    async def _parse_request(self, reader):
        # PULL HEADER DATA AND SPLIT LINES
        header_data = await reader.readuntil(b"\r\n\r\n")
        lines = header_data.decode().split("\r\n")
        # PULL FIRST REQUEST LINE
        request_line = lines[0]
        method, path, version = request_line.split(" ", 2)

        # PULL REQUEST HEADERS
        headers = {}
        for line in lines[1:]:
            if not line:
                continue
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()

        # PULL REQUEST BODY
        body = b""
        content_length = int(headers.get("Content-Length", 0))
        if content_length:
            body = await reader.readexactly(content_length)

        return method, path, version, headers, body

    def _get_handler(self, request_method: str, request_path: str) -> tuple[Callable | None, dict]:
        for (route_method, route_path) in self.routes:
            if route_method != request_method:
                continue
            if len(route_path.split("/")) != len(request_path.split("/")):
                continue
            kwargs = {}
            for route_part, request_part in zip(route_path.split("/"), request_path.split("/")):
                if route_part == request_part:
                    continue
                if route_part.startswith("{") and route_part.endswith("}"):
                    kwargs[route_part.strip("{}")] = request_part
                    continue
                break
            else:
                handler = self.routes[(route_method, route_path)]
                return handler, kwargs
        return None, {}

    async def create_server(self, host: str, port: int):
        return await asyncio.start_server(self.handle_client, host, port)

    async def server_forever(self, host: str, port: int):
        server = await self.create_server(host, port)
        self.logger.info("Server running on http://%s:%s", host, port)
        async with server:
            await server.serve_forever()

    def run(self, host: str, port: int):
        asyncio.run(self.server_forever(host, port))

