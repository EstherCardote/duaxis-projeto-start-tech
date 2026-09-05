import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import Response
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
from relatorio_service import montar_pdf_relatorio


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


class PerguntaChat(BaseModel):
    mensagem: str


class CardRelatorio(BaseModel):
    rotulo: str = ""
    valor: str = ""
    texto: str = ""
    chips: list[str] = []
    barra: float | None = None
    largo: bool = False


class LinhaRelatorio(BaseModel):
    titulo: str = ""
    subtitulo: str = ""
    valor: str = ""
    rotulo_valor: str = ""
    selo: str = ""
    nota: str = ""
    detalhes: list[CardRelatorio] = []


class SecaoRelatorio(BaseModel):
    titulo: str = ""
    data: str = ""
    texto: str = ""
    paragrafos: list[str] = []
    cards: list[CardRelatorio] = []
    lista: list[str] = []
    linhas: list[LinhaRelatorio] = []


class PedidoRelatorio(BaseModel):
    secoes: list[SecaoRelatorio]


@app.get("/api/health")
def inicio():
    return {
        "status": "online",
        "sistema": "DUAXIS",
    }


def _saudacao_por_hora(hora):
    if 5 <= hora < 12:
        return "Bom dia"
    if 12 <= hora < 18:
        return "Boa tarde"
    return "Boa noite"


@app.get("/api/horario")
def horario():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    return {
        "timezone": "America/Sao_Paulo",
        "hora": agora.hour,
        "saudacao": _saudacao_por_hora(agora.hour),
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


@app.post("/api/relatorio")
def gerar_relatorio(pedido: PedidoRelatorio):
    secoes = [secao.model_dump() for secao in pedido.secoes]
    try:
        pdf_bytes, nome_arquivo = montar_pdf_relatorio(secoes)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nome_arquivo}"'
        },
    )


FRONTEND_DIR = ROOT_DIR / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )
