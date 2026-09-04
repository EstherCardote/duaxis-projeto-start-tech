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

def comparar_lucro(
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

    atual = calcular_lucro(data_inicio, data_fim)

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

    anterior = calcular_lucro(
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
        
    inicio_atual_p = pd.Period(atual["periodo_inicio"], freq="M")
    fim_atual_p = pd.Period(atual["periodo_fim"], freq="M")
    inicio_ant_p = pd.Period(anterior["periodo_inicio"], freq="M")
    fim_ant_p = pd.Period(anterior["periodo_fim"], freq="M")

    if inicio_atual_p <= fim_ant_p and inicio_ant_p <= fim_atual_p:
        raise ValueError(
            "Os períodos da comparação não podem compartilhar meses. "
            "Para um mês contra o anterior, envie data_inicio e "
            "data_fim iguais a esse mês e não envie o período anterior."
        )    

    lucro_atual = atual["lucro_apos_despesas"]
    lucro_anterior = anterior["lucro_apos_despesas"]
    diferenca = round(lucro_atual - lucro_anterior, 2)

    if lucro_anterior <= 0:
        variacao_percentual = None
    else:
        variacao_percentual = round(
            (diferenca / lucro_anterior) * 100,
            2,
        )

    if diferenca > 0:
        direcao = "alta"
    elif diferenca < 0:
        direcao = "queda"
    else:
        direcao = "estavel"

    return {
        "indicador": "lucro_apos_despesas",
        "criterio": atual["criterio"],
        "fonte": atual["fonte"],
        "meses_comparados": meses_atual,
        "periodo_atual": {
            "periodo_inicio": atual["periodo_inicio"],
            "periodo_fim": atual["periodo_fim"],
            "lucro_apos_despesas": lucro_atual,
            "faturamento_total": atual["faturamento_total"],
            "custo_mercadorias_vendidas": atual["custo_mercadorias_vendidas"],
            "despesa_operacional": atual["despesa_operacional"],
            "registros_analisados": atual["registros_analisados"],
        },
        "periodo_anterior": {
            "periodo_inicio": anterior["periodo_inicio"],
            "periodo_fim": anterior["periodo_fim"],
            "lucro_apos_despesas": lucro_anterior,
            "faturamento_total": anterior["faturamento_total"],
            "custo_mercadorias_vendidas": anterior["custo_mercadorias_vendidas"],
            "despesa_operacional": anterior["despesa_operacional"],
            "registros_analisados": anterior["registros_analisados"],
        },
        "diferenca": diferenca,
        "variacao_percentual": variacao_percentual,
        "direcao": direcao,
    }


def _efeito_contribuicao_lucro(contribuicao):
    if contribuicao > 0:
        return "aumentou_lucro"
    if contribuicao < 0:
        return "reduziu_lucro"
    return "neutro"


def _rotulo_competencia_pt(periodo):
    nomes = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro",
    }
    partes = str(periodo).split("-")
    if len(partes) < 2:
        return str(periodo)
    return f"{nomes[int(partes[1])]} de {partes[0]}"


def _rotulo_intervalo_pt(bloco):
    inicio = bloco["periodo_inicio"]
    fim = bloco["periodo_fim"]
    if inicio == fim:
        return _rotulo_competencia_pt(inicio)
    return (
        f"{_rotulo_competencia_pt(inicio)} a "
        f"{_rotulo_competencia_pt(fim)}"
    )


def _nome_parcela_com_artigo(rotulo):
    if rotulo == "CMV":
        return "o CMV"
    if rotulo == "Despesa operacional":
        return "a despesa operacional"
    return "o faturamento"


def _formatar_percentual_pt(valor):
    if valor is None:
        return None
    return f"{float(valor):.2f}".replace(".", ",") + "%"


def _montar_textos_variacao_lucro(retorno):
    atual_lbl = _rotulo_intervalo_pt(retorno["periodo_atual"])
    anterior_lbl = _rotulo_intervalo_pt(retorno["periodo_anterior"])
    direcao = retorno["direcao"]
    principal_id = retorno["parcela_principal"]
    contribuicoes = retorno["contribuicoes"]
    principal = next(
        (item for item in contribuicoes if item["parcela"] == principal_id),
        None,
    )

    if direcao == "queda":
        verbo = "caiu"
    elif direcao == "alta":
        verbo = "subiu"
    else:
        verbo = "ficou estável"

    if direcao == "estavel" or principal is None:
        return (
            f"O lucro {verbo} em {atual_lbl} na comparação com {anterior_lbl}.",
            [
                "A decomposição é aritmética "
                "(faturamento - CMV - despesa). "
                "Não identifica causa comercial nem caixa."
            ],
            [],
        )

    nome_principal = _nome_parcela_com_artigo(principal["rotulo"])
    pct = _formatar_percentual_pt(principal["percentual_da_diferenca"])
    resumo = (
        f"O lucro {verbo} em {atual_lbl} na comparação com {anterior_lbl}. "
        f"A parcela principal da variação foi {nome_principal}"
    )
    if pct:
        resumo += f" ({pct} da diferença)."
    else:
        resumo += "."

    analises = [
        "A decomposição é aritmética (faturamento - CMV - despesa). "
        "Não identifica promoção, sazonalidade nem caixa."
    ]
    for item in contribuicoes:
        if item["parcela"] == principal_id:
            continue
        nome = _nome_parcela_com_artigo(item["rotulo"])
        if item["efeito"] == "reduziu_lucro":
            analises.append(
                f"{nome[0].upper() + nome[1:]} também reduziu "
                "o lucro nesta comparação."
            )
        elif item["efeito"] == "aumentou_lucro" and direcao == "queda":
            analises.append(
                f"{nome[0].upper() + nome[1:]} puxou o lucro "
                "para cima e não explica a queda."
            )

    if direcao == "queda":
        recomendacoes = [
            (
                f"Investigar primeiro {nome_principal}, "
                "que foi a parcela que mais puxou a queda. "
                "Não dispara promoção nem corte de despesa "
                "só com esta conta."
            ),
            (
                "A política do DUAXIS é olhar a decomposição "
                "do lucro (faturamento, CMV e despesa por competência). "
                "A recomendação é onde olhar, não o que gastar."
            ),
        ]
    else:
        recomendacoes = [
            (
                f"Acompanhar {nome_principal}, "
                "parcela que mais puxou a alta do lucro."
            ),
            (
                "A política do DUAXIS é olhar a decomposição "
                "do lucro (faturamento, CMV e despesa por competência)."
            ),
        ]

    return resumo, analises, recomendacoes


def explicar_variacao_lucro(
    data_inicio=None,
    data_fim=None,
    data_inicio_anterior=None,
    data_fim_anterior=None,
):
    comparacao = comparar_lucro(
        data_inicio,
        data_fim,
        data_inicio_anterior,
        data_fim_anterior,
    )

    atual = comparacao["periodo_atual"]
    anterior = comparacao["periodo_anterior"]
    diferenca = comparacao["diferenca"]

    delta_faturamento = round(
        atual["faturamento_total"] - anterior["faturamento_total"],
        2,
    )
    delta_cmv = round(
        atual["custo_mercadorias_vendidas"]
        - anterior["custo_mercadorias_vendidas"],
        2,
    )
    delta_despesa = round(
        atual["despesa_operacional"] - anterior["despesa_operacional"],
        2,
    )

    parcelas = [
        (
            "faturamento_total",
            "Faturamento",
            delta_faturamento,
        ),
        (
            "custo_mercadorias_vendidas",
            "CMV",
            round(-delta_cmv, 2),
        ),
        (
            "despesa_operacional",
            "Despesa operacional",
            round(-delta_despesa, 2),
        ),
    ]

    contribuicoes = []
    for parcela, rotulo, contribuicao in parcelas:
        if diferenca == 0:
            percentual_da_diferenca = None
        else:
            percentual_da_diferenca = round(
                (contribuicao / diferenca) * 100,
                2,
            )

        contribuicoes.append(
            {
                "parcela": parcela,
                "rotulo": rotulo,
                "contribuicao": contribuicao,
                "percentual_da_diferenca": percentual_da_diferenca,
                "efeito": _efeito_contribuicao_lucro(contribuicao),
            }
        )

    if diferenca == 0:
        parcela_principal = None
    else:
        candidatas = [
            item
            for item in contribuicoes
            if (
                (item["contribuicao"] < 0 and diferenca < 0)
                or
                (item["contribuicao"] > 0 and diferenca > 0)
            )
        ]
        if not candidatas:
            candidatas = contribuicoes
        principal = max(
            candidatas,
            key=lambda item: abs(item["contribuicao"]),
        )
        parcela_principal = principal["parcela"]

    retorno = {
        "indicador": "lucro_apos_despesas",
        "criterio": (
            "decomposição aritmética da variação do lucro "
            "após despesas (faturamento − CMV − despesa)"
        ),
        "fonte": comparacao["fonte"],
        "meses_comparados": comparacao["meses_comparados"],
        "periodo_atual": atual,
        "periodo_anterior": anterior,
        "diferenca": diferenca,
        "variacao_percentual": comparacao["variacao_percentual"],
        "direcao": comparacao["direcao"],
        "contribuicoes": contribuicoes,
        "parcela_principal": parcela_principal,
    }
    resumo, analises, recomendacoes = _montar_textos_variacao_lucro(
        retorno
    )
    retorno["resumo"] = resumo
    retorno["analises"] = analises
    retorno["recomendacoes"] = recomendacoes
    return retorno


def _resolver_categoria_despesa(categoria):
    if categoria is None:
        return None
    texto = str(categoria).strip()
    if texto == "" or texto.lower() in ("null", "none", "todas"):
        return None

    aliases = {
        "aluguel": "Aluguel",
        "energia": "Energia",
        "luz": "Energia",
        "marketing": "Marketing",
        "tecnologia": "Tecnologia",
        "frete": "Frete Operacional",
        "frete operacional": "Frete Operacional",
        "impostos": "Impostos",
        "imposto": "Impostos",
    }
    chave = texto.lower()
    if chave in aliases:
        return aliases[chave]

    for nome in CATEGORIAS_DESPESA:
        if nome.lower() == chave:
            return nome

    permitidas = ", ".join(CATEGORIAS_DESPESA)
    raise ValueError(
        f'Categoria "{texto}" não é despesa operacional. '
        f"Use uma destas: {permitidas}. "
        "Compra de mercadorias não entra nesta simulação."
    )


def simular_lucro_despesa(
    percentual,
    categoria=None,
    data_inicio=None,
    data_fim=None,
):
    if percentual is None or str(percentual).strip() == "":
        raise ValueError(
            "Informe o percentual da simulação "
            "(ex.: 8 para +8% ou -10 para redução)."
        )

    percentual = float(percentual)
    if percentual == 0:
        raise ValueError(
            "O percentual da simulação não pode ser zero."
        )

    if data_inicio is not None and str(data_inicio).strip() == "":
        data_inicio = None
    if data_fim is not None and str(data_fim).strip() == "":
        data_fim = None

    lucro = calcular_lucro(data_inicio, data_fim)
    despesas = calcular_despesas(
        lucro["periodo_inicio"],
        lucro["periodo_fim"],
    )
    categoria_resolvida = _resolver_categoria_despesa(categoria)

    fator = 1 + (percentual / 100.0)
    por_categoria = {
        item["categoria"]: item["valor"]
        for item in despesas["despesa_por_categoria"]
    }

    if categoria_resolvida is None:
        despesa_simulada = round(
            despesas["despesa_total"] * fator,
            2,
        )
        escopo = "todas_operacionais"
        valor_categoria_real = None
        valor_categoria_simulado = None
    else:
        valor_categoria_real = round(
            float(por_categoria.get(categoria_resolvida, 0.0)),
            2,
        )
        valor_categoria_simulado = round(
            valor_categoria_real * fator,
            2,
        )
        despesa_simulada = round(
            despesas["despesa_total"]
            - valor_categoria_real
            + valor_categoria_simulado,
            2,
        )
        escopo = categoria_resolvida

    lucro_simulado = round(
        lucro["faturamento_total"]
        - lucro["custo_mercadorias_vendidas"]
        - despesa_simulada,
        2,
    )
    impacto = round(
        lucro_simulado - lucro["lucro_apos_despesas"],
        2,
    )

    return {
        "periodo_inicio": lucro["periodo_inicio"],
        "periodo_fim": lucro["periodo_fim"],
        "fonte": lucro["fonte"],
        "criterio": (
            "simulação ceteris paribus: faturamento e CMV "
            "iguais; só a despesa operacional muda"
        ),
        "percentual_despesa": percentual,
        "escopo": escopo,
        "categoria": categoria_resolvida,
        "faturamento_total": lucro["faturamento_total"],
        "custo_mercadorias_vendidas": lucro["custo_mercadorias_vendidas"],
        "despesa_real": lucro["despesa_operacional"],
        "despesa_simulada": despesa_simulada,
        "valor_categoria_real": valor_categoria_real,
        "valor_categoria_simulado": valor_categoria_simulado,
        "lucro_real": lucro["lucro_apos_despesas"],
        "lucro_simulado": lucro_simulado,
        "impacto": impacto,
        "ainda_tem_lucro": lucro_simulado > 0,
        "registros_analisados": lucro["registros_analisados"],
    }


def simular_lucro_cmv(
    percentual,
    data_inicio=None,
    data_fim=None,
):
    if percentual is None or str(percentual).strip() == "":
        raise ValueError(
            "Informe o percentual da simulação "
            "(ex.: 10 para +10% ou -5 para redução)."
        )

    percentual = float(percentual)
    if percentual == 0:
        raise ValueError(
            "O percentual da simulação não pode ser zero."
        )

    if data_inicio is not None and str(data_inicio).strip() == "":
        data_inicio = None
    if data_fim is not None and str(data_fim).strip() == "":
        data_fim = None

    lucro = calcular_lucro(data_inicio, data_fim)
    fator = 1 + (percentual / 100.0)
    cmv_real = lucro["custo_mercadorias_vendidas"]
    cmv_simulado = round(cmv_real * fator, 2)
    lucro_simulado = round(
        lucro["faturamento_total"]
        - cmv_simulado
        - lucro["despesa_operacional"],
        2,
    )
    impacto = round(
        lucro_simulado - lucro["lucro_apos_despesas"],
        2,
    )

    return {
        "periodo_inicio": lucro["periodo_inicio"],
        "periodo_fim": lucro["periodo_fim"],
        "fonte": lucro["fonte"],
        "criterio": (
            "simulação ceteris paribus: faturamento e "
            "despesa operacional iguais; só o CMV muda"
        ),
        "percentual_cmv": percentual,
        "cmv_real": cmv_real,
        "cmv_simulado": cmv_simulado,
        "faturamento_total": lucro["faturamento_total"],
        "despesa_operacional": lucro["despesa_operacional"],
        "lucro_real": lucro["lucro_apos_despesas"],
        "lucro_simulado": lucro_simulado,
        "impacto": impacto,
        "ainda_tem_lucro": lucro_simulado > 0,
        "registros_analisados": lucro["registros_analisados"],
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


def comparar_fluxo_caixa(
    data_inicio=None,
    data_fim=None,
    data_inicio_anterior=None,
    data_fim_anterior=None,
):
    if data_inicio is None and data_fim is None:
        dados = movimentacoes_financeiras.copy()
        dados["data_movimentacao"] = pd.to_datetime(
            dados["data_movimentacao"]
        )
        periodo_base = obter_periodo_base(
            dados,
            "data_movimentacao"
        )
        ultimo_mes = min(
            periodo_base["data_maxima"],
            pd.Period("2026-07", freq="M"),
        )
        data_inicio = str(ultimo_mes)
        data_fim = str(ultimo_mes)

    atual = calcular_fluxo_caixa(data_inicio, data_fim)

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

    anterior = calcular_fluxo_caixa(
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

    saldo_atual = atual["saldo"]
    saldo_anterior = anterior["saldo"]
    diferenca = round(saldo_atual - saldo_anterior, 2)

    if saldo_anterior <= 0:
        variacao_percentual = None
    else:
        variacao_percentual = round(
            (diferenca / saldo_anterior) * 100,
            2,
        )

    if diferenca > 0:
        direcao = "alta"
    elif diferenca < 0:
        direcao = "queda"
    else:
        direcao = "estavel"

    return {
        "indicador": "saldo",
        "criterio": atual["criterio"],
        "fonte": atual["fonte"],
        "meses_comparados": meses_atual,
        "periodo_atual": {
            "periodo_inicio": atual["periodo_inicio"],
            "periodo_fim": atual["periodo_fim"],
            "saldo": saldo_atual,
            "entradas": atual["entradas"],
            "saidas": atual["saidas"],
            "registros_analisados": atual["registros_analisados"],
        },
        "periodo_anterior": {
            "periodo_inicio": anterior["periodo_inicio"],
            "periodo_fim": anterior["periodo_fim"],
            "saldo": saldo_anterior,
            "entradas": anterior["entradas"],
            "saidas": anterior["saidas"],
            "registros_analisados": anterior["registros_analisados"],
        },
        "diferenca": diferenca,
        "variacao_percentual": variacao_percentual,
        "direcao": direcao,
    }