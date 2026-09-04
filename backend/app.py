import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dashboard_service import (
    montar_kpis_dashboard,
    montar_grafico_faturamento,
    montar_grafico_lucro,
)

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

@app.get("/api/dashboard")
def dashboard(data_inicio: str | None = None, data_fim: str | None = None):
    return montar_kpis_dashboard(data_inicio, data_fim)


@app.get("/api/dashboard/faturamento")
def dashboard_faturamento(
    data_inicio: str | None = None,
    data_fim: str | None = None,
):
    try:
        return montar_grafico_faturamento(data_inicio, data_fim)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro


@app.get("/api/dashboard/lucro")
def dashboard_lucro(
    data_inicio: str | None = None,
    data_fim: str | None = None,
):
    try:
        return montar_grafico_lucro(data_inicio, data_fim)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

@app.post("/api/chat")
def chat(pergunta: PerguntaChat):

    data_hora_pergunta = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    )

    resultado = processar_pergunta_com_tools(
        pergunta.mensagem
    )

    resultado["data_hora_pergunta"] = (
        data_hora_pergunta.isoformat(
            timespec="seconds"
        )
    )

    return resultado


FRONTEND_DIR = ROOT_DIR / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )
