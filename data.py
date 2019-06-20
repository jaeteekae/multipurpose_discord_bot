import settings
import json

class DataObj:
    away = {}
    bdays = {}
    gifs = {}
    links = {}

    def __init__(self):
        try:
            with open(settings.AWAY_FILE,'r') as f:
                obj = json.load(f)
                self.away = obj
        except:
            pass

        try:
            with open(settings.GIF_FILE,'r') as f:
                obj = json.load(f)
                self.gifs = obj
        except:
            pass

        try:
            with open(settings.LINKS_FILE,'r') as f:
                obj = json.load(f)
                self.links = obj
        except:
            pass


        try:
            with open(settings.BDAY_FILE,'r') as f:
                obj = json.load(f)
                self.bdays = obj
        except:
            pass


data = DataObj()