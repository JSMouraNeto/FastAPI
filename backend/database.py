# database.py
from sqlmodel import create_engine, SQLModel

# O nome do arquivo do banco de dados principal da aplicação.
DATABASE_URL = "sqlite:///./database.db"

# Engine de conexão com o banco de dados principal.
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """
    Cria a tabela 'item' no arquivo database.db se ela não existir.
    """
    SQLModel.metadata.create_all(engine)
