#!/usr/bin/env python3

import unittest
import tempfile
from pathlib import Path
from noapp import Template
from noapp.template_tokenizer import tokenizer, TokenKind
from noapp.template_parser import (
    parser,
    TextNode,
    VariableNode,
    FunctionCallNode,
    MethodCallNode,
    ExtendsNode,
    BlockNode,
    ForNode,
    render_nodes
)
from test_objects import Author, Post


class TestTokenizer(unittest.TestCase):
    def test_tokenize_variable(self):
        source = (
            "{% extends 'layout.html' %}"
            "{% block content %}"
            "<h1>Hello, World! {{ hello.world }} </h1>"
            "{% endblock content %}"
        )
        tokens = tokenizer(source)
        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].kind, TokenKind.BLOCK)
        self.assertEqual(tokens[0].value, "extends 'layout.html'")
        self.assertEqual(tokens[1].kind, TokenKind.BLOCK)
        self.assertEqual(tokens[1].value, "block content")
        self.assertEqual(tokens[2].kind, TokenKind.TEXT)
        self.assertEqual(tokens[2].value, "<h1>Hello, World! ")
        self.assertEqual(tokens[3].kind, TokenKind.VARIABLE)
        self.assertEqual(tokens[3].value, "hello.world")
        self.assertEqual(tokens[4].kind, TokenKind.TEXT)
        self.assertEqual(tokens[4].value, " </h1>")
        self.assertEqual(tokens[5].kind, TokenKind.BLOCK)
        self.assertEqual(tokens[5].value, "endblock content")


class TestParser(unittest.TestCase):
    def test_parse_variable(self):
        nodes = parser(tokenizer("{{ hello.world }}"))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], VariableNode)
        self.assertEqual(nodes[0].expression, "hello.world")

    def test_parse_extends(self):
        nodes = parser(tokenizer("{% extends 'layout.html' %}"))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], ExtendsNode)
        self.assertEqual(nodes[0].filename, "layout.html")

    def test_parse_block(self):
        source = (
            "{% block content %}"
            "<h1>Hello</h1>"
            "{% endblock content %}"
        )
        nodes = parser(tokenizer(source))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], BlockNode)
        self.assertEqual(nodes[0].name, "content")
        self.assertEqual(len(nodes[0].children), 1)
        self.assertIsInstance(nodes[0].children[0], TextNode)
        self.assertEqual(nodes[0].children[0].value, "<h1>Hello</h1>")

    def test_parse_for_loop(self):
        source = (
            "{% for post in posts %}"
            "<h1>{{ post.title }}</h1>"
            "{% endfor %}"
        )
        nodes = parser(tokenizer(source))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], ForNode)
        self.assertEqual(nodes[0].item_name, "post")
        self.assertEqual(nodes[0].iterable_name, "posts")
        self.assertEqual(len(nodes[0].children), 3)
        self.assertIsInstance(nodes[0].children[0], TextNode)
        self.assertIsInstance(nodes[0].children[1], VariableNode)
        self.assertIsInstance(nodes[0].children[2], TextNode)

    def test_render_for_loop(self):
        source = (
            "{% for post in posts %}"
            "<h1>{{ post.title }}</h1>"
            "{% endfor %}"
        )
        posts = [
            Post(id=1, author=Author(id=1, username="John"), title="First", content="Hello", date_posted="1999-12-31"),
            Post(id=2, author=Author(id=2, username="Jane"), title="Second", content="World", date_posted="2000-01-01"),
        ]
        nodes = parser(tokenizer(source))
        result = render_nodes(nodes, context={"posts": posts})
        self.assertEqual(result, "<h1>First</h1><h1>Second</h1>")

    def test_render_for_loop_inside_block(self):
        source = (
            "{% block content %}"
            "{% for post in posts %}"
            "<h1>{{ post.title }}</h1>"
            "{% endfor %}"
            "{% endblock content %}"
        )
        posts = [
            Post(id=1, author=Author(id=1, username="John"), title="First", content="Hello", date_posted="1999-12-31"),
            Post(id=2, author=Author(id=2, username="Jane"), title="Second", content="World", date_posted="2000-01-01"),
        ]
        nodes = parser(tokenizer(source))
        result = render_nodes(nodes, context={"posts": posts})
        self.assertEqual(result, "<h1>First</h1><h1>Second</h1>")

    def test_parse_function_call(self):
        source = "{{ url_for('home') }}"
        nodes = parser(tokenizer(source))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], FunctionCallNode)
        self.assertEqual(nodes[0].function_name, "url_for")
        self.assertEqual(nodes[0].args, "'home'")

    def test_parse_method_call(self):
        source = '{{ post.date_posted.strftime("%B %d, %Y") }}'
        nodes = parser(tokenizer(source))
        self.assertEqual(len(nodes), 1)
        self.assertIsInstance(nodes[0], MethodCallNode)
        self.assertEqual(nodes[0].object_expression, "post.date_posted")
        self.assertEqual(nodes[0].method_name, "strftime")
        self.assertEqual(nodes[0].args, '"%B %d, %Y"')

    def test_render_function_call_node(self):
        source = "{{ url_for('home') }}"
        def url_for(name):
            return "/" + name
        nodes = parser(tokenizer(source))
        result = render_nodes(nodes, context={"url_for": url_for})
        self.assertEqual(result, "/home")

    def test_render_method_call_node(self):
        source = '{{ post.date_posted.strftime("%B %d, %Y") }}'
        post = Post(
            id=1,
            author=Author(id=1, username="John"),
            title="Hello",
            content="World",
            date_posted="1999-12-31",
        )
        nodes = parser(tokenizer(source))
        result = render_nodes(nodes, context={"post": post})
        self.assertEqual(result, "December 31, 1999")

    def test_render_function_call_with_keyword_argument(self):
        source = "{{ url_for('post_page', post_id=post.id) }}"
        post = Post(
            id=12,
            author=Author(id=1, username="John"),
            title="Hello",
            content="World",
            date_posted="1999-12-31",
        )
        def url_for(name, **kwargs):
            return f"/posts/{kwargs['post_id']}"
        nodes = parser(tokenizer(source))
        result = render_nodes(nodes, context={"post": post, "url_for": url_for})
        self.assertEqual(result, "/posts/12")

    def test_render_function_call_with_multiple_positional_arguments(self):
        source = "{{ make_url('users', 'profile') }}"
        def make_url(first, second):
            return f"/{first}/{second}"
        nodes = parser(tokenizer(source))
        result = render_nodes(nodes, context={"make_url": make_url})
        self.assertEqual(result, "/users/profile")


class TestTemplate(unittest.TestCase):
    def test_render_template_with_parent_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            (template_dir / "layout.html").write_text(
                "<html>"
                "<body>"
                "{% block content %}"
                "<p>Default</p>"
                "{% endblock content %}"
                "</body>"
                "</html>"
            )
            (template_dir / "home.html").write_text(
                "{% extends 'layout.html' %}"
                "{% block content %}"
                "<h1>Hello</h1>"
                "{% endblock content %}"
            )
            template = Template(directory=template_dir)
            result = template.response("home.html")
            self.assertEqual(result, "<html><body><h1>Hello</h1></body></html>")

    def test_render_template_with_multiple_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            (template_dir / "layout.html").write_text(
                "<html>"
                "<head>"
                "{% block title %}Default{% endblock title %}"
                "</head>"
                "<body>"
                "{% block content %}Default{% endblock content %}"
                "</body>"
                "</html>"
            )
            (template_dir / "home.html").write_text(
                "{% extends 'layout.html' %}"
                "{% block title %}Home{% endblock title %}"
                "{% block content %}<h1>Hello</h1>{% endblock content %}"
            )
            template = Template(directory=template_dir)
            result = template.response("home.html")
            self.assertEqual(result, "<html><head>Home</head><body><h1>Hello</h1></body></html>",)

    def test_render_template_with_for_loop(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            (template_dir / "layout.html").write_text(
                "<html>"
                "<body>"
                "{% block content %}"
                "{% endblock content %}"
                "</body>"
                "</html>"
            )
            (template_dir / "home.html").write_text(
                "{% extends 'layout.html' %}"
                "{% block content %}"
                "{% for post in posts %}"
                "<h2>{{ post.title }}</h2>"
                "<p>{{ post.author.username }}</p>"
                "<p>{{ post.content }}</p>"
                "{% endfor %}"
                "{% endblock content %}"
            )
            posts = [
                Post(id=1, author=Author(id=1, username="John"), title="First", content="Hello", date_posted="1999-12-31"),
                Post(id=2, author=Author(id=2, username="Jane"), title="Second", content="World", date_posted="2000-01-01"),
            ]
            template = Template(directory=template_dir)
            result = template.response("home.html", posts=posts)
            self.assertEqual(
                result,
                "<html><body>"
                "<h2>First</h2>"
                "<p>John</p>"
                "<p>Hello</p>"
                "<h2>Second</h2>"
                "<p>Jane</p>"
                "<p>World</p>"
                "</body></html>",
            )

    def test_render_real_home_template(self):
        template_dir = Path(__file__).parent.parent / "templates"
        template = Template(directory=template_dir)

        posts = [
            Post(id=12, author=Author(id=7, username="JohnDoe", image_path="/tmp"), title="First Post", content="Hello World", date_posted="1999-12-31"),
            Post(id=13, author=Author(id=8, username="JaneDoe", image_path="/tmp"), title="Second Post", content="Another post", date_posted="2000-01-01"),
        ]

        def url_for(name, **kwargs):
            if name == "home":
                return "/"
            if name == "post_page":
                return f"/posts/{kwargs['post_id']}"
            if name == "user_post_page":
                return f"/users/{kwargs['user_id']}"
            raise ValueError(f"Unknown route: {name}")

        result = template.response(
            "home.html",
            title="Home",
            posts=posts,
            url_for=url_for,
        )
        self.assertIn("<title>Home</title>", result)
        self.assertIn("JohnDoe", result)
        self.assertIn("JaneDoe", result)
        self.assertIn("First Post", result)
        self.assertIn("Second Post", result)
        self.assertIn("December 31, 1999", result)
        self.assertIn("January 01, 2000", result)
        self.assertIn('href="/posts/12"', result)
        self.assertIn('href="/posts/13"', result)
        self.assertIn('href="/users/7"', result)
        self.assertIn('href="/users/8"', result)

    def test_render_layout_home_url(self):
        template_dir = Path(__file__).parent.parent / "templates"
        template = Template(directory=template_dir)

        def url_for(name, **kwargs):
            if name == "home":
                return "/"
            raise ValueError(name)

        result = template.response(
            "layout.html",
            title="Home",
            url_for=url_for,
        )
        self.assertIn('href="/"', result)


if __name__ == "__main__":
    unittest.main()

