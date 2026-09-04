import pandas as pd

from financeiro_service import (
    comparar_faturamento,
    comparar_lucro,
)
from logistica_service import (
    obter_estoque_em_data,
    consultar_pedidos_atrasados,
)
from ml_service import listar_produtos_reposicao

def montar_kpis_dashboard(data_inicio=None, data_fim=None):
    fat = comparar_faturamento(data_inicio, data_fim)
    lucro = comparar_lucro(data_inicio, data_fim)

    mes_ref = fat["periodo_atual"]["periodo_inicio"]
    estoque = obter_estoque_em_data(mes_ref)
    unidades_estoque = int(estoque["estoque_na_data"].sum())

    reposicao = listar_produtos_reposicao()

    mes_atrasos = pd.Period(
    fat["periodo_atual"]["periodo_fim"],
    freq="M",
    )
    data_referencia_atrasos = str(
        mes_atrasos.to_timestamp(how="end").date()
    )
    atrasados = consultar_pedidos_atrasados(
        data_referencia_atrasos
    )

    barras_atraso = []
    for pedido in atrasados["pedidos"]:
        barras_atraso.append({
            "id_compra": pedido["id_compra"],
            "rotulo": pedido["nome_produto"],
            "nome_fornecedor": pedido["nome_fornecedor"],
            "dias_atraso": int(pedido["dias_atraso"]),
        })

    return {
        "periodo_inicio": fat["periodo_atual"]["periodo_inicio"],
        "periodo_fim": fat["periodo_atual"]["periodo_fim"],
        "periodo_anterior_inicio": fat["periodo_anterior"]["periodo_inicio"],
        "kpis": {
            "faturamento": {
                "valor": fat["periodo_atual"]["faturamento_total"],
                "variacao_percentual": fat["variacao_percentual"],
                "direcao": fat["direcao"],
                "rotulo": "Faturamento",
                "modulo": "financeiro",
            },
            "lucro": {
                "valor": lucro["periodo_atual"]["lucro_apos_despesas"],
                "variacao_percentual": lucro["variacao_percentual"],
                "direcao": lucro["direcao"],
                "rotulo": "Lucro após despesas",
                "modulo": "financeiro",
            },
            "estoque": {
                "valor": unidades_estoque,
                "variacao_percentual": None,
                "direcao": None,
                "rotulo": "Unidades em estoque",
                "modulo": "logistica",
            },
            "reposicao": {
                "valor": reposicao["total_reposicao"],
                "variacao_percentual": None,
                "direcao": None,
                "rotulo": "Produtos com reposição",
                "modulo": "logistica",
            },
        },
        "graficos": {
            "pedidos_atrasados": {
                "titulo": "Pedidos atrasados",
                "total": atrasados["total_atrasados"],
                "data_referencia": atrasados["data_referencia"],
                "barras": barras_atraso,
            },
        },
    }
