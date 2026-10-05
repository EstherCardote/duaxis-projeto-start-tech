import hmac as hmac_stdlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, hmac as crypto_hmac
from dotenv import load_dotenv
from fastapi import Header, HTTPException
from passlib.context import CryptContext

BASE_DIR = Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"
HMAC_ARQUIVO = BASE_DIR / "seguranca" / "hmac_esperado.json"

load_dotenv(BASE_DIR / ".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SESSAO_HORAS = 8


def _segredo_hmac():
    segredo = os.getenv("HMAC_SECRET", "").strip()
    if not segredo:
        raise RuntimeError(
            "HMAC_SECRET não encontrada no backend/.env. "
            "Essa chave assina os CSVs contra manipulação."
        )
    return segredo.encode("utf-8")


def hmac_sha256(mensagem: bytes) -> str:
    assinador = crypto_hmac.HMAC(_segredo_hmac(), hashes.SHA256())
    assinador.update(mensagem)
    return assinador.finalize().hex()


def _arquivos_csv():
    return sorted(DADOS_DIR.glob("*.csv"))


def calcular_hmac_bases():
    registros = {}
    for caminho in _arquivos_csv():
        registros[caminho.name] = hmac_sha256(caminho.read_bytes())
    return registros


def gerar_arquivo_hmac():
    HMAC_ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    registros = calcular_hmac_bases()
    HMAC_ARQUIVO.write_text(
        json.dumps(registros, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return registros


def verificar_integridade_bases():
    atuais = calcular_hmac_bases()
    if not HMAC_ARQUIVO.exists():
        gerar_arquivo_hmac()
        print(
            "Arquivo de integridade HMAC criado em "
            f"{HMAC_ARQUIVO}. Nas próximas subidas o backend "
            "recusa CSV adulterado."
        )
        return atuais

    esperados = json.loads(HMAC_ARQUIVO.read_text(encoding="utf-8"))
    if atuais != esperados:
        raise RuntimeError(
            "Integridade das bases falhou (HMAC). "
            "Algum CSV foi alterado. Se a mudança for "
            "intencional, rode no backend: "
            "python security_service.py"
        )
    return atuais


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    if not senha or not senha_hash:
        return False
    return pwd_context.verify(senha, senha_hash)


def autenticar_gestor(usuario: str, senha: str) -> str:
    esperado_usuario = os.getenv("GESTOR_USUARIO", "").strip()
    senha_hash = os.getenv("GESTOR_SENHA_HASH", "").strip()
    if not esperado_usuario or not senha_hash:
        raise RuntimeError(
            "GESTOR_USUARIO ou GESTOR_SENHA_HASH ausentes no .env."
        )
    if usuario.strip() != esperado_usuario:
        raise ValueError("Usuário ou senha inválidos.")
    if not verificar_senha(senha, senha_hash):
        raise ValueError("Usuário ou senha inválidos.")
    return esperado_usuario


def emitir_token(usuario: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(hours=SESSAO_HORAS)
    exp_ts = str(int(expira.timestamp()))
    nonce = secrets.token_hex(8)
    payload = f"{usuario}.{exp_ts}.{nonce}"
    assinatura = hmac_sha256(payload.encode("utf-8"))
    return f"{payload}.{assinatura}"


def validar_token(token: str):
    if not token or token.count(".") < 3:
        return None
    usuario, exp_ts, nonce, assinatura = token.split(".", 3)
    payload = f"{usuario}.{exp_ts}.{nonce}"
    esperada = hmac_sha256(payload.encode("utf-8"))
    if not hmac_stdlib.compare_digest(assinatura, esperada):
        return None
    try:
        expira = datetime.fromtimestamp(int(exp_ts), tz=timezone.utc)
    except ValueError:
        return None
    if datetime.now(timezone.utc) > expira:
        return None
    esperado_usuario = os.getenv("GESTOR_USUARIO", "").strip()
    if usuario != esperado_usuario:
        return None
    return usuario


def exigir_gestor(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Faça login como gestor para continuar.",
        )
    token = authorization.split(" ", 1)[1].strip()
    usuario = validar_token(token)
    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada.",
        )
    return usuario


if __name__ == "__main__":
    gerar_arquivo_hmac()
    print(f"HMAC atualizado: {HMAC_ARQUIVO}")
