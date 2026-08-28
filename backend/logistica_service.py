from pathlib import Path

import pandas as pd

from ml_service import analisar_reposicao

# =========================================================
# CAMINHO BASE DO BACKEND
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# CARREGAMENTO DAS BASES
# =========================================================

compras = pd.read_csv(
    BASE_DIR / "dados" / "compras_urban_style.csv",
    sep=";"
)

produtos = pd.read_csv(
    BASE_DIR / "dados" / "produtos_urban_style.csv",
    sep=";"
)

fornecedores = pd.read_csv(
    BASE_DIR / "dados" / "fornecedores_urban_style.csv",
    sep=";"
)

vendas = pd.read_csv(
    BASE_DIR / "dados" / "vendas_urban_style.csv",
    sep=";"
)

estoque = pd.read_csv(
    BASE_DIR / "dados" / "estoque_urban_style.csv",
    sep=";"
)

# =========================================================
# FUNÇÃO: CONSULTAR PEDIDOS ATUALMENTE ATRASADOS
# =========================================================

def consultar_pedidos_atrasados():

    # Cria uma cópia da base original
    dados = compras.copy()


    # -----------------------------------------------------
    # CONVERTE AS DATAS
    # -----------------------------------------------------

    dados["data_prevista_entrega"] = pd.to_datetime(
        dados["data_prevista_entrega"]
    )

    dados["data_entrega_real"] = pd.to_datetime(
        dados["data_entrega_real"],
        errors="coerce"
    )


    # -----------------------------------------------------
    # DATA DE REFERÊNCIA
    # -----------------------------------------------------
    #
    # Nossa base simulada termina em 31/07/2026.
    #
    # Portanto, analisamos quais pedidos estavam
    # atrasados nessa data.
    # -----------------------------------------------------

    data_referencia = pd.Timestamp(
        "2026-07-31"
    )


    # -----------------------------------------------------
    # IDENTIFICA PEDIDOS ATUALMENTE ATRASADOS
    # -----------------------------------------------------
    #
    # Para ser considerado atrasado:
    #
    # 1. A data prevista de entrega já passou
    #
    # 2. O pedido ainda não possui data de entrega real
    #
    # 3. O status ainda está aberto:
    #    - Pendente
    #    - Em trânsito
    # -----------------------------------------------------

    status_abertos = [
        "Pendente",
        "Em trânsito"
    ]


    filtro_atrasados = (

        (
            dados["data_prevista_entrega"]
            <
            data_referencia
        )

        &

        (
            dados["data_entrega_real"].isna()
        )

        &

        (
            dados["status"].isin(
                status_abertos
            )
        )

    )


    atrasados = dados[
        filtro_atrasados
    ].copy()


    # -----------------------------------------------------
    # CALCULA QUANTOS DIAS O PEDIDO ESTÁ ATRASADO
    # -----------------------------------------------------

    atrasados["dias_atraso"] = (

        data_referencia

        -

        atrasados["data_prevista_entrega"]

    ).dt.days


    # =====================================================
    # ADICIONA O NOME DO PRODUTO
    # =====================================================

    produtos_aux = produtos[
        [
            "id",
            "nome"
        ]
    ].rename(
        columns={
            "id": "produto_id",
            "nome": "nome_produto"
        }
    )


    atrasados = atrasados.merge(
        produtos_aux,
        on="produto_id",
        how="left"
    )


    # =====================================================
    # ADICIONA O NOME DO FORNECEDOR
    # =====================================================

    fornecedores_aux = fornecedores[
        [
            "id",
            "nome_fantasia"
        ]
    ].rename(
        columns={
            "id": "fornecedor_id",
            "nome_fantasia": "nome_fornecedor"
        }
    )


    atrasados = atrasados.merge(
        fornecedores_aux,
        on="fornecedor_id",
        how="left"
    )


    # -----------------------------------------------------
    # ORDENA DO MAIOR ATRASO PARA O MENOR
    # -----------------------------------------------------

    atrasados = atrasados.sort_values(
        by="dias_atraso",
        ascending=False
    )


    # -----------------------------------------------------
    # SELECIONA AS COLUNAS QUE SERÃO ENVIADAS AO DUAXIS
    # -----------------------------------------------------

    colunas = [

        "id_compra",

        "fornecedor_id",
        "nome_fornecedor",

        "produto_id",
        "nome_produto",

        "quantidade",

        "status",

        "data_prevista_entrega",

        "dias_atraso",

        "valor_total"

    ]


    atrasados = atrasados[
        colunas
    ]


    # -----------------------------------------------------
    # FORMATA A DATA PARA TEXTO
    # -----------------------------------------------------

    atrasados[
        "data_prevista_entrega"
    ] = (

        atrasados[
            "data_prevista_entrega"
        ]

        .dt.strftime(
            "%Y-%m-%d"
        )

    )


    # -----------------------------------------------------
    # TRANSFORMA O DATAFRAME EM LISTA DE DICIONÁRIOS
    # -----------------------------------------------------

    pedidos = atrasados.to_dict(
        orient="records"
    )


    # -----------------------------------------------------
    # RETORNO FINAL
    # -----------------------------------------------------

    return {

        "total_atrasados":
            len(pedidos),

        "data_referencia":
            "2026-07-31",

        "pedidos":
            pedidos

    }

# =========================================================
# FUNÇÃO: LISTAR PRODUTOS COM MAIOR RISCO DE RUPTURA
# =========================================================

def listar_produtos_maior_risco():

    produtos_analisados = []

    for produto_id in produtos["id"]:

        analise = analisar_reposicao(
            produto_id
        )

        cobertura = analise[
            "cobertura_estoque_dias"
        ]

        lead_time = analise[
            "lead_time_dias"
        ]

        margem_cobertura = (
            cobertura - lead_time
        )

        indice_cobertura = (
            cobertura / lead_time
            if lead_time > 0
            else float("inf")
        )
        if indice_cobertura <= 1:

            nivel_risco = "Crítico"

        elif indice_cobertura <= 1.5:

            nivel_risco = "Alto"

        elif indice_cobertura <= 2:

            nivel_risco = "Moderado"

        else:

            nivel_risco = "Baixo"
            

        analise_risco = {
            "produto_id":
                analise["produto_id"],

            "nome_produto":
                analise["nome_produto"],

            "demanda_prevista":
                analise["demanda_prevista"],

            "estoque_atual":
                analise["estoque_atual"],

            "estoque_minimo":
                analise["estoque_minimo"],

            "cobertura_estoque_dias":
                cobertura,

            "lead_time_dias":
                lead_time,

            "margem_cobertura_dias":
                round(
                    margem_cobertura,
                    2
                ),

            "indice_cobertura":
                round(
                    indice_cobertura,
                    2
                ),
            "nivel_risco":
                nivel_risco    
        }

        produtos_analisados.append(
            analise_risco
        )
        produtos_analisados = sorted(
            produtos_analisados,
            key=lambda produto:
                produto["indice_cobertura"]
        )
        
    total_critico = sum(
    1
    for produto in produtos_analisados
    if produto["nivel_risco"] == "Crítico"
)

    total_alto = sum(
        1
        for produto in produtos_analisados
        if produto["nivel_risco"] == "Alto"
    )

    total_moderado = sum(
        1
        for produto in produtos_analisados
        if produto["nivel_risco"] == "Moderado"
    )

    total_baixo = sum(
        1
        for produto in produtos_analisados
        if produto["nivel_risco"] == "Baixo"
    )

    return {
        "total_analisados":
            len(produtos_analisados),

        "total_critico":
            total_critico,

        "total_alto":
            total_alto,

        "total_moderado":
            total_moderado,

        "total_baixo":
            total_baixo,

        "produtos":
            
            produtos_analisados
    }

# =========================================================
# FUNÇÃO: LISTAR PRODUTOS COM MENOR GIRO
# =========================================================

def listar_produtos_baixo_giro():

    dados_vendas = vendas.copy()

    dados_vendas["data_venda"] = pd.to_datetime(
    dados_vendas["data_venda"]
)
    dados_vendas = dados_vendas[
    dados_vendas["status"] == "Concluída"
    ].copy()
    
    dados_vendas["mes"] = (
    dados_vendas["data_venda"]
    .dt.to_period("M")
)
    vendas_mensais = (
    dados_vendas
    .groupby(
        [
            "produto_id",
            "mes"
        ],
        as_index=False
    )
    ["quantidade"]
    .sum()
)
    meses = pd.period_range(
    start="2023-08",
    end="2026-07",
    freq="M"
)
    grade_completa = pd.MultiIndex.from_product(
        [
            produtos["id"],
            meses
        ],
        names=[
            "produto_id",
            "mes"
        ]
    ).to_frame(
        index=False
    )

    historico_mensal = grade_completa.merge(
    vendas_mensais,
    on=[
        "produto_id",
        "mes"
    ],
    how="left"
)
    historico_mensal["quantidade"] = (
    historico_mensal["quantidade"]
    .fillna(0)
    .astype(int)
)
# -----------------------------------------------------
# DEFINE OS PERÍODOS DA ANÁLISE
# -----------------------------------------------------

    mes_referencia = pd.Period(
        "2026-07",
        freq="M"
    )
    inicio_12_meses = (
    mes_referencia - 11
)
    historico_12_meses = historico_mensal[
    (
        historico_mensal["mes"]
        >= inicio_12_meses
    )
    &
    (
        historico_mensal["mes"]
        <= mes_referencia
    )
].copy()
    
    vendas_12_meses = (
    historico_12_meses
    .groupby(
        "produto_id",
        as_index=False
    )
    ["quantidade"]
    .sum()
    .rename(
        columns={
            "quantidade":
                "vendas_12_meses"
        }
    )
)
    vendas_12_meses[
    "media_mensal_12_meses"
    ] = (
    vendas_12_meses[
        "vendas_12_meses"
    ] / 12
    ).round(2)

    inicio_3_meses = (
    mes_referencia - 2
)
    historico_3_meses = historico_mensal[
    (
        historico_mensal["mes"]
        >= inicio_3_meses
    )
    &
    (
        historico_mensal["mes"]
        <= mes_referencia
    )
    ].copy()

    vendas_3_meses = (
    historico_3_meses
    .groupby(
        "produto_id",
        as_index=False
    )
    ["quantidade"]
    .sum()
    .rename(
        columns={
            "quantidade":
                "vendas_3_meses"
        }
    )
)
    vendas_3_meses[
    "media_mensal_3_meses"
] = (
    vendas_3_meses[
        "vendas_3_meses"
    ] / 3
).round(2)
    
    periodos_sazonais = historico_mensal[
    historico_mensal["mes"].dt.month.isin(
        [5, 6, 7]
    )
].copy()

    periodos_sazonais["ano"] = (
    periodos_sazonais["mes"].dt.year
)

    comparacao_sazonal = (
    periodos_sazonais
    .groupby(
        [
            "produto_id",
            "ano"
        ],
        as_index=False
    )
    ["quantidade"]
    .sum()
)
    historico_sazonal_anterior = (
    comparacao_sazonal[
        comparacao_sazonal["ano"] < 2026
    ]
    .groupby(
        "produto_id",
        as_index=False
    )
    ["quantidade"]
    .mean()
    .rename(
        columns={
            "quantidade":
                "media_mesmo_periodo_historico"
        }
    )
)
    analise_sazonal = vendas_3_meses.merge(
    historico_sazonal_anterior,
    on="produto_id",
    how="left"
)
    analise_sazonal[
    "variacao_sazonal_percentual"
] = (
    (
        analise_sazonal["vendas_3_meses"]
        -
        analise_sazonal[
            "media_mesmo_periodo_historico"
        ]
    )
    /
    analise_sazonal[
        "media_mesmo_periodo_historico"
    ].replace(0, pd.NA)
    *
    100
    ).round(2)

    analise_giro = vendas_12_meses.merge(
    analise_sazonal,
    on="produto_id",
    how="left"
)
    estoque_aux = estoque[
    [
        "produto_id",
        "estoque_atual"
    ]
    ].copy()

    analise_giro = analise_giro.merge(
    estoque_aux,
    on="produto_id",
    how="left"
)
    analise_giro[
    "cobertura_estoque_12m"
] = (
    analise_giro["estoque_atual"]
    /
    analise_giro[
        "media_mensal_12_meses"
    ].replace(0, pd.NA)
    ).round(2)

    analise_giro[
    "cobertura_estoque_3m"
] = (
    analise_giro["estoque_atual"]
    /
    analise_giro[
        "media_mensal_3_meses"
    ].replace(0, pd.NA)
    ).round(2)

    analise_giro[
    "variacao_ritmo_recente_percentual"
] = (
    (
        analise_giro[
            "media_mensal_3_meses"
        ]
        -
        analise_giro[
            "media_mensal_12_meses"
        ]
    )
    /
    analise_giro[
        "media_mensal_12_meses"
    ].replace(0, pd.NA)
    *
    100
    ).round(2)

    produtos_aux = produtos[
    [
        "id",
        "nome"
    ]
    ].rename(
    columns={
        "id": "produto_id",
        "nome": "nome_produto"
    }
)
    analise_giro = analise_giro.merge(
    produtos_aux,
    on="produto_id",
    how="left"
)
    analise_giro = analise_giro[
    [
        "produto_id",
        "nome_produto",
        "estoque_atual",

        "vendas_12_meses",
        "media_mensal_12_meses",

        "vendas_3_meses",
        "media_mensal_3_meses",

        "media_mesmo_periodo_historico",
        "variacao_sazonal_percentual",

        "variacao_ritmo_recente_percentual",

        "cobertura_estoque_12m",
        "cobertura_estoque_3m"
    ]
]

    analise_giro[
    "ritmo_recente_desacelerando"
] = (
    analise_giro[
        "variacao_ritmo_recente_percentual"
    ] < 0
)

    analise_giro[
    "abaixo_historico_sazonal"
] = (
    analise_giro[
        "variacao_sazonal_percentual"
    ] < 0
)

    candidatos_baixo_giro = analise_giro[
    (
        analise_giro[
            "ritmo_recente_desacelerando"
        ]
    )
    &
    (
        analise_giro[
            "abaixo_historico_sazonal"
        ]
    )
].copy()

    candidatos_baixo_giro = (
    candidatos_baixo_giro
    .sort_values(
        by="cobertura_estoque_3m",
        ascending=False
    )
)
    
    candidatos_baixo_giro = (
    candidatos_baixo_giro
    .reset_index(
        drop=True
    )
)
    
    candidatos_baixo_giro[
    "posicao"
] = (
    candidatos_baixo_giro.index + 1
)

    colunas_retorno = [
    "posicao",
    "produto_id",
    "nome_produto",
    "estoque_atual",

    "vendas_12_meses",
    "media_mensal_12_meses",

    "vendas_3_meses",
    "media_mensal_3_meses",

    "media_mesmo_periodo_historico",
    "variacao_ritmo_recente_percentual",
    "variacao_sazonal_percentual",

    "cobertura_estoque_12m",
    "cobertura_estoque_3m"
]

    candidatos_baixo_giro = (
    candidatos_baixo_giro[
        colunas_retorno
    ]
)
    
    produtos_baixo_giro = (
    candidatos_baixo_giro
    .to_dict(
        orient="records"
    )
)
    return {
    "total_analisados":
        len(analise_giro),

    "total_candidatos":
        len(produtos_baixo_giro),

    "periodo_referencia":
        "2026-05 a 2026-07",

    "produtos":
        produtos_baixo_giro
}


# =========================================================
# TESTE TEMPORÁRIO
# =========================================================

if __name__ == "__main__":

    resultado = listar_produtos_baixo_giro()

    print(
        "Total analisados:",
        resultado["total_analisados"]
    )

    print(
        "Total candidatos:",
        resultado["total_candidatos"]
    )

    print(
        "Período:",
        resultado["periodo_referencia"]
    )

    print(
        "\nProdutos com menor giro:\n"
    )

    for produto in resultado["produtos"][:10]:

        print(
            produto["posicao"],
            "-",
            produto["produto_id"],
            "-",
            produto["nome_produto"],
            "| estoque:",
            produto["estoque_atual"],
            "| cobertura recente:",
            produto["cobertura_estoque_3m"],
            "| variação recente:",
            produto[
                "variacao_ritmo_recente_percentual"
            ],
            "%",
            "| variação sazonal:",
            produto[
                "variacao_sazonal_percentual"
            ],
            "%"
        )