import settings
import json, os
from datetime import datetime

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

    def write_to_disk(self):
        self.remove_old_links()
        with open(settings.AWAY_FILE,'w') as f:
            json.dump(self.away,f)
        with open(settings.GIF_FILE,'w') as f:
            json.dump(self.gifs,f)
        with open(settings.LINKS_FILE,'w') as f:
            json.dump(self.links,f)

    def remove_old_links(self):
        now = datetime.now()
        old = []
        for key, val in self.links.items():
            then = datetime.fromtimestamp(val)
            if (now-then).days>0:
                old.append(key)

        for link in old:
            self.links.pop(link)


data = DataObj()