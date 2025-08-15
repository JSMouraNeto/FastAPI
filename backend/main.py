# main.py
import os
import tempfile
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from sqlmodel import Session, select, delete
from sqlalchemy import create_engine as sqlalchemy_create_engine, text
from typing import List, Annotated, Dict

# Importe os objetos e modelos necessários
from database import engine, create_db_and_tables
from models import Item

app = FastAPI(
    title="API de Processamento de Dados",
    description="API para carregar e consultar dados de processos."
)

@app.on_event("startup")
def on_startup():
    """
    Função de inicialização simplificada:
    Apenas garante que a tabela 'Item' exista no banco de dados 'database.db'.
    A lógica de popular o banco foi movida para a rota de upload.
    """
    print("Iniciando aplicação e verificando estrutura do banco de dados...")
    create_db_and_tables()
    print("Aplicação pronta.")

def get_session():
    """
    Dependência do FastAPI para fornecer uma sessão do banco de dados por requisição.
    """
    with Session(engine) as session:
        yield session

@app.post("/upload-db/")
def upload_and_process_database(
    file: UploadFile, 
    session: Session = Depends(get_session)
):
    """
    Processa um arquivo .sqlite enviado:
    1. Limpa os dados antigos da tabela 'Item'.
    2. Lê as tabelas 'processes1', 'processes2', 'processes3' em ordem.
    3. Insere os novos dados no banco de dados principal ('database.db').
    """
    if not file.filename.endswith((".sqlite", ".db")):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Por favor, envie um arquivo .sqlite ou .db.")

    # Usa um arquivo temporário para segurança e gerenciamento
    with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as tmp:
        tmp.write(file.file.read())
        source_db_path = tmp.name

    print(f"Arquivo temporário '{source_db_path}' criado. Processando...")
    source_engine = None # Define fora do try para estar no escopo do finally
    try:
        # 1. Limpa a tabela 'Item' no banco de dados principal antes de inserir novos dados
        print("Limpando dados antigos da tabela 'Item'...")
        session.exec(delete(Item))
        session.commit()

        # 2. Conecta ao banco de dados de origem (arquivo temporário)
        source_engine = sqlalchemy_create_engine(f"sqlite:///{source_db_path}")
        
        # Tabelas a serem processadas em ordem para simular o timestamp
        tables_to_process = ["processes1", "processes2", "processes3"]
        items_added_count = 0

        with source_engine.connect() as source_connection:
            for table_name in tables_to_process:
                print(f"Lendo dados da tabela '{table_name}'...")
                query = text(f"""
                    SELECT 
                        PackageName AS package_name, 
                        Uid AS uid, 
                        Pids AS pids, 
                        Metrics AS metrics 
                    FROM {table_name}
                """)
                
                results = source_connection.execute(query)
                
                # Converte cada linha em um objeto Item e adiciona à sessão
                for row in results:
                    item_obj = Item(**row._asdict())
                    session.add(item_obj)
                    items_added_count += 1
        
        # 3. Salva (commit) todos os novos itens no banco de dados de uma vez
        session.commit()
        print(f"Commit realizado. Total de {items_added_count} itens inseridos.")

    except Exception as e:
        # Em caso de erro, reverte a transação e levanta uma exceção HTTP
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Falha ao processar o banco de dados: {e}")
    finally:
        # 4. Garante que o engine seja descartado para liberar o arquivo
        if source_engine:
            source_engine.dispose()
            print("Engine do banco de dados de origem descartado.")

        # 5. Garante que o arquivo temporário seja sempre removido
        if os.path.exists(source_db_path):
            os.remove(source_db_path)
            print(f"Arquivo temporário '{source_db_path}' removido.")

    return {
        "message": "Banco de dados processado e atualizado com sucesso.",
        "total_items_inseridos": items_added_count
    }

@app.get("/process", response_model=Dict[str, List[Item]])
def get_process_data(session: Session = Depends(get_session)):
    """
    Retorna um único objeto JSON contendo uma lista de todos os
    itens da base de dados 'database.db'.
    """
    items = session.exec(select(Item)).all()
    return {"processos": items}
