from sqlalchemy import Column, Integer, String, Boolean, Date, Interval, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class GCMember(Base):
	__tablename__ = "gcmember"

	id = Column(Integer, primary_key=True)
	discord_id = Column(Integer)
	nickname = Column(String)
	real_name = Column(String)

	owned_pools = relationship(lambda: BettingPool, foreign_keys=lambda: BettingPool.owner_id, back_populates="owner")
	won_pools = relationship(lambda: BettingPool, foreign_keys=lambda: BettingPool.winner_id, back_populates="winner")

	# betting_wins = relationship("BettingPool", back_populates="gcmember")
	# bets_made = relationship("Bet", back_populates="gcmember")
	# birthday = Column(Date)
	# timezone_id = Column(Integer, ForeignKey(timezone.id))

	# timezone = relationship("Timezone", back_populates="gcmember")

class BettingPool(Base):
	__tablename__ = "bettingpool"

	id = Column(Integer, primary_key=True)
	name = Column(String)
	created_at = Column(Date)
	finalized = Column(Boolean)

	owner_id = Column(Integer, ForeignKey("gcmember.id"))
	owner = relationship("GCMember", back_populates="owned_pools", foreign_keys=[owner_id])

	winner_id = Column(Integer, ForeignKey("gcmember.id"))
	winner = relationship("GCMember", back_populates="won_pools", foreign_keys=[winner_id])

	# bets = relationship("Bet", back_populates="bettingpool")

	def __repr__(self):
		return self.name

# class Bet(Base):
# 	__tablename__ = "bets"

# 	id = Column(Integer, primary_key=True)
# 	text = Column(String)
# 	crowns = Column(Integer)

# 	better_id = Column(Integer, ForeignKey("gcmember.id"))
# 	# better = relationship("GCMember", back_populates="bets")

# 	bettingpool_id = Column(Integer, ForeignKey("bettingpool.id"))
# 	bettingpool = relationship("BettingPool", back_populates="bets")

# class Timezone(Base):
# 	__tablename__ = "timezone"

# 	id = Column(Integer, primary_key=True)
# 	utc = Column(Integer)
# 	utc_timedelta = Column(Interval)
# 	initialism = Column(String)

# 	members = relationship("GCMember", back_populates="timezone")

# class Receipt(Base):
# 	receipter_id = Column(Integer) # foreign key
# 	author_id = Column(Integer) # foreign key
# 	url = Column(string)
# 	rec_text = Column(string)
# 	# receipted_at = whatever datetime now here
# 	# attachments?