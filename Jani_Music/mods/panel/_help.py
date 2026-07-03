# © @BabiesIQ

from typing import Union  
from pyrogram import filters, types, enums  
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton  
  
from Jani_Music import app  
from Jani_Music.helpers import help_pannel  
from Jani_Music.helpers._store import get_lang  
from Jani_Music.helpers.wrap._lang import LanguageStart, languageCB  
from Jani_Music.helpers.kb._help import help_back_markup, private_help_panel  
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT  
from strings import get_string, helpers  
  
HELP_MAP = {  
    "1": helpers.HELP_1,  
    "3": helpers.HELP_3,  
    "6": helpers.HELP_6,  
    "7": helpers.HELP_7,  
    "10": helpers.HELP_10,  
    "11": helpers.HELP_11,  
    "12": helpers.HELP_12,  
    "13": helpers.HELP_13,  
    "15": helpers.HELP_15,  
}  
  
@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)  
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)  
async def helper_private(client: app, update: Union[types.Message, types.CallbackQuery]):  
    is_callback = isinstance(update, types.CallbackQuery)  
  
    if is_callback:  
        try:  
            await update.answer()  
        except:  
            pass  
  
        chat_id = update.message.chat.id  
        language = await get_lang(chat_id)  
        _ = get_string(language)  
  
        keyboard = help_pannel(_, True)  
        try:
            if update.message.media:
                await update.edit_message_caption(
                    caption=_["help_1"].format(SUPPORT_CHAT),
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                )
            else:
                await update.edit_message_text(
                    _["help_1"].format(SUPPORT_CHAT),
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                )
        except Exception:
            pass  
  
    else:  
        try:  
            await update.delete()  
        except:  
            pass  
  
        language = await get_lang(update.chat.id)  
        _ = get_string(language)  
        keyboard = help_pannel(_)  
  
        await update.reply_photo(  
            photo=START_IMG_URL,  
            caption=_["help_1"].format(SUPPORT_CHAT),  
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML,
        )  
  
@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)  
@LanguageStart  
async def help_com_group(client, message: Message, _):  
    keyboard = private_help_panel(_)  
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))  
  
@app.on_callback_query(filters.regex("^h:") & ~BANNED_USERS)  
@languageCB  
async def helper_cb(_, CallbackQuery, language):  
    try:  
        _, key = CallbackQuery.data.split(":")  
    except:  
        return await CallbackQuery.answer("Invalid!", show_alert=True)  
  
    text = HELP_MAP.get(key)  
    if not text:  
        return await CallbackQuery.answer("Invalid!", show_alert=True)  
  
    keyboard = help_back_markup(language)  
  
    try:
        if CallbackQuery.message.media:
            await CallbackQuery.edit_message_caption(
                caption=text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            await CallbackQuery.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )
    except Exception:
        pass
  
  
@app.on_callback_query(filters.regex('managebot123'))  
async def on_back_button(client, query):  
    parts = query.data.split(None, 1)  
    if len(parts) < 2:  
        return  
    cb = parts[1]  
  
    chat_id = query.message.chat.id  
    language = await get_lang(chat_id)  
    _ = get_string(language)  
  
    keyboard = help_pannel(_, True)  
  
    if cb == "settings_back_helper":
        try:
            if query.message.media:
                await query.edit_message_caption(
                    caption=_["help_1"].format(SUPPORT_CHAT),
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                )
            else:
                await query.edit_message_text(
                    _["help_1"].format(SUPPORT_CHAT),
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML,
                )
        except Exception:
            pass
