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

# TESTE PROVISORIO
if __name__ == "__main__":

    bruto = vendas.copy()
    bruto["data_venda"] = pd.to_datetime(bruto["data_venda"])
    bruto["mes"] = bruto["data_venda"].dt.to_period("M")

    independente = bruto[
    (bruto["status"] == "Concluída")
    &
    (bruto["mes"] >= pd.Period("2026-01", freq="M"))
    &
    (bruto["mes"] <= pd.Period("2026-03", freq="M"))
]

    soma_liquido = round(float(independente["valor_liquido"].sum()), 2)
    soma_bruto = round(float(independente["valor_bruto"].sum()), 2)
    soma_desc = round(float(independente["valor_desconto"].sum()), 2)
    n_vendas = int(len(independente))

    funcao = calcular_faturamento(
    data_inicio="2026-01",
    data_fim="2026-03"
)

    print("independente faturamento:", soma_liquido)
    print("funcao       faturamento:", funcao["faturamento_total"])
    print("independente vendas:     ", n_vendas)
    print("funcao       vendas:     ", funcao["total_vendas"])
    print("bruto - desconto == liquido?", soma_bruto - soma_desc == soma_liquido)
