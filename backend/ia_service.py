# Biblioteca pdrão do Python
import os

# Biblioteca para manipulação de arquivos JSON
import json

from ml_service import (
    analisar_reposicao,
    listar_produtos_reposicao
)

from logistica_service import consultar_pedidos_atrasados

# lê o .env
from dotenv import load_dotenv
# Classe que cria nosso cliente para conversar com o modelo
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

os.getenv("GROQ_API_KEY")

# Se não existir chave, pare o programa com uma mensagem compreensivel
if not api_key:
    raise ValueError(
        "GROQ_API_KEY não encontrada. "
        "Verifique o arquivo .env."
    )

# Objeto que sabe qual serviço utilizar + qual chave utilizar
cliente = Groq(
    api_key=api_key
)

# Função que recebe uma pergunta do usuário e retorna a intenção e o ID do produto
def interpretar_pergunta(pergunta):

# Cria uma resposta do modelo de linguagem com base na pergunta do usuário
    resposta = cliente.chat.completions.create(
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


resultado = processar_pergunta_usuario(
    "Tem algum produto ainda atrasado?"
)

print(resultado["tipo_resposta"])
print(resultado["total_atrasados"])

for pedido in resultado["pedidos"][:5]:
    print(
        pedido["id_compra"],
        "- produto:",
        pedido["nome_produto"],
        f"({pedido['produto_id']})",
        "- fornecedor:",
        pedido["nome_fornecedor"],
        f"({pedido['fornecedor_id']})",
        "- atraso:",
        pedido["dias_atraso"],
        "dias"
    )