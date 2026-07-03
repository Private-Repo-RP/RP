# © @BabiesIQ

from pyrogram import Client

import config

from .._logging import LOGGER

assistants = []
assistantids = []

class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="JanyAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )

    async def start(self):
        LOGGER(__name__).info(f"Starting Assistants...")
        if config.STRING1:
            await self.one.start()
            try:
                await self.one.join_chat("https://t.me/+gF7M1_0PC803ZjU9")
                await self.one.join_chat("https://t.me/YTM_Points")
            except:
                pass
            assistants.append(1)
            if config.LOGGER_ID and config.LOGGER_ID != 0:
                try:
                    await self.one.get_chat(config.LOGGER_ID)
                    await self.one.send_message(config.LOGGER_ID, "✅ Assistant Started Successfully!")
                    LOGGER(__name__).info("Assistant log message sent to LOGGER_ID.")
                except Exception as e:
                    LOGGER(__name__).warning(
                        f"Assistant could not send to log group ({type(e).__name__}: {e}). Continuing anyway."
                    )
            self.one.id = self.one.me.id
            self.one.name = self.one.me.mention
            self.one.username = self.one.me.username
            assistantids.append(self.one.id)
            LOGGER(__name__).info(f"Assistant Started as {self.one.name}")

    async def stop(self):
        LOGGER(__name__).info(f"Stopping Assistants...")
        try:
            if config.STRING1:
                await self.one.stop()
        except:
            pass