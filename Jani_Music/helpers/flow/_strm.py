# © @BabiesIQ

import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto

import config
from Jani_Music import YouTube, app
from Jani_Music.engine._vclient import Jany
from Jani_Music.misc import db
from Jani_Music.helpers._store import add_active_video_chat, is_active_chat
from Jani_Music.helpers._exc import AssistantErr
from Jani_Music.helpers.kb import aq_markup, close_markup, stream_markup, stream_markup_timer
from Jani_Music.helpers._paste import BABYBin
from Jani_Music.helpers.flow._que import put_queue, put_queue_index
from Jani_Music.helpers._thumb import get_thumb

async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return
    if forceplay:
        await Jany.force_stop_stream(chat_id)
    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue
            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search, False if spotify else True)
            except:
                continue
            if str(duration_min) == "None":
                continue
            if duration_sec > config.DURATION_LIMIT:
                continue
            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=status, videoid=True
                    )
                except:
                    raise AssistantErr(_["play_14"])
                await Jany.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )
                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                    forceplay=forceplay,
                )
                img = await get_thumb(vidid)
                button = stream_markup_timer(_, chat_id, "00:00", duration_min)
                cap = _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                )
                try:
                    await mystic.edit_media(InputMediaPhoto(media=img, caption=cap))
                    try:
                        await mystic.edit_reply_markup(InlineKeyboardMarkup(button))
                    except Exception:
                        pass
                    run = mystic
                except Exception:
                    run = await app.send_photo(
                        original_chat_id,
                        photo=img,
                        has_spoiler=True,
                        caption=cap,
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
        if count == 0:
            return
        else:
            link = await BABYBin(msg)
            lines = msg.count("\n")
            if lines >= 17:
                car = os.linesep.join(msg.split(os.linesep)[:17])
            else:
                car = msg
            upl = close_markup(_)
            return await app.send_photo(
                original_chat_id,
                caption=_["play_21"].format(position, link),
                reply_markup=upl,
            )
    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        status = True if video else None
        try:
            file_path, direct = await YouTube.download(
                vidid, mystic, videoid=True, video=status
            )
        except:
            raise AssistantErr(_["play_14"])
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Jany.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail,
            )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            img = await get_thumb(vidid)
            button = stream_markup_timer(_, chat_id, "00:00", duration_min)
            cap = _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23],
                duration_min,
                user_name,
            )
            try:
                await mystic.edit_media(InputMediaPhoto(media=img, caption=cap))
                try:
                    await mystic.edit_reply_markup(InlineKeyboardMarkup(button))
                except Exception:
                    pass
                run = mystic
            except Exception:
                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    has_spoiler=True,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(button),
                )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Jany.join_call(chat_id, original_chat_id, file_path, video=None)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                forceplay=forceplay,
            )
            button = stream_markup_timer(_, chat_id, "00:00", duration_min)
            cap = _["stream_1"].format(config.SUPPORT_CHAT, title[:23], duration_min, user_name)
            try:
                await mystic.edit_media(InputMediaPhoto(media=config.SOUNCLOUD_IMG_URL, caption=cap))
                try:
                    await mystic.edit_reply_markup(InlineKeyboardMarkup(button))
                except Exception:
                    pass
                run = mystic
            except Exception:
                run = await app.send_photo(
                    original_chat_id,
                    has_spoiler=True,
                    photo=config.SOUNCLOUD_IMG_URL,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(button),
                )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Jany.join_call(chat_id, original_chat_id, file_path, video=status)
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            if video:
                await add_active_video_chat(chat_id)
            button = stream_markup_timer(_, chat_id, "00:00", duration_min)
            cap = _["stream_1"].format(link, title[:23], duration_min, user_name)
            photo = config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL
            try:
                await mystic.edit_media(InputMediaPhoto(media=photo, caption=cap))
                try:
                    await mystic.edit_reply_markup(InlineKeyboardMarkup(button))
                except Exception:
                    pass
                run = mystic
            except Exception:
                run = await app.send_photo(
                    original_chat_id,
                    photo=photo,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(button),
                )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        thumbnail = result["thumb"]
        duration_min = "Live Track"
        status = True if video else None
        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await app.send_message(
                chat_id=original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise AssistantErr(_["str_3"])
            await Jany.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail if thumbnail else None,
            )
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            img = await get_thumb(vidid)
            button = stream_markup(_, chat_id)
            cap = _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23],
                duration_min,
                user_name,
            )
            try:
                await mystic.edit_media(InputMediaPhoto(media=img, caption=cap))
                try:
                    await mystic.edit_reply_markup(InlineKeyboardMarkup(button))
                except Exception:
                    pass
                run = mystic
            except Exception:
                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    has_spoiler=True,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(button),
                )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
    elif streamtype == "index":
        link = result
        title = "ɪɴᴅᴇx ᴏʀ ᴍ3ᴜ8 ʟɪɴᴋ"
        duration_min = "00:00"
        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await mystic.edit_caption(
                caption=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await Jany.join_call(
                chat_id,
                original_chat_id,
                link,
                video=True if video else None,
            )
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            button = stream_markup(_, chat_id)
            cap = _["stream_2"].format(user_name)
            try:
                await mystic.edit_media(InputMediaPhoto(media=config.STREAM_IMG_URL, caption=cap))
                try:
                    await mystic.edit_reply_markup(InlineKeyboardMarkup(button))
                except Exception:
                    pass
                run = mystic
            except Exception:
                run = await app.send_photo(
                    original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    has_spoiler=True,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(button),
                )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
