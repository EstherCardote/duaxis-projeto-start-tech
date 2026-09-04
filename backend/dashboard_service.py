import pandas as pd

from financeiro_service import (
    vendas,
    comparar_faturamento,
    comparar_lucro,
)
from logistica_service import (
    obter_estoque_em_data,
    consultar_pedidos_atrasados,
    resumir_estoque_por_categoria,
)
from ml_service import listar_produtos_reposicao

NOMES_MES_CURTO = (
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
)


def _rotulo_mes_curto(periodo):
    mes = pd.Period(str(periodo), freq="M")
    return NOMES_MES_CURTO[mes.month - 1]


def _vendas_concluidas():
    dados = vendas.copy()
    dados["data_venda"] = pd.to_datetime(dados["data_venda"])
    return dados[dados["status"] == "Concluída"].copy()


def _limites_historico_vendas(dados):
    return (
        dados["data_venda"].min().normalize(),
        dados["data_venda"].max().normalize(),
    )


def _rotulo_mes_ano(periodo):
    return f"{_rotulo_mes_curto(periodo)}/{str(periodo.year)[2:]}"


def _pontos_diarios(recorte, data_inicio, data_fim):
    por_dia = recorte.groupby(
        recorte["data_venda"].dt.normalize()
    )["valor_liquido"].sum()
    pontos = []
    dia = data_inicio
    quantidade_dias = (data_fim - data_inicio).days + 1
    while dia <= data_fim:
        mostrar = (
            quantidade_dias <= 14
            or dia.day == 1
            or dia.day % 5 == 0
            or dia == data_inicio
            or dia == data_fim
        )
        pontos.append({
            "rotulo": f"{dia.day:02d}/{dia.month:02d}",
            "data": str(dia.date()),
            "mostrar_rotulo": bool(mostrar),
            "valor": round(float(por_dia.get(dia, 0.0)), 2),
        })
        dia += pd.Timedelta(days=1)
    return pontos


def _pontos_mensais(recorte, data_inicio, data_fim):
    por_mes = recorte.groupby(
        recorte["data_venda"].dt.to_period("M")
    )["valor_liquido"].sum()
    mes_atual = data_inicio.to_period("M")
    mes_fim = data_fim.to_period("M")
    quantidade_meses = (mes_fim - mes_atual).n + 1
    pontos = []
    indice = 0
    while mes_atual <= mes_fim:
        mostrar = quantidade_meses <= 12 or indice % 2 == 0 or mes_atual == mes_fim
        pontos.append({
            "rotulo": _rotulo_mes_ano(mes_atual),
            "data": str(mes_atual),
            "mostrar_rotulo": bool(mostrar),
            "valor": round(float(por_mes.get(mes_atual, 0.0)), 2),
        })
        mes_atual += 1
        indice += 1
    return pontos


def _pontos_anuais(recorte, data_inicio, data_fim):
    por_ano = recorte.groupby(
        recorte["data_venda"].dt.year
    )["valor_liquido"].sum()
    pontos = []
    for ano in range(data_inicio.year, data_fim.year + 1):
        pontos.append({
            "rotulo": str(ano),
            "data": str(ano),
            "mostrar_rotulo": True,
            "valor": round(float(por_ano.get(ano, 0.0)), 2),
        })
    return pontos


def montar_grafico_faturamento(data_inicio=None, data_fim=None):
    dados = _vendas_concluidas()
    data_minima, data_maxima = _limites_historico_vendas(dados)

    if data_inicio is None or str(data_inicio).strip() == "":
        data_inicio = (data_maxima.to_period("M") - 5).to_timestamp(how="start")
    else:
        data_inicio = pd.Timestamp(data_inicio).normalize()

    if data_fim is None or str(data_fim).strip() == "":
        data_fim = data_maxima
    else:
        data_fim = pd.Timestamp(data_fim).normalize()

    if data_inicio > data_fim:
        raise ValueError(
            "A data inicial não pode ser posterior à data final."
        )

    recorte = dados[
        (dados["data_venda"] >= data_inicio)
        & (dados["data_venda"] <= data_fim)
    ]
    total = round(float(recorte["valor_liquido"].sum()), 2)
    quantidade_dias = (data_fim - data_inicio).days + 1

    if quantidade_dias <= 62:
        granularidade = "dia"
        pontos = _pontos_diarios(recorte, data_inicio, data_fim)
    elif quantidade_dias <= 731:
        granularidade = "mes"
        pontos = _pontos_mensais(recorte, data_inicio, data_fim)
    else:
        granularidade = "ano"
        pontos = _pontos_anuais(recorte, data_inicio, data_fim)

    return {
        "titulo": "Faturamento",
        "data_inicio": str(data_inicio.date()),
        "data_fim": str(data_fim.date()),
        "data_minima": str(data_minima.date()),
        "data_maxima": str(data_maxima.date()),
        "granularidade": granularidade,
        "total": total,
        "pontos": pontos,
    }


def montar_kpis_dashboard(data_inicio=None, data_fim=None):
    fat = comparar_faturamento(data_inicio, data_fim)
    lucro = comparar_lucro(data_inicio, data_fim)

    mes_ref = fat["periodo_atual"]["periodo_inicio"]
    estoque = obter_estoque_em_data(mes_ref)
    unidades_estoque = int(estoque["estoque_na_data"].sum())
    nivel_estoque = resumir_estoque_por_categoria(estoque)

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
            "categoria": pedido["categoria"],
            "nome_fornecedor": pedido["nome_fornecedor"],
            "dias_atraso": int(pedido["dias_atraso"]),
            "data_prevista_entrega": pedido["data_prevista_entrega"],
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
            "nivel_estoque": {
                "titulo": "Nível de Estoque",
                "total_unidades": nivel_estoque["total_unidades"],
                "produtos_abaixo_minimo": nivel_estoque[
                    "produtos_abaixo_minimo"
                ],
                "barras": nivel_estoque["barras"],
            },
            "pedidos_atrasados": {
                "titulo": "Pedidos atrasados",
                "total": atrasados["total_atrasados"],
                "data_referencia": atrasados["data_referencia"],
                "barras": barras_atraso,
            },
        },
    }
