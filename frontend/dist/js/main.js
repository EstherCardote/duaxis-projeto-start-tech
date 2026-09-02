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

  if (campoChat.dataset.consultando === "1") {
    return;
  }

  const mensagemUsuario = adicionarMensagemUsuario(pergunta);

  campoChat.value = "";
  campoChat.dataset.consultando = "1";
  const indicadorConsultando = adicionarIndicadorConsultando();

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
    } else if (nomeFerramenta === "comparar_despesas") {
      adicionarRespostaComparacaoDespesas(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "comparar_lucro") {
      adicionarRespostaComparacaoLucro(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "explicar_variacao_lucro") {
      adicionarRespostaExplicarVariacaoLucro(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "comparar_fluxo_caixa") {
      adicionarRespostaComparacaoFluxoCaixa(
        resultadoFerramenta,
        dados.resposta_ia,
        dados.data_hora_pergunta,
      );
    } else if (nomeFerramenta === "comparar_faturamento") {
      adicionarRespostaComparacaoFaturamento(
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
    } else if (nomeFerramenta === "calcular_fluxo_caixa") {
      adicionarRespostaFluxoCaixa(
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
  } finally {
    removerIndicadorConsultando(indicadorConsultando);
    delete campoChat.dataset.consultando;
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

function formatarCompetencia(mes) {
  if (!mes) {
    return "";
  }

  const texto = String(mes);

  if (texto.includes(" a ")) {
    return texto
      .split(" a ")
      .map(formatarCompetencia)
      .join(" a ");
  }

  const partes = texto.split("-");

  if (partes.length === 2 && partes[0].length === 4) {
    return `${partes[1]}/${partes[0]}`;
  }

  return texto;
}

const R2_MODELO_DEMANDA_PERCENTUAL = 76;

function formatarAtualizacaoPesquisa(dataHora) {
  if (!dataHora) {
    return "";
  }

  const data = new Date(dataHora);

  const hora = data.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "America/Sao_Paulo",
  });

  return `Hoje às ${hora}`;
}

function montarBlocoConfiabilidade({
  nivel,
  registros,
  fontes,
  limitacao,
  dataHora,
}) {
  const chips = (fontes || [])
    .map(
      (fonte) => `
        <span class="confiabilidade-chip">
          <i data-lucide="check"></i>
          ${fonte}
        </span>
      `,
    )
    .join("");

  const registrosFormatados = Number(registros ?? 0).toLocaleString("pt-BR");

  return `
    <section class="resposta-duaxis__secao resposta-duaxis__secao--confiabilidade">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="shield-check"></i>
        <span>CONFIABILIDADE DA ANÁLISE</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Nível de confiança</span>
            <strong>${nivel}%</strong>
            <div class="confiabilidade-barra" aria-hidden="true">
              <div class="confiabilidade-barra__preenchimento" style="width: ${nivel}%"></div>
            </div>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo confiabilidade-rotulo-com-icone">
              <i data-lucide="database"></i>
              Registros analisados
            </span>
            <strong>${registrosFormatados}</strong>
          </div>
          <div class="confiabilidade-card confiabilidade-card--largo">
            <span class="confiabilidade-card__rotulo">Fontes utilizadas</span>
            <div class="confiabilidade-fontes">
              ${chips}
            </div>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo confiabilidade-rotulo-com-icone">
              <i data-lucide="clock"></i>
              Última atualização
            </span>
            <strong>${formatarAtualizacaoPesquisa(dataHora)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo confiabilidade-rotulo-com-icone">
              <i data-lucide="circle-alert"></i>
              Possíveis limitações
            </span>
            <p class="confiabilidade-card__texto">${limitacao}</p>
          </div>
        </div>
      </div>
    </section>
  `;
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

function separarResumoEAnalise(textoIa) {
  if (!textoIa) {
    return { resumo: "", analise: "", recomendacoes: "" };
  }

  const texto = String(textoIa).replace(/\r\n/g, "\n").trim();

  function bloco(nomeRegex) {
    const padrao = new RegExp(
      `\\[\\[\\s*${nomeRegex}\\s*\\]\\]\\s*([\\s\\S]*?)(?=\\[\\[|$)`,
      "i",
    );
    const encontrado = texto.match(padrao);
    return encontrado ? encontrado[1].trim() : "";
  }

  if (!/\[\[/.test(texto)) {
    return { resumo: texto, analise: "", recomendacoes: "" };
  }

  return {
    resumo: bloco("RESUMO"),
    analise: bloco("AN[AÁ]LISE"),
    recomendacoes: bloco("RECOMENDAC[OÕ]ES"),
  };
}

function formatarTopicosHtml(texto) {
  if (!texto) {
    return "";
  }

  const itens = texto
    .split("\n")
    .map((linha) => linha.trim())
    .filter(Boolean)
    .map((linha) => linha.replace(/^[-*•]\s+/, "").replace(/^\d+[.)]\s+/, ""));

  if (itens.length >= 2) {
    const lis = itens
      .map((item) => `<li>${converterTextoIaParaHtml(item)}</li>`)
      .join("");

    return `
      <ul class="resposta-duaxis__lista resposta-duaxis__lista--analise">
        ${lis}
      </ul>
    `;
  }

  return converterTextoIaParaHtml(texto);
}

function montarBlocoResumoExecutivo(textoIa, dataHora) {
  const { resumo } = separarResumoEAnalise(textoIa);

  return `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="file-text"></i>
        <div class="resposta-duaxis__identificacao">
          <span class="resposta-duaxis__data">
            ${formatarDataHoraChat(dataHora)}
          </span>
          <span>RESUMO EXECUTIVO</span>
        </div>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto">
        ${converterTextoIaParaHtml(resumo)}
      </div>
    </section>
  `;
}

function montarBlocoAnalise(textoAnalise) {
  const corpo = formatarTopicosHtml(textoAnalise);
  const classeVazio = corpo ? "" : "resposta-duaxis__conteudo--vazio";

  return `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="search"></i>
        <span>ANÁLISE</span>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto ${classeVazio}">
        ${corpo}
      </div>
    </section>
  `;
}

function montarBlocoRecomendacoes(textoRecomendacoes) {
  const corpo = formatarTopicosHtml(textoRecomendacoes);
  const classeVazio = corpo ? "" : "resposta-duaxis__conteudo--vazio";

  return `
    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="lightbulb"></i>
        <span>RECOMENDAÇÕES</span>
      </div>
      <div class="resposta-duaxis__conteudo resposta-ia-texto ${classeVazio}">
        ${corpo}
      </div>
    </section>
  `;
}

function montarBotaoGerarRelatorio() {
  return `
    <section class="resposta-duaxis__secao resposta-duaxis__secao--relatorio">
      <button type="button" class="resposta-duaxis__relatorio">
        <i data-lucide="file-text"></i>
        <span>Gerar Relatório</span>
      </button>
    </section>
  `;
}

function montarBlocosFinais(configConfiabilidade) {
  const { analise, recomendacoes } = separarResumoEAnalise(
    configConfiabilidade.textoIa,
  );

  return `
    ${montarBlocoAnalise(analise)}
    ${montarBlocoRecomendacoes(recomendacoes)}
    ${montarBlocoConfiabilidade(configConfiabilidade)}
    ${montarBotaoGerarRelatorio()}
  `;
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
    ${montarBlocoResumoExecutivo(texto, dataHora)}
    ${montarBlocoAnalise(separarResumoEAnalise(texto).analise)}
    ${montarBlocoRecomendacoes(separarResumoEAnalise(texto).recomendacoes)}
    ${montarBotaoGerarRelatorio()}
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

    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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


    ${montarBlocosFinais({
      nivel: R2_MODELO_DEMANDA_PERCENTUAL,
      registros: dados.total_analisados,
      fontes: ["Logística"],
      limitacao:
        "A demanda é prevista por Random Forest (R² 0,76). Não é fato histórico.",
      dataHora,
      textoIa,
    })}

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

function adicionarIndicadorConsultando() {
  const container = document.getElementById("mensagens-chat-dv");

  if (!container) {
    return null;
  }

  const linhaMensagem = document.createElement("div");
  linhaMensagem.className = "linha-chat linha-chat--duaxis";

  const avatar = document.createElement("div");
  avatar.className = "avatar-chat avatar-chat--duaxis";
  avatar.innerHTML = '<i data-lucide="bot"></i>';

  const mensagem = document.createElement("div");
  mensagem.className =
    "mensagem-chat mensagem-chat--duaxis mensagem-chat--consultando";
  mensagem.innerHTML = `
    <span class="consultando-dados">
      Consultando dados<span class="consultando-dados__pontos"></span>
    </span>
  `;

  linhaMensagem.appendChild(avatar);
  linhaMensagem.appendChild(mensagem);
  container.appendChild(linhaMensagem);

  inicializarIconesLucide();

  linhaMensagem.scrollIntoView({
    behavior: "smooth",
    block: "end",
  });

  return linhaMensagem;
}

function removerIndicadorConsultando(linhaMensagem) {
  if (linhaMensagem) {
    linhaMensagem.remove();
  }
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
        ${montarBlocoResumoExecutivo(textoIa, dataHora)}

        <section class="resposta-duaxis__secao">

            <div class="resposta-duaxis__cabecalho">
                <i data-lucide="package-search"></i>
                <span>REPOSIÇÃO</span>
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

                    <li>
                        Quantidade recomendada:
                        <strong>${dados.quantidade_recomendada} unidades</strong>,
                        com impacto financeiro estimado de
                        <strong>${impactoFormatado}</strong>.
                    </li>

                </ul>

            </div>

        </section>

        ${montarBlocosFinais({
          nivel: R2_MODELO_DEMANDA_PERCENTUAL,
          registros: 1,
          fontes: ["Logística"],
          limitacao:
            "A demanda é prevista por Random Forest (R² 0,76). Não é fato histórico.",
          dataHora,
          textoIa,
        })}
    `;

  linhaResposta.appendChild(avatarDuaxis);

  linhaResposta.appendChild(bloco);

  container.appendChild(linhaResposta);

  inicializarIconesLucide();

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

    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">

      <div class="resposta-duaxis__cabecalho">

        <i data-lucide="shield-alert"></i>

        <span>
          PRODUTOS MAIS EXPOSTOS
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

        <div class="lista-produtos-risco">
          ${linhasProdutos}
        </div>

      </div>

    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.total_analisados,
      fontes: ["Logística"],
      limitacao:
        "Risco calculado por cobertura de estoque versus lead time. Nenhuma limitação significativa identificada.",
      dataHora,
      textoIa,
    })}

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

    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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


    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.total_atrasados,
      fontes: ["Logística"],
      limitacao:
        "Situação reconstruída na data de referência, não o status gravado hoje no arquivo.",
      dataHora,
      textoIa,
    })}

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

    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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
          <strong>${formatarCompetencia(dados.periodo_referencia)}</strong>.
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


    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.total_analisados,
      fontes: ["Logística"],
      limitacao:
        "Candidatos a menor giro pelo critério determinístico. Não é classificação de produto encalhado.",
      dataHora,
      textoIa,
    })}

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

    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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
          <strong>${formatarCompetencia(dados.periodo_referencia)}</strong>.
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


    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.total_fornecedores,
      fontes: ["Logística"],
      limitacao:
        "Ranking por taxa percentual de atraso nas entregas. Pedidos ainda não entregues não entram.",
      dataHora,
      textoIa,
    })}

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
      ? formatarCompetencia(dados.periodo_inicio)
      : `${formatarCompetencia(dados.periodo_inicio)} a ${formatarCompetencia(dados.periodo_fim)}`;

  function linhaMes(item, indice) {
    const extra = indice >= 5 ? " mes-faturamento-extra" : "";
    return `
          <div class="produto-reposicao${extra}">
            <div class="produto-reposicao__info">
              <strong>${formatarCompetencia(item.mes)}</strong>
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
  ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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

      ${
        meses.length > 1
          ? `
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
          `
          : ""
      }
    </div>
  </section>

  ${montarBlocosFinais({
    nivel: 100,
    registros: dados.total_vendas,
    fontes: ["Financeiro"],
    limitacao:
      "Cálculo determinístico das vendas concluídas por competência. Nenhuma limitação significativa identificada.",
    dataHora,
    textoIa,
  })}
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

function adicionarRespostaComparacaoFaturamento(dados, textoIa, dataHora) {
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

  function formatarPeriodo(bloco) {
    if (bloco.periodo_inicio === bloco.periodo_fim) {
      return formatarCompetencia(bloco.periodo_inicio);
    }
    return `${formatarCompetencia(bloco.periodo_inicio)} a ${formatarCompetencia(bloco.periodo_fim)}`;
  }

  function formatarVariacao(valor) {
    if (valor === null || valor === undefined) {
      return "—";
    }
    return `${Number(valor).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}%`;
  }

  const atual = dados.periodo_atual;
  const anterior = dados.periodo_anterior;

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="chart-no-axes-column"></i>
        <span>COMPARAÇÃO DE FATURAMENTO</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(atual)}
            </span>
            <strong>${formatarValor(atual.faturamento_total)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(anterior)}
            </span>
            <strong>${formatarValor(anterior.faturamento_total)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Diferença</span>
            <strong>${formatarValor(dados.diferenca)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Variação</span>
            <strong>${formatarVariacao(dados.variacao_percentual)}</strong>
          </div>
        </div>
      </div>
    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros: (atual.total_vendas || 0) + (anterior.total_vendas || 0),
      fontes: ["Financeiro"],
      limitacao:
        "Comparação determinística do faturamento líquido por competência. Não explica a causa da variação.",
      dataHora,
      textoIa,
    })}
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

function adicionarRespostaComparacaoDespesas(dados, textoIa, dataHora) {
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

  function formatarPeriodo(bloco) {
    if (bloco.periodo_inicio === bloco.periodo_fim) {
      return formatarCompetencia(bloco.periodo_inicio);
    }
    return `${formatarCompetencia(bloco.periodo_inicio)} a ${formatarCompetencia(bloco.periodo_fim)}`;
  }

  function formatarVariacao(valor) {
    if (valor === null || valor === undefined) {
      return "—";
    }
    return `${Number(valor).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}%`;
  }

  const atual = dados.periodo_atual;
  const anterior = dados.periodo_anterior;

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="receipt"></i>
        <span>COMPARAÇÃO DE DESPESAS</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(atual)}
            </span>
            <strong>${formatarValor(atual.despesa_total)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(anterior)}
            </span>
            <strong>${formatarValor(anterior.despesa_total)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Diferença</span>
            <strong>${formatarValor(dados.diferenca)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Variação</span>
            <strong>${formatarVariacao(dados.variacao_percentual)}</strong>
          </div>
        </div>
      </div>
    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros:
        (atual.registros_analisados || 0) +
        (anterior.registros_analisados || 0),
      fontes: ["Financeiro"],
      limitacao:
        "Comparação determinística da despesa operacional por competência. Não inclui compra de mercadorias e não explica a causa da variação.",
      dataHora,
      textoIa,
    })}
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

function adicionarRespostaComparacaoLucro(dados, textoIa, dataHora) {
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

  function formatarPeriodo(bloco) {
    if (bloco.periodo_inicio === bloco.periodo_fim) {
      return formatarCompetencia(bloco.periodo_inicio);
    }
    return `${formatarCompetencia(bloco.periodo_inicio)} a ${formatarCompetencia(bloco.periodo_fim)}`;
  }

  function formatarVariacao(valor) {
    if (valor === null || valor === undefined) {
      return "—";
    }
    return `${Number(valor).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}%`;
  }

  const atual = dados.periodo_atual;
  const anterior = dados.periodo_anterior;

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="calculator"></i>
        <span>COMPARAÇÃO DE LUCRO</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(atual)}
            </span>
            <strong>${formatarValor(atual.lucro_apos_despesas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(anterior)}
            </span>
            <strong>${formatarValor(anterior.lucro_apos_despesas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Diferença</span>
            <strong>${formatarValor(dados.diferenca)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Variação</span>
            <strong>${formatarVariacao(dados.variacao_percentual)}</strong>
          </div>
        </div>
      </div>
    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros:
        (atual.registros_analisados || 0) +
        (anterior.registros_analisados || 0),
      fontes: ["Financeiro"],
      limitacao:
        "Comparação do lucro após despesas (faturamento − CMV − despesa). Não é lucro líquido contábil e não explica a causa.",
      dataHora,
      textoIa,
    })}
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

function adicionarRespostaExplicarVariacaoLucro(dados, textoIa, dataHora) {
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

  function formatarPeriodo(bloco) {
    if (bloco.periodo_inicio === bloco.periodo_fim) {
      return formatarCompetencia(bloco.periodo_inicio);
    }
    return `${formatarCompetencia(bloco.periodo_inicio)} a ${formatarCompetencia(bloco.periodo_fim)}`;
  }

  function formatarVariacao(valor) {
    if (valor === null || valor === undefined) {
      return "—";
    }
    return `${Number(valor).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}%`;
  }

  function textoEfeito(efeito) {
    if (efeito === "aumentou_lucro") {
      return "Aumentou o lucro";
    }
    if (efeito === "reduziu_lucro") {
      return "Reduziu o lucro";
    }
    return "Sem efeito";
  }

  const atual = dados.periodo_atual;
  const anterior = dados.periodo_anterior;
  const contribuicoes = dados.contribuicoes || [];
  const principal = contribuicoes.find(
    (item) => item.parcela === dados.parcela_principal,
  );

  function linhaContribuicao(item) {
    const percentual =
      item.percentual_da_diferenca === null ||
      item.percentual_da_diferenca === undefined
        ? "—"
        : `${Number(item.percentual_da_diferenca).toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}% da diferença`;

    return `
      <div class="produto-reposicao">
        <div class="produto-reposicao__info">
          <strong>${item.rotulo}</strong>
          <span>${textoEfeito(item.efeito)} · ${percentual}</span>
        </div>
        <div class="produto-reposicao__impacto">
          ${formatarValor(item.contribuicao)}
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
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="layers"></i>
        <span>O QUE EXPLICA A VARIAÇÃO DO LUCRO</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(atual)}
            </span>
            <strong>${formatarValor(atual.lucro_apos_despesas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(anterior)}
            </span>
            <strong>${formatarValor(anterior.lucro_apos_despesas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Diferença</span>
            <strong>${formatarValor(dados.diferenca)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Parcela principal</span>
            <strong>${principal ? principal.rotulo : "—"}</strong>
          </div>
        </div>
        ${contribuicoes.map(linhaContribuicao).join("")}
      </div>
    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros:
        (atual.registros_analisados || 0) +
        (anterior.registros_analisados || 0),
      fontes: ["Financeiro"],
      limitacao:
        "Decomposição aritmética da diferença do lucro após despesas (faturamento − CMV − despesa). Não identifica causa comercial nem é caixa.",
      dataHora,
      textoIa,
    })}
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

function adicionarRespostaComparacaoFluxoCaixa(dados, textoIa, dataHora) {
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

  function formatarPeriodo(bloco) {
    if (bloco.periodo_inicio === bloco.periodo_fim) {
      return formatarCompetencia(bloco.periodo_inicio);
    }
    return `${formatarCompetencia(bloco.periodo_inicio)} a ${formatarCompetencia(bloco.periodo_fim)}`;
  }

  function formatarVariacao(valor) {
    if (valor === null || valor === undefined) {
      return "—";
    }
    return `${Number(valor).toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}%`;
  }

  const atual = dados.periodo_atual;
  const anterior = dados.periodo_anterior;

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="arrow-left-right"></i>
        <span>COMPARAÇÃO DE FLUXO DE CAIXA</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(atual)}
            </span>
            <strong>${formatarValor(atual.saldo)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">
              ${formatarPeriodo(anterior)}
            </span>
            <strong>${formatarValor(anterior.saldo)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Diferença</span>
            <strong>${formatarValor(dados.diferenca)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Variação</span>
            <strong>${formatarVariacao(dados.variacao_percentual)}</strong>
          </div>
        </div>
      </div>
    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros:
        (atual.registros_analisados || 0) +
        (anterior.registros_analisados || 0),
      fontes: ["Financeiro"],
      limitacao:
        "Comparação do saldo de caixa (entradas − saídas na data da movimentação). Não é faturamento nem lucro e não explica a causa.",
      dataHora,
      textoIa,
    })}
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
      ? formatarCompetencia(dados.periodo_inicio)
      : `${formatarCompetencia(dados.periodo_inicio)} a ${formatarCompetencia(dados.periodo_fim)}`;

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
          <strong>${formatarCompetencia(item.mes)}</strong>
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
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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

    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.registros_analisados,
      fontes: ["Financeiro"],
      limitacao:
        "Apenas despesas operacionais por competência. Compra de mercadorias não entra.",
      dataHora,
      textoIa,
    })}
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
      ? formatarCompetencia(dados.periodo_inicio)
      : `${formatarCompetencia(dados.periodo_inicio)} a ${formatarCompetencia(dados.periodo_fim)}`;

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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

    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.registros_analisados,
      fontes: ["Financeiro"],
      limitacao:
        "Resultado operacional simplificado (faturamento − CMV − despesa). Não é lucro líquido contábil.",
      dataHora,
      textoIa,
    })}
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
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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

    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.registros_analisados,
      fontes: ["Financeiro"],
      limitacao:
        "Saldo reconstruído na data. O arquivo já contém recebimentos futuros.",
      dataHora,
      textoIa,
    })}
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
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

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

    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.registros_analisados,
      fontes: ["Financeiro"],
      limitacao:
        "Saldo reconstruído na data. O arquivo já contém pagamentos futuros.",
      dataHora,
      textoIa,
    })}
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

function adicionarRespostaFluxoCaixa(dados, textoIa, dataHora) {
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

  const meses = dados.fluxo_mensal || [];
  const categorias = dados.saidas_por_categoria || [];

  const periodo =
    dados.periodo_inicio === dados.periodo_fim
      ? formatarCompetencia(dados.periodo_inicio)
      : `${formatarCompetencia(dados.periodo_inicio)} a ${formatarCompetencia(dados.periodo_fim)}`;

  function linhaMes(item, indice) {
    const extra = indice >= 5 ? " mes-fluxo-extra" : "";
    return `
      <div class="produto-reposicao${extra}">
        <div class="produto-reposicao__info">
          <strong>${formatarCompetencia(item.mes)}</strong>
          <span>Entradas ${formatarValor(item.entradas)} · Saídas ${formatarValor(item.saidas)}</span>
        </div>
        <div class="produto-reposicao__impacto">
          ${formatarValor(item.saldo)}
        </div>
      </div>
    `;
  }

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

  const linhaResposta = document.createElement("div");
  linhaResposta.className = "linha-chat linha-chat--duaxis";

  const avatarDuaxis = document.createElement("div");
  avatarDuaxis.className = "avatar-chat avatar-chat--duaxis";
  avatarDuaxis.innerHTML = `<i data-lucide="bot"></i>`;

  const bloco = document.createElement("div");
  bloco.className = "resposta-duaxis resposta-duaxis--lista";

  bloco.innerHTML = `
    ${montarBlocoResumoExecutivo(textoIa, dataHora)}

    <section class="resposta-duaxis__secao">
      <div class="resposta-duaxis__cabecalho">
        <i data-lucide="arrow-left-right"></i>
        <span>FLUXO DE CAIXA</span>
      </div>
      <div class="resposta-duaxis__conteudo">
        <div class="confiabilidade-grade">
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Entradas</span>
            <strong>${formatarValor(dados.entradas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Saídas</span>
            <strong>${formatarValor(dados.saidas)}</strong>
          </div>
          <div class="confiabilidade-card">
            <span class="confiabilidade-card__rotulo">Saldo do período</span>
            <strong>${formatarValor(dados.saldo)}</strong>
          </div>
        </div>

        <p class="reposicao-intro">Fluxo por mês:</p>
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

        <p class="reposicao-intro">Saídas por categoria:</p>
        <div class="lista-produtos-reposicao">
          ${categorias.map(linhaCategoria).join("")}
        </div>
      </div>
    </section>

    ${montarBlocosFinais({
      nivel: 100,
      registros: dados.registros_analisados,
      fontes: ["Financeiro"],
      limitacao:
        "Usa a data da movimentação, não a competência. Não há saldo inicial de caixa na base.",
      dataHora,
      textoIa,
    })}
  `;

  linhaResposta.appendChild(avatarDuaxis);
  linhaResposta.appendChild(bloco);
  container.appendChild(linhaResposta);

  const extras = bloco.querySelectorAll(".mes-fluxo-extra");
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
