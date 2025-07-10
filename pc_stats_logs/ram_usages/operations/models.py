# operations.models.py

from typing import Optional, List
from pydantic import BaseModel

class PcStatsCreateData(BaseModel):
    pc_usage: Optional[float] = None
    pc_freq: Optional[float] = None
    ram_usage: Optional[float] = None
    ram_available: Optional[float] = None
    internet_receive: Optional[float] = None
    internet_sent: Optional[float] = None
class GpuStatsCreateData(BaseModel):
    gpu_id:int
    ram_usage: Optional[float] = None
    ram_available: Optional[float] = None
    temp: Optional[float] = None