from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ml_service import analisar_reposicao
from ia_service import processar_pergunta_usuario


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
class PerguntaChat(BaseModel):
    mensagem: str

# Função que interpreta a pergunta do usuário e retorna a intenção e o ID do produto
@app.get("/")
def inicio():

    return {
        "status": "online",
        "sistema": "DUAXIS"
    }

# Endpoint para analisar a reposição de um produto específico
@app.get("/api/previsao/{produto_id}")
def previsao_produto(produto_id: str):

    resultado = analisar_reposicao(
        produto_id
    )

    return resultado


# Endpoint para processar a pergunta do usuário e retornar o resultado da análise de reposição
@app.post("/api/chat")
def chat(pergunta: PerguntaChat):

    resultado = processar_pergunta_usuario(
        pergunta.mensagem
    )

    return resultado
        