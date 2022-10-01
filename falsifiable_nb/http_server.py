import http.server
import socketserver
from pathlib import Path

import click


def serve_dir(
    dir_path: Path, initial_port: int = 8000, fail_on_first_bad_port: bool = False
):
    # Create a simple http request handler with the given directory as the root
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dir_path), **kwargs)

    port = initial_port
    for i in range(100):
        try:
            httpd = socketserver.TCPServer(("", port), Handler)
            click.echo(f"Serving at http://localhost:{port}")

            # Serve forever in a new thread
            import threading

            t = threading.Thread(target=httpd.serve_forever, daemon=True).start()
            return t
        except OSError as e:
            # TODO: verify this works on Windows and MacOS
            if fail_on_first_bad_port or "in use" not in str(e):
                raise
            else:
                port += 1
