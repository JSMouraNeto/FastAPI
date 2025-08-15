# models.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    """
    Define a estrutura da tabela 'item' no banco de dados principal.
    A chave primária agora é um ID numérico autoincrementado.
    """
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    package_name: str
    uid: int
    pids: str
    metrics: str


# class Item2(SQLModel, table=True):
#     """
#     Define a estrutura da tabela 'item' no banco de dados principal.
#     A chave primária agora é um ID numérico autoincrementado.
#     """
#     timestamp: str = Field(default=None, primary_key=True, index=True)
#     uid: str
#     packagen_name = str
#     usagetime = str
#     delta_cpu_time = str
#     cpu_usage = float
#     rx_data = int
#     tx_data = int
