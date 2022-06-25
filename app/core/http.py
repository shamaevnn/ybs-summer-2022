from dataclasses import dataclass

import httpx


@dataclass
class HTTPCli:
    client: httpx.AsyncClient


http_cli: HTTPCli = HTTPCli(
    client=httpx.AsyncClient(timeout=30.0),
)


async def http_cli_init() -> None:
    global http_cli
    http_cli = HTTPCli(
        client=httpx.AsyncClient(timeout=60.0),
    )


async def http_cli_close() -> None:
    await http_cli.client.aclose()
