"""Command-line interface for the Bang websocket server."""

from __future__ import annotations

import argparse
import asyncio
import logging
from collections.abc import Sequence

from .server import BangServer


def main(argv: Sequence[str] | None = None) -> None:
    """Parse ``argv`` and launch the Bang websocket server.

    When ``--show-token`` is supplied, the function prints a join token for the
    configured server and exits without starting it.
    """

    parser = argparse.ArgumentParser(description="Start Bang websocket server")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--certfile", help="Path to SSL certificate", default=None)
    parser.add_argument("--keyfile", help="Path to SSL key", default=None)
    parser.add_argument("--token-key", help="Key for join tokens", default=None)
    parser.add_argument(
        "--show-token",
        action="store_true",
        help="Display join token and exit",
    )
    args = parser.parse_args(argv)

    server = BangServer(
        host=args.host,
        port=args.port,
        certfile=args.certfile,
        keyfile=args.keyfile,
        token_key=args.token_key,
    )

    if args.show_token:
        logging.info(server.generate_join_token())
        return

    asyncio.run(server.start())


if __name__ == "__main__":
    main()
