from pathlib import Path

import pandas as pd

from ml_service import analisar_reposicao
from periodo_service import (
    obter_periodo_base,
    resolver_periodo
)

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

movimentacoes_estoque = pd.read_csv(
    BASE_DIR
    / "dados"
    / "movimentacoes_estoque_urban_style.csv",
    sep=";"
)

# =========================================================
# FUNÇÃO: CONSULTAR PEDIDOS ATUALMENTE ATRASADOS
# =========================================================

def _formatar_data_pt(data):
    return pd.Timestamp(data).strftime("%d/%m/%Y")


def _montar_textos_pedidos_atrasados(
    total_atrasados,
    data_referencia,
    pedidos,
):
    data_lbl = _formatar_data_pt(data_referencia)

    if total_atrasados <= 0:
        return (
            f"Não há pedidos atrasados em {data_lbl}.",
            [
                (
                    "Atrasado nesta data significa: a entrega prevista "
                    "já tinha passado e a mercadoria ainda não havia "
                    "chegado."
                ),
                (
                    "Isso é reconstrução histórica, não o status "
                    "gravado hoje no arquivo."
                ),
            ],
            [],
        )

    palavra = "pedido atrasado" if total_atrasados == 1 else "pedidos atrasados"

    resumo = f"Há {total_atrasados} {palavra} em {data_lbl}."

    analises = [
        (
            "Atrasado nesta data significa: a entrega prevista "
            "já tinha passado e a mercadoria ainda não havia chegado."
        ),
        (
            "A lista está ordenada pelo maior atraso em dias. "
            "Não é ranking de taxa de atraso do fornecedor."
        ),
    ]

    recomendacoes = [
        (
            "Acompanhar com os fornecedores os pedidos da lista, "
            "começando pelos de maior atraso."
        ),
    ]

    return resumo, analises, recomendacoes


def consultar_pedidos_atrasados(data_referencia=None):

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


    if (
        data_referencia is None
        or pd.isna(data_referencia)
        or str(data_referencia).strip() == ""
    ):

        data_referencia = pd.Timestamp(
            "2026-07-31"
        )

    else:

        data_referencia = pd.Timestamp(
            data_referencia
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
            |
            (
                dados["data_entrega_real"]
                >
                data_referencia
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

    data_ref_texto = data_referencia.strftime("%Y-%m-%d")
    resumo, analises, recomendacoes = _montar_textos_pedidos_atrasados(
        total_atrasados=len(pedidos),
        data_referencia=data_ref_texto,
        pedidos=pedidos,
    )

    return {

        "total_atrasados":
            len(pedidos),

        "data_referencia":
            data_ref_texto,

        "pedidos":
            pedidos,

        "resumo":
            resumo,

        "analises":
            analises,

        "recomendacoes":
            recomendacoes,

    }

def listar_fornecedores_atrasos(
    data_inicio=None,
    data_fim=None
):

    dados = compras.copy()

    dados["data_compra"] = pd.to_datetime(
        dados["data_compra"]
    )

    dados["data_prevista_entrega"] = pd.to_datetime(
        dados["data_prevista_entrega"]
    )

    dados["data_entrega_real"] = pd.to_datetime(
        dados["data_entrega_real"],
        errors="coerce"
    )


    # =====================================================
    # DEFINE O PERÍODO DA ANÁLISE
    # =====================================================

    periodo_base = obter_periodo_base(
        dados,
        "data_compra"
    )

    periodo_consulta = resolver_periodo(
        data_minima=periodo_base["data_minima"],
        data_maxima=periodo_base["data_maxima"],
        data_inicio=data_inicio,
        data_fim=data_fim,
        meses_padrao=3
    )

    periodo_inicio = (
        periodo_consulta["periodo_inicio"]
    )

    periodo_fim = (
        periodo_consulta["periodo_fim"]
    )


    # =====================================================
    # FILTRA AS COMPRAS REALIZADAS NO PERÍODO
    # =====================================================

    dados["periodo_compra"] = (
        dados["data_compra"]
        .dt.to_period("M")
    )

    compras_periodo = dados[
        (
            dados["periodo_compra"]
            >= periodo_inicio
        )
        &
        (
            dados["periodo_compra"]
            <= periodo_fim
        )
    ].copy()


    # =====================================================
    # IDENTIFICA COMPRAS ENTREGUES COM ATRASO
    # =====================================================

    compras_periodo[
        "entregue_com_atraso"
    ] = (
        compras_periodo[
            "data_entrega_real"
        ].notna()
        &
        (
            compras_periodo[
                "data_entrega_real"
            ]
            >
            compras_periodo[
                "data_prevista_entrega"
            ]
        )
    )


    # =====================================================
    # CALCULA DIAS DE ATRASO
    # =====================================================

    compras_periodo[
        "dias_atraso"
    ] = 0

    compras_periodo.loc[
        compras_periodo[
            "entregue_com_atraso"
        ],
        "dias_atraso"
    ] = (
        compras_periodo.loc[
            compras_periodo[
                "entregue_com_atraso"
            ],
            "data_entrega_real"
        ]
        -
        compras_periodo.loc[
            compras_periodo[
                "entregue_com_atraso"
            ],
            "data_prevista_entrega"
        ]
    ).dt.days


    # =====================================================
    # AGRUPA POR FORNECEDOR
    # =====================================================

    resumo = (
        compras_periodo
        .groupby(
            "fornecedor_id",
            as_index=False
        )
        .agg(
            total_pedidos=(
                "id_compra",
                "count"
            ),

            pedidos_atrasados=(
                "entregue_com_atraso",
                "sum"
            ),

            media_dias_atraso=(
                "dias_atraso",
                lambda valores:
                    valores[
                        valores > 0
                    ].mean()
            ),

            maior_atraso_dias=(
                "dias_atraso",
                "max"
            )
        )
    )


    # =====================================================
    # CALCULA TAXA DE ATRASO
    # =====================================================

    resumo[
        "taxa_atraso_percentual"
    ] = (
        resumo[
            "pedidos_atrasados"
        ]
        /
        resumo[
            "total_pedidos"
        ]
        *
        100
    ).round(2)


    resumo[
        "media_dias_atraso"
    ] = (
        resumo[
            "media_dias_atraso"
        ]
        .fillna(0)
        .round(2)
    )


    # =====================================================
    # ADICIONA NOME DO FORNECEDOR
    # =====================================================

    fornecedores_aux = fornecedores[
        [
            "id",
            "nome_fantasia"
        ]
    ].rename(
        columns={
            "id":
                "fornecedor_id",

            "nome_fantasia":
                "nome_fornecedor"
        }
    )

    resumo = resumo.merge(
        fornecedores_aux,
        on="fornecedor_id",
        how="left"
    )


    # =====================================================
    # ORDENA PELA TAXA DE ATRASO
    # =====================================================

    resumo = resumo.sort_values(
        by=[
            "taxa_atraso_percentual",
            "pedidos_atrasados",
            "media_dias_atraso"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )


    resumo = resumo.reset_index(
        drop=True
    )

    resumo["posicao"] = (
        resumo.index + 1
    )


    # =====================================================
    # ORGANIZA COLUNAS
    # =====================================================

    resumo = resumo[
        [
            "posicao",
            "fornecedor_id",
            "nome_fornecedor",
            "total_pedidos",
            "pedidos_atrasados",
            "taxa_atraso_percentual",
            "media_dias_atraso",
            "maior_atraso_dias"
        ]
    ]


    return {

        "periodo_referencia":
            f"{periodo_inicio} a {periodo_fim}",

        "total_fornecedores":
            len(resumo),

        "fornecedores":
            resumo.to_dict(
                orient="records"
            )
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

def obter_estoque_em_data(
    data_referencia
):
    dados = movimentacoes_estoque.copy()

    dados[
        "data_movimentacao"
    ] = pd.to_datetime(
        dados["data_movimentacao"]
    )

    dados[
        "periodo"
    ] = (
        dados["data_movimentacao"]
        .dt.to_period("M")
    )

    periodo_referencia = pd.Period(
        data_referencia,
        freq="M"
    )

    dados = dados[
        dados["periodo"]
        <= periodo_referencia
    ].copy()

    dados[
        "ordem_movimentacao"
    ] = (
        dados[
            "id_movimentacao_estoque"
        ]
        .str.extract(
            r"(\d+)"
        )[0]
        .astype(int)
    )

    dados = dados.sort_values(
        by=[
            "produto_id",
            "ordem_movimentacao"
        ]
    )

    estoque_historico = (
        dados
        .groupby(
            "produto_id",
            as_index=False
        )
        .tail(1)
    )

    estoque_historico = (
        estoque_historico[
            [
                "produto_id",
                "estoque_posterior"
            ]
        ]
        .rename(
            columns={
                "estoque_posterior":
                    "estoque_na_data"
            }
        )
    )

    return estoque_historico

# =========================================================
# FUNÇÃO: LISTAR PRODUTOS COM MENOR GIRO
# =========================================================

def listar_produtos_baixo_giro(data_inicio=None,
    data_fim=None):

    dados_vendas = vendas.copy()

    dados_vendas["data_venda"] = pd.to_datetime(
    dados_vendas["data_venda"]
)
    periodo_base = obter_periodo_base(
    dados_vendas,
    "data_venda"
)

    periodo_consulta = resolver_periodo(
        data_minima=periodo_base["data_minima"],
        data_maxima=periodo_base["data_maxima"],
        data_inicio=data_inicio,
        data_fim=data_fim,
        meses_padrao=3
    )

    periodo_inicio = (
        periodo_consulta["periodo_inicio"]
    )

    periodo_fim = (
        periodo_consulta["periodo_fim"]
    )

    quantidade_meses_periodo = (
    periodo_fim.ordinal
    - periodo_inicio.ordinal
    + 1
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
    start=periodo_base["data_minima"],
    end=periodo_base["data_maxima"],
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

    mes_referencia = periodo_fim
    
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

    inicio_periodo = periodo_inicio

    historico_periodo = historico_mensal[
    (
        historico_mensal["mes"]
        >= inicio_periodo
    )
    &
    (
        historico_mensal["mes"]
        <= mes_referencia
    )
    ].copy()

    vendas_periodo = (
    historico_periodo
    .groupby(
        "produto_id",
        as_index=False
    )
    ["quantidade"]
    .sum()
    .rename(
        columns={
            "quantidade":
                "vendas_periodo"
        }
    )
)
    vendas_periodo[
    "media_mensal_periodo"
] = (
    vendas_periodo[
        "vendas_periodo"
    ] / quantidade_meses_periodo
).round(2)

    # -----------------------------------------------------
    # COMPARAÇÃO SAZONAL
    # -----------------------------------------------------
    #
    # Compara o período analisado com janelas equivalentes
    # dos anos anteriores.
    #
    # Exemplo:
    #
    # período analisado:
    # 2025-11 a 2026-02
    #
    # períodos históricos:
    # 2024-11 a 2025-02
    # 2023-11 a 2024-02
    #
    # Somente janelas totalmente contidas no histórico
    # disponível são consideradas.
    # -----------------------------------------------------

    janelas_historicas = []

    deslocamento_anos = 1

    while True:

        inicio_historico = (
            periodo_inicio
            - (12 * deslocamento_anos)
        )

        fim_historico = (
            periodo_fim
            - (12 * deslocamento_anos)
        )

        if inicio_historico < periodo_base["data_minima"]:
            break

        historico_janela = historico_mensal[
            (
                historico_mensal["mes"]
                >= inicio_historico
            )
            &
            (
                historico_mensal["mes"]
                <= fim_historico
            )
        ].copy()

        vendas_janela = (
            historico_janela
            .groupby(
                "produto_id",
                as_index=False
            )
            ["quantidade"]
            .sum()
            .rename(
                columns={
                    "quantidade":
                        "vendas_periodo_historico"
                }
            )
        )

        vendas_janela[
            "periodo_historico"
        ] = deslocamento_anos

        janelas_historicas.append(
            vendas_janela
        )

        deslocamento_anos += 1


    if janelas_historicas:

        historico_sazonal = pd.concat(
            janelas_historicas,
            ignore_index=True
        )

        historico_sazonal_anterior = (
            historico_sazonal
            .groupby(
                "produto_id",
                as_index=False
            )
            ["vendas_periodo_historico"]
            .mean()
            .rename(
                columns={
                    "vendas_periodo_historico":
                        "media_mesmo_periodo_historico"
                }
            )
        )

    else:

        historico_sazonal_anterior = pd.DataFrame(
            columns=[
                "produto_id",
                "media_mesmo_periodo_historico"
            ]
        )


    analise_sazonal = vendas_periodo.merge(
        historico_sazonal_anterior,
        on="produto_id",
        how="left"
    )

    analise_sazonal[
        "variacao_sazonal_percentual"
    ] = (
        (
            analise_sazonal["vendas_periodo"]
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
    estoque_aux = obter_estoque_em_data(
    periodo_fim
)

    analise_giro = analise_giro.merge(
    estoque_aux,
    on="produto_id",
    how="left"
)
    analise_giro[
    "cobertura_estoque_12m"
] = (
    analise_giro["estoque_na_data"]
    /
    analise_giro[
        "media_mensal_12_meses"
    ].replace(0, pd.NA)
).round(2)

    analise_giro[
    "cobertura_estoque_periodo"
] = (
    analise_giro["estoque_na_data"]
    /
    analise_giro[
        "media_mensal_periodo"
    ].replace(0, pd.NA)
).round(2)

    analise_giro[
    "variacao_ritmo_recente_percentual"
] = (
    (
        analise_giro[
            "media_mensal_periodo"
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
        "estoque_na_data",

        "vendas_12_meses",
        "media_mensal_12_meses",

        "vendas_periodo",
        "media_mensal_periodo",

        "media_mesmo_periodo_historico",
        "variacao_sazonal_percentual",

        "variacao_ritmo_recente_percentual",

        "cobertura_estoque_12m",
        "cobertura_estoque_periodo"
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

    print(
        "Produtos com desaceleração recente:",
        analise_giro[
            "ritmo_recente_desacelerando"
        ].sum()
    )

    print(
        "Produtos abaixo do histórico sazonal:",
        analise_giro[
            "abaixo_historico_sazonal"
        ].sum()
    )

    print(
        "Produtos que atendem aos dois critérios:",
        (
            analise_giro[
                "ritmo_recente_desacelerando"
            ]
            &
            analise_giro[
                "abaixo_historico_sazonal"
            ]
        ).sum()
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
        by="cobertura_estoque_periodo",
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
    "estoque_na_data",

    "vendas_12_meses",
    "media_mensal_12_meses",

    "vendas_periodo",
    "media_mensal_periodo",

    "media_mesmo_periodo_historico",
    "variacao_ritmo_recente_percentual",
    "variacao_sazonal_percentual",

    "cobertura_estoque_12m",
    "cobertura_estoque_periodo"
]

    candidatos_baixo_giro = (
    candidatos_baixo_giro[
        colunas_retorno
    ]
)
    candidatos_baixo_giro = (
    candidatos_baixo_giro
    .rename(
        columns={
            "estoque_na_data":
                "estoque_periodo"
        }
    )
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
    f"{periodo_inicio} a {periodo_fim}",

    "produtos":
        produtos_baixo_giro
}


# =========================================================
# TESTE TEMPORÁRIO
# =========================================================

if __name__ == "__main__":

    dados_teste = compras.copy()

    dados_teste[
        "data_compra"
    ] = pd.to_datetime(
        dados_teste["data_compra"]
    )

    dados_teste[
        "data_prevista_entrega"
    ] = pd.to_datetime(
        dados_teste[
            "data_prevista_entrega"
        ]
    )

    dados_teste[
        "data_entrega_real"
    ] = pd.to_datetime(
        dados_teste[
            "data_entrega_real"
        ],
        errors="coerce"
    )


    # -----------------------------------------------------
    # FILTRA FOR006 + JAN A JUN/2026
    # -----------------------------------------------------

    fornecedor_teste = dados_teste[
        (
            dados_teste[
                "fornecedor_id"
            ] == "FOR006"
        )
        &
        (
            dados_teste[
                "data_compra"
            ] >= "2026-01-01"
        )
        &
        (
            dados_teste[
                "data_compra"
            ] <= "2026-06-30"
        )
    ].copy()


    fornecedor_teste[
        "dias_atraso"
    ] = (
        fornecedor_teste[
            "data_entrega_real"
        ]
        -
        fornecedor_teste[
            "data_prevista_entrega"
        ]
    ).dt.days


    atrasados = fornecedor_teste[
        fornecedor_teste[
            "dias_atraso"
        ] > 0
    ]


    print(
        "\nTotal de pedidos FOR006:",
        len(fornecedor_teste)
    )

    print(
        "Pedidos atrasados:",
        len(atrasados)
    )

    print(
        "\nPedidos que atrasaram:"
    )

    print(
        atrasados[
            [
                "id_compra",
                "data_compra",
                "data_prevista_entrega",
                "data_entrega_real",
                "dias_atraso"
            ]
        ].to_string(
            index=False
        )
    )