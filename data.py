import settings
import json, os
from datetime import datetime

class DataObj:

    def __init__(self):
        if not os.path.isdir(settings.DATA_FOLDER):
            os.makedirs(settings.DATA_FOLDER)

        try:
            with open(settings.AWAY_FILE,'r') as f:
                obj = json.load(f)
                self.away = obj
        except:
            self.away = {}

        try:
            with open(settings.GIF_FILE,'r') as f:
                obj = json.load(f)
                self.gifs = obj
        except:
            self.gifs = {}

        try:
            with open(settings.LINKS_FILE,'r') as f:
                obj = json.load(f)
                self.links = obj
        except:
            self.link = {}

        try:
            with open(settings.BDAY_FILE,'r') as f:
                obj = json.load(f)
                self.bdays = obj
        except:
            self.bdays = {}

        try:
            with open(settings.STATS_FILE,'r') as f:
                obj = json.load(f)
                self.stats = obj
            self.stats_initted = True
        except:
            self.stats = {}
            self.stats_initted = False

    def set_stats(self, stats):
        self.stats = stats
        self.stats_initted = True

    def write_to_disk(self):
        self.remove_old_links()
        with open(settings.AWAY_FILE,'w') as f:
            json.dump(self.away,f)
        with open(settings.GIF_FILE,'w') as f:
            json.dump(self.gifs,f)
        with open(settings.LINKS_FILE,'w') as f:
            json.dump(self.links,f)
        with open(settings.STATS_FILE,'w') as f:
            json.dump(self.stats,f)

    def remove_old_links(self):
        now = datetime.now()
        old = []
        for key, val in self.links.items():
            then = datetime.fromtimestamp(val)
            if (now-then).days>0:
                old.append(key)

        for link in old:
            self.links.pop(link)

    def turnover_stats(self):
        # if it's the start of a new month
        if datetime.now().day == 1:
            ltd = self.stats['all_time']
            # consolidate data
            for day in self.stats['days']:
                for personid, messages in day.items():
                    person = ltd[personid]
                    for channel, num in messages.items():
                        if channel in person:
                            person[channel] += num
                        else:
                            person[channel] = num
            self.stats['days'] = []

        new_day = {}
        self.stats['days'].append(new_day)

    def track_message(self, channelid, personid):
        today = self.stats['days'][-1]

        # first post by personid of the day
        if personid not in today:
            today[personid] = {channelid: 1}
        else:
            # first post by personid in channelid of the day
            if channelid not in today[personid]:
                today[personid][channelid] = 1
            # not the first post, so increment
            else:
                today[personid][channelid] += 1



data = DataObj()