#!/usr/bin/env python3

import unittest
from noapp import App
from test_client import TestClient

class TestApp(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = App()
        self.client = TestClient(self.app)
        await self.client.start()

    async def asyncTearDown(self):
        await self.client.close()

    async def test_get_root(self):
        @self.app.get('/')
        async def index():
            return "<h1>Hello</h1>"

        response = await self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"<h1>Hello</h1>")

    async def test_missing_route_returns_404(self):
        response = await self.client.get("/missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, b"404 Not Found")

    def test_url_for_root(self):
        @self.app.get('/')
        async def index():
            return "<h1>Hello</h1>"

        result = self.app.url_for("index")
        self.assertEqual(result, "/")

    def test_get_handler_exact_route(self):
        @self.app.get('/')
        async def index():
            return "<h1>Hello</h1>"

        handler, kwargs = self.app._get_handler("GET", "/")
        self.assertIsNotNone(handler)
        self.assertEqual(handler.__name__, "index")
        self.assertEqual(kwargs, {})

    def test_get_handler_wrong_path_returns_none(self):
        handler, kwargs = self.app._get_handler("GET", "/users/12")
        self.assertIsNone(handler)
        self.assertEqual(kwargs, {})

    def test_get_handler_missing_segment_returns_none(self):
        @self.app.get("/posts/{post_id}")
        async def post_page(post_id):
            return post_id

        handler, kwargs = self.app._get_handler("GET", "/posts")
        self.assertIsNone(handler)
        self.assertEqual(kwargs, {})

    def test_get_handler_extra_segment_returns_none(self):
        @self.app.get("/posts/{post_id}")
        async def post_page(post_id):
            return post_id

        handler, kwargs = self.app._get_handler("GET", "/posts/12/comments")
        self.assertIsNone(handler)
        self.assertEqual(kwargs, {})

    async def test_path_parameter_available_on_request(self):
        @self.app.get("/posts/{post_id}")
        async def post_page(post_id):
            return post_id

        response = await self.client.get("/posts/12")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"12")

    async def test_route_with_multiple_path_parameters(self):
        @self.app.get("/users/{user_id}/posts/{post_id}")
        async def get_post(user_id, post_id):
            return f"{user_id}:{post_id}"

        response = await self.client.get("/users/7/posts/12")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"7:12")

if __name__ == "__main__":
    unittest.main()

