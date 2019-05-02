"""
Парсер также является точкой входа в приложение.
Не знаю насколько это правильно, взял такой подход из
официальной документации к модулю.

One particularly effective way of handling sub-commands
is to combine the use of the add_subparsers() method
with calls to set_defaults() so that each subparser 
knows which Python function it should execute.

https://docs.python.org/3/library/argparse.html
"""


import argparse
import os

from minechat_client.reader import main as read
from minechat_client.writer import register, send_message

DEFAULT_HOST = "minechat.dvmn.org"
DEFAULT_LISTENER_PORT = 5000
DEFAULT_HISTORY_PATH = "minechat.history"
DEFAULT_WRITER_PORT = 5050


def main():
    """parse command line args and call subcommand"""

    # main parser.
    # if subcommand not specified runs minechat reader
    parser = argparse.ArgumentParser(
        description="Minechat client",
    )
    parser.set_defaults(func=read)
    parser.add_argument(
        "--host",
        help="Minechat ip address or hostname to connect",
        required=False,
        type=str,
        default=os.getenv("MINECHAT_HOST", DEFAULT_HOST),
    )

    parser.add_argument(
        "--port",
        help="Minechat reader port",
        required=False,
        type=int,
        default=os.getenv("MINECHAT_LISTENER_PORT", DEFAULT_LISTENER_PORT),
    )

    parser.add_argument(
        "--history",
        help="Path to file with messages history",
        required=False,
        type=str,
        default=os.getenv("MINECHAT_HISTORY", DEFAULT_HISTORY_PATH)
    )

    # subparsers used for registration and sending messages
    subparsers = parser.add_subparsers()

    # registration parser, for `register` subcommand
    # overrides `--port` option
    registration_parser = subparsers.add_parser(
        "register", help="Register new user"
    )

    registration_parser.add_argument(
        "--port",
        help="Minechat writer port",
        required=False,
        type=int,
        default=os.getenv("MINECHAT_WRITER_PORT", DEFAULT_WRITER_PORT),
    )

    registration_parser.add_argument(
        "name",
        type=str,
        help="Preferred nickname",
    )

    registration_parser.set_defaults(
        func=register
    )

    # messageing parser, for `send` subcommand
    # also overrides `--port` options
    messaging_parser = subparsers.add_parser(
        "send", help="Send message in Minechat"
    )

    messaging_parser.add_argument(
        "message",
        type=str,
        help="Message text"
    )

    messaging_parser.add_argument(
        "--token",
        type=str,
        help="Authorization token",
        required=False,
        default=os.getenv("MINECHAT_AUTH_TOKEN", None)
    )

    messaging_parser.add_argument(
        "--port",
        help="Minechat writer port",
        required=False,
        type=int,
        default=os.getenv("MINECHAT_WRITER_PORT", DEFAULT_WRITER_PORT),
    )

    messaging_parser.set_defaults(
        func=send_message
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
