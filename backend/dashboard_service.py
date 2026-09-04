from financeiro_service import (
    comparar_faturamento,
    comparar_lucro,
)
from logistica_service import obter_estoque_em_data
from ml_service import listar_produtos_reposicao

def montar_kpis_dashboard(data_inicio=None, data_fim=None):
    fat = comparar_faturamento(data_inicio, data_fim)
    lucro = comparar_lucro(data_inicio, data_fim)

    mes_ref = fat["periodo_atual"]["periodo_inicio"]
    estoque = obter_estoque_em_data(mes_ref)
    unidades_estoque = int(estoque["estoque_na_data"].sum())

    reposicao = listar_produtos_reposicao()

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
    }