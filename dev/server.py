#!/usr/bin/env python3

import sys
import time
from pathlib import Path

# Add the project root to Python's module search path so we can import main.py
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from main import app

reload_id = str(time.time_ns())
@app.get("/__reload_check__")
async def reload_check(request):
    return reload_id

RELOAD_SCRIPT = """
<script>
    let reloadId = null;
    let failures = 0;
    async function checkReload() {
        try {
            const response = await fetch("/__reload_check__");
            if (!response.ok) {
                throw new Error();
            }
            failures = 0;
            const currentId = await response.text();
            if (reloadId === null) {
                reloadId = currentId;
            } else if (currentId !== reloadId) {
                location.reload();
            }
        } catch {
            failures++;
            if (failures >= 7) {
                clearInterval(intervalId);
            }
        }
    }
    const intervalId = setInterval(checkReload, 1000);
</script>
"""

original_get_route_response = app._get_route_response

async def get_route_response(request):
    response = await original_get_route_response(request)
    if response.content_type == "text/html":
        html = response.body.decode()
        html = html.replace("</body>", RELOAD_SCRIPT + "</body>")
        response.body = html.encode()
    return response

app._get_route_response = get_route_response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
