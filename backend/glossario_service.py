import unicodedata


def _normalizar(texto):
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    limpo = []
    for caractere in texto:
        if caractere.isalnum() or caractere.isspace():
            limpo.append(caractere)
        else:
            limpo.append(" ")
    return " ".join("".join(limpo).split())


CONCEITOS = [
    {
        "id": "faturamento",
        "rotulo": "Faturamento",
        "modulo": "Financeiro",
        "aliases": (
            "faturamento",
            "faturamento liquido",
            "receita",
            "quanto faturei",
            "vendas em reais",
        ),
        "definicao": (
            "No DUAXIS, faturamento é o valor líquido das vendas "
            "concluídas no período, pela data da venda (competência)."
        ),
        "nao_e": (
            "Não é entrada de caixa nem contas a receber. "
            "O bruto (antes do desconto) não é o indicador da pergunta."
        ),
    },
    {
        "id": "faturamento_bruto",
        "rotulo": "Faturamento bruto",
        "modulo": "Financeiro",
        "aliases": (
            "faturamento bruto",
            "valor bruto",
            "bruto",
        ),
        "definicao": (
            "Valor das vendas concluídas antes dos descontos. "
            "O faturamento da pergunta é o líquido."
        ),
        "nao_e": "Não some bruto e desconto de novo: o backend já entrega o líquido.",
    },
    {
        "id": "ticket_medio",
        "rotulo": "Ticket médio",
        "modulo": "Financeiro",
        "aliases": (
            "ticket medio",
            "ticket",
            "valor medio por venda",
        ),
        "definicao": (
            "Faturamento líquido dividido pela quantidade de "
            "vendas concluídas no período."
        ),
        "nao_e": "Não é o preço de um produto nem o valor de uma parcela.",
    },
    {
        "id": "vendas_concluidas",
        "rotulo": "Vendas concluídas",
        "modulo": "Financeiro",
        "aliases": (
            "vendas concluidas",
            "total de vendas",
            "quantidade de vendas",
        ),
        "definicao": (
            "Número de vendas com status Concluída no período. "
            "É quantidade, não valor em reais."
        ),
        "nao_e": "Não é faturamento. Uma venda pode gerar várias parcelas a receber.",
    },
    {
        "id": "cmv",
        "rotulo": "CMV",
        "modulo": "Financeiro",
        "aliases": (
            "cmv",
            "custo das mercadorias vendidas",
            "custo da mercadoria vendida",
            "custo da mercadoria",
            "custo do que foi vendido",
        ),
        "definicao": (
            "Custo, para a Urban Style, das peças que ela "
            "efetivamente vendeu no período."
        ),
        "nao_e": (
            "Não é despesa operacional. Não é o que a empresa "
            "comprou no mês (isso é compra de mercadorias)."
        ),
    },
    {
        "id": "compra_mercadorias",
        "rotulo": "Compra de mercadorias",
        "modulo": "Financeiro",
        "aliases": (
            "compra de mercadorias",
            "compras",
            "o que a empresa comprou",
        ),
        "definicao": (
            "Aquisição de estoque no período. Pode ser diferente "
            "do CMV, porque nem tudo que se compra é vendido no mesmo mês."
        ),
        "nao_e": (
            "Não entra na despesa operacional. Não é o CMV. "
            "Nas saídas de caixa, a compra pode aparecer."
        ),
    },
    {
        "id": "despesa",
        "rotulo": "Despesa operacional",
        "modulo": "Financeiro",
        "aliases": (
            "despesa",
            "despesas",
            "despesa operacional",
            "gastos operacionais",
            "gasto",
        ),
        "definicao": (
            "Gasto de estrutura por competência: Aluguel, Energia, "
            "Marketing, Tecnologia, Frete Operacional e Impostos."
        ),
        "nao_e": (
            "Não inclui compra de mercadorias. Não é saída de caixa. "
            "Não é CMV."
        ),
    },
    {
        "id": "cmv_vs_despesa",
        "rotulo": "CMV e despesa",
        "modulo": "Financeiro",
        "aliases": (
            "cmv e despesa",
            "cmv vs despesa",
            "diferenca cmv despesa",
            "custo e despesa",
        ),
        "definicao": (
            "CMV é o custo das peças vendidas. Despesa operacional "
            "é o gasto de estrutura (aluguel, energia, marketing etc.)."
        ),
        "nao_e": "Não são a mesma conta. Compra de mercadorias também não é despesa.",
    },
    {
        "id": "lucro_bruto",
        "rotulo": "Lucro bruto",
        "modulo": "Financeiro",
        "aliases": (
            "lucro bruto",
        ),
        "definicao": (
            "Faturamento menos CMV. Ainda não descontou "
            "as despesas operacionais."
        ),
        "nao_e": (
            "Não é o lucro da pergunta no DUAXIS. "
            "O resultado final é o lucro após despesas."
        ),
    },
    {
        "id": "lucro",
        "rotulo": "Lucro após despesas",
        "modulo": "Financeiro",
        "aliases": (
            "lucro",
            "lucro apos despesas",
            "resultado",
            "quanto sobrou",
        ),
        "definicao": (
            "Faturamento menos CMV menos despesa operacional, "
            "por competência. É o lucro que o DUAXIS usa na pergunta."
        ),
        "nao_e": (
            "Não é lucro líquido contábil. Não é saldo de caixa."
        ),
    },
    {
        "id": "faturamento_vs_caixa",
        "rotulo": "Faturamento e caixa",
        "modulo": "Financeiro",
        "aliases": (
            "faturamento e caixa",
            "faturamento vs caixa",
            "diferenca faturamento caixa",
            "faturamento ou caixa",
        ),
        "definicao": (
            "Faturamento é a venda na competência. "
            "Caixa é o dinheiro que entrou ou saiu na data "
            "da movimentação. Podem ser meses diferentes."
        ),
        "nao_e": "Não são o mesmo indicador. O DUAXIS não mistura os dois.",
    },
    {
        "id": "competencia",
        "rotulo": "Competência",
        "modulo": "Financeiro",
        "aliases": (
            "competencia",
            "por competencia",
            "regime de competencia",
        ),
        "definicao": (
            "O fato entra no mês em que a venda ou a despesa ocorreu, "
            "não no mês em que o dinheiro saiu ou entrou."
        ),
        "nao_e": "Não é fluxo de caixa nem data da movimentação bancária.",
    },
    {
        "id": "fluxo_caixa",
        "rotulo": "Fluxo de caixa",
        "modulo": "Financeiro",
        "aliases": (
            "fluxo de caixa",
            "caixa",
            "saldo de caixa",
            "entradas e saidas",
        ),
        "definicao": (
            "Entradas menos saídas na data da movimentação. "
            "As saídas incluem compra de mercadorias e despesas."
        ),
        "nao_e": (
            "Não é faturamento nem lucro. A base não tem estoque "
            "de caixa (saldo acumulado desde o início)."
        ),
    },
    {
        "id": "contas_a_receber",
        "rotulo": "Contas a receber",
        "modulo": "Financeiro",
        "aliases": (
            "contas a receber",
            "a receber",
            "inadimplencia",
            "parcelas em aberto",
        ),
        "definicao": (
            "Parcelas já emitidas até a data de referência e ainda "
            "não recebidas nessa data."
        ),
        "nao_e": (
            "Não é faturamento do período. Não é dinheiro já recebido no caixa."
        ),
    },
    {
        "id": "contas_a_pagar",
        "rotulo": "Contas a pagar",
        "modulo": "Financeiro",
        "aliases": (
            "contas a pagar",
            "a pagar",
            "o que a empresa deve",
        ),
        "definicao": (
            "Obrigações em aberto na data de referência: "
            "já emitidas e ainda não pagas nessa data."
        ),
        "nao_e": (
            "Não é despesa operacional do mês. Não é valor já pago no caixa."
        ),
    },
    {
        "id": "vencido_a_vencer",
        "rotulo": "Vencido e a vencer",
        "modulo": "Financeiro",
        "aliases": (
            "vencido",
            "a vencer",
            "valor vencido",
            "valor a vencer",
        ),
        "definicao": (
            "No contas a receber ou a pagar em aberto: vencido já passou "
            "do vencimento na data de referência; a vencer ainda não."
        ),
        "nao_e": "Os dois somam o valor em aberto. Não são faturamento.",
    },
    {
        "id": "simulacao",
        "rotulo": "Simulação (e se)",
        "modulo": "Financeiro",
        "aliases": (
            "simulacao",
            "e se",
            "ceteris paribus",
            "lucro real",
            "lucro simulado",
            "impacto no lucro",
        ),
        "definicao": (
            "Recalcula o lucro mudando só uma parcela. "
            "Lucro real é o do período; simulado é o cenário; "
            "impacto é a diferença entre os dois."
        ),
        "nao_e": (
            "Não inventa ação comercial. Não é fluxo de caixa. "
            "As parcelas que não entram no cenário ficam iguais."
        ),
    },
    {
        "id": "reposicao",
        "rotulo": "Reposição",
        "modulo": "Logística",
        "aliases": (
            "reposicao",
            "repor estoque",
            "quantidade recomendada",
        ),
        "definicao": (
            "Quantidade sugerida de compra a partir da demanda prevista, "
            "do estoque e do lead time."
        ),
        "nao_e": "Não é um pedido já feito ao fornecedor.",
    },
    {
        "id": "cobertura",
        "rotulo": "Cobertura de estoque",
        "modulo": "Logística",
        "aliases": (
            "cobertura",
            "cobertura de estoque",
            "dias de estoque",
        ),
        "definicao": (
            "Quantos dias o estoque atual duraria na demanda prevista."
        ),
        "nao_e": "Não é o lead time. Os dois são comparados no risco de ruptura.",
    },
    {
        "id": "lead_time",
        "rotulo": "Lead time",
        "modulo": "Logística",
        "aliases": (
            "lead time",
            "prazo de entrega do fornecedor",
            "tempo de reposição",
        ),
        "definicao": (
            "Dias entre pedir a mercadoria e ela estar disponível no estoque."
        ),
        "nao_e": "Não é cobertura de estoque.",
    },
    {
        "id": "risco_ruptura",
        "rotulo": "Risco de ruptura",
        "modulo": "Logística",
        "aliases": (
            "risco de ruptura",
            "ruptura",
            "faltar produto",
        ),
        "definicao": (
            "Compara cobertura de estoque com o lead time. "
            "Pode ser Crítico, Alto, Moderado ou Baixo."
        ),
        "nao_e": "Não é previsão inventada pela LLM; o backend classifica.",
    },
    {
        "id": "baixo_giro",
        "rotulo": "Baixo giro",
        "modulo": "Logística",
        "aliases": (
            "baixo giro",
            "encalhado",
            "estoque parado",
            "produto parado",
        ),
        "definicao": (
            "Candidatos a menor giro: a venda desacelerou e ficou abaixo "
            "do padrão sazonal equivalente."
        ),
        "nao_e": (
            "Não é classificação definitiva de produto encalhado."
        ),
    },
    {
        "id": "taxa_atraso",
        "rotulo": "Taxa de atraso do fornecedor",
        "modulo": "Logística",
        "aliases": (
            "taxa de atraso",
            "fornecedor que mais atrasou",
            "atraso de fornecedor",
        ),
        "definicao": (
            "Percentual de pedidos já entregues que chegaram atrasados. "
            "O ranking usa a taxa, não a quantidade absoluta."
        ),
        "nao_e": "Pedidos ainda não entregues não entram nessa métrica.",
    },
    {
        "id": "duaxis",
        "rotulo": "DUAXIS",
        "modulo": "Sistema",
        "aliases": (
            "duaxis",
            "o que voce faz",
            "o que o duaxis faz",
            "copiloto",
        ),
        "definicao": (
            "Copiloto de IA da Urban Style. Consulta indicadores "
            "calculados no backend; a LLM interpreta, não inventa números."
        ),
        "nao_e": (
            "Não substitui o ERP. Não responde conhecimento geral. "
            "Não treinamos a IA generativa; há um modelo preditivo de demanda."
        ),
    },
    {
        "id": "perguntas_sugeridas",
        "rotulo": "Perguntas que você pode fazer",
        "modulo": "Sistema",
        "aliases": (
            "o que eu posso te perguntar",
            "o que posso te perguntar",
            "o que posso perguntar",
            "o que voce pode responder",
            "o que posso te perguntar",
            "exemplos de perguntas",
            "sugestoes de perguntas",
            "me da sugestoes",
            "o que perguntar",
            "que perguntas posso fazer",
            "como te usar",
            "por onde comecar",
        ),
        "definicao": (
            "Você pode perguntar indicadores da Urban Style, "
            "comparar períodos, simular um 'e se' ou pedir "
            "o significado de um termo do DUAXIS."
        ),
        "nao_e": "",
        "sugestoes": (
            "Quanto faturei em junho de 2026?",
            "Qual foi o lucro em maio de 2026?",
            "O que é CMV?",
            "Qual a diferença entre faturamento e caixa?",
            "Quais produtos precisam de reposição?",
            "E se as despesas de maio de 2026 aumentarem 8%, ainda teremos lucro?",
            "E se o CMV de maio de 2026 subir 10%, ainda teremos lucro?",
            "Há pedidos atrasados?",
        ),
    },
    {
        "id": "modelo_preditivo",
        "rotulo": "Modelo preditivo de demanda",
        "modulo": "Sistema",
        "aliases": (
            "modelo preditivo",
            "machine learning",
            "ml",
            "random forest",
            "previsao de demanda",
            "ia treinada",
        ),
        "definicao": (
            "RandomForest de demanda usado em previsão futura e reposição. "
            "Fato histórico usa dado real, não essa previsão."
        ),
        "nao_e": (
            "Não é a LLM do chat. Não usamos ML para calcular faturamento, "
            "despesa ou lucro."
        ),
    },
]


def _montar(conceito, termo_consultado):
    retorno = {
        "termo_consultado": termo_consultado,
        "conceito_id": conceito["id"],
        "rotulo": conceito["rotulo"],
        "modulo": conceito["modulo"],
        "definicao": conceito["definicao"],
        "nao_e": conceito.get("nao_e") or "",
        "fonte": "Glossário oficial do DUAXIS",
        "criterio": "definição do sistema, não conhecimento geral",
    }
    if conceito.get("sugestoes"):
        retorno["sugestoes"] = list(conceito["sugestoes"])
    return retorno


def explicar_conceito(termo):
    if termo is None or str(termo).strip() == "":
        return {
            "erro": (
                "Informe o termo que deseja explicar "
                "(ex.: CMV, faturamento, despesa)."
            ),
            "termo_consultado": termo,
        }

    consulta = _normalizar(termo)
    if consulta == "":
        return {
            "erro": "Informe o termo que deseja explicar.",
            "termo_consultado": termo,
        }

    for conceito in CONCEITOS:
        chaves = [_normalizar(conceito["id"])] + list(conceito["aliases"])
        chaves = [_normalizar(chave) for chave in chaves]
        if consulta in chaves:
            return _montar(conceito, termo)

    pontuados = []
    for conceito in CONCEITOS:
        chaves = [_normalizar(conceito["id"])] + [
            _normalizar(alias) for alias in conceito["aliases"]
        ]
        melhor = 0
        for chave in chaves:
            if not chave:
                continue
            if chave == consulta:
                melhor = max(melhor, 100)
            elif chave in consulta:
                melhor = max(melhor, 10 + len(chave))
            elif consulta in chave:
                melhor = max(melhor, 5 + len(consulta))
        if melhor > 0:
            pontuados.append((melhor, conceito))

    if not pontuados:
        return {
            "erro": (
                f'Não encontrei "{termo}" no glossário do DUAXIS. '
                "Posso explicar indicadores da Urban Style, como "
                "CMV, faturamento, despesa, lucro, competência "
                "e fluxo de caixa."
            ),
            "termo_consultado": termo,
        }

    pontuados.sort(key=lambda item: item[0], reverse=True)
    return _montar(pontuados[0][1], termo)
