import asyncio
import logging

from typing import Callable
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Request:
    def __init__(self):
        self.method = ""
        self.path = ""
        self.version = ""
        self.headers = {}
        self.body = b""

class Response:
    def __init__(self):
        self.status = ""
        self.content_type = ""
        self.body = b""

class App:
    def __init__(self):
        self.routes = {}
        self.route_names = {}
        self.file_mounts = {}
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

    def mount(self, path: str, directory: Path):
        self.file_mounts[path] = directory

    async def handle_client(self, reader, writer):
        address = writer.get_extra_info("peername")
        try:
            try:
                request = await self._parse_request(reader)
            except asyncio.IncompleteReadError:
                return

            if request.path.startswith(tuple(self.file_mounts)):
                response = self._get_file_response(request.path)
            else:
                response = await self._get_route_response(request)

            self.logger.debug("Connection from %s", address)
            self.logger.debug("Headers: %s", request.headers)
            self.logger.info(
                "%s %s -> %s %s %s bytes",
                request.method,
                request.path,
                response.status,
                response.content_type,
                len(response.body),
            )

            response_message = (
                f"HTTP/1.1 {response.status}\r\n"
                f"Content-Type: {response.content_type}\r\n"
                f"Content-Length: {len(response.body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode() + response.body
            writer.write(response_message)
            await writer.drain()

        finally:
            writer.close()
            await writer.wait_closed()
            self.logger.debug("Connection closed: %s", address)

    async def _parse_request(self, reader) -> Request:
        request = Request()
        # PULL HEADER DATA AND SPLIT LINES
        header_data = await reader.readuntil(b"\r\n\r\n")
        lines = header_data.decode().split("\r\n")
        # PULL FIRST REQUEST LINE
        request_line_parts = lines[0].split(" ", 2)
        request.method = request_line_parts[0]
        request.path = request_line_parts[1]
        request.version = request_line_parts[2]
        # PULL REQUEST HEADERS
        for line in lines[1:]:
            if not line:
                continue
            key, value = line.split(":", 1)
            request.headers[key.strip()] = value.strip()
        # PULL REQUEST BODY
        content_length = int(request.headers.get("Content-Length", 0))
        if content_length:
            request.body = await reader.readexactly(content_length)
        return request

    def _get_file_response(self, path: str) -> Response:
        response = Response()
        # SET FILE PATH BASED ON REQUEST PATH
        for prefix, directory in self.file_mounts.items():
            if path.startswith(prefix):
                file_path = directory / path.removeprefix(prefix)
                break
        # CHECK FILE PATH EXISTS
        if not file_path.exists() or not file_path.is_file():
            response.status = "404 Not Found"
            response.content_type = "text/plain"
            response.body = b"404 Not Found"
            return response
        # READ STATIC FILE
        response.body = file_path.read_bytes()
        # SET CONTENT TYPE
        if file_path.suffix == ".css":
            response.content_type = "text/css"
        elif file_path.suffix == ".svg":
            response.content_type = "image/svg+xml"
        elif file_path.suffix == ".png":
            response.content_type = "image/png"
        elif file_path.suffix in (".jpg", ".jpeg"):
            response.content_type = "image/jpeg"
        else:
            response.content_type = "application/octet-stream"
        # OK RETURN
        response.status = "200 OK"
        return response

    async def _get_route_response(self, request: Request) -> Response:
        response = Response()
        for (method, route) in self.routes:
            if method != request.method:
                continue
            route_parts = route.split("/")
            request_parts = request.path.split("/")
            if len(route_parts) != len(request_parts):
                continue

            kwargs = {}
            kwargs["request"] = request
            for part in zip(route_parts, request_parts):
                if part[0].startswith("{") and part[0].endswith("}"):
                    kwargs[part[0].strip("{}")] = part[1]
                elif part[0] != part[1]:
                    break
            else:
                handler = self.routes[(method, route)]
                try:
                    result = await handler(**kwargs)
                    response.status = "200 OK"
                    response.content_type = "text/html"
                    response.body = result.encode()
                    return response
                except Exception:
                    self.logger.exception(f"Handler {handler.__name__} failed")
                    response.status = "500 Internal Server Error"
                    response.content_type = "text/plain"
                    response.body = b"500 Internal Server Error"
                    return response

        response.status = "404 Not Found"
        response.content_type = "text/plain"
        response.body = b"404 Not Found"
        return response

    async def create_server(self, host: str, port: int):
        return await asyncio.start_server(self.handle_client, host, port)

    async def server_forever(self, host: str, port: int):
        server = await self.create_server(host, port)
        self.logger.info("Server running on http://%s:%s", host, port)
        async with server:
            await server.serve_forever()

    def run(self, host: str, port: int):
        asyncio.run(self.server_forever(host, port))

