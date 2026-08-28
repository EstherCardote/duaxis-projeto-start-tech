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
# TESTE TEMPORÁRIO
# =========================================================

if __name__ == "__main__":

    resultado = listar_produtos_maior_risco()

    print(
        "Total analisados:",
        resultado["total_analisados"]
    )

    print(
        "Crítico:",
        resultado["total_critico"]
    )

    print(
        "Alto:",
        resultado["total_alto"]
    )

    print(
        "Moderado:",
        resultado["total_moderado"]
    )

    print(
        "Baixo:",
        
        resultado["total_baixo"]
    )

    print("\nProdutos com maior risco:\n")

    for produto in resultado["produtos"][:10]:

        print(
            produto["produto_id"],
            "-",
            produto["nome_produto"],
            "| risco:",
            produto["nivel_risco"],
            "| cobertura:",
            produto["cobertura_estoque_dias"],
            "| lead time:",
            produto["lead_time_dias"],
            "| índice:",
            produto["indice_cobertura"]
        )