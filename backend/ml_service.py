from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent


modelo = joblib.load(
    BASE_DIR
    / "modelos"
    / "modelo_demanda_duaxis_final.pkl"
)

features = joblib.load(
    BASE_DIR
    / "modelos"
    / "features_demanda_duaxis_final.pkl"
)


vendas = pd.read_csv(
    BASE_DIR
    / "dados"
    / "vendas_urban_style.csv",
    sep=";"
)

produtos = pd.read_csv(
    BASE_DIR
    / "dados"
    / "produtos_urban_style.csv",
    sep=";"
)

estoque = pd.read_csv(
    BASE_DIR
    / "dados"
    / "estoque_urban_style.csv",
    sep=";"
)

def prever_demanda(produto_id):

    historico_produto = vendas[
        vendas["produto_id"] == produto_id
    ].copy()

    historico_produto["data_venda"] = pd.to_datetime(
        historico_produto["data_venda"]
    )

    historico_produto["periodo"] = (
        historico_produto["data_venda"]
        .dt.to_period("M")
    )

    mensal = (
        historico_produto
        .groupby("periodo")["quantidade"]
        .sum()
    )

    maio = mensal.get(
        pd.Period("2026-05"),
        0
    )

    junho = mensal.get(
        pd.Period("2026-06"),
        0
    )

    julho = mensal.get(
        pd.Period("2026-07"),
        0
    )

    produto = produtos[
        produtos["id"] == produto_id
    ].iloc[0]

    dados = {
        "mes": 8,
        "venda_mes_anterior": julho,
        "venda_2_meses": junho,
        "venda_3_meses": maio,
        "media_3_meses": (
            maio + junho + julho
        ) / 3,
        "tendencia": julho - junho,
        "preco_base": produto["preco_base"]
    }

    # Cria todas as colunas de categoria com valor 0
    for coluna in features:
        if coluna.startswith("categoria_"):
            dados[coluna] = 0

    # Descobre a categoria real do produto
    categoria_produto = produto["categoria"]

    # Monta o nome da coluna correspondente
    coluna_categoria = f"categoria_{categoria_produto}"

    # Marca a categoria correta com 1
    if coluna_categoria in dados:
        dados[coluna_categoria] = 1

    # Transforma o dicionário em DataFrame
    entrada = pd.DataFrame([dados])

    # Coloca as colunas exatamente na mesma ordem usada no treinamento
    entrada = entrada[features]

    # Faz a previsão
    previsao = modelo.predict(entrada)[0]

    # Retorna a previsão arredondada
    return round(previsao)

resultado = prever_demanda("PROD017")

print(resultado)