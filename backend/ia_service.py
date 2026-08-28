# Biblioteca padrão do Python
import os
from pathlib import Path

# Biblioteca para manipulação de arquivos JSON
import json

from ml_service import (
    analisar_reposicao,
    listar_produtos_reposicao
)

from logistica_service import (
    consultar_pedidos_atrasados,
    listar_produtos_maior_risco
)

# lê o .env
from dotenv import load_dotenv
# Classe que cria nosso cliente para conversar com o modelo
from groq import Groq

tools = [

    {
        "type": "function",

        "function": {

            "name": "analisar_reposicao",

            "description": (
                "Analisa a necessidade de reposição de um "
                "produto específico. Use quando o usuário "
                "perguntar sobre estoque, necessidade de compra "
                "ou quantidade recomendada de reposição de um "
                "produto identificado por produto_id."
            ),

            "parameters": {

                "type": "object",
                "properties": {

                    "produto_id": {

                        "type": "string",

                        "description": (
                            "Código do produto no formato PROD017."
                        )
                    }

                },

                "required": [
                    "produto_id"
                ],
                "additionalProperties": False

            }

        }

    },


    {
        "type": "function",

        "function": {

            "name": "listar_produtos_reposicao",

            "description": (
                "Analisa todos os produtos e identifica quais "
                "precisam de reposição. Use quando o usuário "
                "perguntar de forma geral quais produtos, itens "
                "ou mercadorias precisam ser comprados ou repostos."
            ),

            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
            
        }
    },


    {
        "type": "function",

        "function": {

            "name": "consultar_pedidos_atrasados",

            "description": (
                "Consulta os pedidos de compra atualmente "
                "atrasados, ou seja, pedidos ainda não recebidos "
                "cuja data prevista de entrega já foi ultrapassada."
            ),

            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }

        }
    },

    {
    "type": "function",

    "function": {

        "name": "listar_produtos_maior_risco",

        "description": (
            "Analisa todos os produtos da Urban Style e identifica "
            "quais apresentam maior risco de ruptura de estoque. "
            "Use quando o usuário perguntar sobre produtos com maior "
            "risco de faltar, acabar, romper estoque ou ficar sem estoque."
        ),

        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }

    }
}
    

]

funcoes_disponiveis = {

    "analisar_reposicao":
        analisar_reposicao,

    "listar_produtos_reposicao":
        listar_produtos_reposicao,

    "consultar_pedidos_atrasados":
        consultar_pedidos_atrasados,

    "listar_produtos_maior_risco":
    listar_produtos_maior_risco    

}


load_dotenv(Path(__file__).resolve().parent / ".env")

_cliente = None


def get_cliente():
    global _cliente

    if _cliente is None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY não encontrada. "
                "Configure a variável no .env local ou nas Environment Variables da Vercel."
            )

        _cliente = Groq(api_key=api_key)

    return _cliente

# Função que recebe uma pergunta do usuário e retorna a intenção e o ID do produto
def interpretar_pergunta(pergunta):

# Cria uma resposta do modelo de linguagem com base na pergunta do usuário
    resposta = get_cliente().chat.completions.create(
        # Modelo de linguagem que será utilizado para interpretar a pergunta do usuário
        model="openai/gpt-oss-20b",

# Contexto do que o modelo deve fazer e a pergunta do usuário
        messages=[
            {
                # Contexto do que o modelo deve fazer
                "role": "system",
    "content": """
Você é o interpretador de intenções do sistema DUAXIS.

Sua função é identificar o que o usuário deseja fazer.

Você conhece atualmente três intenções:

1. analisar_reposicao

Use quando o usuário estiver perguntando sobre a reposição,
compra, estoque ou necessidade de compra de UM produto específico.

Quando houver um produto específico, identifique também seu ID.

Exemplos:
"Quanto devo comprar do PROD017?"
"Preciso repor o PROD004?"
"O estoque do PROD045 está suficiente?"

2. listar_produtos_reposicao

Use quando o usuário quiser saber QUAIS produtos precisam
de reposição, sem perguntar especificamente sobre um único produto.

Exemplos:
"Quais produtos precisam de reposição?"
"O que preciso comprar para o estoque?"
"Quais itens devo repor?"
"Mostre os produtos que precisam ser comprados."

3. consultar_pedidos_atrasados

Use quando o usuário quiser saber quais compras ou entregas chegaram depois da data prevista.

Exemplos:
"Quais pedidos chegaram atrasados?"
"Quais entregas tiveram atraso?"
"Quais compras foram recebidas depois do prazo?"
"Mostre os pedidos com atraso na entrega."

Responda sempre em JSON utilizando exatamente esta estrutura:

{
    "intencao": "nome_da_intencao",
    "produto_id": "PROD017"
}

Quando não houver um produto específico, produto_id deve ser null.
"""

            },
            {
                # Pergunta do usuário
                "role": "user",
                "content": pergunta
            }
        ],
# Formato da resposta do modelo, que deve ser um JSON
        response_format={
        "type": "json_object"
    },
        
# Temperatura do modelo, que define o nível de criatividade da resposta. 0 = mais objetivo, 1 = mais criativo
        temperature=0
    )
# Conteúdo da resposta do modelo, que é um JSON no formato definido acima
    conteudo = resposta.choices[0].message.content

    resultado = json.loads(conteudo)

    return resultado

def processar_pergunta_usuario(pergunta):

    interpretacao = interpretar_pergunta(pergunta)

    intencao = interpretacao["intencao"]
    produto_id = interpretacao["produto_id"]

    if intencao == "analisar_reposicao":

        resultado = analisar_reposicao(
            produto_id
        )

        resultado["tipo_resposta"] = "reposicao_individual"

        return resultado


    if intencao == "listar_produtos_reposicao":

        analise_reposicao = listar_produtos_reposicao()

        produtos_reposicao = analise_reposicao[
            "produtos_reposicao"
        ]

        impacto_total = sum(
            produto["impacto_financeiro"]
            for produto in produtos_reposicao
        )

        return {
            "tipo_resposta": "lista_reposicao",
            "total_analisados": analise_reposicao[
                "total_analisados"
            ],
            "total_produtos": len(produtos_reposicao),
            "impacto_total": round(impacto_total, 2),
            "produtos": produtos_reposicao
        }


    if intencao == "consultar_pedidos_atrasados":

        resultado = consultar_pedidos_atrasados()

        return {
            "tipo_resposta": "pedidos_atrasados",
            "total_atrasados": resultado["total_atrasados"],
            "pedidos": resultado["pedidos"]
        }


    return {
        "tipo_resposta": "erro",
        "mensagem": "Intenção ainda não suportada."
    }

def preparar_resultado_para_ia(
    nome_funcao,
    resultado
):

    # =====================================================
    # REPOSIÇÃO DE UM PRODUTO ESPECÍFICO
    # =====================================================
    #
    # O resultado já é pequeno.
    # Podemos enviar as informações principais para a IA.
    # =====================================================

    if nome_funcao == "analisar_reposicao":

        return {
            "produto_id":
                resultado["produto_id"],

            "nome_produto":
                resultado["nome_produto"],

            "demanda_prevista":
                resultado["demanda_prevista"],

            "estoque_atual":
                resultado["estoque_atual"],

            "estoque_minimo":
                resultado["estoque_minimo"],

            "quantidade_recomendada":
                resultado["quantidade_recomendada"],

            "impacto_financeiro":
                resultado["impacto_financeiro"],

            "cobertura_estoque_dias":
                resultado["cobertura_estoque_dias"],

            "lead_time_dias":
                resultado["lead_time_dias"],

            "risco_ruptura_imediato":
                resultado["risco_ruptura_imediato"]
        }


    # =====================================================
    # LISTA DE PRODUTOS PARA REPOSIÇÃO
    # =====================================================
    #
    # Aqui temos muitos produtos.
    #
    # O front-end continuará recebendo TODOS,
    # mas a IA recebe somente:
    #
    # - quantidade total
    # - impacto total
    # - os 5 produtos mais prioritários
    # =====================================================

    if nome_funcao == "listar_produtos_reposicao":

        produtos_reposicao = resultado[
            "produtos_reposicao"
        ]

        impacto_total = sum(
            produto["impacto_financeiro"]
            for produto in produtos_reposicao
        )

        principais_produtos = []

        for produto in produtos_reposicao[:5]:

            principais_produtos.append(
                {
                    "produto_id":
                        produto["produto_id"],

                    "nome_produto":
                        produto["nome_produto"],

                    "quantidade_recomendada":
                        produto["quantidade_recomendada"],

                    "impacto_financeiro":
                        produto["impacto_financeiro"]
                }
            )


        return {
            "total_analisados":
                resultado["total_analisados"],

            "total_produtos_reposicao":
                len(produtos_reposicao),

            "impacto_total_estimado":
                round(
                    impacto_total,
                    2
                ),

            "principais_produtos":
                principais_produtos
        }


    # =====================================================
    # PEDIDOS ATUALMENTE ATRASADOS
    # =====================================================
    #
    # Como temos somente 8 pedidos atualmente,
    # podemos enviar todos eles.
    #
    # Mesmo assim, retiramos campos desnecessários.
    # =====================================================

    if nome_funcao == "consultar_pedidos_atrasados":

        pedidos_para_ia = []

        for pedido in resultado["pedidos"]:

            pedidos_para_ia.append(
                {
                    "id_compra":
                        pedido["id_compra"],

                    "nome_produto":
                        pedido["nome_produto"],

                    "produto_id":
                        pedido["produto_id"],

                    "nome_fornecedor":
                        pedido["nome_fornecedor"],

                    "fornecedor_id":
                        pedido["fornecedor_id"],

                    "status":
                        pedido["status"],

                    "data_prevista_entrega":
                        pedido["data_prevista_entrega"],

                    "dias_atraso":
                        pedido["dias_atraso"]
                }
            )


        return {
            "total_atrasados":
                resultado["total_atrasados"],

            "data_referencia":
                resultado["data_referencia"],

            "pedidos":
                pedidos_para_ia
        }
# =====================================================
# PRODUTOS COM MAIOR RISCO DE RUPTURA
# =====================================================
#
# O front-end recebe os 80 produtos completos.
#
# A IA recebe apenas o resumo geral da análise.
#
# Os produtos e indicadores individuais serão
# apresentados visualmente pelo front-end.
# =====================================================

    if nome_funcao == "listar_produtos_maior_risco":

        return {
            "total_analisados":
                resultado["total_analisados"],

            "total_critico":
                resultado["total_critico"],

            "total_alto":
                resultado["total_alto"],

            "total_moderado":
                resultado["total_moderado"],

            "total_baixo":
                resultado["total_baixo"]
        }


    # =====================================================
    # SEGURANÇA
    # =====================================================
    #
    # Se no futuro adicionarmos uma ferramenta
    # e esquecermos de criar uma versão compacta,
    # devolvemos o resultado original.
    # =====================================================

    return resultado


def processar_pergunta_com_tools(pergunta):

    mensagens = [

        {
            "role": "system",

            "content": """
Você é o copiloto corporativo DUAXIS.

Ajude gestores a consultar informações financeiras
e logísticas da empresa.

Você atua exclusivamente no contexto da empresa fictícia
Urban Style e das funcionalidades do sistema DUAXIS.

Não responda perguntas de conhecimento geral, entretenimento,
esportes, política, ciência, cultura, clima, notícias,
curiosidades ou qualquer outro assunto que não esteja
relacionado à Urban Style ou ao DUAXIS.

Se o usuário fizer uma pergunta fora desse escopo,
não responda ao conteúdo da pergunta.

Responda apenas:

"Posso ajudar apenas com informações e análises relacionadas à Urban Style e às funcionalidades do DUAXIS."

Perguntas sobre o próprio DUAXIS, suas funcionalidades,
capacidades ou forma de funcionamento estão dentro do escopo.

Sempre utilize as ferramentas disponíveis quando
a pergunta depender de dados da empresa.

Nunca invente valores, produtos, fornecedores,
estoques, previsões ou resultados financeiros.

Use exclusivamente os dados retornados pelas ferramentas.

Não atribua causas, prioridades, riscos, urgência ou
importância a um dado se essa informação não estiver
explicitamente presente no resultado da ferramenta.

Quando receber uma lista ordenada, não assuma o critério
da ordenação. Apenas descreva os valores apresentados.

Depois de receber o resultado de uma ferramenta,
responda em português claro, profissional e objetivo.

Não utilize tabelas Markdown na resposta.

O front-end já apresenta os dados detalhados em cards
e listas estruturadas.

Use a resposta textual apenas para resumir e explicar
os principais resultados em parágrafos curtos.

Evite repetir na resposta textual os mesmos dados que
serão apresentados pelo front-end.

Não enumere produtos, pedidos, fornecedores ou outros
registros quando esses registros já estiverem presentes
no resultado estruturado da ferramenta.

Não repita individualmente valores como estoque, cobertura,
lead time, quantidade, impacto financeiro, atraso ou outros
indicadores que serão exibidos nos cards ou listas.

Priorize conclusões gerais, padrões e interpretações
sustentadas pelos dados retornados pela ferramenta.

Quando houver níveis de risco, destaque principalmente
a situação geral da análise, como a existência ou ausência
de níveis críticos, altos ou moderados

Quando houver muitos registros, apresente apenas um resumo
da situação geral. Os registros detalhados serão apresentados
pelo front-end e não precisam ser enumerados na resposta textual.
"""

        },

        {
            "role": "user",
            "content": pergunta
        }

    ]
    # =====================================================
    # 1ª CHAMADA AO MODELO
    # =====================================================
    #
    # Aqui a IA recebe:
    #
    # - a pergunta
    # - as ferramentas disponíveis
    #
    # e decide se precisa chamar alguma delas.
    # =====================================================

    resposta = get_cliente().chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=mensagens,

        tools=tools,

        tool_choice="auto",

        temperature=0
    )


    mensagem_modelo = (
        resposta
        .choices[0]
        .message
    )
    # =====================================================
    # VERIFICA SE A IA PEDIU ALGUMA FERRAMENTA
    # =====================================================

    tool_calls = (
        mensagem_modelo.tool_calls
        or []
    )
    # =====================================================
    # SE NÃO PRECISAR DE FERRAMENTA
    # =====================================================
    #
    # Exemplo:
    #
    # "Olá"
    # "O que você pode fazer?"
    #
    # Nesse caso o modelo pode responder diretamente.
    # =====================================================

    if not tool_calls:

        return {
            "tipo_resposta": "texto",
            "resposta_ia": mensagem_modelo.content
        }
    # =====================================================
    # GUARDA A DECISÃO DA IA NO HISTÓRICO
    # =====================================================

    mensagens.append(
        mensagem_modelo
    )
    # =====================================================
    # EXECUTA AS FERRAMENTAS SOLICITADAS
    # =====================================================

    resultados_ferramentas = []

    for tool_call in tool_calls:

        nome_funcao = (
            tool_call
            .function
            .name
        )
        # -------------------------------------------------
        # SEGURANÇA:
        # CONFIRMA SE A FUNÇÃO EXISTE
        # -------------------------------------------------

        if nome_funcao not in funcoes_disponiveis:

            raise ValueError(
                f"Ferramenta desconhecida: {nome_funcao}"
            )
        # -------------------------------------------------
        # ARGUMENTOS VÊM DA IA COMO TEXTO JSON
        # -------------------------------------------------

        argumentos = json.loads(
            tool_call
            .function
            .arguments
        )
        argumentos = {
            chave: valor
            for chave, valor in argumentos.items()
            if chave.strip()
        }
        # -------------------------------------------------
        # PEGA A FUNÇÃO PYTHON REAL
        # -------------------------------------------------

        funcao = funcoes_disponiveis[
            nome_funcao
        ]


        # -------------------------------------------------
        # EXECUTA A FUNÇÃO
        # -------------------------------------------------
        #
        # O **argumentos permite transformar:
        #
        # {
        #   "produto_id": "PROD017"
        # }
        #
        # em:
        #
        # analisar_reposicao(
        #     produto_id="PROD017"
        # )
        # -------------------------------------------------
        if nome_funcao in [
            "listar_produtos_reposicao",
            "consultar_pedidos_atrasados"
            "listar_produtos_maior_risco"
]:
            resultado = funcao()

        else:
            resultado = funcao(
                **argumentos
    )

        # Guarda também para nosso backend/front-end
        resultados_ferramentas.append(
            {
                "ferramenta": nome_funcao,
                "resultado": resultado
            }
        )
        resultado_para_ia = (
            preparar_resultado_para_ia(
            nome_funcao,
            resultado
    )
)
        
        # -------------------------------------------------
        # DEVOLVE O RESULTADO DA FERRAMENTA PARA A IA
        # -------------------------------------------------
        mensagens.append(
            {
                "role": "tool",

                "tool_call_id":
                    tool_call.id,

                "name":
                    nome_funcao,

                "content":
                    json.dumps(
                        resultado_para_ia,
                        ensure_ascii=False
                    )
            }
        )


    # =====================================================
    # 2ª CHAMADA AO MODELO
    # =====================================================
    #
    # Agora a IA já tem:
    #
    # pergunta original
    # +
    # ferramenta escolhida
    # +
    # resultado real da ferramenta
    #
    # Ela deve apenas interpretar e explicar.
    # =====================================================

    resposta_final = (
        get_cliente().chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=mensagens,

            tools=tools,

            # Forçamos agora uma resposta textual.
            # Não queremos outra tool call nesta versão.
            tool_choice="none",

            temperature=0.2
        )
    )


    texto_final = (
        resposta_final
        .choices[0]
        .message
        .content
    )


    # =====================================================
    # RETORNO PARA O BACKEND
    # =====================================================

    return {
        "tipo_resposta": "resposta_ia",
        "resposta_ia": texto_final,
        "ferramentas_utilizadas": resultados_ferramentas
    }

# TESTE
if __name__ == "__main__":

    resultado = processar_pergunta_com_tools(
        "Quais produtos têm maior risco de ruptura?"
    )

    print(
        "Resposta IA:",
        resultado["resposta_ia"]
    )

    print(
        "\nFerramenta:",
        resultado[
            "ferramentas_utilizadas"
        ][0]["ferramenta"]
    )
    