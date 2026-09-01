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
        painel
          .querySelectorAll("[data-estatistica-periodo]")
          .forEach((stat) => {
            stat.hidden = stat.dataset.estatisticaPeriodo !== periodo;
          });
      });
    });
  });
}

function inicializarChatDuaxis() {
  const campoChat = document.getElementById("campo-chat-dv");

  const botaoEnviar = document.querySelector(".barra-entrada-dv__enviar");

  if (!campoChat || !botaoEnviar) {
    return;
  }

  botaoEnviar.addEventListener("click", () => enviarPerguntaDuaxis(campoChat));
  campoChat.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter") {
      evento.preventDefault();

      enviarPerguntaDuaxis(campoChat);
    }
  });
}

function urlApiChat() {
  const host = window.location.hostname;

  if (!host || host === "localhost" || host === "127.0.0.1") {
    return "http://127.0.0.1:8000/api/chat";
  }

  return "/api/chat";
}

async function enviarPerguntaDuaxis(campoChat) {
  const pergunta = campoChat.value.trim();

  if (!pergunta) {
    return;
  }

  const mensagemUsuario = adicionarMensagemUsuario(pergunta);

  campoChat.value = "";

  try {
    const resposta = await fetch(urlApiChat(), {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        mensagem: pergunta,
      }),
    });

    if (!resposta.ok) {
      throw new Error(`Erro HTTP ${resposta.status}`);
    }

    const dados = await resposta.json();

    console.log("Resposta do DUAXIS:", dados);
    atualizarDataHoraMensagemUsuario(mensagemUsuario, dados.data_hora_pergunta);

    // ==================================================
    // NOVA LÓGICA DE RESPOSTA
    // ==================================================

    if (dados.tipo_resposta === "texto") {
      adicionarRespostaTextoIa(dados.resposta_ia, dados.data_hora_pergunta);

      return;
    }

    if (
      !dados.ferramentas_utilizadas ||
      dados.ferramentas_utilizadas.length === 0
    ) {
      adicionarRespostaTextoIa(
        dados.resposta_ia || "Não consegui apresentar essa resposta.",
        dados.data_hora_pergunta,
      );

      return;
    }

    const ferramentaUtilizada = dados.ferramentas_utilizadas[0];

    const nomeFerramenta = ferramentaUtilizada.ferramenta;

    const resultadoFerramenta = ferramentaUtilizada.resultado;

    if (nomeFerramenta === "analisar_reposicao") {
      adicionarRespostaDuaxis(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "listar_produtos_reposicao") {
      adicionarRespostaListaReposicao(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "consultar_pedidos_atrasados") {
      adicionarRespostaPedidosAtrasados(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "listar_produtos_maior_risco") {
      adicionarRespostaProdutosMaiorRisco(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "listar_produtos_baixo_giro") {
      adicionarRespostaProdutosBaixoGiro(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "listar_fornecedores_atrasos") {
      adicionarRespostaFornecedoresAtrasos(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "calcular_faturamento") {
      adicionarRespostaFaturamento(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "calcular_despesas") {
      adicionarRespostaDespesas(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "calcular_lucro") {
      adicionarRespostaLucro(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "consultar_contas_a_receber") {
      adicionarRespostaContasAReceber(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "consultar_contas_a_pagar") {
      adicionarRespostaContasAPagar(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else {
      adicionarRespostaTextoIa(
        dados.resposta_ia || "Não consegui apresentar essa resposta.",
        dados.data_hora_pergunta,
      );
    }
  } catch (erro) {
    console.error("Erro ao consultar DUAXIS:", erro);

    adicionarMensagemSistema(
      "Não foi possível consultar os dados neste momento.",
    );
  }
}

function formatarDataHoraChat(dataHora) {
  if (!dataHora) {
    return "";
  }

  const data = new Date(dataHora);

  return data.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function converterTextoIaParaHtml(texto) {
  if (!texto) {
    return "";
  }

  return texto

    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")

    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")

    .replace(/\n/g, "<br>");
}

function adicionarRespostaTextoIa(texto, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
    <i data-lucide="bot"></i>
  `;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis";

  bloco.innerHTML = `

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="sparkles"></i>

        <div class="resposta-duaxis__identificacao">

          <span>
            DUAXIS
          </span>

          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>

        </div>

      </div>

      <div
        class="
          resposta-duaxis__conteudo
          resposta-ia-texto
        "
      >
        ${converterTextoIaParaHtml(texto)}
      </div>

    </section>

  `;

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  inicializarIconesLucide();

  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaListaReposicao(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  const produtos = dados.produtos_reposicao || [];

  const impactoTotal = dados.impacto_financeiro_total || 0;

  const impactoTotalFormatado = impactoTotal.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  const totalProdutos = dados.total_reposicao || 0;

  const produtosPrincipais = produtos.slice(0, 5);

  const produtosRestantes = produtos.slice(5);

  const linhasProdutos = produtosPrincipais
    .map((produto) => {
      const impacto = produto.impacto_financeiro.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
      });

      return `
          <div class="produto-reposicao">

            <div class="produto-reposicao__info">

              <strong>
                ${produto.nome_produto}
              </strong>

              <span>
                 ${produto.produto_id}
                  •
                  ${produto.quantidade_recomendada}
                  unidades recomendadas
              </span>

            </div>

            <div class="produto-reposicao__impacto">
              ${impacto}
            </div>

          </div>
        `;
    })
    .join("");

  const linhasProdutosRestantes = produtosRestantes
    .map((produto) => {
      const impacto = produto.impacto_financeiro.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
      });

      return `
        <div class="produto-reposicao">

          <div class="produto-reposicao__info">

            <strong>
              ${produto.nome_produto}
            </strong>

            <span>
              ${produto.produto_id}
              •
              ${produto.quantidade_recomendada}
              unidades recomendadas
            </span>

          </div>

          <div class="produto-reposicao__impacto">
            ${impacto}
          </div>

        </div>
      `;
    })
    .join("");

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
    <i data-lucide="bot"></i>
  `;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="package-search"></i>

        <div class="resposta-duaxis__identificacao">

          <span>
            RESUMO EXECUTIVO
          </span>

          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>

        </div>

      </div>  

      <div
        class="
          resposta-duaxis__conteudo
          resposta-ia-texto
        "
      >
        ${converterTextoIaParaHtml(textoIa)}
      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="list-ordered"></i>
        <span>PRIORIDADE DE REPOSIÇÃO</span>
      </div>

      <div class="resposta-duaxis__conteudo">

        <p class="reposicao-intro">
          Os produtos com maior quantidade
          recomendada de reposição são:
        </p>

        <div class="lista-produtos-reposicao">
          ${linhasProdutos}
        </div>

        <div
  class="lista-produtos-reposicao lista-produtos-reposicao--oculta"
>
  ${linhasProdutosRestantes}
</div>

        ${
          totalProdutos > 5
            ? `
              <button
                type="button"
                class="botao-ver-todos-reposicao"
              >
                Ver todos os
                ${totalProdutos} produtos
              </button>
            `
            : ""
        }

      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="lightbulb"></i>
        <span>RECOMENDAÇÃO</span>
      </div>

      <div class="resposta-duaxis__conteudo">

        <ul class="
          resposta-duaxis__lista
          resposta-duaxis__lista--recomendacoes
        ">

          <li>
            Priorizar os produtos com maior
            necessidade de reposição.
          </li>

          <li>
            Considerar o impacto financeiro total
            antes de efetuar todas as compras.
          </li>

          <li>
            Acompanhar a demanda prevista e os
            prazos dos fornecedores durante o mês.
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
              Produtos analisados
            </span>

            <strong>
              ${dados.total_analisados}
            </strong>

          </div>

          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Produtos com reposição
            </span>

            <strong>
              ${totalProdutos}
            </strong>

          </div>

          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Modelo
            </span>

            <strong>
              Random Forest
            </strong>

          </div>

          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Desempenho do modelo (R²)
            </span>

            <strong>
              0,76
            </strong>

          </div>

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
          data-pergunta="Quanto devo comprar do PROD017?"
        >
          → Quanto devo comprar do PROD017?
        </button>

        <button
          type="button"
          class="resposta-duaxis__sugestao"
          data-pergunta="Qual produto tem maior risco de ruptura?"
        >
          → Qual produto tem maior risco de ruptura?
        </button>

      </div>

    </section>

  `;

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-reposicao");

  if (botaoVerTodos) {
    botaoVerTodos.addEventListener("click", () => {
      const listaOculta = bloco.querySelector(
        ".lista-produtos-reposicao--oculta",
      );

      if (!listaOculta) {
        return;
      }

      const estaOculta = listaOculta.style.display !== "flex";

      if (estaOculta) {
        listaOculta.style.display = "flex";

        botaoVerTodos.textContent = "Mostrar menos";
      } else {
        listaOculta.style.display = "none";

        botaoVerTodos.textContent = `Ver todos os ${totalProdutos} produtos`;
      }
    });
  }

  inicializarIconesLucide();

  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarMensagemUsuario(texto) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  const linhaMensagem = document.createElement("div");
  linhaMensagem.className = "linha-chat linha-chat--usuario";

  const mensagem = document.createElement("div");

  mensagem.className = "mensagem-chat mensagem-chat--usuario";

  const textoMensagem = document.createElement("div");

  textoMensagem.className = "mensagem-chat__texto";

  textoMensagem.textContent = texto;

  const dataMensagem = document.createElement("span");

  dataMensagem.className = "mensagem-chat__data";

  dataMensagem.hidden = true;

  mensagem.appendChild(textoMensagem);

  mensagem.appendChild(dataMensagem);

  const avatar = document.createElement("div");
  avatar.className = "avatar-chat avatar-chat--usuario";
  avatar.innerHTML = '<i data-lucide="user"></i>';

  linhaMensagem.appendChild(mensagem);
  linhaMensagem.appendChild(avatar);
  container.appendChild(linhaMensagem);

  inicializarIconesLucide();

  linhaMensagem.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
  return dataMensagem;
}

function atualizarDataHoraMensagemUsuario(elementoData, dataHora) {
  if (!elementoData || !dataHora) {
    return;
  }

  elementoData.textContent = formatarDataHoraChat(dataHora);

  elementoData.hidden = false;
}

function adicionarMensagemSistema(texto) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  const linhaMensagem = document.createElement("div");
  linhaMensagem.className = "linha-chat linha-chat--duaxis";

  const avatar = document.createElement("div");
  avatar.className = "avatar-chat avatar-chat--duaxis";
  avatar.innerHTML = '<i data-lucide="bot"></i>';

  const mensagem = document.createElement("div");
  mensagem.className = "mensagem-chat mensagem-chat--duaxis";
  mensagem.textContent = texto;

  linhaMensagem.appendChild(avatar);
  linhaMensagem.appendChild(mensagem);
  container.appendChild(linhaMensagem);

  inicializarIconesLucide();

  linhaMensagem.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaDuaxis(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  const impactoFormatado = dados.impacto_financeiro.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

  const textoRecomendacao =
    dados.quantidade_recomendada > 0
      ? `Adquirir aproximadamente
       <strong>${dados.quantidade_recomendada} unidades</strong>
       de <strong>${dados.nome_produto}</strong>
       (${dados.produto_id}).`
      : `Não há necessidade de reposição de
       <strong>${dados.nome_produto}</strong>
       (${dados.produto_id})
       neste momento.`;

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
  <i data-lucide="bot"></i>
`;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis";

  bloco.innerHTML = `
        <section class="resposta-duaxis__secao">

            <div class="resposta-duaxis__cabecalho">

              <i data-lucide="package-search"></i>

              <div class="resposta-duaxis__identificacao">

                <span>
                  RESUMO EXECUTIVO
                </span>

                <span class="resposta-duaxis__data">
                  ${formatarDataHoraChat(dataHora)}
                </span>

              </div>

            </div>

            <div
              class="
                resposta-duaxis__conteudo
                resposta-ia-texto
              "
            >
              ${converterTextoIaParaHtml(textoIa)}
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
                        ${textoRecomendacao}
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
                            Desempenho do modelo (R²)
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

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  inicializarIconesLucide();

  bloco.querySelectorAll(".resposta-duaxis__sugestao").forEach((botao) => {
    botao.addEventListener("click", () => {
      const campoChat = document.getElementById("campo-chat-dv");

      if (!campoChat) {
        return;
      }

      campoChat.value = botao.dataset.pergunta || "";

      campoChat.focus();
    });
  });

  bloco.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function montarRespostaReposicao(dados) {
  const impactoFormatado = dados.impacto_financeiro.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });

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

function adicionarRespostaProdutosMaiorRisco(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  // ==================================================
  // FILTRA PRODUTOS COM RISCO ACIMA DE BAIXO
  // ==================================================

  const produtosMaiorRisco = dados.produtos.filter(
    (produto) => produto.nivel_risco !== "Baixo",
  );

  // ==================================================
  // CRIA HTML DOS PRODUTOS
  // ==================================================

  const linhasProdutos = produtosMaiorRisco
    .map((produto) => {
      const classeNivel = produto.nivel_risco
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");

      return `
          <div class="produto-risco">

            <div class="produto-risco__cabecalho">

              <div>

                <strong class="produto-risco__nome">
                  ${produto.nome_produto}
                </strong>

                <span class="produto-risco__id">
                  ${produto.produto_id}
                </span>

              </div>

              <span class="
                produto-risco__nivel
                produto-risco__nivel--${classeNivel}
              ">
                ${produto.nivel_risco}
              </span>

            </div>


            <div class="produto-risco__detalhes">

              <div>

                <span class="produto-risco__rotulo">
                  Cobertura
                </span>

                <strong>
                  ${produto.cobertura_estoque_dias} dias
                </strong>

              </div>


              <div>

                <span class="produto-risco__rotulo">
                  Lead time
                </span>

                <strong>
                  ${produto.lead_time_dias} dias
                </strong>

              </div>


              <div>

                <span class="produto-risco__rotulo">
                  Margem de cobertura
                </span>

                <strong>
                  ${produto.margem_cobertura_dias} dias
                </strong>

              </div>


              <div>

                <span class="produto-risco__rotulo">
                  Índice de cobertura
                </span>

                <strong>
                  ${produto.indice_cobertura}
                </strong>

              </div>

            </div>

          </div>
        `;
    })
    .join("");

  // ==================================================
  // CRIA LINHA DO CHAT
  // ==================================================

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
    <i data-lucide="bot"></i>
  `;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis resposta-duaxis--risco";

  // ==================================================
  // CONTEÚDO
  // ==================================================

  bloco.innerHTML = `

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="package-search"></i>

        <div class="resposta-duaxis__identificacao">

          <span>
            RESUMO EXECUTIVO
          </span>

          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>

        </div>

      </div>

      <div
        class="
          resposta-duaxis__conteudo
          resposta-ia-texto
        "
      >
        ${converterTextoIaParaHtml(textoIa)}
      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="shield-alert"></i>

        <span>
          PRODUTOS MAIS EXPOSTOS
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <div class="lista-produtos-risco">
          ${linhasProdutos}
        </div>

      </div>

    </section>


    <section
      class="
        resposta-duaxis__secao
        resposta-duaxis__secao--confiabilidade
      "
    >

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="chart-no-axes-column"></i>

        <span>
          VISÃO GERAL DO RISCO
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <div class="confiabilidade-grade">

          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Produtos analisados
            </span>

            <strong>
              ${dados.total_analisados}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Risco crítico
            </span>

            <strong>
              ${dados.total_critico}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Risco alto
            </span>

            <strong>
              ${dados.total_alto}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Risco moderado
            </span>

            <strong>
              ${dados.total_moderado}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Risco baixo
            </span>

            <strong>
              ${dados.total_baixo}
            </strong>

          </div>

        </div>

      </div>

    </section>

  `;

  // ==================================================
  // ADICIONA NA TELA
  // ==================================================

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  inicializarIconesLucide();

  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaPedidosAtrasados(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  // ==================================================
  // SEPARA OS 5 MAIORES ATRASOS
  // ==================================================

  const pedidosPrincipais = dados.pedidos.slice(0, 5);

  const pedidosRestantes = dados.pedidos.slice(5);

  // ==================================================
  // FUNÇÃO AUXILIAR PARA FORMATAR DATA
  // ==================================================

  function formatarData(data) {
    if (!data) {
      return "-";
    }

    const partes = data.split("-");

    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  }

  // ==================================================
  // FUNÇÃO AUXILIAR PARA FORMATAR VALOR
  // ==================================================

  function formatarValor(valor) {
    return valor.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  // ==================================================
  // CRIA HTML DE UM PEDIDO
  // ==================================================

  function criarHtmlPedido(pedido) {
    const valorFormatado = formatarValor(pedido.valor_total);

    const dataPrevista = formatarData(pedido.data_prevista_entrega);

    return `
      <div class="pedido-atrasado">

        <div class="pedido-atrasado__cabecalho">

          <div>

            <strong class="pedido-atrasado__id">
              ${pedido.id_compra}
            </strong>

            <div class="pedido-atrasado__produto">

              ${pedido.nome_produto}

              <span>
                (${pedido.produto_id})
              </span>

            </div>

          </div>

          <div class="pedido-atrasado__dias">
            ${pedido.dias_atraso}
            ${pedido.dias_atraso === 1 ? "dia" : "dias"}
          </div>

        </div>


        <div class="pedido-atrasado__detalhes">

          <div>

            <span class="pedido-atrasado__rotulo">
              Fornecedor
            </span>

            <strong>
              ${pedido.nome_fornecedor}
            </strong>

            <small>
              ${pedido.fornecedor_id}
            </small>

          </div>


          <div>

            <span class="pedido-atrasado__rotulo">
              Previsto
            </span>

            <strong>
              ${dataPrevista}
            </strong>

          </div>


          <div>

            <span class="pedido-atrasado__rotulo">
              Status
            </span>

            <strong>
              ${pedido.status}
            </strong>

          </div>


          <div>

            <span class="pedido-atrasado__rotulo">
              Quantidade
            </span>

            <strong>
              ${pedido.quantidade}
            </strong>

          </div>


          <div>

            <span class="pedido-atrasado__rotulo">
              Valor
            </span>

            <strong>
              ${valorFormatado}
            </strong>

          </div>

        </div>

      </div>
    `;
  }

  // ==================================================
  // MONTA OS 5 PRIMEIROS
  // ==================================================

  const linhasPrincipais = pedidosPrincipais.map(criarHtmlPedido).join("");

  // ==================================================
  // MONTA OS DEMAIS
  // ==================================================

  const linhasRestantes = pedidosRestantes.map(criarHtmlPedido).join("");

  // ==================================================
  // CRIA A LINHA DO CHAT
  // ==================================================

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
    <i data-lucide="bot"></i>
  `;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis resposta-duaxis--atrasos";

  // ==================================================
  // CONTEÚDO DA RESPOSTA
  // ==================================================

  bloco.innerHTML = `

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="package-search"></i>

        <div class="resposta-duaxis__identificacao">

          <span>
            RESUMO EXECUTIVO
          </span>

          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>

        </div>

      </div>

      <div
        class="
          resposta-duaxis__conteudo
          resposta-ia-texto
        "
      >
        ${converterTextoIaParaHtml(textoIa)}
      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="clock-alert"></i>

        <span>
          MAIORES ATRASOS
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <p class="reposicao-intro">
          Os pedidos com maior atraso na data analisada são:
        </p>


        <div class="lista-pedidos-atrasados">

          ${linhasPrincipais}

        </div>


        <div
          class="
            lista-pedidos-atrasados
            lista-pedidos-atrasados--oculta
          "
        >

          ${linhasRestantes}

        </div>


        ${
          dados.total_atrasados > 5
            ? `
              <button
                type="button"
                class="botao-ver-todos-atrasados"
              >
                Ver todas as
                ${dados.total_atrasados} entregas
              </button>
            `
            : ""
        }

      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="lightbulb"></i>

        <span>
          INSIGHT
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <ul
          class="
            resposta-duaxis__lista
            resposta-duaxis__lista--recomendacoes
          "
        >

          <li>
            Avaliar os fornecedores com maior
            frequência de atrasos.
          </li>

          <li>
            Considerar o histórico de entrega
            nas próximas decisões de compra.
          </li>

          <li>
            Comparar prazo prometido,
            prazo real e score do fornecedor.
          </li>

        </ul>

      </div>

    </section>


    <section
      class="
        resposta-duaxis__secao
        resposta-duaxis__secao--confiabilidade
      "
    >

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="database"></i>

        <span>
          FONTE DA ANÁLISE
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <div class="confiabilidade-grade">


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Registros com atraso
            </span>

            <strong>
              ${dados.total_atrasados}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Tipo de análise
            </span>

            <strong>
              Consulta de dados
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Fonte principal
            </span>

            <strong>
              Compras
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Machine Learning
            </span>

            <strong>
              Não utilizado
            </strong>

          </div>

        </div>

      </div>

    </section>

  `;

  // ==================================================
  // ADICIONA NA TELA
  // ==================================================

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  // ==================================================
  // BOTÃO "VER TODOS"
  // ==================================================

  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-atrasados");

  if (botaoVerTodos) {
    botaoVerTodos.addEventListener("click", () => {
      const listaOculta = bloco.querySelector(
        ".lista-pedidos-atrasados--oculta",
      );

      if (!listaOculta) {
        return;
      }

      const estaOculta = listaOculta.style.display !== "flex";

      if (estaOculta) {
        listaOculta.style.display = "flex";

        botaoVerTodos.textContent = "Mostrar menos";
      } else {
        listaOculta.style.display = "none";

        botaoVerTodos.textContent = `Ver todas as ${dados.total_atrasados} entregas`;
      }
    });
  }

  inicializarIconesLucide();

  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaProdutosBaixoGiro(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  // ==================================================
  // PRODUTOS
  // ==================================================

  const produtos = dados.produtos || [];

  const produtosPrincipais = produtos.slice(0, 5);

  const produtosRestantes = produtos.slice(5);

  // ==================================================
  // FORMATA NÚMEROS
  // ==================================================

  function formatarNumero(valor) {
    if (valor === null || valor === undefined) {
      return "-";
    }

    return Number(valor).toLocaleString("pt-BR", {
      maximumFractionDigits: 2,
    });
  }

  function formatarPercentual(valor) {
    if (valor === null || valor === undefined) {
      return "-";
    }

    return `${Number(valor).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}%`;
  }

  // ==================================================
  // MONTA CARD DO PRODUTO
  // ==================================================

  function montarCardProduto(produto) {
    return `
      <div class="produto-baixo-giro">

        <div class="produto-baixo-giro__cabecalho">

          <div>

            <strong class="produto-baixo-giro__nome">
              ${produto.nome_produto}
            </strong>

            <span class="produto-baixo-giro__id">
              ${produto.produto_id}
            </span>

          </div>

          <span class="produto-baixo-giro__posicao">
            #${produto.posicao}
          </span>

        </div>


        <div class="produto-baixo-giro__detalhes">

          <div>

            <span class="produto-baixo-giro__rotulo">
              Vendas no período
            </span>

            <strong>
              ${formatarNumero(produto.vendas_periodo)} un.
            </strong>

          </div>


          <div>

            <span class="produto-baixo-giro__rotulo">
              Média mensal
            </span>

            <strong>
              ${formatarNumero(produto.media_mensal_periodo)} un.
            </strong>

          </div>


          <div>

            <span class="produto-baixo-giro__rotulo">
              Estoque no fim do período
            </span>

            <strong>
              ${formatarNumero(produto.estoque_periodo)} un.
            </strong>

          </div>


          <div>

            <span class="produto-baixo-giro__rotulo">
              Cobertura do estoque
            </span>

            <strong>
              ${formatarNumero(produto.cobertura_estoque_periodo)} meses
            </strong>

          </div>

        </div>


        <div class="produto-baixo-giro__comparacao">

          <span>
            Ritmo recente:
            <strong>
              ${formatarPercentual(produto.variacao_ritmo_recente_percentual)}
            </strong>
          </span>

          <span>
            Comparação sazonal:
            <strong>
              ${formatarPercentual(produto.variacao_sazonal_percentual)}
            </strong>
          </span>

        </div>

      </div>
    `;
  }

  const linhasPrincipais = produtosPrincipais.map(montarCardProduto).join("");

  const linhasRestantes = produtosRestantes.map(montarCardProduto).join("");

  // ==================================================
  // CRIA LINHA DO CHAT
  // ==================================================

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
    <i data-lucide="bot"></i>
  `;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis resposta-duaxis--baixo-giro";

  // ==================================================
  // CONTEÚDO
  // ==================================================

  bloco.innerHTML = `

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="package-search"></i>

        <div class="resposta-duaxis__identificacao">

          <span>
            RESUMO EXECUTIVO
          </span>

          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>

        </div>

      </div>


      <div
        class="
          resposta-duaxis__conteudo
          resposta-ia-texto
        "
      >
        ${converterTextoIaParaHtml(textoIa)}
      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="chart-no-axes-column-decreasing"></i>

        <span>
          PRODUTOS DE MENOR GIRO
        </span>

      </div>


      <div class="resposta-duaxis__conteudo">

        <p class="reposicao-intro">
          Produtos que apresentam desaceleração de vendas
          e desempenho abaixo do histórico sazonal no período
          <strong>${dados.periodo_referencia}</strong>.
        </p>


        <div class="lista-produtos-baixo-giro">

          ${linhasPrincipais}

        </div>


        <div
          class="
            lista-produtos-baixo-giro
            lista-produtos-baixo-giro--oculta
          "
        >

          ${linhasRestantes}

        </div>


        ${
          produtos.length > 5
            ? `
              <button
                type="button"
                class="botao-ver-todos-baixo-giro"
              >
                Ver todos os
                ${produtos.length} produtos
              </button>
            `
            : ""
        }

      </div>

    </section>


    <section
      class="
        resposta-duaxis__secao
        resposta-duaxis__secao--confiabilidade
      "
    >

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="database"></i>

        <span>
          FONTE DA ANÁLISE
        </span>

      </div>


      <div class="resposta-duaxis__conteudo">

        <div class="confiabilidade-grade">


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Produtos analisados
            </span>

            <strong>
              ${dados.total_analisados}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Candidatos a menor giro
            </span>

            <strong>
              ${dados.total_candidatos}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Período
            </span>

            <strong>
              ${dados.periodo_referencia}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Fonte principal
            </span>

            <strong>
              Vendas + Estoque
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Machine Learning
            </span>

            <strong>
              Não utilizado
            </strong>

          </div>


        </div>

      </div>

    </section>

  `;

  // ==================================================
  // ADICIONA NA TELA
  // ==================================================

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  inicializarIconesLucide();

  // ==================================================
  // BOTÃO VER TODOS
  // ==================================================

  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-baixo-giro");

  const listaOculta = bloco.querySelector(".lista-produtos-baixo-giro--oculta");

  if (botaoVerTodos && listaOculta) {
    let expandido = false;

    botaoVerTodos.addEventListener("click", () => {
      expandido = !expandido;

      listaOculta.classList.toggle(
        "lista-produtos-baixo-giro--visivel",
        expandido,
      );

      botaoVerTodos.textContent = expandido
        ? "Mostrar menos"
        : `Ver todos os ${produtos.length} produtos`;
    });
  }

  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaFornecedoresAtrasos(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  // ==================================================
  // SEPARA OS 5 PRIMEIROS FORNECEDORES
  // ==================================================

  const fornecedores = dados.fornecedores || [];

  const fornecedoresPrincipais = fornecedores.slice(0, 5);

  const fornecedoresRestantes = fornecedores.slice(5);

  // ==================================================
  // CRIA HTML DE UM FORNECEDOR
  // ==================================================

  function criarHtmlFornecedor(fornecedor) {
    const mediaAtraso = Number(fornecedor.media_dias_atraso).toLocaleString(
      "pt-BR",
      {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      },
    );

    const taxaAtraso = Number(fornecedor.taxa_atraso_percentual).toLocaleString(
      "pt-BR",
      {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      },
    );

    return `
      <div class="fornecedor-atraso">

        <div class="fornecedor-atraso__cabecalho">

          <div>

            <strong class="fornecedor-atraso__nome">
              ${fornecedor.posicao}º
              ${fornecedor.nome_fornecedor}
            </strong>

            <span class="fornecedor-atraso__id">
              ${fornecedor.fornecedor_id}
            </span>

          </div>

          <div class="fornecedor-atraso__taxa">
            ${taxaAtraso}%
          </div>

        </div>


        <div class="fornecedor-atraso__detalhes">

          <div>

            <span class="fornecedor-atraso__rotulo">
              Pedidos
            </span>

            <strong>
              ${fornecedor.total_pedidos}
            </strong>

          </div>


          <div>

            <span class="fornecedor-atraso__rotulo">
              Atrasados
            </span>

            <strong>
              ${fornecedor.pedidos_atrasados}
            </strong>

          </div>


          <div>

            <span class="fornecedor-atraso__rotulo">
              Média de atraso
            </span>

            <strong>
              ${mediaAtraso}
              ${Number(fornecedor.media_dias_atraso) === 1 ? "dia" : "dias"}
            </strong>

          </div>


          <div>

            <span class="fornecedor-atraso__rotulo">
              Maior atraso
            </span>

            <strong>
              ${fornecedor.maior_atraso_dias}
              ${fornecedor.maior_atraso_dias === 1 ? "dia" : "dias"}
            </strong>

          </div>

        </div>

      </div>
    `;
  }

  // ==================================================
  // MONTA AS LISTAS
  // ==================================================

  const linhasPrincipais = fornecedoresPrincipais
    .map(criarHtmlFornecedor)
    .join("");

  const linhasRestantes = fornecedoresRestantes
    .map(criarHtmlFornecedor)
    .join("");

  // ==================================================
  // CRIA A LINHA DO CHAT
  // ==================================================

  const linhaResposta = document.createElement("div");

  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");

  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";

  avatarDuaxis.innerHTML = `
    <i data-lucide="bot"></i>
  `;

  const bloco = document.createElement("div");

  bloco.className = "resposta-duaxis resposta-duaxis--fornecedores";

  // ==================================================
  // CONTEÚDO
  // ==================================================

  bloco.innerHTML = `

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="truck"></i>

        <div class="resposta-duaxis__identificacao">

          <span>
            RESUMO EXECUTIVO
          </span>

          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>

        </div>

      </div>

      <div
        class="
          resposta-duaxis__conteudo
          resposta-ia-texto
        "
      >
        ${converterTextoIaParaHtml(textoIa)}
      </div>

    </section>


    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="chart-no-axes-column-increasing"></i>

        <span>
          DESEMPENHO DOS FORNECEDORES
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <p class="reposicao-intro">
          Ranking por taxa de atraso nas compras
          realizadas no período
          <strong>${dados.periodo_referencia}</strong>.
        </p>


        <div class="lista-fornecedores-atrasos">

          ${linhasPrincipais}

        </div>


        <div
          class="
            lista-fornecedores-atrasos
            lista-fornecedores-atrasos--oculta
          "
        >

          ${linhasRestantes}

        </div>


        ${
          fornecedores.length > 5
            ? `
              <button
                type="button"
                class="botao-ver-todos-fornecedores"
              >
                Ver todos os
                ${fornecedores.length} fornecedores
              </button>
            `
            : ""
        }

      </div>

    </section>


    <section
      class="
        resposta-duaxis__secao
        resposta-duaxis__secao--confiabilidade
      "
    >

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="database"></i>

        <span>
          FONTE DA ANÁLISE
        </span>

      </div>

      <div class="resposta-duaxis__conteudo">

        <div class="confiabilidade-grade">


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Fornecedores analisados
            </span>

            <strong>
              ${dados.total_fornecedores}
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Critério principal
            </span>

            <strong>
              Taxa de atraso
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Fonte principal
            </span>

            <strong>
              Compras
            </strong>

          </div>


          <div class="confiabilidade-card">

            <span class="confiabilidade-card__rotulo">
              Machine Learning
            </span>

            <strong>
              Não utilizado
            </strong>

          </div>


        </div>

      </div>

    </section>

  `;

  // ==================================================
  // ADICIONA NA TELA
  // ==================================================

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  // ==================================================
  // BOTÃO "VER TODOS"
  // ==================================================

  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-fornecedores");

  if (botaoVerTodos) {
    botaoVerTodos.addEventListener("click", () => {
      const listaOculta = bloco.querySelector(
        ".lista-fornecedores-atrasos--oculta",
      );

      if (!listaOculta) {
        return;
      }

      const estaOculta = listaOculta.style.display !== "flex";

      if (estaOculta) {
        listaOculta.style.display = "flex";

        botaoVerTodos.textContent = "Mostrar menos";
      } else {
        listaOculta.style.display = "none";

        botaoVerTodos.textContent = `Ver todos os ${fornecedores.length} fornecedores`;
      }
    });
  }

  inicializarIconesLucide();

  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaFaturamento(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  function formatarValor(valor) {
    return Number(valor).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  const meses = dados.faturamento_mensal || [];

  const periodo =
    dados.periodo_inicio === dados.periodo_fim
      ? dados.periodo_inicio
      : `${dados.periodo_inicio} a ${dados.periodo_fim}`;

  function linhaMes(item, indice) {
    const extra = indice >= 5 ? " mes-faturamento-extra" : "";
    return `
          <div class="produto-reposicao${extra}">
            <div class="produto-reposicao__info">
              <strong>${item.mes}</strong>
              <span>${item.total_vendas} vendas</span>
            </div>
            <div class="produto-reposicao__impacto">
              ${formatarValor(item.faturamento)}
            </div>
          </div>
        `;
  }
  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
  <section class="resposta-duaxis__secao">
    <div class="resposta-duaxis__cabecalho">
      <i data-lucide="banknote"></i>
      <div class="resposta-duaxis__identificacao">
        <span>RESUMO EXECUTIVO</span>
        <span class="resposta-duaxis__data">
          ${formatarDataHoraChat(dataHora)}
        </span>
      </div>
    </div>
    <div class="resposta-duaxis__conteudo resposta-ia-texto">
      ${converterTextoIaParaHtml(textoIa)}
    </div>
  </section>

  <section class="resposta-duaxis__secao">
    <div class="resposta-duaxis__cabecalho">
      <i data-lucide="circle-dollar-sign"></i>
      <span>FATURAMENTO</span>
    </div>
    <div class="resposta-duaxis__conteudo">
      <div class="confiabilidade-grade">
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Faturamento líquido</span>
          <strong>${formatarValor(dados.faturamento_total)}</strong>
        </div>
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Vendas concluídas</span>
          <strong>${dados.total_vendas}</strong>
        </div>
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Ticket médio</span>
          <strong>${formatarValor(dados.ticket_medio)}</strong>
        </div>
      </div>

      <p class="reposicao-intro">Faturamento por competência:</p>
      <div class="lista-produtos-reposicao">
        ${meses.map(linhaMes).join("")}
      </div>
      ${
        meses.length > 5
          ? `<button type="button" class="botao-ver-todos-reposicao">
               Ver todos os ${meses.length} meses
             </button>`
          : ""
      }
    </div>
  </section>

  <section class="resposta-duaxis__secao resposta-duaxis__secao--confiabilidade">
    <div class="resposta-duaxis__cabecalho">
      <i data-lucide="database"></i>
      <span>FONTE DA ANÁLISE</span>
    </div>
    <div class="resposta-duaxis__conteudo">
      <div class="confiabilidade-grade">
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Período</span>
          <strong>${periodo}</strong>
        </div>
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Fonte</span>
          <strong>Vendas (valor_liquido)</strong>
        </div>
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Critério</span>
          <strong>Vendas concluídas por competência</strong>
        </div>
        <div class="confiabilidade-card">
          <span class="confiabilidade-card__rotulo">Machine Learning</span>
          <strong>Não utilizado</strong>
        </div>
      </div>
    </div>
  </section>
`;
  linhaResposta.appendChild(avatarDuaxis);
  linhaResposta.appendChild(bloco);
  container.appendChild(linhaResposta);

  const extras = bloco.querySelectorAll(".mes-faturamento-extra");
  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-reposicao");

  extras.forEach((card) => {
    card.style.display = "none";
  });

  if (botaoVerTodos && extras.length > 0) {
    botaoVerTodos.addEventListener("click", () => {
      const estaOculta = extras[0].style.display === "none";

      extras.forEach((card) => {
        card.style.display = estaOculta ? "flex" : "none";
      });

      botaoVerTodos.textContent = estaOculta
        ? "Mostrar menos"
        : `Ver todos os ${meses.length} meses`;
    });
  }

  inicializarIconesLucide();
  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaDespesas(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  function formatarValor(valor) {
    return Number(valor).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  const categorias = dados.despesa_por_categoria || [];
  const meses = dados.despesa_mensal || [];

  const periodo =
    dados.periodo_inicio === dados.periodo_fim
      ? dados.periodo_inicio
      : `${dados.periodo_inicio} a ${dados.periodo_fim}`;

  function linhaCategoria(item) {
    return `
      <div class="produto-reposicao">
        <div class="produto-reposicao__info">
          <strong>${item.categoria}</strong>
        </div>
        <div class="produto-reposicao__impacto">
          ${formatarValor(item.valor)}
        </div>
      </div>
    `;
  }

  function linhaMes(item, indice) {
    const extra = indice >= 5 ? " mes-despesa-extra" : "";
    return `
      <div class="produto-reposicao${extra}">
        <div class="produto-reposicao__info">
          <strong>${item.mes}</strong>
        </div>
        <div class="produto-reposicao__impacto">
          ${formatarValor(item.despesa)}
        </div>
      </div>
    `;
  }

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="wallet"></i>
        <div class="resposta-duaxis__identificacao">
          <span>RESUMO EXECUTIVO</span>
          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>
        </div>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto">
        ${converterTextoIaParaHtml(textoIa)}
      </div>
    </section>

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="receipt"></i>
        <span>DESPESAS OPERACIONAIS</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Despesa total</span>
            <strong>${formatarValor(dados.despesa_total)}</strong>
          </div>
        </div>

        <p class="reposicao-intro">Por categoria:</p>
        <div class="lista-produtos-reposicao">
          ${categorias.map(linhaCategoria).join("")}
        </div>

        <p class="reposicao-intro">Por competência:</p>
        <div class="lista-produtos-reposicao">
          ${meses.map(linhaMes).join("")}
        </div>
        ${
          meses.length > 5
            ? `<button type="button" class="botao-ver-todos-reposicao">
                 Ver todos os ${meses.length} meses
               </button>`
            : ""
        }
      </div>
    </section>

    <section class="resposta-duaxis__secao resposta-duaxis__secao--confiabilidade">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="database"></i>
        <span>FONTE DA ANÁLISE</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Período</span>
            <strong>${periodo}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Fonte</span>
            <strong>Movimentações financeiras</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Critério</span>
            <strong>Despesas operacionais por competência</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Compra de mercadorias</span>
            <strong>Não incluída (custo)</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Machine Learning</span>
            <strong>Não utilizado</strong>
          </div>
        </div>
      </div>
    </section>
  `;

  linhaResposta.appendChild(avatarDuaxis);
  linhaResposta.appendChild(bloco);
  container.appendChild(linhaResposta);

  const extras = bloco.querySelectorAll(".mes-despesa-extra");
  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-reposicao");

  extras.forEach((card) => {
    card.style.display = "none";
  });

  if (botaoVerTodos && extras.length > 0) {
    botaoVerTodos.addEventListener("click", () => {
      const estaOculta = extras[0].style.display === "none";
      extras.forEach((card) => {
        card.style.display = estaOculta ? "flex" : "none";
      });
      botaoVerTodos.textContent = estaOculta
        ? "Mostrar menos"
        : `Ver todos os ${meses.length} meses`;
    });
  }

  inicializarIconesLucide();
  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaLucro(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  function formatarValor(valor) {
    return Number(valor).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  const periodo =
    dados.periodo_inicio === dados.periodo_fim
      ? dados.periodo_inicio
      : `${dados.periodo_inicio} a ${dados.periodo_fim}`;

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="trending-up"></i>
        <div class="resposta-duaxis__identificacao">
          <span>RESUMO EXECUTIVO</span>
          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>
        </div>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto">
        ${converterTextoIaParaHtml(textoIa)}
      </div>
    </section>

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="calculator"></i>
        <span>RESULTADO DO PERÍODO</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Faturamento</span>
            <strong>${formatarValor(dados.faturamento_total)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">CMV</span>
            <strong>${formatarValor(dados.custo_mercadorias_vendidas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Lucro bruto</span>
            <strong>${formatarValor(dados.lucro_bruto)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Despesas operacionais</span>
            <strong>${formatarValor(dados.despesa_operacional)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Lucro após despesas</span>
            <strong>${formatarValor(dados.lucro_apos_despesas)}</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="resposta-duaxis__secao resposta-duaxis__secao--confiabilidade">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="database"></i>
        <span>FONTE DA ANÁLISE</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Período</span>
            <strong>${periodo}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Fonte</span>
            <strong>Vendas + movimentações financeiras</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">CMV</span>
            <strong>Custo das mercadorias vendidas (não compras)</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Critério</span>
            <strong>Resultado operacional simplificado por competência</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Machine Learning</span>
            <strong>Não utilizado</strong>
          </div>
        </div>
      </div>
    </section>
  `;

  linhaResposta.appendChild(avatarDuaxis);
  linhaResposta.appendChild(bloco);
  container.appendChild(linhaResposta);

  inicializarIconesLucide();
  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaContasAReceber(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  function formatarValor(valor) {
    return Number(valor).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  const clientes = dados.clientes || [];

  function linhaCliente(item, indice) {
    const extra = indice >= 5 ? " cliente-receber-extra" : "";
    return `
      <div class="produto-reposicao${extra}">
        <div class="produto-reposicao__info">
          <strong>${item.nome_cliente}</strong>
          <span>${item.total_parcelas} parcelas</span>
        </div>
        <div class="produto-reposicao__impacto">
          ${formatarValor(item.valor_em_aberto)}
        </div>
      </div>
    `;
  }

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="wallet"></i>
        <div class="resposta-duaxis__identificacao">
          <span>RESUMO EXECUTIVO</span>
          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>
        </div>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto">
        ${converterTextoIaParaHtml(textoIa)}
      </div>
    </section>

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="hand-coins"></i>
        <span>CONTAS A RECEBER</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Em aberto</span>
            <strong>${formatarValor(dados.valor_em_aberto)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Vencido</span>
            <strong>${formatarValor(dados.valor_vencido)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">A vencer</span>
            <strong>${formatarValor(dados.valor_a_vencer)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Parcelas</span>
            <strong>${dados.total_parcelas_abertas}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Clientes</span>
            <strong>${dados.total_clientes}</strong>
          </div>
        </div>

        <p class="reposicao-intro">Saldo em aberto por cliente:</p>
        <div class="lista-produtos-reposicao">
          ${clientes.map(linhaCliente).join("")}
        </div>
        ${
          clientes.length > 5
            ? `<button type="button" class="botao-ver-todos-reposicao">
                 Ver todos os ${clientes.length} clientes
               </button>`
            : ""
        }
      </div>
    </section>

    <section class="resposta-duaxis__secao resposta-duaxis__secao--confiabilidade">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="database"></i>
        <span>FONTE DA ANÁLISE</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Data de referência</span>
            <strong>${dados.data_referencia}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Fonte</span>
            <strong>Contas a receber</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Critério</span>
            <strong>${dados.criterio}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Machine Learning</span>
            <strong>Não utilizado</strong>
          </div>
        </div>
      </div>
    </section>
  `;

  linhaResposta.appendChild(avatarDuaxis);
  linhaResposta.appendChild(bloco);
  container.appendChild(linhaResposta);

  const extras = bloco.querySelectorAll(".cliente-receber-extra");
  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-reposicao");

  extras.forEach((card) => {
    card.style.display = "none";
  });

  if (botaoVerTodos && extras.length > 0) {
    botaoVerTodos.addEventListener("click", () => {
      const estaOculta = extras[0].style.display === "none";

      extras.forEach((card) => {
        card.style.display = estaOculta ? "flex" : "none";
      });

      botaoVerTodos.textContent = estaOculta
        ? "Mostrar menos"
        : `Ver todos os ${clientes.length} clientes`;
    });
  }

  inicializarIconesLucide();
  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}

function adicionarRespostaContasAPagar(dados, textoIa, dataHora) {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return;
  }

  function formatarValor(valor) {
    return Number(valor).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });
  }

  const fornecedores = dados.fornecedores || [];

  function linhaFornecedor(item, indice) {
    const extra = indice >= 5 ? " fornecedor-pagar-extra" : "";
    return `
      <div class="produto-reposicao${extra}">
        <div class="produto-reposicao__info">
          <strong>${item.nome_fornecedor}</strong>
          <span>${item.total_contas} contas</span>
        </div>
        <div class="produto-reposicao__impacto">
          ${formatarValor(item.valor_em_aberto)}
        </div>
      </div>
    `;
  }

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="wallet"></i>
        <div class="resposta-duaxis__identificacao">
          <span>RESUMO EXECUTIVO</span>
          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>
        </div>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto">
        ${converterTextoIaParaHtml(textoIa)}
      </div>
    </section>

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="banknote-arrow-up"></i>
        <span>CONTAS A PAGAR</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Em aberto</span>
            <strong>${formatarValor(dados.valor_em_aberto)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Vencido</span>
            <strong>${formatarValor(dados.valor_vencido)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">A vencer</span>
            <strong>${formatarValor(dados.valor_a_vencer)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Contas</span>
            <strong>${dados.total_contas_abertas}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Fornecedores</span>
            <strong>${dados.total_fornecedores}</strong>
          </div>
        </div>

        <p class="reposicao-intro">Saldo em aberto por fornecedor:</p>
        <div class="lista-produtos-reposicao">
          ${fornecedores.map(linhaFornecedor).join("")}
        </div>
        ${
          fornecedores.length > 5
            ? `<button type="button" class="botao-ver-todos-reposicao">
                 Ver todos os ${fornecedores.length} fornecedores
               </button>`
            : ""
        }
      </div>
    </section>

    <section class="resposta-duaxis__secao resposta-duaxis__secao--confiabilidade">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="database"></i>
        <span>FONTE DA ANÁLISE</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Data de referência</span>
            <strong>${dados.data_referencia}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Fonte</span>
            <strong>Contas a pagar</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Critério</span>
            <strong>${dados.criterio}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Machine Learning</span>
            <strong>Não utilizado</strong>
          </div>
        </div>
      </div>
    </section>
  `;

  linhaResposta.appendChild(avatarDuaxis);
  linhaResposta.appendChild(bloco);
  container.appendChild(linhaResposta);

  const extras = bloco.querySelectorAll(".fornecedor-pagar-extra");
  const botaoVerTodos = bloco.querySelector(".botao-ver-todos-reposicao");

  extras.forEach((card) => {
    card.style.display = "none";
  });

  if (botaoVerTodos && extras.length > 0) {
    botaoVerTodos.addEventListener("click", () => {
      const estaOculta = extras[0].style.display === "none";

      extras.forEach((card) => {
        card.style.display = estaOculta ? "flex" : "none";
      });

      botaoVerTodos.textContent = estaOculta
        ? "Mostrar menos"
        : `Ver todos os ${fornecedores.length} fornecedores`;
    });
  }

  inicializarIconesLucide();
  linhaResposta.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });
}