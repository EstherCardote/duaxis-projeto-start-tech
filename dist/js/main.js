// Inicializa tudo quando a página carregar
document.addEventListener("DOMContentLoaded", () => {
  inicializarIconesLucide();
  inicializarAlternadorTema();
  inicializarMenuLateral();
  inicializarMenuMobile();

  inicializarEtiquetasSugestao();
  inicializarFiltrosAlertas();
  inicializarAtualizacaoAlertas();
  inicializarBotaoValidacao();
  inicializarAbasPainel();
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

// Configura busca e filtros da página de alertas
function inicializarFiltrosAlertas() {
  const etiquetasFiltro = document.querySelectorAll(".etiqueta-filtro");
  const cartoesAlerta = document.querySelectorAll(".cartao-alerta");

  if (!etiquetasFiltro.length || !cartoesAlerta.length) return;

  let filtroAtivo = "todos";
  let termoBusca = "";

  const campoBuscaAlertas = document.getElementById("busca-alertas");
  if (campoBuscaAlertas) {
    campoBuscaAlertas.addEventListener("input", () => {
      termoBusca = campoBuscaAlertas.value.toLowerCase().trim();
      aplicarFiltrosAlertas(cartoesAlerta, filtroAtivo, termoBusca);
    });
  }

  etiquetasFiltro.forEach((etiqueta) => {
    etiqueta.addEventListener("click", () => {
      etiquetasFiltro.forEach((e) =>
        e.classList.remove("etiqueta-filtro--ativo"),
      );
      etiqueta.classList.add("etiqueta-filtro--ativo");
      filtroAtivo = etiqueta.dataset.filtro || "todos";
      aplicarFiltrosAlertas(cartoesAlerta, filtroAtivo, termoBusca);
    });
  });
}

// Mostra ou esconde cartões conforme filtro e busca
function aplicarFiltrosAlertas(cartoes, filtro, termoBusca) {
  cartoes.forEach((cartao) => {
    const categoria = cartao.dataset.categoria || "";
    const texto = cartao.textContent.toLowerCase();

    let correspondeFiltro = true;

    switch (filtro) {
      case "financeiro":
        correspondeFiltro = categoria === "financeiro";
        break;
      case "rh":
        correspondeFiltro = categoria === "rh";
        break;
      case "logistica":
        correspondeFiltro = categoria === "logistica";
        break;
      default:
        correspondeFiltro = true;
    }

    const correspondeBusca = !termoBusca || texto.includes(termoBusca);
    cartao.style.display = correspondeFiltro && correspondeBusca ? "" : "none";
  });
}

// Simula atualização da lista de alertas
function inicializarAtualizacaoAlertas() {
  const botaoAtualizar = document.getElementById("botao-atualizar-alertas");
  const textoAtualizar = document.getElementById("texto-atualizar-alertas");

  if (!botaoAtualizar || !textoAtualizar) return;

  botaoAtualizar.addEventListener("click", () => {
    textoAtualizar.textContent = "Atualizado";
    botaoAtualizar.disabled = true;

    setTimeout(() => {
      textoAtualizar.textContent = "Atualizar";
      botaoAtualizar.disabled = false;
    }, 2000);
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
