import asyncio

class TestResponse:
    def __init__(self, status_code: int, headers: dict, body: bytes):
        self.status_code = status_code
        self.headers = headers
        self.body = body

class TestClient:
    def __init__(self, server):
        self.server = server
        self.host = self.server.sockets[0].getsockname()[0]
        self.port = self.server.sockets[0].getsockname()[1]

    async def get(self, path: str):
        reader, writer = await asyncio.open_connection(
            self.host,
            self.port,
        )
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"\r\n"
        )
        writer.write(request.encode())
        await writer.drain()

        raw_response = await reader.read()

        writer.close()
        await writer.wait_closed()
        return self._parse_response(raw_response)

    def _parse_response(self, raw_response: bytes):
        header_data, body = raw_response.split(b"\r\n\r\n", 1)
        lines = header_data.decode().split("\r\n")

        status_line = lines[0]
        version, status_code, reason = status_line.split(" ", 2)

        headers = {}

        for line in lines[1:]:
            name, value = line.split(":", 1)
            headers[name.strip()] = value.strip()

        return TestResponse(
            status_code=int(status_code),
            headers=headers,
            body=body,
        )

