# Biblioteca pdrão do Python
import os

# Biblioteca para manipulação de arquivos JSON
import json

from ml_service import analisar_reposicao

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

Neste momento, você conhece apenas uma intenção:

analisar_reposicao

Essa intenção deve ser utilizada quando o usuário quiser saber
se precisa comprar, repor ou adquirir determinado produto.

Identifique também o ID do produto mencionado pelo usuário.

Responda somente com um JSON no seguinte formato:

{
    "intencao": "analisar_reposicao",
    "produto_id": "PROD017"
}
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

# Função que processa a pergunta do usuário e retorna o resultado da análise de reposição
def processar_pergunta_usuario(pergunta):

    interpretacao = interpretar_pergunta(pergunta)

    intencao = interpretacao["intencao"]
    produto_id = interpretacao["produto_id"]

    if intencao == "analisar_reposicao":

        resultado = analisar_reposicao(
            produto_id
        )

        return resultado

    return {
        "erro": "Intenção ainda não suportada."
    }


resultado = processar_pergunta_usuario(
    "Preciso repor o PROD004?"
)

print(resultado)