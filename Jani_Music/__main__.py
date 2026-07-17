# © @BabiesIQ

import asyncio
import importlib
import os

from aiohttp import web
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Jani_Music import LOGGER, app, userbot
from Jani_Music.engine._vclient import Jany
from Jani_Music.misc import sudo
from Jani_Music.mods import ALL_MODULES
from Jani_Music.helpers._store import get_banned_users, get_gbanned
from config import BANNED_USERS


async def _health(request):
    return web.Response(text="OK")


async def start_health_server():
    port = int(os.environ.get("PORT", 8080))
    _app = web.Application()
    _app.router.add_get("/", _health)
    _app.router.add_get("/health", _health)
    runner = web.AppRunner(_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    LOGGER(__name__).info(f"Railway health server started on port {port}")


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("Jani_Music.mods" + all_module)
    LOGGER("Jani_Music.mods").info("Successfully Imported Modules...")
    await userbot.start()
    await Jany.start()
    try:
        await asyncio.wait_for(
            Jany.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"),
            timeout=15,
        )
    except (NoActiveGroupCall, asyncio.TimeoutError):
        pass
    except Exception:
        pass
    await Jany.decorators()
    LOGGER("Jani_Music").info(
        "Bot Started Successfully 🎉 ©️ | @BabiesIQ |"
    )
    # Railway health check — PORT par respond karna zaroori hai
    await start_health_server()
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("Jani_Music").info("Stopping Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
