// Inicializa tudo quando a página carregar
document.addEventListener("DOMContentLoaded", () => {
  inicializarIconesLucide();
  inicializarAlternadorTema();
  inicializarMenuLateral();
  inicializarMenuMobile();

  inicializarEtiquetasSugestao();
  inicializarFiltrosSugestoesDv();
  inicializarFiltrosIndicadores();
  inicializarBotaoValidacao();
  inicializarAbasPainel();

  inicializarChatDuaxis();
});

// Renderiza os ícones Lucide na página
function inicializarIconesLucide() {
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

function isMenuMobile() {
  return window.matchMedia("(max-width: 1023px)").matches;
}

// Recolhe ou expande o menu lateral (desktop)
function inicializarMenuLateral() {
  const menuLateral = document.getElementById("menu-lateral");
  const botaoAlternar = document.getElementById("alternar-menu-lateral");

  if (!botaoAlternar || !menuLateral) return;

  botaoAlternar.addEventListener("click", () => {
    const recolhido = menuLateral.classList.toggle("menu-lateral--recolhido");
    botaoAlternar.setAttribute(
      "aria-label",
      recolhido ? "Expandir menu" : "Recolher menu",
    );
    atualizarIconeMenuLateral(botaoAlternar, recolhido);
  });

  atualizarIconeMenuLateral(
    botaoAlternar,
    menuLateral.classList.contains("menu-lateral--recolhido"),
  );
}

// Menu lateral deslizante em telas menores
function inicializarMenuMobile() {
  const menuLateral = document.getElementById("menu-lateral");
  const overlay = document.getElementById("menu-overlay");
  const botaoAbrir = document.getElementById("abrir-menu-mobile");
  const botaoFechar = document.getElementById("fechar-menu-mobile");

  if (!menuLateral) return;

  function abrirMenuMobile() {
    if (!isMenuMobile()) return;
    menuLateral.classList.add("menu-lateral--aberto");
    if (overlay) {
      overlay.classList.add("menu-overlay--visivel");
      overlay.setAttribute("aria-hidden", "false");
    }
    document.body.classList.add("menu-aberto");
  }

  function fecharMenuMobile() {
    menuLateral.classList.remove("menu-lateral--aberto");
    if (overlay) {
      overlay.classList.remove("menu-overlay--visivel");
      overlay.setAttribute("aria-hidden", "true");
    }
    document.body.classList.remove("menu-aberto");
  }

  if (botaoAbrir) {
    botaoAbrir.addEventListener("click", abrirMenuMobile);
  }

  if (botaoFechar) {
    botaoFechar.addEventListener("click", fecharMenuMobile);
  }

  if (overlay) {
    overlay.addEventListener("click", fecharMenuMobile);
  }

  menuLateral.querySelectorAll(".menu-lateral__item").forEach((item) => {
    item.addEventListener("click", () => {
      if (isMenuMobile()) fecharMenuMobile();
    });
  });

  window.addEventListener("resize", () => {
    if (!isMenuMobile()) fecharMenuMobile();
  });
}

// Troca o ícone do botão de recolher/expandir menu
function atualizarIconeMenuLateral(botao, recolhido) {
  const icone = botao.querySelector("[data-lucide]");
  if (icone) {
    icone.setAttribute(
      "data-lucide",
      recolhido ? "panel-left-open" : "panel-left-close",
    );
    inicializarIconesLucide();
  }
}

// Alterna entre tema claro e escuro
function inicializarAlternadorTema() {
  const elementoHtml = document.documentElement;
  const botao = document.getElementById("alternar-tema");

  if (!botao) return;

  botao.addEventListener("click", () => {
    const modoEscuro = !elementoHtml.classList.contains("dark");
    elementoHtml.classList.toggle("dark", modoEscuro);
    localStorage.setItem("tema", modoEscuro ? "escuro" : "claro");
    inicializarIconesLucide();
  });
}

// Preenche o campo de chat ao clicar em uma sugestão
function inicializarEtiquetasSugestao() {
  const campoChat = document.getElementById("campo-chat");
  const campoChatDv = document.getElementById("campo-chat-dv");

  document.querySelectorAll(".etiqueta[data-sugestao]").forEach((etiqueta) => {
    etiqueta.addEventListener("click", () => {
      if (campoChat) {
        campoChat.value = etiqueta.dataset.sugestao || "";
        campoChat.focus();
      }
    });
  });

  document
    .querySelectorAll(".cartao-sugestao-dv[data-sugestao]")
    .forEach((cartao) => {
      cartao.addEventListener("click", () => {
        if (campoChatDv) {
          campoChatDv.value = cartao.dataset.sugestao || "";
          campoChatDv.focus();
        }
      });
    });
}

// Filtra sugestões de perguntas do Copiloto Corporativo por base
function inicializarFiltrosSugestoesDv() {
  const container = document.getElementById("sugestoes-dv-container");
  if (!container) return;

  const etiquetasFiltro = container.querySelectorAll(".etiqueta-filtro");
  const cartoesSugestao = container.querySelectorAll(".cartao-sugestao-dv");

  if (!etiquetasFiltro.length || !cartoesSugestao.length) return;

  let filtroAtivo = "todos";

  etiquetasFiltro.forEach((etiqueta) => {
    etiqueta.addEventListener("click", () => {
      etiquetasFiltro.forEach((e) =>
        e.classList.remove("etiqueta-filtro--ativo"),
      );
      etiqueta.classList.add("etiqueta-filtro--ativo");
      filtroAtivo = etiqueta.dataset.filtro || "todos";
      aplicarFiltroSugestoesDv(cartoesSugestao, filtroAtivo);
    });
  });
}

function aplicarFiltroSugestoesDv(cartoes, filtro) {
  cartoes.forEach((cartao) => {
    const categoria = cartao.dataset.categoria || "";
    const corresponde = filtro === "todos" || categoria === filtro;
    cartao.style.display = corresponde ? "" : "none";
  });
}

// Filtra cards de indicadores do dashboard por base
function inicializarFiltrosIndicadores() {
  const container = document.getElementById("indicadores-container");
  if (!container) return;

  const etiquetasFiltro = container.querySelectorAll(".etiqueta-filtro");
  const cartoesIndicador = container.querySelectorAll(".cartao-indicador");

  if (!etiquetasFiltro.length || !cartoesIndicador.length) return;

  let filtroAtivo = "todos";

  etiquetasFiltro.forEach((etiqueta) => {
    etiqueta.addEventListener("click", () => {
      etiquetasFiltro.forEach((e) =>
        e.classList.remove("etiqueta-filtro--ativo"),
      );
      etiqueta.classList.add("etiqueta-filtro--ativo");
      filtroAtivo = etiqueta.dataset.filtro || "todos";
      aplicarFiltroIndicadores(cartoesIndicador, filtroAtivo);
    });
  });
}

function aplicarFiltroIndicadores(cartoes, filtro) {
  cartoes.forEach((cartao) => {
    const categoria = cartao.dataset.categoria || "";
    const corresponde = filtro === "todos" || categoria === filtro;
    cartao.style.display = corresponde ? "" : "none";
  });
}

// Simula validação de fontes de dados
function inicializarBotaoValidacao() {
  const botaoValidar = document.getElementById("botao-validar");

  if (!botaoValidar) return;

  botaoValidar.addEventListener("click", () => {
    const htmlOriginal = botaoValidar.innerHTML;
    botaoValidar.disabled = true;
    botaoValidar.textContent = "Validando...";

    setTimeout(() => {
      botaoValidar.disabled = false;
      botaoValidar.innerHTML = htmlOriginal;
      inicializarIconesLucide();
    }, 2000);
  });
}

// Alterna abas de período nos painéis de gráfico
function inicializarAbasPainel() {
  document.querySelectorAll(".painel-grafico__abas").forEach((grupoAbas) => {
    const painel = grupoAbas.closest(".painel-grafico");
    const abas = grupoAbas.querySelectorAll(".painel-grafico__aba");

    abas.forEach((aba) => {
      aba.addEventListener("click", () => {
        abas.forEach((item) =>
          item.classList.remove("painel-grafico__aba--ativa"),
        );
        aba.classList.add("painel-grafico__aba--ativa");

        const periodo = aba.dataset.periodo;
        painel.querySelectorAll("[data-grafico-periodo]").forEach((grafico) => {
          grafico.hidden = grafico.dataset.graficoPeriodo !== periodo;
        });
        painel.querySelectorAll("[data-estatistica-periodo]").forEach((stat) => {
          stat.hidden = stat.dataset.estatisticaPeriodo !== periodo;
        });
      });
    });
  });
}

function inicializarChatDuaxis() {

  const campoChat = document.getElementById("campo-chat-dv");

  const botaoEnviar = document.querySelector(
    ".barra-entrada-dv__enviar"
  );

  if (!campoChat || !botaoEnviar) {
    return;
  }

  botaoEnviar.addEventListener(
    "click",
    () => enviarPerguntaDuaxis(campoChat)
  );

}

async function enviarPerguntaDuaxis(campoChat) {

  const pergunta = campoChat.value.trim();

  if (!pergunta) {
    return;
  }

  adicionarMensagemUsuario(
    pergunta
  );

  campoChat.value = "";

  const produtoEncontrado = pergunta.match(
    /PROD\d{3}/i
  );

  if (!produtoEncontrado) {

    console.log(
      "Nenhum produto encontrado."
    );

    return;
  }

  const produtoId =
    produtoEncontrado[0].toUpperCase();

  try {

    const resposta = await fetch(
      `http://127.0.0.1:8000/api/previsao/${produtoId}`
    );

    if (!resposta.ok) {
      throw new Error(
        `Erro HTTP ${resposta.status}`
      );
    }

    const dados = await resposta.json();

    adicionarRespostaDuaxis(
      dados
    );

  } catch (erro) {

    console.error(
      "Erro ao consultar DUAXIS:",
      erro
    );
  }
}

function adicionarMensagemUsuario(texto) {

  const container = document.getElementById(
    "mensagens-chat-dv"
  );

  if (!container) {
    return;
  }

  const mensagem = document.createElement("div");

  mensagem.className =
    "mensagem-chat mensagem-chat--usuario";

  mensagem.textContent = texto;

  container.appendChild(mensagem);
}

function adicionarRespostaDuaxis(dados) {

  const container = document.getElementById(
    "mensagens-chat-dv"
  );

  if (!container) {
    return;
  }

  const impactoFormatado =
    dados.impacto_financeiro.toLocaleString(
      "pt-BR",
      {
        style: "currency",
        currency: "BRL"
      }
    );

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis";

  bloco.innerHTML = `
        <section class="resposta-duaxis__secao">

            <div class="resposta-duaxis__cabecalho">
                <i data-lucide="file-text"></i>
                <span>RESUMO EXECUTIVO</span>
            </div>

            <div class="resposta-duaxis__conteudo">

                Para o produto
                <strong>${dados.produto_id}</strong>,
                a demanda prevista para agosto é de
                aproximadamente
                <strong>${dados.demanda_prevista} unidades</strong>.

                Recomenda-se adquirir
                <strong>${dados.quantidade_recomendada} unidades</strong>,
                com impacto financeiro estimado de
                <strong>${impactoFormatado}</strong>.

            </div>

        </section>


        <section class="resposta-duaxis__secao">

            <div class="resposta-duaxis__cabecalho">
                <i data-lucide="search"></i>
                <span>ANÁLISE</span>
            </div>

            <div class="resposta-duaxis__conteudo">

                <ul class="resposta-duaxis__lista">

                    <li>
                        O estoque atual do produto é de
                        <strong>${dados.estoque_atual} unidades</strong>,
                        enquanto o estoque mínimo definido é de
                        <strong>${dados.estoque_minimo} unidades</strong>.
                    </li>

                    <li>
                        Com base na demanda prevista, o estoque atual
                        oferece aproximadamente
                        <strong>${dados.cobertura_estoque_dias} dias</strong>
                        de cobertura.
                    </li>

                    <li>
                        O prazo médio de reposição do fornecedor é de
                        <strong>${dados.lead_time_dias} dias</strong>.
                    </li>

                </ul>

            </div>

        </section>


        <section class="resposta-duaxis__secao">

            <div class="resposta-duaxis__cabecalho">
                <i data-lucide="lightbulb"></i>
                <span>RECOMENDAÇÕES</span>
            </div>

            <div class="resposta-duaxis__conteudo">

                <ul class="
                    resposta-duaxis__lista
                    resposta-duaxis__lista--recomendacoes
                ">

                    <li>
                        Adquirir aproximadamente
                        <strong>
                            ${dados.quantidade_recomendada} unidades
                        </strong>
                        do ${dados.produto_id}.
                    </li>

                    <li>
                        A compra terá impacto financeiro estimado de
                        <strong>${impactoFormatado}</strong>.
                    </li>

                    <li>
                        Monitorar o estoque durante o mês,
                        principalmente se ocorrer aumento inesperado
                        da demanda.
                    </li>

                </ul>

            </div>

        </section>


        <section class="
            resposta-duaxis__secao
            resposta-duaxis__secao--confiabilidade
        ">

            <div class="resposta-duaxis__cabecalho">
                <i data-lucide="shield-check"></i>
                <span>CONFIABILIDADE DA ANÁLISE</span>
            </div>

            <div class="resposta-duaxis__conteudo">

                <div class="confiabilidade-grade">

                    <div class="confiabilidade-card">

                        <span class="confiabilidade-card__rotulo">
                            Modelo utilizado
                        </span>

                        <strong>
                            Random Forest
                        </strong>

                    </div>


                    <div class="confiabilidade-card">

                        <span class="confiabilidade-card__rotulo">
                            R² do modelo
                        </span>

                        <strong>
                            0,76
                        </strong>

                    </div>


                    <div class="confiabilidade-card">

                        <span class="confiabilidade-card__rotulo">
                            Risco imediato de ruptura
                        </span>

                        <strong>
                            ${dados.risco_ruptura_imediato}
                        </strong>

                    </div>


                    <div class="confiabilidade-card">

                        <span class="confiabilidade-card__rotulo">
                            Fontes utilizadas
                        </span>

                        <strong>
                            Logística + Financeiro
                        </strong>

                    </div>

                </div>


                <div class="confiabilidade-limitacao">

                    <strong>Possíveis limitações</strong>

                    <p>
                        A previsão é baseada no histórico disponível
                        e pode não considerar eventos futuros não
                        registrados, como promoções inesperadas,
                        mudanças de comportamento do consumidor ou
                        atrasos extraordinários de fornecedores.
                    </p>

                </div>

            </div>

        </section>


        <section class="
            resposta-duaxis__secao
            resposta-duaxis__secao--sugestoes
        ">

            <div class="resposta-duaxis__conteudo">

                <strong>
                    ✨ Você também pode perguntar:
                </strong>

                <button
                    type="button"
                    class="resposta-duaxis__sugestao"
                    data-pergunta="Quais produtos precisam de reposição?"
                >
                    → Quais produtos precisam de reposição?
                </button>

                <button
                    type="button"
                    class="resposta-duaxis__sugestao"
                    data-pergunta="Qual produto tem maior risco de ruptura?"
                >
                    → Qual produto tem maior risco de ruptura?
                </button>

                <button
                    type="button"
                    class="resposta-duaxis__sugestao"
                    data-pergunta="Qual o impacto financeiro das reposições?"
                >
                    → Qual o impacto financeiro das reposições?
                </button>

            </div>

        </section>


        <button
            type="button"
            class="resposta-duaxis__relatorio"
        >
            <i data-lucide="file-text"></i>
            Gerar Relatório
        </button>
    `;

  container.appendChild(bloco);

  inicializarIconesLucide();

  bloco.scrollIntoView({
    behavior: "smooth",
    block: "end"
  });
}

function montarRespostaReposicao(dados) {

  const impactoFormatado =
    dados.impacto_financeiro.toLocaleString(
      "pt-BR",
      {
        style: "currency",
        currency: "BRL"
      }
    );

  return (
    `Para o ${dados.produto_id}, ` +
    `a demanda prevista para agosto é de aproximadamente ` +
    `${dados.demanda_prevista} unidades. ` +
    `O estoque atual é de ${dados.estoque_atual} unidades ` +
    `e o estoque mínimo é de ${dados.estoque_minimo}. ` +
    `Recomenda-se adquirir ${dados.quantidade_recomendada} unidades, ` +
    `com impacto financeiro estimado de ${impactoFormatado}. ` +
    `O risco imediato de ruptura é ${dados.risco_ruptura_imediato.toLowerCase()}.`
  );
}