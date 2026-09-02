from pathlib import Path
import pandas as pd

from periodo_service import (
    obter_periodo_base,
    resolver_periodo
)

BASE_DIR = Path(__file__).resolve().parent

vendas = pd.read_csv(
    BASE_DIR / "dados" / "vendas_urban_style.csv",
    sep=";"
)

movimentacoes_financeiras = pd.read_csv(
    BASE_DIR / "dados" / "movimentacoes_financeiras_urban_style.csv",
    sep=";"
)

CATEGORIAS_DESPESA = [
    "Aluguel",
    "Energia",
    "Marketing",
    "Tecnologia",
    "Frete Operacional",
    "Impostos",
]

contas_a_receber = pd.read_csv(
    BASE_DIR / "dados" / "contas_a_receber_urban_style.csv",
    sep=";"
)
clientes = pd.read_csv(
    BASE_DIR / "dados" / "clientes_urban_style.csv",
    sep=";"
)

contas_a_pagar = pd.read_csv(
    BASE_DIR / "dados" / "contas_a_pagar_urban_style.csv",
    sep=";"
)
fornecedores = pd.read_csv(
    BASE_DIR / "dados" / "fornecedores_urban_style.csv",
    sep=";"
)

def calcular_faturamento(
    data_inicio=None,
    data_fim=None
):
    dados = vendas.copy()

    dados["data_venda"] = pd.to_datetime(
        dados["data_venda"]
    )

    dados = dados[
        dados["status"] == "Concluída"
    ].copy()

    periodo_base = obter_periodo_base(
        dados,
        "data_venda"
    )

    periodo_consulta = resolver_periodo(
        data_minima=periodo_base["data_minima"],
        data_maxima=periodo_base["data_maxima"],
        data_inicio=data_inicio,
        data_fim=data_fim,
        meses_padrao=3
    )

    periodo_inicio = periodo_consulta["periodo_inicio"]
    periodo_fim = periodo_consulta["periodo_fim"]

    dados["mes"] = dados["data_venda"].dt.to_period("M")

    vendas_periodo = dados[
        (dados["mes"] >= periodo_inicio)
        &
        (dados["mes"] <= periodo_fim)
    ].copy()

    total_vendas = int(len(vendas_periodo))
    quantidade_itens = int(vendas_periodo["quantidade"].sum())
    faturamento_bruto = round(float(vendas_periodo["valor_bruto"].sum()), 2)
    descontos = round(float(vendas_periodo["valor_desconto"].sum()), 2)
    faturamento_total = round(float(vendas_periodo["valor_liquido"].sum()), 2)

    if total_vendas > 0:
        ticket_medio = round(faturamento_total / total_vendas, 2)
    else:
        ticket_medio = 0.0

    faturamento_mensal = (
        vendas_periodo
        .groupby("mes")
        .agg(
            total_vendas=("id_venda", "count"),
            faturamento=("valor_liquido", "sum")
        )
        .reset_index()
        .sort_values("mes")
    )

    faturamento_mensal["mes"] = (
        faturamento_mensal["mes"].astype(str)
    )
    faturamento_mensal["faturamento"] = (
        faturamento_mensal["faturamento"].round(2)
    )  
    return {
        "periodo_inicio": str(periodo_inicio),
        "periodo_fim": str(periodo_fim),
        "fonte": "vendas",
        "criterio": "vendas concluídas por competência",
        "indicador": "valor_liquido",
        "total_vendas": total_vendas,
        "quantidade_itens": quantidade_itens,
        "faturamento_bruto": faturamento_bruto,
        "descontos": descontos,
        "faturamento_total": faturamento_total,
        "ticket_medio": ticket_medio,
        "faturamento_mensal": faturamento_mensal.to_dict(
            orient="records"
        )
    }

def _quantidade_meses(periodo_inicio, periodo_fim):
    inicio = pd.Period(str(periodo_inicio), freq="M")
    fim = pd.Period(str(periodo_fim), freq="M")
    return (fim - inicio).n + 1


def comparar_faturamento(
    data_inicio=None,
    data_fim=None,
    data_inicio_anterior=None,
    data_fim_anterior=None,
):
    if data_inicio is None and data_fim is None:
        dados = vendas.copy()
        dados["data_venda"] = pd.to_datetime(dados["data_venda"])
        dados = dados[dados["status"] == "Concluída"]
        ultimo_mes = str(
            obter_periodo_base(dados, "data_venda")["data_maxima"]
        )
        data_inicio = ultimo_mes
        data_fim = ultimo_mes

    atual = calcular_faturamento(data_inicio, data_fim)

    meses_atual = _quantidade_meses(
        atual["periodo_inicio"],
        atual["periodo_fim"],
    )

    if data_inicio_anterior is None and data_fim_anterior is None:
        inicio_atual = pd.Period(atual["periodo_inicio"], freq="M")
        fim_anterior = inicio_atual - 1
        inicio_anterior = fim_anterior - (meses_atual - 1)
        data_inicio_anterior = str(inicio_anterior)
        data_fim_anterior = str(fim_anterior)

    anterior = calcular_faturamento(
        data_inicio_anterior,
        data_fim_anterior,
    )

    meses_anterior = _quantidade_meses(
        anterior["periodo_inicio"],
        anterior["periodo_fim"],
    )

    if meses_atual != meses_anterior:
        raise ValueError(
            "Os períodos da comparação precisam ter "
            "a mesma quantidade de meses."
        )

    fat_atual = atual["faturamento_total"]
    fat_anterior = anterior["faturamento_total"]
    diferenca = round(fat_atual - fat_anterior, 2)

    if fat_anterior == 0:
        variacao_percentual = None
    else:
        variacao_percentual = round(
            (diferenca / fat_anterior) * 100,
            2,
        )

    if diferenca > 0:
        direcao = "alta"
    elif diferenca < 0:
        direcao = "queda"
    else:
        direcao = "estavel"

    return {
        "indicador": "faturamento_total",
        "criterio": atual["criterio"],
        "fonte": atual["fonte"],
        "meses_comparados": meses_atual,
        "periodo_atual": {
            "periodo_inicio": atual["periodo_inicio"],
            "periodo_fim": atual["periodo_fim"],
            "faturamento_total": fat_atual,
            "total_vendas": atual["total_vendas"],
            "ticket_medio": atual["ticket_medio"],
        },
        "periodo_anterior": {
            "periodo_inicio": anterior["periodo_inicio"],
            "periodo_fim": anterior["periodo_fim"],
            "faturamento_total": fat_anterior,
            "total_vendas": anterior["total_vendas"],
            "ticket_medio": anterior["ticket_medio"],
        },
        "diferenca": diferenca,
        "variacao_percentual": variacao_percentual,
        "direcao": direcao,
    }    

def calcular_despesas(
    data_inicio=None,
    data_fim=None
):
    dados = movimentacoes_financeiras.copy()

    dados = dados[
        (dados["tipo"] == "Despesa")
        &
        (dados["categoria"].isin(CATEGORIAS_DESPESA))
    ].copy()

    dados["data_competencia"] = pd.to_datetime(
        dados["competencia"]
    )

    periodo_base = obter_periodo_base(
        dados,
        "data_competencia"
    )

    periodo_consulta = resolver_periodo(
        data_minima=periodo_base["data_minima"],
        data_maxima=periodo_base["data_maxima"],
        data_inicio=data_inicio,
        data_fim=data_fim,
        meses_padrao=3
    )

    periodo_inicio = periodo_consulta["periodo_inicio"]
    periodo_fim = periodo_consulta["periodo_fim"]

    dados["mes"] = dados["data_competencia"].dt.to_period("M")

    despesas_periodo = dados[
        (dados["mes"] >= periodo_inicio)
        &
        (dados["mes"] <= periodo_fim)
    ].copy()

    despesa_total = round(
        float(despesas_periodo["valor"].sum()),
        2
    )

    despesa_por_categoria = (
        despesas_periodo
        .groupby("categoria")["valor"]
        .sum()
        .reset_index()
        .sort_values("valor", ascending=False)
    )
    despesa_por_categoria["valor"] = (
        despesa_por_categoria["valor"].round(2)
    )

    despesa_mensal = (
        despesas_periodo
        .groupby("mes")["valor"]
        .sum()
        .reset_index()
        .sort_values("mes")
    )
    despesa_mensal["mes"] = despesa_mensal["mes"].astype(str)
    despesa_mensal["despesa"] = despesa_mensal["valor"].round(2)
    despesa_mensal = despesa_mensal[["mes", "despesa"]]

    return {
        "periodo_inicio": str(periodo_inicio),
        "periodo_fim": str(periodo_fim),
        "fonte": "movimentacoes_financeiras",
        "criterio": "despesas operacionais por competência",
        "indicador": "valor",
        "despesa_total": despesa_total,
        "despesa_por_categoria": despesa_por_categoria.to_dict(
            orient="records"
        ),
        "despesa_mensal": despesa_mensal.to_dict(
            orient="records"
        ),
        "registros_analisados": int(len(despesas_periodo))
    }

def comparar_despesas(
    data_inicio=None,
    data_fim=None,
    data_inicio_anterior=None,
    data_fim_anterior=None,
):
    if data_inicio is None and data_fim is None:
        dados = movimentacoes_financeiras.copy()
        dados = dados[
            (dados["tipo"] == "Despesa")
            &
            (dados["categoria"].isin(CATEGORIAS_DESPESA))
        ].copy()
        dados["data_competencia"] = pd.to_datetime(
            dados["competencia"]
        )
        ultimo_mes = str(
            obter_periodo_base(
                dados,
                "data_competencia"
            )["data_maxima"]
        )
        data_inicio = ultimo_mes
        data_fim = ultimo_mes

    atual = calcular_despesas(data_inicio, data_fim)

    meses_atual = _quantidade_meses(
        atual["periodo_inicio"],
        atual["periodo_fim"],
    )

    if data_inicio_anterior is None and data_fim_anterior is None:
        inicio_atual = pd.Period(atual["periodo_inicio"], freq="M")
        fim_anterior = inicio_atual - 1
        inicio_anterior = fim_anterior - (meses_atual - 1)
        data_inicio_anterior = str(inicio_anterior)
        data_fim_anterior = str(fim_anterior)

    anterior = calcular_despesas(
        data_inicio_anterior,
        data_fim_anterior,
    )

    meses_anterior = _quantidade_meses(
        anterior["periodo_inicio"],
        anterior["periodo_fim"],
    )

    if meses_atual != meses_anterior:
        raise ValueError(
            "Os períodos da comparação precisam ter "
            "a mesma quantidade de meses."
        )

    desp_atual = atual["despesa_total"]
    desp_anterior = anterior["despesa_total"]
    diferenca = round(desp_atual - desp_anterior, 2)

    if desp_anterior == 0:
        variacao_percentual = None
    else:
        variacao_percentual = round(
            (diferenca / desp_anterior) * 100,
            2,
        )

    if diferenca > 0:
        direcao = "alta"
    elif diferenca < 0:
        direcao = "queda"
    else:
        direcao = "estavel"

    return {
        "indicador": "despesa_total",
        "criterio": atual["criterio"],
        "fonte": atual["fonte"],
        "meses_comparados": meses_atual,
        "periodo_atual": {
            "periodo_inicio": atual["periodo_inicio"],
            "periodo_fim": atual["periodo_fim"],
            "despesa_total": desp_atual,
            "registros_analisados": atual["registros_analisados"],
        },
        "periodo_anterior": {
            "periodo_inicio": anterior["periodo_inicio"],
            "periodo_fim": anterior["periodo_fim"],
            "despesa_total": desp_anterior,
            "registros_analisados": anterior["registros_analisados"],
        },
        "diferenca": diferenca,
        "variacao_percentual": variacao_percentual,
        "direcao": direcao,
    }    

def calcular_lucro(
    data_inicio=None,
    data_fim=None
):
    faturamento = calcular_faturamento(
        data_inicio,
        data_fim
    )

    despesas = calcular_despesas(
        data_inicio,
        data_fim
    )

    dados = vendas.copy()
    dados["data_venda"] = pd.to_datetime(dados["data_venda"])
    dados = dados[dados["status"] == "Concluída"].copy()
    dados["mes"] = dados["data_venda"].dt.to_period("M")

    periodo_inicio = pd.Period(
        faturamento["periodo_inicio"],
        freq="M"
    )
    periodo_fim = pd.Period(
        faturamento["periodo_fim"],
        freq="M"
    )

    vendas_periodo = dados[
        (dados["mes"] >= periodo_inicio)
        &
        (dados["mes"] <= periodo_fim)
    ]

    cmv = round(float(vendas_periodo["custo_total"].sum()), 2)
    lucro_bruto = round(float(vendas_periodo["lucro_bruto"].sum()), 2)

    lucro_apos_despesas = round(
        faturamento["faturamento_total"]
        - cmv
        - despesas["despesa_total"],
        2
    )

    return {
        "periodo_inicio": faturamento["periodo_inicio"],
        "periodo_fim": faturamento["periodo_fim"],
        "fonte": "vendas + movimentacoes_financeiras",
        "criterio": "resultado operacional simplificado por competência",
        "faturamento_total": faturamento["faturamento_total"],
        "custo_mercadorias_vendidas": cmv,
        "lucro_bruto": lucro_bruto,
        "despesa_operacional": despesas["despesa_total"],
        "lucro_apos_despesas": lucro_apos_despesas,
        "registros_analisados": faturamento["total_vendas"]
    }        

def consultar_contas_a_receber(data_referencia=None):

    dados = contas_a_receber.copy()

    dados["data_emissao"] = pd.to_datetime(dados["data_emissao"])
    dados["data_vencimento"] = pd.to_datetime(dados["data_vencimento"])
    dados["data_recebimento"] = pd.to_datetime(dados["data_recebimento"])

    if (
        data_referencia is None
        or pd.isna(data_referencia)
        or str(data_referencia).strip() == ""
    ):
        data_referencia = pd.Timestamp("2026-07-31")
    else:
        data_referencia = pd.Timestamp(data_referencia)

    abertas = dados[
        (dados["data_emissao"] <= data_referencia)
        &
        (dados["data_recebimento"] > data_referencia)
    ].copy()

    abertas["vencida"] = (
        abertas["data_vencimento"] < data_referencia
    )

    valor_em_aberto = round(float(abertas["valor_original"].sum()), 2)
    valor_vencido = round(
        float(abertas.loc[abertas["vencida"], "valor_original"].sum()),
        2
    )
    valor_a_vencer = round(valor_em_aberto - valor_vencido, 2)

    clientes_aux = clientes[["id", "nome"]].rename(
        columns={"id": "cliente_id", "nome": "nome_cliente"}
    )
    abertas["valor_vencido_linha"] = abertas["valor_original"].where(
    abertas["vencida"],
    0
)
    ranking = (
        abertas
        .groupby("cliente_id", as_index=False)
        .agg(
            valor_em_aberto=("valor_original", "sum"),
            total_parcelas=("id_conta_receber", "count"),
            valor_vencido=("valor_vencido_linha", "sum")
        )
    )
    ranking = ranking.merge(clientes_aux, on="cliente_id", how="left")
    ranking["valor_em_aberto"] = ranking["valor_em_aberto"].round(2)
    ranking["valor_vencido"] = ranking["valor_vencido"].round(2)
    ranking = ranking.sort_values("valor_em_aberto", ascending=False)

    return {
        "data_referencia": str(data_referencia.date()),
        "fonte": "contas_a_receber",
        "criterio": "parcelas emitidas e ainda não recebidas na data",
        "total_parcelas_abertas": int(len(abertas)),
        "total_clientes": int(len(ranking)),
        "valor_em_aberto": valor_em_aberto,
        "valor_vencido": valor_vencido,
        "valor_a_vencer": valor_a_vencer,
        "clientes": ranking.to_dict(orient="records"),
        "registros_analisados": int(len(dados))
    }


def consultar_contas_a_pagar(data_referencia=None):

    dados = contas_a_pagar.copy()

    dados["data_emissao"] = pd.to_datetime(dados["data_emissao"])
    dados["data_vencimento"] = pd.to_datetime(dados["data_vencimento"])
    dados["data_pagamento"] = pd.to_datetime(dados["data_pagamento"])

    if (
        data_referencia is None
        or pd.isna(data_referencia)
        or str(data_referencia).strip() == ""
    ):
        data_referencia = pd.Timestamp("2026-07-31")
    else:
        data_referencia = pd.Timestamp(data_referencia)

    abertas = dados[
        (dados["data_emissao"] <= data_referencia)
        &
        (dados["data_pagamento"] > data_referencia)
    ].copy()

    abertas["vencida"] = (
        abertas["data_vencimento"] < data_referencia
    )

    valor_em_aberto = round(float(abertas["valor_original"].sum()), 2)
    valor_vencido = round(
        float(abertas.loc[abertas["vencida"], "valor_original"].sum()),
        2
    )
    valor_a_vencer = round(valor_em_aberto - valor_vencido, 2)

    fornecedores_aux = fornecedores[["id", "nome_fantasia"]].rename(
        columns={"id": "fornecedor_id", "nome_fantasia": "nome_fornecedor"}
    )

    abertas["valor_vencido_linha"] = abertas["valor_original"].where(
        abertas["vencida"],
        0
    )

    ranking = (
        abertas
        .groupby("fornecedor_id", as_index=False)
        .agg(
            valor_em_aberto=("valor_original", "sum"),
            total_contas=("id_conta_pagar", "count"),
            valor_vencido=("valor_vencido_linha", "sum")
        )
    )
    ranking = ranking.merge(fornecedores_aux, on="fornecedor_id", how="left")
    ranking["valor_em_aberto"] = ranking["valor_em_aberto"].round(2)
    ranking["valor_vencido"] = ranking["valor_vencido"].round(2)
    ranking = ranking.sort_values("valor_em_aberto", ascending=False)

    return {
        "data_referencia": str(data_referencia.date()),
        "fonte": "contas_a_pagar",
        "criterio": "contas emitidas e ainda não pagas na data",
        "total_contas_abertas": int(len(abertas)),
        "total_fornecedores": int(len(ranking)),
        "valor_em_aberto": valor_em_aberto,
        "valor_vencido": valor_vencido,
        "valor_a_vencer": valor_a_vencer,
        "fornecedores": ranking.to_dict(orient="records"),
        "registros_analisados": int(len(dados))
    }


def calcular_fluxo_caixa(
    data_inicio=None,
    data_fim=None
):
    dados = movimentacoes_financeiras.copy()
    dados["data_movimentacao"] = pd.to_datetime(
        dados["data_movimentacao"]
    )

    if data_inicio is not None and str(data_inicio).strip() == "":
        data_inicio = None
    if data_fim is not None and str(data_fim).strip() == "":
        data_fim = None

    periodo_base = obter_periodo_base(
        dados,
        "data_movimentacao"
    )

    if data_inicio is None and data_fim is None:
        data_maxima = min(
            periodo_base["data_maxima"],
            pd.Period("2026-07", freq="M")
        )
    else:
        data_maxima = periodo_base["data_maxima"]

    periodo_consulta = resolver_periodo(
        data_minima=periodo_base["data_minima"],
        data_maxima=data_maxima,
        data_inicio=data_inicio,
        data_fim=data_fim,
        meses_padrao=3
    )

    periodo_inicio = periodo_consulta["periodo_inicio"]
    periodo_fim = periodo_consulta["periodo_fim"]

    dados["mes"] = dados["data_movimentacao"].dt.to_period("M")

    periodo = dados[
        (dados["mes"] >= periodo_inicio)
        &
        (dados["mes"] <= periodo_fim)
    ].copy()

    entradas = round(
        float(periodo.loc[periodo["tipo"] == "Receita", "valor"].sum()),
        2
    )
    saidas = round(
        float(periodo.loc[periodo["tipo"] == "Despesa", "valor"].sum()),
        2
    )
    saldo = round(entradas - saidas, 2)

    entradas_mes = (
        periodo[periodo["tipo"] == "Receita"]
        .groupby("mes")["valor"]
        .sum()
        .rename("entradas")
    )
    saidas_mes = (
        periodo[periodo["tipo"] == "Despesa"]
        .groupby("mes")["valor"]
        .sum()
        .rename("saidas")
    )
    fluxo_mensal = (
        pd.concat([entradas_mes, saidas_mes], axis=1)
        .fillna(0)
        .reset_index()
        .sort_values("mes")
    )
    fluxo_mensal["mes"] = fluxo_mensal["mes"].astype(str)
    fluxo_mensal["entradas"] = fluxo_mensal["entradas"].round(2)
    fluxo_mensal["saidas"] = fluxo_mensal["saidas"].round(2)
    fluxo_mensal["saldo"] = (
        fluxo_mensal["entradas"] - fluxo_mensal["saidas"]
    ).round(2)

    saidas_por_categoria = (
        periodo[periodo["tipo"] == "Despesa"]
        .groupby("categoria")["valor"]
        .sum()
        .reset_index()
        .sort_values("valor", ascending=False)
    )
    saidas_por_categoria["valor"] = saidas_por_categoria["valor"].round(2)

    return {
        "periodo_inicio": str(periodo_inicio),
        "periodo_fim": str(periodo_fim),
        "fonte": "movimentacoes_financeiras",
        "criterio": "entradas e saídas pela data da movimentação",
        "entradas": entradas,
        "saidas": saidas,
        "saldo": saldo,
        "fluxo_mensal": fluxo_mensal.to_dict(orient="records"),
        "saidas_por_categoria": saidas_por_categoria.to_dict(
            orient="records"
        ),
        "registros_analisados": int(len(periodo))
    }

# TESTE PROVISORIO
from financeiro_service import calcular_despesas, comparar_despesas

abr = calcular_despesas("2026-04", "2026-04")
mai = calcular_despesas("2026-05", "2026-05")
print("abril", abr["despesa_total"])
print("maio", mai["despesa_total"])
print("conta na mão", round(mai["despesa_total"] - abr["despesa_total"], 2))

c = comparar_despesas("2026-05", "2026-05", "2026-04", "2026-04")
print(c["periodo_atual"])
print(c["periodo_anterior"])
print(c["diferenca"], c["variacao_percentual"], c["direcao"]) 