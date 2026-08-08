// Inicializa tudo quando a página carregar
document.addEventListener("DOMContentLoaded", () => {
  inicializarIconesLucide();
  inicializarAlternadorTema();

  const menuLateral = document.getElementById("menu-lateral");
  const botaoAlternar = document.getElementById("alternar-menu-lateral");

  // Recolhe ou expande o menu lateral
  if (botaoAlternar && menuLateral) {
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

  inicializarEtiquetasSugestao();
  inicializarFiltrosAlertas();
  inicializarAtualizacaoAlertas();
  inicializarBotaoValidacao();
});

// Renderiza os ícones Lucide na página
function inicializarIconesLucide() {
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
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
    const prioridade = cartao.dataset.prioridade || "";
    const categoria = cartao.dataset.categoria || "";
    const leitura = cartao.dataset.leitura || "";
    const texto = cartao.textContent.toLowerCase();

    let correspondeFiltro = true;

    switch (filtro) {
      case "nao-lidos":
        correspondeFiltro = leitura === "nao-lido";
        break;
      case "alta":
        correspondeFiltro = prioridade === "alta";
        break;
      case "financeiro":
        correspondeFiltro = categoria === "financeiro";
        break;
      case "estoque":
        correspondeFiltro = categoria === "estoque";
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
