from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .ml_service import analisar_reposicao


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def inicio():

    return {
        "status": "online",
        "sistema": "DUAXIS"
    }


@app.get("/api/previsao/{produto_id}")
def previsao_produto(produto_id: str):

    resultado = analisar_reposicao(
        produto_id
    )

    return resultado