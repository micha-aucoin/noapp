#!/usr/bin/env python3

import logging
from pathlib import Path
from noapp import App, Template

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s", 
)

templates_dir = Path(__file__).parent / "templates"
template = Template(directory=templates_dir)
app = App()

@app.get("/")
async def index(request):
    return template.response(
        "layout.html",
        title="what up!",
        heading="Hello, World!",
    )

def main():
    app.run(host="127.0.0.1", port=8080)

if __name__ == "__main__":
    main()

