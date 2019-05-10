"""
Здесь тоже "изобрел" пару декораторов.
Но они вроде простые и от дублирования кода избавляют
"""

import asyncio
import json
import logging
import sys
from functools import wraps

import minechat_client.connector as connector


def timeout_wrapper(coro, timeout=2):
    """decorator, wraps coroutine in asyncio.wait_for.
    For entry points should be used before @entry_point"""
    @wraps(coro)
    async def wrapper(args):
        try:
            await asyncio.wait_for(coro(args), timeout)
        except asyncio.TimeoutError:
            print("Timeout. Try again later")
    return wrapper


def entry_point(coro):
    """decorator, wraps coroutine in simple (not async)
    function calling asyncio.run. Result could be passed
    into the argument parser like subcommand entry point
    """
    @wraps(coro)
    def wrapper(args):
        logging.basicConfig(level=logging.DEBUG)
        asyncio.run(coro(args))
    return wrapper


def sanitize(message, eol="\n"):
    """helper function.
    truncate space symbols at the beginning
    and at the end of string,
    then replace new lines inside the string
    and at last append new line at the end of string
    """
    return "{}{}".format(message.strip().replace("\n", " "), eol)


async def read(reader):
    """helper for reading from stream"""
    raw_data = await reader.readline()
    decoded_data = raw_data.decode("utf-8").strip()
    logging.debug(decoded_data)
    return decoded_data


async def send(writer, data: bytes or str):
    """helper for writing into stream"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    writer.write(data)
    await writer.drain()


async def authenticate(token, reader, writer):
    """authenticate user by token"""
    logging.debug("Authentication")
    await read(reader)  # log auth greetings
    await send(writer, "{}\n".format(token))
    logging.debug("Auth rusponse:")
    response = await read(reader)
    try:
        account_info = json.loads(response)
    except json.JSONDecodeError:
        logging.error("Mailformed response, please try again later")
    else:
        return account_info


@entry_point
@timeout_wrapper
async def register(args):
    """register new user"""
    async with connector.MinechatConnection(args.host, args.port) as (
        reader, writer
    ):
        await read(reader)  # log auth greetings
        await send(writer, b"\n")  # skip auth
        await read(reader)  # log registration greetings
        await send(writer, sanitize(args.name))  # send name
        response = await read(reader)
        try:
            account = json.loads(response)
        except json.JSONDecodeError:
            logging.error("Mailformed response, please try again later")
        else:
            print(
                ("Your were succesfully registered as {}, "
                 "your authorization token is: {}")
                .format(account["nickname"], account["account_hash"])
            )
            return account


@entry_point
@timeout_wrapper
async def send_message(args):
    """send message to minechat"""
    async with connector.MinechatConnection(args.host, args.port) as (
        reader, writer
    ):
        account_info = await authenticate(
            args.token, reader, writer
        )
        if account_info is None:
            print("Unknown token. Check you entered token correctly "
                  "or register the new account", file=sys.stderr)
            exit(1)
        # message doesn't appear in the chat if only one `\n` used
        logging.debug("Sending message")
        await send(writer, sanitize(args.message, eol="\n\n"))
        logging.debug("Message sent")
