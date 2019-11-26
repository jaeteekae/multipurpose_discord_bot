from sqlalchemy import Column, Integer, String, Date, Interval, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class GCMember(Base):
	__tablename__ = "gcmember"

	id = Column(Integer, primary_key=True)
	discord_id = Column(Integer)
	nickname = Column(String)
	real_name = Column(String)
	# birthday = Column(Date)
	# timezone_id = Column(Integer, ForeignKey(timezone.id))

	# timezone = relationship("Timezone", back_populates="gcmember")

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