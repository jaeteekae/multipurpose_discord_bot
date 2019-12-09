import json, os
from datetime import datetime
from data import data
from models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pdb

engine = create_engine('sqlite:///gcdb.db')
Session = sessionmaker(bind=engine)
session = Session()

pools = session.query(BettingPool).filter_by(finalized=True).all()

for p in pools:
	winning_bets = session.query(Bet).filter_by(pool=p, winning_bet=True).all()
	losing_bets = session.query(Bet).filter_by(pool=p, winning_bet=False).all()
	all_bets = session.query(Bet).filter_by(pool=p).all()

	for l in losing_bets:
		l.winnings = 0-l.crowns

	total_crowns = 0
	winners_bets_sum = 0

	for b in all_bets:
		total_crowns += b.crowns
	for b in winning_bets:
		winners_bets_sum += b.crowns

	# hand out the winnings
	for w in winning_bets:
		w.winnings = round(w.crowns/winners_bets_sum*total_crowns)
		
session.commit()


