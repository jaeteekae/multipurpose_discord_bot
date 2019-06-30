import secret
import os

TOKEN = secret.TOKEN
LC_CHANNEL_ID = secret.LC_CHANNEL_ID
RECEIPTS_CHANNEL_ID = secret.RECEIPTS_CHANNEL_ID
PREFIX = "!"

DATA_FOLDER = "data"

AWAY_FILE = os.path.join(DATA_FOLDER,"away.json")
AWAY_COLOR = 0x72FF7B # lime green

BDAY_FILE = os.path.join(DATA_FOLDER,"bdays.json")
BDAY_COLOR = 0x494ce5 # soft blue

GIF_FILE = os.path.join(DATA_FOLDER,"gif_shortcuts.json")
GIF_FOLDER = "gifs"
GIF_COLOR = 0xa175c4 # soft purple

LINKS_FILE = os.path.join(DATA_FOLDER,"gen_links.json")

STATS_FILE = os.path.join(DATA_FOLDER,"stats.json")
STATS_COLOR = 0xede361 # soft yellow

CONVERT_COLOR = 0xc84dd1 # dusty pink