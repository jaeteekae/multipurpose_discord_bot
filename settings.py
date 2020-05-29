import secret
import os

TOKEN = secret.TOKEN
LC_CHANNEL_ID = secret.LC_CHANNEL_ID
RECEIPTS_CHANNEL_ID = secret.RECEIPTS_CHANNEL_ID
BIRTHDAY_CHANNEL_ID = secret.BIRTHDAY_CHANNEL_ID
PREFIX = "!"
TESTING_PREFIX = "&"

DATABASE_PATH = "sqlite:///gcdb.db"

DATA_FOLDER = "data"
STATIC_FOLDER = "imgs"
PRAISE_FOLDER = os.path.join(STATIC_FOLDER,"praise_gifs")
MAIN_GUILD_NAME = 'Ep3: The GC Tries Discord'

AWAY_FILE = os.path.join(DATA_FOLDER,"away.json")
AWAY_COLOR = 0x72FF7B # lime green

BDAY_FILE = os.path.join(DATA_FOLDER,"bdays.json")
BDAY_COLOR = 0x494ce5 # soft blue

GIF_FILE = os.path.join(DATA_FOLDER,"gif_shortcuts.json")
GIF_FOLDER = os.path.join(STATIC_FOLDER,"gifs")
GIF_COLOR = 0xa175c4 # soft purple

TMP_IMG_FOLDER = os.path.join(STATIC_FOLDER,"tmp")
RECEIPT_FILE = os.path.join(DATA_FOLDER,"receipts.json")
RECEIPT_COLOR = 0xc5fffc # pale blue

LINKS_FILE = os.path.join(DATA_FOLDER,"gen_links.json")

STATS_FILE = os.path.join(DATA_FOLDER,"stats.json")
STATS_COLOR = 0xede361 # soft yellow

BET_COLOR = 0xed041f # bright red

CONVERT_COLOR = 0xc84dd1 # dusty pink

OSHA_COLOR = 0xed041f # bright red

TESTING = False
PRODUCTION = not TESTING

