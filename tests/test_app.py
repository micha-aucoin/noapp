#!/usr/bin/env python3

import unittest
from noapp import App, Response
from test_client import TestClient

class TestApp(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.app = App()
        self.server = await self.app.create_server(
            host='127.0.0.1',
            port=0,
        )
        self.client = TestClient(server=self.server)

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def test_get_root(self):
        @self.app.get('/')
        async def index(request):
            resp =  Response()
            return resp.html("<h1>Hello</h1>")

        response = await self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"<h1>Hello</h1>")

    async def test_missing_route_returns_404(self):
        response = await self.client.get("/missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, b"404 Not Found")

    def test_url_for_root(self):
        @self.app.get('/')
        async def index(request):
            resp =  Response()
            return resp.html("<h1>Hello</h1>")

        result = self.app.url_for("index")
        self.assertEqual(result, "/")

    def test_url_for_with_path_parameter(self):
        @self.app.get("/posts/{post_id}")
        async def post_page(request, post_id):
            resp =  Response()
            return resp.text(post_id)

        result = self.app.url_for("post_page", post_id=12)
        self.assertEqual(result, "/posts/12")

    async def test_path_parameter_available_on_request(self):
        @self.app.get("/posts/{post_id}")
        async def post_page(request, post_id):
            resp =  Response()
            return resp.text(post_id)

        response = await self.client.get("/posts/12")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"12")

    async def test_route_with_multiple_path_parameters(self):
        @self.app.get("/users/{user_id}/posts/{post_id}")
        async def get_post(request, user_id, post_id):
            resp =  Response()
            return resp.text(f"{user_id}:{post_id}")

        response = await self.client.get("/users/7/posts/12")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"7:12")

    async def test_request_object_passed_to_handler(self):
        @self.app.get("/hello")
        async def hello(request):
            resp =  Response()
            return resp.text(request.path)

        response = await self.client.get("/hello")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"/hello")

    async def test_request_method_available(self):
        @self.app.get("/hello")
        async def hello(request):
            resp =  Response()
            return resp.text(request.method)

        response = await self.client.get("/hello")
        self.assertEqual(response.body, b"GET")

    async def test_request_headers_available(self):
        @self.app.get("/hello")
        async def hello(request):
            resp =  Response()
            return resp.text(request.headers["Host"])

        response = await self.client.get("/hello")
        self.assertEqual(response.body, b"127.0.0.1")

    async def test_request_with_path_parameter(self):
        @self.app.get("/posts/{post_id}")
        async def post_page(request, post_id):
            resp =  Response()
            return resp.text(f"{request.path}:{post_id}")

        response = await self.client.get("/posts/12")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"/posts/12:12")

if __name__ == "__main__":
    unittest.main()

