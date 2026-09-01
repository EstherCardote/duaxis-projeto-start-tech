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
        )
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
        "lucro_apos_despesas": lucro_apos_despesas
    }        

# TESTE PROVISORIO
if __name__ == "__main__":

    dados_vendas = vendas.copy()
    dados_vendas["data_venda"] = pd.to_datetime(dados_vendas["data_venda"])
    dados_vendas["mes"] = dados_vendas["data_venda"].dt.to_period("M")

    vendas_periodo = dados_vendas[
        (dados_vendas["status"] == "Concluída")
        &
        (dados_vendas["mes"] >= pd.Period("2026-01", freq="M"))
&
(dados_vendas["mes"] <= pd.Period("2026-03", freq="M"))
    ]

    fat = round(float(vendas_periodo["valor_liquido"].sum()), 2)
    cmv = round(float(vendas_periodo["custo_total"].sum()), 2)
    bruto = round(float(vendas_periodo["lucro_bruto"].sum()), 2)

    dados_desp = movimentacoes_financeiras.copy()
    dados_desp["mes"] = pd.to_datetime(
        dados_desp["competencia"]
    ).dt.to_period("M")

    desp_periodo = dados_desp[
        (dados_desp["tipo"] == "Despesa")
        &
        (dados_desp["categoria"].isin(CATEGORIAS_DESPESA))
        &
        (dados_desp["mes"] >= pd.Period("2026-01", freq="M"))
&
(dados_desp["mes"] <= pd.Period("2026-03", freq="M"))
    ]

    desp = round(float(desp_periodo["valor"].sum()), 2)
    lucro = round(fat - cmv - desp, 2)

    funcao = calcular_lucro(
        data_inicio="2026-01",
        data_fim="2026-03"
    )

    print("independente fat / funcao:", fat, funcao["faturamento_total"])
    print("independente cmv / funcao:", cmv, funcao["custo_mercadorias_vendidas"])
    print("independente bruto / funcao:", bruto, funcao["lucro_bruto"])
    print("independente desp / funcao:", desp, funcao["despesa_operacional"])
    print("independente lucro / funcao:", lucro, funcao["lucro_apos_despesas"])
    print("bruto == fat - cmv?", bruto == round(fat - cmv, 2))