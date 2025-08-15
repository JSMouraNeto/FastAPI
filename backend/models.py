# models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Metrica(SQLModel, table=True):

    timestamp: str = Field(index=True, primary_key=True)
    usagetime: str
    delta_cpu_time: str
    cpu_usage: float
    rx_data: int
    tx_data: int
   
   
    item_id: Optional[int] = Field(default=None, foreign_key="item.id")
    # Propriedade de relacionamento para acessar o 'Item' pai a partir de uma 'Metrica'
    item: Optional["Item"] = Relationship(back_populates="metricas")

class Item(SQLModel, table=True):
   
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    package_name: str
    uid: int
    pids: str  # Mantemos o pids como está
   
    
    metricas: List["Metrica"] = Relationship(back_populates="item")


class MetricaRead(SQLModel):
   
    timestamp: str
    usagetime: str
    delta_cpu_time: str
    cpu_usage: float
    rx_data: int
    tx_data: int

class ItemReadWithMetrics(SQLModel):

    id: int
    package_name: str
    uid: int
    pids: str
    metricas: List[MetricaRead] = []

Metrica.model_rebuild()
Item.model_rebuild()