# DUAXIS

Copiloto corporativo de IA para a empresa de demonstração **Urban Style** (varejo de roupas). O gestor pergunta em português e recebe números calculados no backend, com interpretação da IA.

O DUAXIS **não substitui** um ERP. Nesta versão as bases são CSVs sintéticos (agosto/2023 a julho/2026).

---

## O que você precisa ter instalado

- **Python 3.12, 3.13 ou 3.14**
- **Node.js** (para gerar o CSS com Tailwind)
- Uma chave da **Groq** (o chat não funciona sem ela)

No Windows, use o **PowerShell**. Os comandos abaixo assumem que você já está na pasta do repositório:

`duaxis-projeto-start-tech`

---

## 1. Ambiente Python

Na pasta raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install fpdf2
```

O `fpdf2` é usado para gerar o PDF do relatório. Se o `Activate.ps1` for bloqueado, rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

No macOS/Linux o activate é `source .venv/bin/activate`.

---

## 2. Chave da IA

O backend lê o arquivo **`backend/.env`** (não o da pasta raiz).

1. Copie o exemplo:

```powershell
Copy-Item .env.example backend\.env
```

2. Abra `backend/.env` e cole a chave:

```
GROQ_API_KEY=sua_chave_aqui
```

Sem essa chave, o Dashboard até abre, mas o Copiloto não responde.

---

## 3. CSS do frontend (primeiro uso ou quando mudar o visual)

Na pasta raiz, **com o venv tanto faz** — isso é Node:

```powershell
npm install
npm run build
```

Enquanto você edita `frontend/src/input.css`, deixe um terminal só para o Tailwind:

```powershell
npm run dev
```

Deixe esse terminal aberto. Ele recompila o CSS a cada salvamento.

---

## 4. Subir o backend

Abra **outro** terminal, ative o venv de novo e entre na pasta `backend`:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app:app --reload
```

Quando aparecer que o servidor está no ar, o sistema está em:

**http://127.0.0.1:8000/**

Páginas:

| Tela | Endereço |
|---|---|
| Dashboard | http://127.0.0.1:8000/ |
| Copiloto Corporativo | http://127.0.0.1:8000/copiloto-corporativo.html |
| Fontes de Dados | http://127.0.0.1:8000/fontes-de-dados.html |

O FastAPI serve o frontend em `frontend/dist`. Não precisa de outro servidor HTML.

Para parar o backend: `Ctrl + C` no terminal do uvicorn.

---

## Resumo do dia a dia

Dois terminais, os dois na pasta do projeto:

1. **CSS (opcional se você não for mexer em estilo):** `npm run dev`
2. **API + site:** venv ativo → `cd backend` → `python -m uvicorn app:app --reload`

Depois abra http://127.0.0.1:8000/ no navegador.

Pergunta de teste no copiloto:

`Qual foi o faturamento de junho de 2026?`

---

## Se algo falhar

| Sintoma | O que checar |
|---|---|
| `GROQ_API_KEY não encontrada` | O arquivo é `backend/.env`, não `.env` na raiz. |
| Tela sem estilo / CSS antigo | Rodar `npm run build` ou deixar `npm run dev` ligado e recarregar com F5. |
| `No module named 'app'` | O uvicorn precisa ser iniciado **de dentro** de `backend`. |
| `No module named 'fpdf'` | `pip install fpdf2` com o venv ativo. |
| Porta 8000 ocupada | Já existe um uvicorn rodando. Feche o outro terminal ou use `Ctrl + C`. |
| Copiloto não responde | Backend no ar? Chave Groq válida? Console do navegador (F12) mostra erro de rede? |

A data de demonstração do mundo Urban Style é **31 de julho de 2026**. Perguntas de fato histórico devem usar meses até essa data.
