import pandas as pd

from financeiro_service import (
    contas_a_pagar,
    contas_a_receber,
    consultar_contas_a_pagar,
    consultar_contas_a_receber,
    movimentacoes_financeiras,
    vendas,
)
from logistica_service import (
    compras,
    consultar_pedidos_atrasados,
)

DATA_HOJE_MVP = pd.Timestamp("2026-07-31")
DATA_ONTEM_MVP = pd.Timestamp("2026-07-30")
DATA_MINIMA = pd.Timestamp("2023-08-01")
DIAS_MEDIA = 7


def _resolver_data_do_dia(data_referencia=None):
    if (
        data_referencia is None
        or pd.isna(data_referencia)
        or str(data_referencia).strip() == ""
    ):
        return DATA_ONTEM_MVP

    texto = str(data_referencia).strip().lower()
    if texto in ("none", "null"):
        return DATA_ONTEM_MVP
    if texto in ("ontem", "yesterday"):
        return DATA_ONTEM_MVP
    if texto in ("hoje", "today"):
        return DATA_HOJE_MVP
    if texto in ("anteontem",):
        return DATA_HOJE_MVP - pd.Timedelta(days=2)

    dia = pd.Timestamp(data_referencia).normalize()

    if dia > DATA_HOJE_MVP:
        raise ValueError(
            "A data está depois de 31/07/2026, "
            "último dia do histórico da Urban Style."
        )
    if dia < DATA_MINIMA:
        raise ValueError(
            "A data está antes do histórico disponível "
            "(a partir de 01/08/2023)."
        )
    return dia


def _rotulo_relativo(dia):
    if dia == DATA_ONTEM_MVP:
        return "ontem"
    if dia == DATA_HOJE_MVP:
        return "hoje"
    if dia == DATA_HOJE_MVP - pd.Timedelta(days=2):
        return "anteontem"
    return None


def _variacao_percentual(atual, base):
    if base == 0:
        return None
    return round(((atual - base) / base) * 100, 2)


def _normalizar_data(serie):
    return pd.to_datetime(serie, errors="coerce").dt.normalize()


def _faturamento_do_dia(vendas_ok, dia):
    do_dia = vendas_ok[vendas_ok["data_venda"] == dia].copy()
    total_vendas = int(len(do_dia))
    faturamento = round(float(do_dia["valor_liquido"].sum()), 2)
    itens = int(do_dia["quantidade"].sum()) if total_vendas else 0
    ticket = round(faturamento / total_vendas, 2) if total_vendas else 0.0

    canais = (
        do_dia
        .groupby("canal_venda", as_index=False)
        .agg(
            total_vendas=("id_venda", "count"),
            faturamento=("valor_liquido", "sum"),
        )
        .sort_values("faturamento", ascending=False)
    )
    canais["faturamento"] = canais["faturamento"].round(2)

    return {
        "total_vendas": total_vendas,
        "quantidade_itens": itens,
        "faturamento_total": faturamento,
        "ticket_medio": ticket,
        "canais": canais.to_dict(orient="records"),
        "registros": total_vendas,
    }


def _serie_contexto_faturamento(vendas_ok, dia):
    anteontem = dia - pd.Timedelta(days=1)
    fat_dia = _faturamento_do_dia(vendas_ok, dia)["faturamento_total"]
    fat_anteontem = _faturamento_do_dia(
        vendas_ok,
        anteontem,
    )["faturamento_total"]

    inicio_media = dia - pd.Timedelta(days=DIAS_MEDIA)
    dias_media = pd.date_range(
        start=max(inicio_media, DATA_MINIMA),
        end=dia - pd.Timedelta(days=1),
        freq="D",
    )
    valores_media = [
        _faturamento_do_dia(vendas_ok, pd.Timestamp(item))["faturamento_total"]
        for item in dias_media
    ]
    if valores_media:
        media_7_dias = round(
            sum(valores_media) / len(valores_media),
            2,
        )
    else:
        media_7_dias = 0.0

    return {
        "anteontem": {
            "data": str(anteontem.date()),
            "faturamento": fat_anteontem,
        },
        "media_7_dias": media_7_dias,
        "dias_na_media": int(len(valores_media)),
        "grafico": [
            {
                "rotulo": "Anteontem",
                "data": str(anteontem.date()),
                "faturamento": fat_anteontem,
            },
            {
                "rotulo": "Média 7 dias",
                "data": None,
                "faturamento": media_7_dias,
            },
            {
                "rotulo": "O dia",
                "data": str(dia.date()),
                "faturamento": fat_dia,
            },
        ],
        "variacao_vs_anteontem_percentual": _variacao_percentual(
            fat_dia,
            fat_anteontem,
        ),
        "variacao_vs_media_percentual": _variacao_percentual(
            fat_dia,
            media_7_dias,
        ),
    }


def _compras_do_dia(dia):
    dados = compras.copy()
    dados["data_compra"] = _normalizar_data(dados["data_compra"])
    dados["data_entrega_real"] = _normalizar_data(
        dados["data_entrega_real"]
    )

    emitidas = dados[dados["data_compra"] == dia]
    recebidas = dados[dados["data_entrega_real"] == dia]

    return {
        "compras_emitidas": int(len(emitidas)),
        "valor_compras_emitidas": round(
            float(emitidas["valor_total"].sum()),
            2,
        ),
        "entregas_recebidas": int(len(recebidas)),
        "valor_entregas_recebidas": round(
            float(recebidas["valor_total"].sum()),
            2,
        ),
        "registros": int(len(emitidas) + len(recebidas)),
    }


def _caixa_do_dia(dia):
    dados = movimentacoes_financeiras.copy()
    dados["data_movimentacao"] = _normalizar_data(
        dados["data_movimentacao"]
    )
    do_dia = dados[dados["data_movimentacao"] == dia]

    entradas = round(
        float(do_dia.loc[do_dia["tipo"] == "Receita", "valor"].sum()),
        2,
    )
    saidas = round(
        float(do_dia.loc[do_dia["tipo"] == "Despesa", "valor"].sum()),
        2,
    )
    return {
        "entradas": entradas,
        "saidas": saidas,
        "saldo": round(entradas - saidas, 2),
        "registros": int(len(do_dia)),
    }


def _vencidas_no_dia(dataframe, coluna_liquidacao, dia):
    dados = dataframe.copy()
    dados["data_emissao"] = _normalizar_data(dados["data_emissao"])
    dados["data_vencimento"] = _normalizar_data(dados["data_vencimento"])
    dados[coluna_liquidacao] = _normalizar_data(dados[coluna_liquidacao])

    ainda_abertas = (
        (dados["data_emissao"] <= dia)
        &
        (dados[coluna_liquidacao] > dia)
    )
    venceram_no_dia = dados["data_vencimento"] == dia
    recorte = dados[ainda_abertas & venceram_no_dia]
    return {
        "quantidade": int(len(recorte)),
        "valor": round(float(recorte["valor_original"].sum()), 2),
    }


def _montar_destaques(
    faturamento,
    contexto,
    caixa,
    atrasados,
    receber_venceu,
    pagar_venceu,
):
    destaques = []
    variacao = contexto["variacao_vs_anteontem_percentual"]
    if variacao is not None:
        if variacao < 0:
            destaques.append({
                "codigo": "faturamento_abaixo_dia_anterior",
                "variacao_percentual": variacao,
            })
        elif variacao > 0:
            destaques.append({
                "codigo": "faturamento_acima_dia_anterior",
                "variacao_percentual": variacao,
            })

    if caixa["saldo"] < 0:
        destaques.append({
            "codigo": "caixa_negativo_no_dia",
            "saldo": caixa["saldo"],
        })

    if atrasados > 0:
        destaques.append({
            "codigo": "pedidos_atrasados",
            "quantidade": atrasados,
        })

    if receber_venceu["quantidade"] > 0:
        destaques.append({
            "codigo": "parcelas_venceram_nao_recebidas",
            "quantidade": receber_venceu["quantidade"],
            "valor": receber_venceu["valor"],
        })

    if pagar_venceu["quantidade"] > 0:
        destaques.append({
            "codigo": "contas_venceram_nao_pagas",
            "quantidade": pagar_venceu["quantidade"],
            "valor": pagar_venceu["valor"],
        })

    if faturamento["total_vendas"] == 0:
        destaques.append({
            "codigo": "sem_vendas_concluidas",
        })

    return destaques


def resumir_dia(data_referencia=None):
    dia = _resolver_data_do_dia(data_referencia)
    data_texto = str(dia.date())

    vendas_ok = vendas.copy()
    vendas_ok["data_venda"] = _normalizar_data(vendas_ok["data_venda"])
    vendas_ok = vendas_ok[vendas_ok["status"] == "Concluída"].copy()

    faturamento = _faturamento_do_dia(vendas_ok, dia)
    contexto = _serie_contexto_faturamento(vendas_ok, dia)
    compras_dia = _compras_do_dia(dia)
    caixa = _caixa_do_dia(dia)

    receber = consultar_contas_a_receber(data_texto)
    pagar = consultar_contas_a_pagar(data_texto)
    atrasados = consultar_pedidos_atrasados(data_texto)

    receber_venceu = _vencidas_no_dia(
        contas_a_receber,
        "data_recebimento",
        dia,
    )
    pagar_venceu = _vencidas_no_dia(
        contas_a_pagar,
        "data_pagamento",
        dia,
    )

    total_atrasados = int(atrasados["total_atrasados"])
    destaques = _montar_destaques(
        faturamento,
        contexto,
        caixa,
        total_atrasados,
        receber_venceu,
        pagar_venceu,
    )

    registros_analisados = (
        faturamento["registros"]
        + compras_dia["registros"]
        + caixa["registros"]
    )

    return {
        "data_referencia": data_texto,
        "rotulo_relativo": _rotulo_relativo(dia),
        "fonte": "vendas, compras, movimentacoes_financeiras, contas, pedidos",
        "criterio": (
            "Fatos do dia civil. Faturamento pela data da venda "
            "concluída; caixa pela data da movimentação."
        ),
        "faturamento_total": faturamento["faturamento_total"],
        "total_vendas": faturamento["total_vendas"],
        "quantidade_itens": faturamento["quantidade_itens"],
        "ticket_medio": faturamento["ticket_medio"],
        "canais": faturamento["canais"],
        "variacao_vs_anteontem_percentual": (
            contexto["variacao_vs_anteontem_percentual"]
        ),
        "variacao_vs_media_percentual": (
            contexto["variacao_vs_media_percentual"]
        ),
        "grafico_faturamento": contexto["grafico"],
        "media_7_dias": contexto["media_7_dias"],
        "compras_emitidas": compras_dia["compras_emitidas"],
        "valor_compras_emitidas": compras_dia["valor_compras_emitidas"],
        "entregas_recebidas": compras_dia["entregas_recebidas"],
        "valor_entregas_recebidas": compras_dia["valor_entregas_recebidas"],
        "entradas_caixa": caixa["entradas"],
        "saidas_caixa": caixa["saidas"],
        "saldo_caixa_do_dia": caixa["saldo"],
        "contas_receber_em_aberto": receber["valor_em_aberto"],
        "contas_receber_vencido": receber["valor_vencido"],
        "contas_pagar_em_aberto": pagar["valor_em_aberto"],
        "contas_pagar_vencido": pagar["valor_vencido"],
        "parcelas_venceram_nao_recebidas": receber_venceu,
        "contas_venceram_nao_pagas": pagar_venceu,
        "pedidos_atrasados": total_atrasados,
        "destaques": destaques,
        "limitacao": (
            "A base de vendas não registra devolução. "
            "Faturamento não é entrada de caixa. "
            "Saldo do dia não é lucro nem saldo acumulado."
        ),
        "registros_analisados": registros_analisados,
    }
