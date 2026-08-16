import asyncio
import logging

class App:
    def __init__(self):
        self.routes = {}
        self.logger = logging.getLogger(__name__)

    def get(self, path: str):
        def decorator(func):
            self.routes[("GET", path)] = func
            self.logger.debug("Registered route: GET %s", path)
            return func
        return decorator

    def url_for(self, name: str, **kwargs):
        # breakpoint()
        # (Pdb) n;; l;; pp locals()
        for (method, path), handler in self.routes.items():
            if handler.__name__ == name:
                for key, value in kwargs.items():
                    path = path.replace(
                        "{" + key + "}",
                        str(value),
                    )
                return path
        raise KeyError(f"Route not found: {name}")

    async def handle_client(self, reader, writer):
        # PULL CLIENT ADDRESS
        address = writer.get_extra_info("peername")
        self.logger.info("Connection from %s", address)

        # PARSE REQUEST
        method, path, version, headers, body = await self._parse_request(reader)
        self.logger.info("%s %s %s", method, path, version)
        self.logger.info("Headers: %s", headers)

        # HANDLE REQUEST
        handler = self.routes.get((method, path))
        if handler is None:
            body = b"404 Not Found"
            status = "404 Not Found"
            self.logger.info("%s %s -> 404", method, path)
        else:
            result = await handler(None)
            body = result.encode()
            status = "200 OK"

        # SEND RESPONSE
        response = (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode() + body
        writer.write(response)
        await writer.drain()

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
            body = await reader.readexactly(content_lenght)

        return method, path, version, headers, body


    async def create_server(self, host: str, port: int):
        return await asyncio.start_server(self.handle_client, host, port)

    async def server_forever(self, host: str, port: int):
        server = await self.create_server(host, port)
        self.logger.info("Server running on http://%s:%s", host, port)
        async with server:
            await server.serve_forever()

    def run(self, host: str, port: int):
        asyncio.run(self.server_forever(host, port))

