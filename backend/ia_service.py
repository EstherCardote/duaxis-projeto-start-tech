# Biblioteca padrão do Python
import os
import re
from pathlib import Path

# Biblioteca para manipulação de arquivos JSON
import json

from ml_service import (
    analisar_reposicao,
    listar_produtos_reposicao
)

from logistica_service import (
    consultar_pedidos_atrasados,
    listar_produtos_maior_risco,
    listar_produtos_baixo_giro,
    listar_fornecedores_atrasos
)

from financeiro_service import (
    calcular_faturamento,
    comparar_faturamento,
    calcular_despesas,
    comparar_despesas,
    calcular_lucro,
    comparar_lucro,
    explicar_variacao_lucro,
    simular_lucro_despesa,
    simular_lucro_cmv,
    consultar_contas_a_receber,
    consultar_contas_a_pagar,
    calcular_fluxo_caixa,
    comparar_fluxo_caixa
)

from glossario_service import explicar_conceito

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
                "produto, citado pelo código (PROD017) ou pelo "
                "nome (ex.: Tricô Cinza PP)."
            ),

            "parameters": {

                "type": "object",
                "properties": {

                    "produto_id": {

                        "type": "string",

                        "description": (
                            "Código (PROD017), SKU (US-1017) ou "
                            "nome do produto como o usuário escreveu. "
                            "Passe o texto original. Não invente um "
                            "código se o usuário só informou o nome. "
                            "O backend resolve o cadastro."
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
                "Lista produtos que precisam de reposição e o impacto "
                "total da compra. Use em pergunta geral de reposição "
                "ou o que comprar para o estoque. Sem parâmetros."
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
                "Consulta pedidos de compra que estavam atrasados "
                "em uma determinada data de referência. "
                "Quando o usuário informar uma data, envie "
                "data_referencia no formato YYYY-MM-DD. "
                "Quando nenhuma data for informada, não envie "
                "data_referencia."
            ),

            "parameters": {

            "type": "object",

            "properties": {

                "data_referencia": {
                    "type": "string",
                    "description": (
                        "Data em que deve ser verificada a situação "
                        "dos pedidos, no formato YYYY-MM-DD."
                    )
                }

            },

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

    },

    {
    "type": "function",

    "function": {

        "name": "listar_produtos_baixo_giro",

        "description": (
            "Analisa os produtos da Urban Style e identifica "
            "candidatos a menor giro considerando o histórico "
            "de vendas, o comportamento do período analisado, "
            "a sazonalidade e a cobertura de estoque. "
            "Use quando o usuário perguntar sobre produtos com "
            "baixo giro, menor giro, estoque parado, produtos "
            "encalhados ou itens com desaceleração de vendas "
            "em relação ao estoque. "
            "Quando o usuário informar um período, envie "
            "data_inicio e data_fim no formato YYYY-MM."
        ),
        "parameters": {
            "type": "object",
            "properties": {
        "data_inicio": {
            "type": ["string", "null"],
            "description": (
                "Mês inicial da análise no formato YYYY-MM. "
                "Use null quando o usuário não informar um período."
            )
        },
        "data_fim": {
            "type": ["string", "null"],
            "description": (
                "Mês final da análise no formato YYYY-MM. "
                "Use null quando o usuário não informar um período."
            )
        }

            },
            "required": [],
            "additionalProperties": False
        }
    }
    
},
{
    "type": "function",

    "function": {

        "name": "listar_fornecedores_atrasos",

        "description": (
            "Analisa o desempenho dos fornecedores da Urban Style "
            "em relação a atrasos nas entregas. "
            "Use quando o usuário perguntar quais fornecedores "
            "mais atrasaram entregas, quais possuem maior taxa de atraso "
            "ou sobre o desempenho dos fornecedores em relação a prazos. "
            "Quando o usuário informar um período, envie data_inicio "
            "e data_fim no formato YYYY-MM."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "data_inicio": {
                    "type": "string",
                    "description": (
                        "Mês inicial das compras analisadas "
                        "no formato YYYY-MM."
                    )
                },

                "data_fim": {
                    "type": "string",
                    "description": (
                        "Mês final das compras analisadas "
                        "no formato YYYY-MM."
                    )
                }
            },

            "required": [],

            "additionalProperties": False
        }
    }
},
 {
    "type": "function",
    "function": {
        "name": "calcular_faturamento",
        "description": (
            "Calcula o faturamento da Urban Style em um período. "
            "Faturamento é a soma do valor líquido das vendas "
            "concluídas na competência informada. "
            "Use quando o usuário perguntar quanto faturou, "
            "qual foi o faturamento, receita de vendas ou "
            "ticket médio. "
            "Não use para recebimentos, contas a receber, "
            "fluxo de caixa, lucro ou despesas. "
            "Quando o usuário informar um período, envie "
            "data_inicio e data_fim no formato YYYY-MM. "
            "Quando não informar período, não envie as datas."
            "Não use para comparar períodos, variação percentual ou se o faturamento subiu ou caiu. Use comparar_faturamento."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês inicial no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês final no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "calcular_despesas",
        "description": (
            "Calcula as despesas operacionais da Urban Style "
            "em um período, por competência. "
            "Despesa é gasto de estrutura: aluguel, energia, "
            "marketing, tecnologia, frete operacional e impostos. "
            "Não inclui compra de mercadorias (isso é custo). "
            "Não é faturamento, lucro nem fluxo de caixa. "
            "Use quando o usuário perguntar quanto gastou, "
            "quais foram as despesas ou gastos operacionais. "
            "Quando informar um período, envie data_inicio e "
            "data_fim no formato YYYY-MM. "
            "Quando não informar período, não envie as datas. "
            "Não use para comparar períodos, variação ou se a despesa subiu ou caiu. Use comparar_despesas. "
            "Não use para e se a despesa ou o aluguel mudar. "
            "Use simular_lucro_despesa."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês inicial no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês final no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "calcular_lucro",
        "description": (
            "Calcula o lucro da Urban Style em um período. "
            "O resultado principal é lucro após despesas: "
            "faturamento menos CMV (custo das mercadorias vendidas) "
            "menos despesas operacionais, por competência. "
            "Use quando o usuário perguntar lucro, resultado, "
            "quanto sobrou ou se a empresa lucrou. "
            "Não use para faturamento isolado, só despesas, "
            "compras, caixa ou contas a pagar. "
            "Quando informar um período, envie data_inicio e "
            "data_fim no formato YYYY-MM. "
            "Quando não informar período, não envie as datas. "
            "Não use para comparar períodos ou se o lucro "
            "subiu ou caiu. Use comparar_lucro. "
            "Não use para por que o lucro caiu ou o que "
            "explica a variação. Use explicar_variacao_lucro. "
            "Não use para e se a despesa subir ou cair. "
            "Use simular_lucro_despesa. "
            "Não use para e se o CMV ou o custo da "
            "mercadoria mudar. Use simular_lucro_cmv."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês inicial no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês final no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "simular_lucro_despesa",
        "description": (
            "Simula o lucro após despesas se a despesa "
            "operacional variar um percentual, com "
            "faturamento e CMV iguais. "
            "Use em perguntas e se: despesas, aluguel, "
            "energia, marketing, impostos etc. subirem "
            "ou caírem. percentual: 8 para +8%, -10 "
            "para redução. categoria null = todas as "
            "operacionais; senão Aluguel, Energia, "
            "Marketing, Tecnologia, Frete Operacional "
            "ou Impostos. Não é caixa nem CMV. "
            "Não use para e se o CMV mudar: simular_lucro_cmv. "
            "Um mês: data_inicio e data_fim iguais."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "percentual": {
                    "type": "number",
                    "description": "Variação em % (8 ou -10)."
                },
                "categoria": {
                    "type": ["string", "null"],
                    "description": (
                        "Categoria operacional ou null para todas."
                    )
                },
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês atual YYYY-MM."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês atual YYYY-MM."
                }
            },
            "required": ["percentual"],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "simular_lucro_cmv",
        "description": (
            "Simula o lucro se o CMV (custo das mercadorias "
            "vendidas) variar um percentual, com faturamento "
            "e despesa operacional iguais. "
            "Use em e se: CMV, custo da mercadoria ou custo "
            "do que foi vendido subir ou cair. "
            "percentual: 10 para +10%, -5 para redução. "
            "Não é despesa operacional nem caixa. "
            "Um mês: data_inicio e data_fim iguais."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "percentual": {
                    "type": "number",
                    "description": "Variação em % (10 ou -5)."
                },
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês atual YYYY-MM."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês atual YYYY-MM."
                }
            },
            "required": ["percentual"],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "explicar_conceito",
        "description": (
            "Explica um termo do DUAXIS ou da Urban Style. "
            "Use em 'o que é', 'o que significa', "
            "'qual a diferença' entre indicadores "
            "ou 'o que posso te perguntar'. "
            "Exemplos: CMV, faturamento, despesa, lucro, "
            "competência, caixa, reposição, lead time. "
            "Não calcula valores. Envie o termo como "
            "o usuário escreveu."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "termo": {
                    "type": "string",
                    "description": "Termo ou trecho da pergunta."
                }
            },
            "required": ["termo"],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "consultar_contas_a_receber",
        "description": (
            "Consulta o contas a receber da Urban Style "
            "em uma data de referência. "
            "Parcela em aberto: emitida até a data e ainda "
            "não recebida nessa data. "
            "Use quando o usuário perguntar quanto a receber, "
            "inadimplência, parcelas em aberto ou clientes "
            "que devem. "
            "Não use para faturamento, lucro, despesas, "
            "caixa já recebido ou contas a pagar. "
            "Não confundir com consultar_contas_a_pagar. "
            "Quando informar uma data, envie data_referencia "
            "no formato YYYY-MM-DD. "
            "Quando nenhuma data for informada, não envie "
            "data_referencia."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_referencia": {
                "type": ["string", "null"],
                "description": (
                    "Data em que deve ser reconstruído "
                    "o saldo a receber, no formato YYYY-MM-DD. "
                    "Use null quando o usuário não informar data."
                )
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "consultar_contas_a_pagar",
        "description": (
            "Consulta o contas a pagar da Urban Style "
            "em uma data de referência. "
            "Conta em aberto: emitida até a data e ainda "
            "não paga nessa data. São obrigações com "
            "fornecedores de mercadoria, não despesas "
            "operacionais. "
            "Use quando o usuário perguntar quanto a pagar, "
            "o que deve aos fornecedores ou contas em aberto "
            "a pagar. "
            "Não use para faturamento, lucro, despesas "
            "operacionais, caixa já pago, contas a receber "
            "ou fluxo de caixa. "
            "Quando informar uma data, envie data_referencia "
            "no formato YYYY-MM-DD. "
            "Quando nenhuma data for informada, use null."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_referencia": {
                    "type": ["string", "null"],
                    "description": (
                        "Data em que deve ser reconstruído "
                        "o saldo a pagar, no formato YYYY-MM-DD. "
                        "Use null quando o usuário não informar data."
                    )
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "calcular_fluxo_caixa",
        "description": (
            "Calcula o fluxo de caixa da Urban Style "
            "em um período. "
            "Entradas e saídas pela data da movimentação, "
            "não por competência. "
            "Saídas incluem compra de mercadorias e "
            "despesas operacionais. "
            "Use quando o usuário perguntar fluxo de caixa, "
            "quanto entrou ou saiu de dinheiro, recebimentos "
            "e pagamentos efetivos. "
            "Não use para faturamento, lucro, despesas "
            "operacionais isoladas, contas a receber "
            "ou contas a pagar. "
            "Não use para comparar períodos ou se o fluxo "
            "subiu ou caiu. Use comparar_fluxo_caixa. "
            "Quando informar um período, envie data_inicio e "
            "data_fim no formato YYYY-MM. "
            "Um único mês: envie o mesmo valor nos dois. "
            "Quando não informar período, use null."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês inicial no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": (
                        "Mês final no formato YYYY-MM. "
                        "Use null quando o usuário não informar período."
                    )
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "comparar_faturamento",
        "description": (
            "Compara o faturamento líquido de dois períodos "
            "do mesmo tamanho. Use quando o usuário perguntar "
            "se o faturamento subiu ou caiu, a variação, "
            "a diferença entre meses ou 'comparar faturamento'. "
            "Não explique a causa da variação. "
            "Não use para um único período sem comparação "
            "(aí use calcular_faturamento). "
            "Não use para lucro, despesa ou fluxo de caixa. "
            "Período atual: data_inicio e data_fim (YYYY-MM). "
            "Período anterior: data_inicio_anterior e "
            "data_fim_anterior. Se o usuário não informar o "
            "anterior, não envie esses campos."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período atual (YYYY-MM)."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês final do período atual (YYYY-MM)."
                },
                "data_inicio_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período anterior (YYYY-MM)."
                },
                "data_fim_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês final do período anterior (YYYY-MM)."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "comparar_despesas",
        "description": (
            "Compara a despesa operacional de dois períodos "
            "do mesmo tamanho. Use quando o usuário perguntar "
            "se a despesa subiu ou caiu, a variação de gastos "
            "operacionais ou 'comparar despesas'. "
            "Despesa não inclui compra de mercadorias. "
            "Não explique a causa da variação. "
            "Não use para um único período sem comparação "
            "(aí use calcular_despesas). "
            "Não use para faturamento, lucro ou fluxo de caixa. "
            "Período atual: data_inicio e data_fim (YYYY-MM). "
            "Se o usuário não informar o período anterior, "
            "não envie data_inicio_anterior nem data_fim_anterior."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período atual (YYYY-MM)."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês final do período atual (YYYY-MM)."
                },
                "data_inicio_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período anterior (YYYY-MM)."
                },
                "data_fim_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês final do período anterior (YYYY-MM)."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "comparar_lucro",
        "description": (
            "Compara o lucro após despesas de dois períodos "
            "do mesmo tamanho. Lucro após despesas = "
            "faturamento − CMV − despesa operacional. "
            "Use quando o usuário perguntar se o lucro subiu "
            "ou caiu, a variação do resultado ou "
            "'comparar lucro'. "
            "Não explique a causa. Não é lucro líquido contábil. "
            "Não use para um único período (aí use calcular_lucro). "
            "Não use para 'por que caiu', o que explica a "
            "variação ou decomposição das parcelas. "
            "Aí use explicar_variacao_lucro. "
            "Um mês contra o anterior (maio vs abril):"
            "envie data_inicio e data_fim IGUAIS a esse mês"
            "(2026-05 e 2026-05). Não envie data_inicio_anterior"
            "nem data_fim_anterior. Não use 2026-04 a 2026-05."
            "Não use para só faturamento, só despesa ou caixa. "
            "Se o usuário não informar o período anterior, "
            "não envie data_inicio_anterior nem data_fim_anterior."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período atual (YYYY-MM)."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês final do período atual (YYYY-MM)."
                },
                "data_inicio_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período anterior (YYYY-MM)."
                },
                "data_fim_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês final do período anterior (YYYY-MM)."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "explicar_variacao_lucro",
        "description": (
            "Decompõe a variação do lucro após despesas entre "
            "dois períodos do mesmo tamanho. "
            "Mostra quanto da diferença veio de faturamento, "
            "CMV e despesa operacional. "
            "Use quando o usuário perguntar por que o lucro "
            "caiu ou subiu, o que explica a variação do lucro "
            "ou quais parcelas puxaram o resultado. "
            "Não inventa causa comercial, sazonalidade nem caixa. "
            "Não use só para dizer se subiu ou caiu "
            "(aí use comparar_lucro). "
            "Não use para um único período (aí use calcular_lucro). "
            "Se o usuário não informar o período anterior, "
            "não envie data_inicio_anterior nem data_fim_anterior."
            "Um mês contra o anterior (maio vs abril):"
            "envie data_inicio e data_fim IGUAIS a esse mês"
            "(2026-05 e 2026-05). Não envie data_inicio_anterior"
            "nem data_fim_anterior. Não use 2026-04 a 2026-05."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês do período atual (YYYY-MM). Um só mês: o mesmo valor em data_inicio e data_fim."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês do período atual (YYYY-MM). Um só mês: o mesmo valor em data_inicio e data_fim."
                },
                "data_inicio_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período anterior (YYYY-MM)."
                },
                "data_fim_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês final do período anterior (YYYY-MM)."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    }
},

{
    "type": "function",
    "function": {
        "name": "comparar_fluxo_caixa",
        "description": (
            "Compara o saldo de fluxo de caixa de dois períodos "
            "do mesmo tamanho. Saldo = entradas − saídas pela "
            "data da movimentação, não por competência. "
            "Saídas incluem compra de mercadorias e despesas. "
            "Use quando o usuário perguntar se o fluxo, o caixa, "
            "o saldo de caixa ou as entradas e saídas subiram "
            "ou caíram, a variação ou 'comparar fluxo de caixa'. "
            "Não explique a causa. Não é faturamento nem lucro. "
            "Não use para um único período "
            "(aí use calcular_fluxo_caixa). "
            "Se o usuário não informar o período anterior, "
            "não envie data_inicio_anterior nem data_fim_anterior."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_inicio": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período atual (YYYY-MM)."
                },
                "data_fim": {
                    "type": ["string", "null"],
                    "description": "Mês final do período atual (YYYY-MM)."
                },
                "data_inicio_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês inicial do período anterior (YYYY-MM)."
                },
                "data_fim_anterior": {
                    "type": ["string", "null"],
                    "description": "Mês final do período anterior (YYYY-MM)."
                }
            },
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
    listar_produtos_maior_risco,

    "listar_produtos_baixo_giro":
    listar_produtos_baixo_giro,

    "listar_fornecedores_atrasos":
    listar_fornecedores_atrasos,

    "calcular_faturamento":
    calcular_faturamento,

    "comparar_faturamento":
    comparar_faturamento,

    "calcular_despesas":
    calcular_despesas,

    "comparar_despesas":
    comparar_despesas,

    "calcular_lucro":
    calcular_lucro,

    "comparar_lucro":
    comparar_lucro,

    "explicar_variacao_lucro":
    explicar_variacao_lucro,

    "explain_variacao_lucro":
    explicar_variacao_lucro,

    "simular_lucro_despesa":
    simular_lucro_despesa,

    "simular_lucro_cmv":
    simular_lucro_cmv,

    "explicar_conceito":
    explicar_conceito,

    "explainar_conceito":
    explicar_conceito,

    "explain_conceito":
    explicar_conceito,

    "consultar_contas_a_receber":
    consultar_contas_a_receber,

    "consultar_contas_a_pagar":
    consultar_contas_a_pagar,

    "calcular_fluxo_caixa":
    calcular_fluxo_caixa,

    "comparar_fluxo_caixa":
    comparar_fluxo_caixa

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

Quando a ferramenta listar_fornecedores_atrasos for utilizada,
considere que o ranking principal é baseado na taxa percentual
de pedidos entregues com atraso.

Não confunda maior taxa de atraso com maior quantidade absoluta
de pedidos atrasados.

Use expressões como "maior taxa de atraso" ou
"maior percentual de atrasos" ao interpretar o ranking.
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

        return {
            "total_analisados":
                resultado["total_analisados"],

            "total_produtos_reposicao":
                resultado["total_reposicao"],

            "impacto_total_estimado":
                resultado["impacto_financeiro_total"]
        }


    # =====================================================
    # PEDIDOS ATRASADOS
    # =====================================================
    #
    # O front-end recebe a lista completa.
    # A IA só precisa do total e da data.
    # =====================================================

    if nome_funcao == "consultar_pedidos_atrasados":

        return {
            "total_atrasados":
                resultado["total_atrasados"],

            "data_referencia":
                resultado["data_referencia"]
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
    # PRODUTOS COM MENOR GIRO
    # =====================================================
    #
    # O front-end recebe todos os candidatos encontrados.
    #
    # A IA recebe apenas um resumo geral e alguns
    # indicadores dos primeiros produtos do ranking.
    #
    # Isso evita repetir no texto todos os dados que
    # serão apresentados visualmente pelo front-end.
    # =====================================================

    if nome_funcao == "listar_produtos_baixo_giro":

        return {
        "total_analisados":
            resultado["total_analisados"],

        "total_candidatos":
            resultado["total_candidatos"],

        "periodo_referencia":
            resultado["periodo_referencia"],

        "criterios_utilizados": {
            "desaceleracao_periodo":
                (
                    "Média mensal do período analisado "
                    "abaixo da média mensal dos últimos 12 meses."
                ),

            "comparacao_sazonal":
                (
                    "Vendas do período analisado abaixo da média "
                    "do mesmo período nos anos históricos comparáveis."
                ),

            "ordenacao":
                (
                    "Os candidatos são ordenados pela cobertura "
                    "de estoque calculada com o ritmo médio "
                    "do período analisado, da maior para a menor."
                )
        },

        "interpretacao":
            (
                "Os resultados representam candidatos a menor giro "
                "e não uma classificação definitiva de estoque parado."
            )
    }

    if nome_funcao == "listar_fornecedores_atrasos":

        fornecedores_resultado = resultado[
            "fornecedores"
        ]

        principais_fornecedores = []

        for fornecedor in (
            fornecedores_resultado[:5]
        ):

            principais_fornecedores.append(
                {
                    "fornecedor_id":
                        fornecedor[
                            "fornecedor_id"
                        ],

                    "nome_fornecedor":
                        fornecedor[
                            "nome_fornecedor"
                        ],

                    "total_pedidos":
                        fornecedor[
                            "total_pedidos"
                        ],

                    "pedidos_atrasados":
                        fornecedor[
                            "pedidos_atrasados"
                        ],

                    "taxa_atraso_percentual":
                        fornecedor[
                            "taxa_atraso_percentual"
                        ],

                    "media_dias_atraso":
                        fornecedor[
                            "media_dias_atraso"
                        ]
                }
            )


        return {

            "periodo_referencia":
                resultado[
                    "periodo_referencia"
                ],

            "total_fornecedores":
                resultado[
                    "total_fornecedores"
                ],

            "criterio_ranking":
                (
                    "Fornecedores ordenados principalmente "
                    "pela taxa percentual de pedidos entregues "
                    "com atraso no período analisado."
                ),

            "principais_fornecedores":
                principais_fornecedores
        }

    if nome_funcao == "calcular_faturamento":

        return {
            "periodo_inicio":
                resultado["periodo_inicio"],

            "periodo_fim":
                resultado["periodo_fim"],

            "fonte":
                resultado["fonte"],

            "criterio":
                resultado["criterio"],

            "indicador":
                resultado["indicador"],

            "total_vendas":
                resultado["total_vendas"],

            "faturamento_bruto":
                resultado["faturamento_bruto"],

            "descontos":
                resultado["descontos"],
            
            "total_vendas":
                resultado["total_vendas"],

            "faturamento_total":
                resultado["faturamento_total"],

            "ticket_medio":
                resultado["ticket_medio"],

            "faturamento_bruto":
                resultado["faturamento_bruto"],

            "descontos":
                resultado["descontos"]
            }

    if nome_funcao == "comparar_faturamento":

        return {
            "periodo_atual": resultado["periodo_atual"],
            "periodo_anterior": resultado["periodo_anterior"],
            "diferenca": resultado["diferenca"],
            "variacao_percentual": resultado["variacao_percentual"],
            "direcao": resultado["direcao"],
            "meses_comparados": resultado["meses_comparados"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "comparar_despesas":

        return {
            "periodo_atual": resultado["periodo_atual"],
            "periodo_anterior": resultado["periodo_anterior"],
            "diferenca": resultado["diferenca"],
            "variacao_percentual": resultado["variacao_percentual"],
            "direcao": resultado["direcao"],
            "meses_comparados": resultado["meses_comparados"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "comparar_lucro":

        return {
            "periodo_atual": resultado["periodo_atual"],
            "periodo_anterior": resultado["periodo_anterior"],
            "diferenca": resultado["diferenca"],
            "variacao_percentual": resultado["variacao_percentual"],
            "direcao": resultado["direcao"],
            "meses_comparados": resultado["meses_comparados"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "explicar_variacao_lucro":

        return {
            "periodo_atual": {
                "periodo_inicio": resultado["periodo_atual"]["periodo_inicio"],
                "periodo_fim": resultado["periodo_atual"]["periodo_fim"],
            },
            "periodo_anterior": {
                "periodo_inicio": resultado["periodo_anterior"]["periodo_inicio"],
                "periodo_fim": resultado["periodo_anterior"]["periodo_fim"],
            },
            "diferenca": resultado["diferenca"],
            "variacao_percentual": resultado["variacao_percentual"],
            "direcao": resultado["direcao"],
            "contribuicoes": resultado["contribuicoes"],
            "parcela_principal": resultado["parcela_principal"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "simular_lucro_despesa":

        return {
            "periodo_inicio": resultado["periodo_inicio"],
            "periodo_fim": resultado["periodo_fim"],
            "percentual_despesa": resultado["percentual_despesa"],
            "escopo": resultado["escopo"],
            "lucro_simulado": resultado["lucro_simulado"],
            "impacto": resultado["impacto"],
            "manteria_lucro": resultado["ainda_tem_lucro"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "simular_lucro_cmv":

        return {
            "periodo_inicio": resultado["periodo_inicio"],
            "periodo_fim": resultado["periodo_fim"],
            "percentual_cmv": resultado["percentual_cmv"],
            "lucro_simulado": resultado["lucro_simulado"],
            "impacto": resultado["impacto"],
            "manteria_lucro": resultado["ainda_tem_lucro"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "explicar_conceito":

        if "erro" in resultado:
            return {
                "erro": resultado["erro"],
                "termo_consultado": resultado.get(
                    "termo_consultado"
                )
            }

        return {
            "rotulo": resultado["rotulo"],
            "definicao": resultado["definicao"],
            "nao_e": resultado.get("nao_e") or "",
            "modulo": resultado["modulo"],
            "sugestoes": resultado.get("sugestoes") or []
        }

    if nome_funcao == "comparar_fluxo_caixa":

        return {
            "periodo_atual": resultado["periodo_atual"],
            "periodo_anterior": resultado["periodo_anterior"],
            "diferenca": resultado["diferenca"],
            "variacao_percentual": resultado["variacao_percentual"],
            "direcao": resultado["direcao"],
            "meses_comparados": resultado["meses_comparados"],
            "criterio": resultado["criterio"]
        }

    if nome_funcao == "calcular_despesas":

        return {
            "periodo_inicio":
                resultado["periodo_inicio"],
            "periodo_fim":
                resultado["periodo_fim"],
            "fonte":
                resultado["fonte"],
            "criterio":
                resultado["criterio"],
            "despesa_total":
                resultado["despesa_total"]
        }

    if nome_funcao == "calcular_lucro":

        return {
            "periodo_inicio":
                resultado["periodo_inicio"],
            "periodo_fim":
                resultado["periodo_fim"],
            "criterio":
                resultado["criterio"],
            "faturamento_total":
                resultado["faturamento_total"],
            "custo_mercadorias_vendidas":
                resultado["custo_mercadorias_vendidas"],
            "lucro_bruto":
                resultado["lucro_bruto"],
            "despesa_operacional":
                resultado["despesa_operacional"],
            "lucro_apos_despesas":
                resultado["lucro_apos_despesas"]
        }

    if nome_funcao == "consultar_contas_a_receber":

        return {
            "data_referencia":
                resultado["data_referencia"],
            "criterio":
                resultado["criterio"],
            "total_parcelas_abertas":
                resultado["total_parcelas_abertas"],
            "total_clientes":
                resultado["total_clientes"],
            "valor_em_aberto":
                resultado["valor_em_aberto"],
            "valor_vencido":
                resultado["valor_vencido"],
            "valor_a_vencer":
                resultado["valor_a_vencer"]
        }

    if nome_funcao == "consultar_contas_a_pagar":

        return {
            "data_referencia":
                resultado["data_referencia"],
            "criterio":
                resultado["criterio"],
            "total_contas_abertas":
                resultado["total_contas_abertas"],
            "total_fornecedores":
                resultado["total_fornecedores"],
            "valor_em_aberto":
                resultado["valor_em_aberto"],
            "valor_vencido":
                resultado["valor_vencido"],
            "valor_a_vencer":
                resultado["valor_a_vencer"]
        }

    if nome_funcao == "calcular_fluxo_caixa":

        return {
            "periodo_inicio":
                resultado["periodo_inicio"],
            "periodo_fim":
                resultado["periodo_fim"],
            "criterio":
                resultado["criterio"],
            "entradas":
                resultado["entradas"],
            "saidas":
                resultado["saidas"],
            "saldo":
                resultado["saldo"]
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


def _resumo_ia_vazio(texto):
    if texto is None:
        return True
    texto = str(texto).strip()
    if texto == "":
        return True
    if "[[" not in texto:
        return False
    inicio = texto.upper().find("[[RESUMO]]")
    if inicio < 0:
        return True
    resto = texto[inicio + len("[[RESUMO]]"):]
    proximo = resto.find("[[")
    corpo = resto if proximo < 0 else resto[:proximo]
    return corpo.strip() == ""


NOMES_CANONICOS_FERRAMENTAS = {
    "explain_variacao_lucro":
    "explicar_variacao_lucro",
    "explainar_conceito":
    "explicar_conceito",
    "explain_conceito":
    "explicar_conceito",
}


def _ler_failed_generation(texto_erro):
    if (
        "tool_use_failed" not in texto_erro
        and "was not in request.tools" not in texto_erro
    ):
        return None

    padrao = re.search(
        r"failed_generation['\"]:\s*['\"](\{.*\})['\"]",
        texto_erro,
    )
    if not padrao:
        return None

    bruto = padrao.group(1).replace('\\"', '"')
    try:
        dados = json.loads(bruto)
    except json.JSONDecodeError:
        return None

    nome = dados.get("name")
    argumentos = dados.get("arguments", {})
    if isinstance(argumentos, str):
        try:
            argumentos = json.loads(argumentos)
        except json.JSONDecodeError:
            argumentos = {}
    if not nome:
        return None
    return {
        "name": nome,
        "arguments": argumentos or {}
    }


def _texto_fallback_simular(resultado, ferramenta="simular_lucro_despesa"):
    if resultado.get("ainda_tem_lucro"):
        frase = "Nesse cenário a Urban Style manteria lucro."
    else:
        frase = (
            "Nesse cenário a Urban Style não manteria lucro."
        )
    if ferramenta == "simular_lucro_cmv":
        primeiro = (
            "- Faturamento e despesa operacional permanecem "
            "iguais; só o CMV muda."
        )
    else:
        primeiro = (
            "- Faturamento e CMV permanecem iguais; "
            "só a despesa operacional muda."
        )
    return (
        "[[RESUMO]]\n"
        f"{frase}\n"
        "[[ANALISE]]\n"
        f"{primeiro}\n"
        "- A simulação é por competência, não por caixa.\n"
        "[[RECOMENDACOES]]\n"
    )


def _texto_fallback_lista_reposicao(resultado):
    resumo = resultado.get("resumo") or (
        f"{resultado.get('total_reposicao', 0)} produtos "
        "precisam de reposição."
    )
    return (
        "[[RESUMO]]\n"
        f"{resumo}\n"
        "[[ANALISE]]\n"
        "[[RECOMENDACOES]]\n"
    )


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

Quando a ferramenta calcular_despesas for utilizada,
despesa_total é o valor em reais das despesas operacionais.
Não inclua compra de mercadorias nesse conceito.
Não enumere categorias nem meses.
Informe período e despesa total.

Quando a ferramenta calcular_lucro for utilizada,
o lucro da pergunta é lucro_apos_despesas.
lucro_bruto não é o resultado final.
Não some nem subtraia de novo: use os campos retornados.
Não enumere meses.
Informe período e lucro após despesas.
Pode citar lucro bruto só para contextualizar, sem trocar os dois.
Não use “apenas”, “pouco” ou “preocupante” se a ferramenta não classificou o resultado.

Quando a ferramenta consultar_contas_a_receber for utilizada,
o valor da pergunta é valor_em_aberto.
Não é faturamento nem valor já recebido no caixa.
valor_vencido e valor_a_vencer somam valor_em_aberto.
Não enumere clientes.
Informe a data de referência e os totais.
Não use “crítico” ou “preocupante” se a ferramenta não classificou.

Quando a ferramenta consultar_contas_a_pagar for utilizada,
o valor da pergunta é valor_em_aberto.
Não é despesa operacional nem valor já pago no caixa.
Não confundir com contas a receber.
valor_vencido e valor_a_vencer somam valor_em_aberto.
Não enumere fornecedores.
Informe a data de referência e os totais.
Não use “crítico” ou “preocupante” se a ferramenta não classificou.

Quando a ferramenta calcular_fluxo_caixa for utilizada,
o resultado da pergunta é saldo, com entradas e saídas.
Não é faturamento, lucro nem contas em aberto.
Não é só despesa operacional: as saídas incluem compra de mercadorias.
Não some nem subtraia de novo: use os campos retornados.
Não enumere meses nem categorias.
Informe período, entradas, saídas e saldo.

Quando receber uma lista ordenada, não assuma o critério
da ordenação. Apenas descreva os valores apresentados.

Depois de receber o resultado de uma ferramenta,
responda em português claro, profissional e objetivo.

Não utilize tabelas Markdown na resposta.

O front-end já apresenta os números, listas e cards.
Sua resposta textual alimenta dois blocos diferentes.
Não misture os dois.

Quando a pergunta estiver fora do escopo, responda APENAS
a frase de recusa, sem marcadores.

Se a ferramenta devolver um campo erro, use só [[RESUMO]]
com a mensagem. Não invente produto, valor ou análise.

Quando houver resultado válido de ferramenta, a resposta
DEVE usar exatamente este formato, sem texto fora dos blocos:

[[RESUMO]]
Uma única frase que responde exatamente o que foi perguntado.
Só período + o indicador pedido.
Exemplo se perguntaram o faturamento:
Em junho de 2026 o faturamento da Urban Style foi de R$ 196.500,48.
Não cite ticket, quantidade de vendas, descontos, bruto,
categorias, produtos ou qualquer campo extra.
Não antecipe a análise.
Não use segunda frase.

[[ANALISE]]
- Primeira leitura
- Segunda leitura
- Terceira leitura (só se o resultado da ferramenta sustentar)

[[RECOMENDACOES]]

Regras do resumo:
Responda cru. Se perguntaram faturamento, só faturamento.
Se perguntaram lucro, só lucro após despesas e o período.
Se perguntaram reposição de um produto, só o produto e a
quantidade recomendada (com nome e código).

Regras da análise:
Escreva 2 ou 3 tópicos, cada um começando com "- ".
Interprete o significado dos dados, não recopie os cards.
Não repita faturamento líquido, vendas concluídas, ticket
médio nem outros valores já visíveis nos cards.
Pode usar campos que o card não mostra (ex.: bruto e
desconto) para explicar composição, sem reenunciar o total
do card como se fosse novidade.
Não defina um indicador com as próprias palavras do rótulo
("ticket médio é o valor médio por venda").
Não copie o resumo.
Não invente causas, sazonalidade, mercado, comparação com
outro período, urgência ou prioridade se isso não veio na
ferramenta.
Não enumere produtos, pedidos, clientes, fornecedores,
categorias ou meses que o card já lista.
Não use números que não estejam no resultado da ferramenta.
Se os dados não sustentarem 3 tópicos honestos, escreva 2.
Nunca complete com achismo.

Regras das recomendações:
Deixe [[RECOMENDACOES]] sempre vazio.
O frontend exibe recomendações só quando o backend
já calculou a ação (regra + números). Não invente
promoção, desconto, marketing, meta, corte de custo
ou troca de fornecedor.

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

Quando a ferramenta listar_produtos_baixo_giro for utilizada,
trate os resultados como candidatos a menor giro, e não como
uma classificação definitiva de produtos encalhados ou estoque parado.

Quando a ferramenta consultar_pedidos_atrasados for utilizada,
escreva só o [[RESUMO]] com total e data. Deixe [[ANALISE]]
e [[RECOMENDACOES]] vazios. Não enumere pedidos. Não sugira
trocar fornecedor nem multa.

Quando a ferramenta listar_produtos_reposicao for utilizada,
escreva só o [[RESUMO]] com total de produtos e impacto.
Deixe [[ANALISE]] e [[RECOMENDACOES]] vazios. Não enumere
produtos. Não fale de caixa, faturamento nem urgência.

Quando a ferramenta analisar_reposicao for utilizada,
o backend já resolveu o produto. Use produto_id e nome_produto
juntos na resposta textual (ex.: Tricô Cinza PP (PROD017)).
Não invente código nem nome.

Se a ferramenta devolver um campo erro, explique a mensagem
ao usuário. Não chame a ferramenta de novo na mesma resposta.

Quando a ferramenta calcular_faturamento for utilizada,
o campo faturamento_total é o valor em reais (valor líquido).
O campo total_vendas é a quantidade de vendas, não um valor monetário.
Não some nem subtraia bruto e desconto para obter o líquido:
use faturamento_total.
Não enumere o faturamento mês a mês.
No [[RESUMO]], informe só o período e o faturamento_total.
Não cite ticket_medio nem total_vendas no resumo.
Na [[ANALISE]], não repita os três números do card
(faturamento líquido, vendas, ticket).
Pode explicar que o valor é competência, não caixa, e que
bruto menos descontos chega ao líquido, sem reenunciar o
total do card.

Roteamento financeiro:
- o que é / o que significa / diferença entre termos → explicar_conceito
- o que posso perguntar / que perguntas posso fazer → explicar_conceito
- subiu/caiu/comparar → comparar_*
- por que o lucro variou → explicar_variacao_lucro
- e se despesa/aluguel/energia etc. → simular_lucro_despesa
- e se CMV/custo da mercadoria → simular_lucro_cmv
Um mês: o mesmo YYYY-MM em data_inicio e data_fim.
Se o usuário não informou o período anterior, não envie
data_inicio_anterior nem data_fim_anterior.

Comparações (comparar_faturamento, comparar_despesas,
comparar_lucro, comparar_fluxo_caixa):
[[RESUMO]] uma frase: subiu/caiu/estável e a % COM sinal
(+3,58% ou -4,20%). Cite os períodos. Não cite os dois
valores em R$ se houver %. Se variacao_percentual for null,
cite só a diferença em R$, sem inventar %.
[[ANALISE]] 2 tópicos com "- ". Não repita totais, diferença
em R$ nem %. Use só o que o card não mostra.
Deixe [[RECOMENDACOES]] vazio.
comparar_faturamento: total_vendas e ticket_medio; competência, não caixa.
comparar_despesas: registros_analisados; competência, não caixa nem CMV.
comparar_lucro: cite faturamento, CMV e despesa dos dois períodos;
lucro = fat − CMV − despesa; não diga que uma parcela "causou".
comparar_fluxo_caixa: cite entradas e saídas; saldo = entradas − saídas
na data da movimentação, não competência.

explicar_variacao_lucro:
[[RESUMO]] uma frase: caiu/subiu, períodos e parcela_principal.
Deixe [[ANALISE]] e [[RECOMENDACOES]] vazios.
Não invente promoção, caixa nem causa comercial.

simular_lucro_despesa:
Não copie a palavra ainda da pergunta.
Resumo: uma frase no condicional, por exemplo
“Nesse cenário a Urban Style não manteria lucro.”
Análise: 2 tópicos; fat e CMV iguais; competência,
não caixa; sem margem e sem repetir R$ do card.
Deixe [[RECOMENDACOES]] vazio.

simular_lucro_cmv:
Não copie a palavra ainda da pergunta.
Resumo: uma frase no condicional, por exemplo
“Nesse cenário a Urban Style não manteria lucro.”
Análise: 2 tópicos; fat e despesa iguais; só o CMV muda;
competência, não caixa; sem margem e sem repetir R$ do card.
Deixe [[RECOMENDACOES]] vazio.

explicar_conceito:
Use a definição da ferramenta. Não invente.
[[RESUMO]] uma frase com o que é.
Se houver sugestoes, o resumo diz que o card lista exemplos.
Deixe [[ANALISE]] e [[RECOMENDACOES]] vazios.

Explique apenas os critérios explicitamente retornados pela ferramenta.

Não recomende promoções, redução de compras, alterações de reposição,
liquidação de estoque ou qualquer outra ação comercial se a ferramenta
não tiver analisado e retornado explicitamente essa recomendação.

Depois de receber o resultado de uma ferramenta,
não chame ferramenta de novo. Responda só com [[RESUMO]] e [[ANALISE]].
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

    recuperacao = None
    try:
        resposta = get_cliente().chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=mensagens,

            tools=tools,

            tool_choice="auto",

            temperature=0
        )
    except Exception as erro:
        texto_erro = str(erro)
        if (
            "rate_limit" in texto_erro
            or "Request too large" in texto_erro
        ):
            return {
                "tipo_resposta": "texto",
                "resposta_ia": (
                    "A consulta ultrapassou o limite temporário "
                    "da Groq. Aguarde cerca de um minuto e "
                    "tente de novo."
                )
            }
        recuperacao = _ler_failed_generation(texto_erro)
        if recuperacao is None:
            raise


    resultados_ferramentas = []

    if recuperacao is not None:
        nome_funcao = NOMES_CANONICOS_FERRAMENTAS.get(
            recuperacao["name"],
            recuperacao["name"],
        )
        if nome_funcao not in funcoes_disponiveis:
            raise ValueError(
                f"Ferramenta desconhecida: {nome_funcao}"
            )
        argumentos = {
            chave: valor
            for chave, valor in recuperacao["arguments"].items()
            if str(chave).strip()
        }
        funcao = funcoes_disponiveis[nome_funcao]
        try:
            resultado = funcao(**argumentos)
        except ValueError as erro:
            resultado = {"erro": str(erro)}
        resultados_ferramentas.append(
            {
                "ferramenta": nome_funcao,
                "resultado": resultado
            }
        )
        recorte = preparar_resultado_para_ia(
            nome_funcao,
            resultado
        )
        mensagens.append(
            {
                "role": "user",
                "content": (
                    "Resultado da ferramenta:\n"
                    + json.dumps(recorte, ensure_ascii=False)
                    + "\nResponda só com [[RESUMO]] e [[ANALISE]]. "
                    "Deixe [[RECOMENDACOES]] vazio."
                )
            }
        )
        tool_calls = []
    else:
        mensagem_modelo = (
            resposta
            .choices[0]
            .message
        )
        tool_calls = (
            mensagem_modelo.tool_calls
            or []
        )
        if not tool_calls:
            return {
                "tipo_resposta": "texto",
                "resposta_ia": mensagem_modelo.content
            }
        mensagens.append(
            mensagem_modelo
        )
    # =====================================================
    # EXECUTA AS FERRAMENTAS SOLICITADAS
    # =====================================================

    for tool_call in tool_calls:

        nome_funcao_modelo = (
            tool_call
            .function
            .name
        )

        nome_funcao = NOMES_CANONICOS_FERRAMENTAS.get(
            nome_funcao_modelo,
            nome_funcao_modelo
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
        try:
            if nome_funcao in [
                "listar_produtos_reposicao",
                "listar_produtos_maior_risco"
            ]:
                resultado = funcao()
            else:
                resultado = funcao(
                    **argumentos
                )
        except ValueError as erro:
            mensagens.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": nome_funcao_modelo,
                    "content": json.dumps(
                        {"erro": str(erro)},
                        ensure_ascii=False
                    )
                }
            )
            continue

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
                    nome_funcao_modelo,

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
    # Reposição, variação do lucro e pedidos atrasados:
    # textos já vêm do backend. Pula a 2ª chamada.
    # =====================================================

    if (
        len(resultados_ferramentas) == 1
        and resultados_ferramentas[0]["ferramenta"]
        in (
            "listar_produtos_reposicao",
            "explicar_variacao_lucro",
            "consultar_pedidos_atrasados",
        )
    ):
        texto_final = _texto_fallback_lista_reposicao(
            resultados_ferramentas[0]["resultado"]
        )
    else:
        resposta_final = (
        get_cliente().chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=mensagens,

            temperature=0
        )
    )


        texto_final = (
            resposta_final
            .choices[0]
            .message
            .content
        )

        if _resumo_ia_vazio(texto_final):
            for item in resultados_ferramentas:
                if item["ferramenta"] in (
                    "simular_lucro_despesa",
                    "simular_lucro_cmv",
                ):
                    texto_final = _texto_fallback_simular(
                        item["resultado"],
                        item["ferramenta"],
                    )
                    break
                if item["ferramenta"] == "explicar_conceito":
                    resultado = item["resultado"]
                    if resultado.get("erro"):
                        texto_final = (
                            "[[RESUMO]]\n"
                            f"{resultado['erro']}\n"
                            "[[ANALISE]]\n"
                            "[[RECOMENDACOES]]\n"
                        )
                    else:
                        texto_final = (
                            "[[RESUMO]]\n"
                            f"{resultado['definicao']}\n"
                            "[[ANALISE]]\n"
                            f"- {resultado['nao_e']}\n"
                            "[[RECOMENDACOES]]\n"
                        )
                    break


    # =====================================================
    # RETORNO PARA O BACKEND
    # =====================================================

    if not resultados_ferramentas:
        return {
            "tipo_resposta": "texto",
            "resposta_ia": texto_final
        }

    return {
        "tipo_resposta": "resposta_ia",
        "resposta_ia": texto_final,
        "ferramentas_utilizadas": resultados_ferramentas
    }

# TESTE
