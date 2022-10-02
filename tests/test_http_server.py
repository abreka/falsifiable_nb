import pytest

from falsifiable_nb.http_server import tcp_server_for, port_range, random_port_sampler


def test_tcp_server_for():
    from http.server import SimpleHTTPRequestHandler

    # Assumes that port 14000 is free
    server = tcp_server_for(
        "localhost", port_range(14000, 14010), SimpleHTTPRequestHandler
    )
    assert server is not None
    assert server.server_address == ("127.0.0.1", 14000)
    server.server_close()

    # Connect again
    server = tcp_server_for(
        "localhost", port_range(14000, 14010), SimpleHTTPRequestHandler
    )
    assert server is not None
    assert server.server_address == ("127.0.0.1", 14000)
    server.server_close()


def test_random_port_sampler():
    items = set(random_port_sampler(8000, 8010, 5))
    assert len(items) == 5

    with pytest.raises(ValueError):
        list(random_port_sampler(8000, 8010, 11))
