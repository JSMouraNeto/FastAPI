# models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Metrica(SQLModel, table=True):
    timestamp: datetime = Field(index=True, primary_key=True)
    usagetime: str
    delta_cpu_time: str
    cpu_usage: float
    rx_data: int
    tx_data: int
    
    item_id: Optional[int] = Field(default=None, foreign_key="item.id")
    item: Optional["Item"] = Relationship(back_populates="metricas")

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    package_name: str
    uid: int
    
    metricas: List["Metrica"] = Relationship(back_populates="item")

class MetricaRead(SQLModel):
    timestamp: datetime
    usagetime: str
    delta_cpu_time: str
    cpu_usage: float
    rx_data: int
    tx_data: int

class ItemReadWithMetrics(SQLModel):
    id: int
    package_name: str
    uid: int
    metricas: List[MetricaRead] = []

Metrica.model_rebuild()
Item.model_rebuild()