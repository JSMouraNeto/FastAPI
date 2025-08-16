# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
## No Windows:

        venv\Scripts\activate

## No macOS/Linux:
        source venv/bin/activate

2. Instalação das DependênciasCom o ambiente virtual ativado, instale as bibliotecas necessárias.

        pip install fastapi uvicorn sqlmodel

3. Executando a AplicaçãoExecute o servidor da API com o Uvicorn.

        uvicorn main:app --reload
acesse http://127.0.0.1:8000/docs. 

Você verá a documentação interativa da API (Swagger UI).
