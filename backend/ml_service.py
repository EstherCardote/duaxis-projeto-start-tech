from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent


modelo = joblib.load(BASE_DIR
    / "modelos"
    / "modelo_demanda_duaxis_final.pkl")

features = joblib.load(BASE_DIR
    / "modelos"
    / "features_demanda_duaxis_final.pkl")

vendas = pd.read_csv(BASE_DIR
    / "dados"
    / "vendas_urban_style.csv",sep=";")

produtos = pd.read_csv(BASE_DIR
    / "dados"
    / "produtos_urban_style.csv",sep=";")

estoque = pd.read_csv(BASE_DIR
    / "dados"
    / "estoque_urban_style.csv",sep=";")

def prever_demanda(produto_id):

    historico_produto = vendas[vendas["produto_id"] == produto_id].copy()

    historico_produto["data_venda"] = pd.to_datetime(historico_produto["data_venda"])

    historico_produto["periodo"] = (historico_produto["data_venda"].dt.to_period("M"))

    mensal = (historico_produto.groupby("periodo")["quantidade"].sum())

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

def analisar_reposicao(produto_id):

    demanda_prevista = prever_demanda(produto_id)

    estoque_produto = estoque[
        estoque["produto_id"] == produto_id
    ]

    if estoque_produto.empty:
        raise ValueError(
            f"Produto {produto_id} não encontrado no estoque."
        )

    estoque_produto = estoque_produto.iloc[0]

    estoque_atual = estoque_produto["estoque_atual"]

    estoque_minimo = estoque_produto["estoque_minimo"]

    lead_time_dias = estoque_produto["lead_time_dias"]

    quantidade_recomendada = (
        demanda_prevista
        + estoque_minimo
        - estoque_atual
    )

    quantidade_recomendada = max(
        0,
        quantidade_recomendada
    )

    demanda_diaria = demanda_prevista / 30

    if demanda_diaria > 0:
        cobertura_estoque_dias = (
            estoque_atual
            / demanda_diaria
        )
    else:
        cobertura_estoque_dias = float(999.0)

    if cobertura_estoque_dias <= lead_time_dias:
        risco_ruptura = "Alto"

    elif cobertura_estoque_dias <= lead_time_dias + 7:
        risco_ruptura = "Médio"

    else:
        risco_ruptura = "Baixo"

    produto = produtos[
        produtos["id"] == produto_id
    ]

    if produto.empty:
        raise ValueError(
            f"Produto {produto_id} não encontrado no cadastro de produtos."
        )

    produto = produto.iloc[0]

    custo_base = produto["custo_base"]

    impacto_financeiro = (
        quantidade_recomendada
        * custo_base
    )

    impacto_financeiro = round(
        impacto_financeiro,
        2
    )

    return {
        "produto_id": produto_id,
        "demanda_prevista": demanda_prevista,
        "estoque_atual": int(estoque_atual),
        "estoque_minimo": int(estoque_minimo),
        "lead_time_dias": int(lead_time_dias),
        "cobertura_estoque_dias": float(round(cobertura_estoque_dias, 2)),
        "quantidade_recomendada": int(quantidade_recomendada),
        "custo_base": float(custo_base),
        "impacto_financeiro": float(impacto_financeiro),
        "risco_ruptura_imediato": risco_ruptura
    }

def listar_produtos_reposicao():

    produtos_reposicao = []

    for produto_id in produtos["id"]:

        resultado = analisar_reposicao(
            produto_id
        )

        if resultado["quantidade_recomendada"] > 0:

            produtos_reposicao.append(
                resultado
            )

    produtos_reposicao.sort(
        key=lambda produto:
        produto["quantidade_recomendada"],
        reverse=True
    )

    return {
    "total_analisados": len(produtos),
    "produtos_reposicao": produtos_reposicao
}
    



