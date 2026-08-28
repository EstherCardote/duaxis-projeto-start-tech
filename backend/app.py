import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ml_service import analisar_reposicao
from ia_service import processar_pergunta_com_tools


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PerguntaChat(BaseModel):
    mensagem: str


@app.get("/api/health")
def inicio():
    return {
        "status": "online",
        "sistema": "DUAXIS",
    }


@app.get("/api/previsao/{produto_id}")
def previsao_produto(produto_id: str):
    return analisar_reposicao(produto_id)


@app.post("/api/chat")
def chat(pergunta: PerguntaChat):
    return processar_pergunta_com_tools(pergunta.mensagem)


FRONTEND_DIR = ROOT_DIR / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )
