import http.server
import socketserver
from pathlib import Path
from typing import Iterable, Generator
import random
import threading
import click


def serve_dir(dir_path: Path, port_sampler: Iterable[int], host: str = "localhost"):
    # Create a simple http request handler with the given directory as the root
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dir_path), **kwargs)

    httpd = tcp_server_for(host, port_sampler, Handler)
    host, port = httpd.server_address
    click.echo(f"Serving at http://{host}:{port}")

    t = threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return t


def port_range(start: int, end: int) -> Iterable[int]:
    """
    Create an iterable of ports from start to end (inclusive).
    """
    return range(start, end + 1)


def random_port_sampler(
    lb: int, ub: int, n: int, seed=None
) -> Generator[int, None, None]:
    """
    Create an iterable of random ports.
    """
    if ub - lb < n:
        raise ValueError(f"Not enough ports to sample from (ub - lb < n)")

    candidates = range(lb, ub)
    sampled = set()
    rng = random.Random(seed)
    while len(sampled) < n:
        port = rng.choice(candidates)
        if port not in sampled:
            yield port
            sampled.add(port)


def tcp_server_for(
    host: str, port_sampler: Iterable[int], req_handler
) -> socketserver.TCPServer:
    """
    Create a TCP server for the given host and using a port sampler.

    :param host: the host to listen on
    :param port_sampler: an iterable of ports to try sequentially
    :param req_handler: the handler for the TCP server
    :return: the TCP server
    """
    for port in port_sampler:
        try:
            return socketserver.TCPServer((host, port), req_handler)
        except OSError as e:
            # TODO: verify this works on Windows and MacOS
            if "in use" not in str(e):
                raise
            else:
                port += 1
