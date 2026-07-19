# © @BabiesIQ

import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters
load_dotenv()
API_ID = int(getenv("API_ID", None))
API_HASH = getenv("API_HASH", None)
BOT_TOKEN = getenv("BOT_TOKEN", None)
OWNER_USERNAME = getenv("OWNER_USERNAME","")
BOT_USERNAME = getenv("BOT_USERNAME" , "")
BOT_NAME = getenv("BOT_NAME" , "")
ASSUSERNAME = getenv("ASSUSERNAME" , "")
BASE_URL = getenv("BASE_URL", "https://api.babiesiq.tech")
API_KEY = getenv("API_KEY", "ADMINBABYX_BE1B36999F84D14C6DAF231FA4768710577EC9A1")
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://Jani_Sanatani_Power:RamRP@jani.elxnxrd.mongodb.net/?appName=Jani")
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
_logger_id_raw = getenv("LOGGER_ID", "0")
LOGGER_ID = int(_logger_id_raw) if _logger_id_raw and _logger_id_raw.lstrip("-").isdigit() else 0
OWNER_ID = int(getenv("OWNER_ID", None))
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/Private-Repo-RP/RP",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None) or getenv("GITHUB_TOKEN", None)
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/Jani_Ki_Jaanu") 
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+dOsOTS5XXMxhNzJh")
SOURCE = getenv("SOURCE", "https://t.me/Jani_Sanatani_Power")
CHAT = getenv("CHAT", "")
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))
STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", "")
STRING3 = getenv("STRING_SESSION3", "")
STRING4 = getenv("STRING_SESSION4", "")
STRING5 = getenv("STRING_SESSION5", "")
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
START_IMG_URL = getenv(
    "START_IMG_URL", "https://litter.catbox.moe/lgmcdj.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://litter.catbox.moe/lgmcdj.jpg"
)
PLAYLIST_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
STATS_IMG_URL = "https://litter.catbox.moe/kafl29.jpg"
TELEGRAM_AUDIO_URL = "https://litter.catbox.moe/kafl29.jpg"
TELEGRAM_VIDEO_URL = "https://litter.catbox.moe/kafl29.jpg"
STREAM_IMG_URL = "https://telegra.ph/file/03efec694e41e891b29dc.jpg"
IQ_Proxy = "https://i.ytimg.com/vi"
SOUNCLOUD_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
YOUTUBE_IMG_URL = "https://telegra.ph/file/4dc854f961cd3ce46899b.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://telegra.ph/file/6c741a6bc1e1663ac96fc.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://telegra.ph/file/6c741a6bc1e1663ac96fc.jpg"
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))
if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )

__all__ = [
    "IQ_Proxy",
]
