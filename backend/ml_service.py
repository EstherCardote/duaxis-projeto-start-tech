from pathlib import Path
import re
import unicodedata

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


def _normalizar_texto(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    return re.sub(r"\s+", " ", texto)


def _mensagem_produtos_ambiguos(candidatos, identificador):
    linhas = [
        f"{linha['id']} — {linha['nome']} ({linha['categoria']})"
        for _, linha in candidatos.iterrows()
    ]
    lista = "; ".join(linhas)
    return (
        f'Encontrei mais de um produto para "{identificador}": {lista}. '
        "Informe o código do produto para continuar."
    )


def resolver_produto(identificador):
    if identificador is None or str(identificador).strip() == "":
        raise ValueError(
            "Informe o código ou o nome do produto."
        )

    bruto = str(identificador).strip()
    chave = _normalizar_texto(bruto)

    por_id = produtos[
        produtos["id"].astype(str).str.upper() == bruto.upper()
    ]
    if len(por_id) == 1:
        return str(por_id.iloc[0]["id"])

    por_sku = produtos[
        produtos["sku"].astype(str).str.upper() == bruto.upper()
    ]
    if len(por_sku) == 1:
        return str(por_sku.iloc[0]["id"])

    nomes_norm = produtos["nome"].map(_normalizar_texto)

    por_nome = produtos[nomes_norm == chave]
    if len(por_nome) == 1:
        return str(por_nome.iloc[0]["id"])
    if len(por_nome) > 1:
        raise ValueError(
            _mensagem_produtos_ambiguos(por_nome, bruto)
        )

    tokens = [token for token in chave.split(" ") if token]

    def nome_corresponde(nome_n):
        if chave in nome_n or nome_n in chave:
            return True
        return all(token in nome_n for token in tokens)

    candidatos = produtos[nomes_norm.map(nome_corresponde)]

    if len(candidatos) == 1:
        return str(candidatos.iloc[0]["id"])
    if len(candidatos) > 1:
        raise ValueError(
            _mensagem_produtos_ambiguos(candidatos, bruto)
        )

    raise ValueError(
        f'Nenhum produto encontrado para "{bruto}". '
        "Informe o código (ex.: PROD017) ou o nome cadastrado."
    )


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

    produto_id = resolver_produto(produto_id)

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

    nome_produto = produto["nome"]

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
        "nome_produto": str(nome_produto),
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


def _formatar_reais(valor):
    texto = f"{float(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _montar_recomendacoes_lista_reposicao(
    total_analisados,
    total_reposicao,
    impacto_financeiro_total,
):
    if total_reposicao <= 0:
        return []

    impacto = _formatar_reais(impacto_financeiro_total)

    return [
        (
            f"Emitir a reposição dos {total_reposicao} produtos "
            f"com quantidade recomendada maior que zero. "
            f"Impacto estimado de compra: {impacto}."
        ),
        (
            "A política de compras da Urban Style manda repor "
            "quando a demanda prevista do próximo mês, somada "
            "ao estoque mínimo, fica acima do estoque atual."
        ),
        (
            f"Essa regra vale para {total_reposicao} dos "
            f"{total_analisados} produtos analisados."
        ),
    ]


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

    impacto_financeiro_total = sum(
    produto["impacto_financeiro"]
    for produto in produtos_reposicao
)

    impacto_financeiro_total = round(
    impacto_financeiro_total,
    2
)

    return {
    "total_analisados":
        len(produtos),

    "total_reposicao":
        len(produtos_reposicao),

    "impacto_financeiro_total":
        impacto_financeiro_total,

    "produtos_reposicao":
        produtos_reposicao,

    "recomendacoes":
        _montar_recomendacoes_lista_reposicao(
            total_analisados=len(produtos),
            total_reposicao=len(produtos_reposicao),
            impacto_financeiro_total=impacto_financeiro_total,
        ),
}

# TESTE TEMPORARIO
if __name__ == "__main__":

    total_independente = 0
    produtos_com_reposicao = 0

    for produto_id in produtos["id"]:

        analise = analisar_reposicao(
            produto_id
        )

        if (
            analise["quantidade_recomendada"]
            > 0
        ):

            produtos_com_reposicao += 1

            impacto_calculado = (
                analise["quantidade_recomendada"]
                *
                analise["custo_base"]
            )

            impacto_calculado = round(
                impacto_calculado,
                2
            )

            if (
                impacto_calculado
                != analise["impacto_financeiro"]
            ):

                print(
                    "DIVERGÊNCIA:",
                    produto_id,
                    impacto_calculado,
                    analise["impacto_financeiro"]
                )

            total_independente += (
                impacto_calculado
            )


    total_independente = round(
        total_independente,
        2
    )


    print(
        "\nProdutos com reposição:",
        produtos_com_reposicao
    )

    print(
        "Impacto total independente:",
        total_independente
    )


    resultado_agrupado = (
        listar_produtos_reposicao()
    )

    print(
        "Impacto retornado pela função:",
        resultado_agrupado[
            "impacto_financeiro_total"
        ]
    )