import settings
import json, os
from datetime import datetime

# Yes I know I should be using a proper database at this point ¯\_(ツ)_/¯
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
            if 'emojis' not in self.stats:
                self.stats['emojis'] = {}
            self.stats_initted = True
        except:
            self.stats = {}
            self.stats_initted = False

    def set_stats(self, stats):
        self.stats = stats
        self.stats_initted = True

    def set_guild(self, guild):
        self.guild = guild

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
        new_day = {}
        self.stats['days'].append(new_day)

        if len(self.stats['days']>30):
            oldest_day = self.stats['days'][0]
            self.stats['days'] = self.stats['days'][1:]

            ltd = self.stats['all_time']
            for personid, messages in oldest_day:
                person = ltd[personid]
                for channel, num in messages.items():
                    if channel in person:
                        person[channel] += num
                    else:
                        person[channel] = num

    def turnover_hour(self):
        self.stats['hours'].append({})
        if len(self.stats['hours'])>25:
            self.stats['hours'] = self.stats['hours'][-24:]

    def track_message(self, channelid, personid):
        today = self.stats['days'][-1]
        this_hour = self.stats['hours'][-1]

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

        if personid not in this_hour:
            this_hour[personid] = {channelid: 1}
        else:
            # first post by personid in channelid of the day
            if channelid not in this_hour[personid]:
                this_hour[personid][channelid] = 1
            # not the first post, so increment
            else:
                this_hour[personid][channelid] += 1

    def track_emoji(self, msg):
        emostats = self.stats['emojis']
        while('<:' in msg):
            msg = msg[msg.find('<:')+2:]
            msg = msg[msg.find(':')+1:]
            emojid = msg[:msg.find('>')]

            if emojid in emostats:
                emostats[emojid] += 1
            else:
                emostats[emojid] = 1

    def track_emoji_react(self, emoji):
        eid = str(emoji.id)
        emostats = self.stats['emojis']

        if eid in emostats:
            emostats[eid] += 1
        else:
            emostats[eid] = 1

    def filter_bots(self, s):
        stats = []
        for e in s:
            entry = e.copy()
            pids = e.keys()
            for p in pids:
                memobj = data.guild.get_member(int(p))
                if not memobj or memobj.bot:
                    entry.pop(p)
            stats.append(entry)
        return stats

    def get_day_stats(self):
        s = self.stats['hours'][-24:]
        return self.filter_bots(s)

    def get_week_stats(self):
        s = self.stats['days'][-7:]
        return self.filter_bots(s)

    def get_month_stats(self):
        s = self.stats['days']
        return self.filter_bots(s)

    def get_all_stats(self):
        stats = self.stats['days'].copy()
        allt = self.stats['all_time'].copy()
        stats.append(allt)
        return self.filter_bots(stats)


data = DataObj()