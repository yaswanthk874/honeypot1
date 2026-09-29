from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AttackLog(Base):
    __tablename__ = 'attack_logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_ip = Column(String(50), nullable=False)
    targeted_port = Column(Integer, nullable=False)
    service_mimicked = Column(String(50))
    payload = Column(Text)
    attacker_profile = Column(String(50))

class AttackerProfile(Base):
    __tablename__ = 'attacker_profiles'
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(50), unique=True, nullable=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_attacks = Column(Integer, default=0)
    classification = Column(String(50), default="unknown") # script kiddie, botnet, advanced
    frequent_ports = Column(String(100)) # comma separated list of ports
