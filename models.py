from sqlalchemy import Column, Table, Integer, String, Boolean, Date, Interval, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class GCMember(Base):
	__tablename__ = "gcmember"

	id = Column(Integer, primary_key=True)
	discord_id = Column(Integer)
	nickname = Column(String)
	real_name = Column(String)
	crowns = Column(Integer)

	owned_pools = relationship(lambda: BettingPool, foreign_keys=lambda: BettingPool.owner_id, back_populates="owner")
	bets = relationship(lambda: Bet, foreign_keys=lambda: Bet.better_id, back_populates="better")
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

	bets = relationship(lambda: Bet, foreign_keys=lambda: Bet.pool_id, back_populates="pool")

	def __repr__(self):
		return self.name

class Bet(Base):
	__tablename__ = "bets"

	id = Column(Integer, primary_key=True)
	text = Column(String)
	crowns = Column(Integer)
	winning_bet = Column(Boolean)

	better_id = Column(Integer, ForeignKey("gcmember.id"))
	better = relationship("GCMember", back_populates="bets", foreign_keys=[better_id])

	pool_id = Column(Integer, ForeignKey("bettingpool.id"))
	pool = relationship("BettingPool", back_populates="bets", foreign_keys=[pool_id])
	
	winnings = Column(Integer)

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