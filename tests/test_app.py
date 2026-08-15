#!/usr/bin/env python3

import unittest
from noapp import App
from test_client import TestClient

class TestApp(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = App()

        @self.app.get('/')
        async def index(request):
            return "<h1>Hello</h1>"

        self.client = TestClient(self.app)
        await self.client.start()

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_root(self):
        response = await self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"<h1>Hello</h1>")

    async def test_missing_route_returns_404(self):
        response = await self.client.get("/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, b"404 Not Found")

if __name__ == "__main__":
    unittest.main()

