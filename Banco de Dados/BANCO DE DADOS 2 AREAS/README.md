# Motor Urban Style — DUAXIS

Período simulado: agosto/2023 a julho/2026 (36 meses)

## Objetivo
Gerar, a partir de um único motor, bases coerentes de Financeiro e Logística para o MVP do DUAXIS.

## Regras principais
- 80 produtos, 120 clientes e 18 fornecedores.
- Cada produto possui demanda-base, popularidade, tendência mensal e perfil sazonal.
- Categorias de inverno vendem mais entre maio e agosto.
- Categorias de verão vendem mais entre novembro e fevereiro.
- Acessórios têm pico em novembro/dezembro.
- Promoções elevam demanda em maio, junho, novembro e dezembro.
- Há ruído aleatório moderado (~10%) para evitar dados perfeitos.
- O estoque é reposto antes de atingir níveis críticos, com compras ligadas ao fornecedor do produto.
- Toda compra gera entrada de estoque, conta a pagar e movimentação financeira.
- Toda venda concluída gera saída de estoque, conta a receber e movimentação financeira.
- Custos aumentam gradualmente ao longo dos anos.
- O fornecedor FOR001 (FashionTex Malhas) sofre choque adicional de +18% a partir de março/2026.
- Frete operacional aumenta 22% a partir de maio/2026.
- Os dados foram criados para conter padrões reais aprendíveis, mas não resultados perfeitos.

## Arquivos gerados
1. produtos_urban_style
2. clientes_urban_style
3. fornecedores_urban_style
4. vendas_urban_style
5. compras_urban_style
6. estoque_urban_style
7. movimentacoes_estoque_urban_style
8. contas_a_receber_urban_style
9. contas_a_pagar_urban_style
10. movimentacoes_financeiras_urban_style

Cada base é exportada em JSON e CSV com separador `;`.
