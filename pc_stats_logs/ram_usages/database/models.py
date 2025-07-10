# database/models.py
from typing import Any
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, BigInteger, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
Base = declarative_base()


# def to_dict(obj: Base) -> dict[str, Any]:
#     return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
def to_dict(obj: Base) -> dict[str, Any]:
    """
    Converts a SQLAlchemy model instance to a dictionary,
    using the Python attribute names (keys) for the dictionary keys.
    """
    # Corrected: Use c.key (Python attribute name) instead of c.name (database column name)
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}

class PcStats(Base):
    __tablename__ = "pc_stats"
    time = Column('time',DateTime, primary_key=True, default=datetime.datetime.now)
    pc_usage = Column('pc_usage',Float, nullable = True)
    pc_freq = Column('pc_freq',Float, nullable = True)
    
    ram_usage = Column('ram_usage', Float, nullable = True)
    ram_available = Column('ram_available', Float, nullable = True)
    
    internet_receive = Column('internet_receive', Float, nullable = True)
    internet_sent = Column('internet_sent', Float, nullable=True)

class GpuStats(Base):
    __tablename__ = "gpu_stats"
    time = Column('time',DateTime, primary_key=True, default=datetime.datetime.now)
    gpu_id = Column('gpu_id',Integer, nullable = False)
    ram_usage = Column('ram_usage', Float, nullable = True)
    ram_available = Column('ram_available', Float, nullable = True)
    temp = Column('temp', Float, nullable = True)