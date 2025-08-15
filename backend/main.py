# main.py
import os
import tempfile
from datetime import datetime
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Query
from sqlmodel import Session, select, delete
from sqlalchemy import create_engine as sqlalchemy_create_engine, text
from sqlalchemy.orm import contains_eager
from typing import List, Annotated, Dict, Optional

from database import engine, create_db_and_tables
from models import Item, Metrica, ItemReadWithMetrics

app = FastAPI(
    title="API de Processamento de Dados",
    description="API para carregar e consultar dados de processos e suas métricas."
)

@app.on_event("startup")
def on_startup():
    print("Iniciando aplicação e verificando estrutura do banco de dados...")
    create_db_and_tables()
    print("Aplicação pronta.")

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/upload-db/")
def upload_and_process_database(
    file: UploadFile, 
    session: Session = Depends(get_session)
):
    if not file.filename.endswith((".sqlite", ".db")):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as tmp:
        tmp.write(file.file.read())
        source_db_path = tmp.name

    print(f"Arquivo temporário '{source_db_path}' criado. Processando...")
    source_engine = None
    
    try:
        print("Limpando dados antigos...")
        session.exec(delete(Metrica))
        session.exec(delete(Item))
        session.commit()

        source_engine = sqlalchemy_create_engine(f"sqlite:///{source_db_path}")
        
        final_items = {}
        final_metrics = {}

        with source_engine.connect() as source_connection:
            for table_name in ["processes1", "processes2", "processes3"]:
                print(f"Lendo e consolidando dados da tabela '{table_name}'...")
                query = text(f"SELECT PackageName, Uid, Metrics FROM {table_name}")
                
                for row in source_connection.execute(query):
                    final_items[row.PackageName] = {"package_name": row.PackageName, "uid": row.Uid}
                    
                    metric_entries = row.Metrics.strip().split(';')
                    for entry in metric_entries:
                        if not entry: continue
                        
                        parts = entry.split(':')
                        if len(parts) == 6:
                            try:
                                # Mantém o timestamp como a string original
                                final_metrics[parts[0]] = {
                                    "timestamp": parts[0],
                                    "usagetime": parts[1],
                                    "delta_cpu_time": parts[2],
                                    "cpu_usage": float(parts[3]),
                                    "rx_data": int(parts[4]),
                                    "tx_data": int(parts[5]),
                                    "package_name": row.PackageName
                                }
                            except (ValueError, IndexError):
                                print(f"  Aviso: Ignorando entrada de métrica mal formada: '{entry}'.")
        
        item_map = {}
        for item_data in final_items.values():
            new_item = Item(**item_data)
            session.add(new_item)
        session.commit()

        for item in session.exec(select(Item)).all():
            item_map[item.package_name] = item.id

        for metric_data in final_metrics.values():
            pkg_name = metric_data.pop("package_name")
            item_id = item_map.get(pkg_name)
            if item_id:
                new_metric = Metrica(**metric_data, item_id=item_id)
                session.add(new_metric)

        session.commit()
        print(f"Commit finalizado. {len(final_items)} itens e {len(final_metrics)} métricas únicas inseridas.")

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Falha ao processar o banco de dados: {e}")
    finally:
        if source_engine:
            source_engine.dispose()
        if os.path.exists(source_db_path):
            os.remove(source_db_path)

    return {
        "message": "Banco de dados processado e atualizado com sucesso.",
        "total_items_inseridos": len(final_items),
        "total_metricas_inseridas": len(final_metrics)
    }

@app.get("/process", response_model=Dict[str, List[ItemReadWithMetrics]])
def get_process_data(
    session: Session = Depends(get_session),
    # Descrições atualizadas para refletir o formato do timestamp original
    start: Optional[str] = Query(default=None, description="Timestamp inicial para o filtro (ex: 1750506177570)"),
    end: Optional[str] = Query(default=None, description="Timestamp final para o filtro (ex: 1750528388365)")
):
    query = select(Item).limit(10)

    if start or end:
        query = query.join(Metrica)
        if start:
            query = query.where(Metrica.timestamp >= start)
        if end:
            query = query.where(Metrica.timestamp <= end)
        
        query = query.options(contains_eager(Item.metricas))
    
    results = session.exec(query).unique().all()
    
    return {"processos": results}
