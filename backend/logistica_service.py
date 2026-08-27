from pathlib import Path

import pandas as pd


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
# TESTE TEMPORÁRIO
# =========================================================

if __name__ == "__main__":

    resultado = consultar_pedidos_atrasados()

    print(
        "Total de pedidos atualmente atrasados:",
        resultado["total_atrasados"]
    )

    for pedido in resultado["pedidos"][:10]:

        print(
            pedido["id_compra"],
            "- produto:",
            pedido["nome_produto"],
            f"({pedido['produto_id']})",
            "- fornecedor:",
            
            pedido["nome_fornecedor"],
            f"({pedido['fornecedor_id']})",
            "- status:",
            pedido["status"],
            "- atraso:",
            pedido["dias_atraso"],
            "dias"
        )