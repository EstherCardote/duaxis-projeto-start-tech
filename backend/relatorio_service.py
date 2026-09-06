from datetime import datetime, date
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo
from fpdf import FPDF

DATA_REFERENCIA_MVP = date(2026, 7, 31)
FUSO = ZoneInfo("America/Sao_Paulo")
LIMITE_SECOES = 40
LIMITE_TEXTO = 8000
LIMITE_ITENS = 200

MARGEM = 12
ALTURA_CABECALHO_SECAO = 8
ALTURA_CABECALHO_COM_DATA = 11.2
PADDING_SECAO = 3
GAP_GRADE = 2.0
GAP_PEDIDOS = 5.0
AZUL = (37, 99, 235)
AZUL_CLARO = (239, 246, 255)
BORDA = (229, 231, 235)
FUNDO_PAGINA = (248, 249, 251)
BRANCO = (255, 255, 255)
TEXTO = (26, 28, 30)
SECUNDARIO = (107, 114, 128)
MUDO = (156, 163, 175)


def _agora_sao_paulo():
    return datetime.now(FUSO)


def data_hora_relatorio():
    agora = _agora_sao_paulo()
    return datetime.combine(
        DATA_REFERENCIA_MVP,
        agora.time().replace(microsecond=0),
        tzinfo=FUSO,
    )


def _caminho_fonte(negrito=False):
    if negrito:
        candidatos = [
            Path(__file__).resolve().parent / "fontes" / "DejaVuSans-Bold.ttf",
            Path(r"C:\Windows\Fonts\arialbd.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ]
    else:
        candidatos = [
            Path(__file__).resolve().parent / "fontes" / "DejaVuSans.ttf",
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    return None


def _limpar_texto(texto):
    if texto is None:
        return ""
    return str(texto).replace("\r\n", "\n").strip()[:LIMITE_TEXTO]


def _limpar_lista(valores, limite=LIMITE_ITENS):
    itens = []
    for valor in valores or []:
        texto = _limpar_texto(valor)
        if texto.startswith("- "):
            texto = texto[2:].strip()
        elif texto.startswith("• "):
            texto = texto[2:].strip()
        if texto:
            itens.append(texto)
        if len(itens) >= limite:
            break
    return itens


class RelatorioPDF(FPDF):
    def __init__(self, familia, tem_negrito):
        super().__init__(format="A4", unit="mm")
        self.familia = familia
        self.tem_negrito = tem_negrito
        self.set_margins(MARGEM, MARGEM, MARGEM)
        self.set_auto_page_break(auto=False)
        self.largura_util = self.w - (2 * MARGEM)

    def header(self):
        self.set_fill_color(*FUNDO_PAGINA)
        self.rect(0, 0, self.w, self.h, style="F")
        if self.page_no() == 1:
            return
        self.set_xy(MARGEM, 8)
        self._fonte(8)
        self.set_text_color(*MUDO)
        self.cell(
            0,
            4,
            "Urban Style  ·  Relatório do Copiloto Corporativo - Duaxis",
        )
        self.set_y(14)

    def footer(self):
        self.set_y(-12)
        self._fonte(7)
        self.set_text_color(*MUDO)
        self.set_x(MARGEM)
        self.cell(
            self.largura_util - 12,
            6,
            "Indicadores calculados no backend. Data de referência do MVP: 31/07/2026",
        )
        self.cell(12, 6, str(self.page_no()), align="R")

    def _fonte(self, tamanho, negrito=False):
        estilo = "B" if negrito and self.tem_negrito else ""
        self.set_font(self.familia, style=estilo, size=tamanho)

    def _y_max(self):
        return self.h - 16

    def _quebrar_se_preciso(self, altura):
        if self.get_y() + altura > self._y_max():
            self.add_page()

    def _caixa(self, x, y, w, h, fundo, borda, raio=2.4):
        if h <= 0 or w <= 0:
            return
        raio = min(raio, h / 2, w / 2, 3.5)
        self.set_fill_color(*fundo)
        self.set_draw_color(*borda)
        self.set_line_width(0.25)
        self.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=raio)

    def _altura_texto(self, texto, largura, tamanho, linha, negrito=False):
        texto = _limpar_texto(texto)
        if not texto:
            return 0
        self._fonte(tamanho, negrito)
        return float(
            self.multi_cell(
                largura,
                linha,
                texto,
                dry_run=True,
                output="HEIGHT",
            )
        )

    def _escrever(self, x, y, largura, texto, tamanho, linha, cor, negrito=False):
        texto = _limpar_texto(texto)
        if not texto:
            return 0
        self.set_xy(x, y)
        self._fonte(tamanho, negrito)
        self.set_text_color(*cor)
        altura = self._altura_texto(texto, largura, tamanho, linha, negrito)
        self.multi_cell(largura, linha, texto, new_x="LEFT", new_y="NEXT")
        return altura

    def desenhar_cabecalho_documento(self):
        self.set_y(MARGEM)
        self._fonte(16, negrito=True)
        self.set_text_color(*AZUL)
        self.cell(0, 7, "Urban Style", new_x="LMARGIN", new_y="NEXT")
        self._fonte(9)
        self.set_text_color(*SECUNDARIO)
        self.cell(
            0,
            5,
            "Relatório do Copiloto Corporativo - Duaxis",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(2)
        y = self.get_y()
        self.set_draw_color(*AZUL)
        self.set_line_width(0.45)
        self.line(MARGEM, y, self.w - MARGEM, y)
        self.ln(5)

    def desenhar_secao(self, secao, data_hora_geracao):
        secao = _normalizar_secao(secao, data_hora_geracao)
        if not _secao_tem_conteudo(secao):
            return

        altura = self._altura_secao(secao)
        cabe_na_pagina_vazia = altura <= (self._y_max() - MARGEM - 4)

        if cabe_na_pagina_vazia:
            self._quebrar_se_preciso(altura)
            self._desenhar_secao_completa(secao, altura)
            return

        self._desenhar_secao_fluida(secao)

    def _altura_cabecalho(self, secao):
        if secao.get("data"):
            return ALTURA_CABECALHO_COM_DATA
        return ALTURA_CABECALHO_SECAO

    def _altura_secao(self, secao):
        largura_conteudo = self.largura_util - (2 * PADDING_SECAO)
        altura = self._altura_cabecalho(secao) + PADDING_SECAO
        altura += self._altura_paragrafos(secao["paragrafos"], largura_conteudo)
        altura += self._altura_grade(secao["cards"], largura_conteudo)
        altura += self._altura_lista(secao["lista"], largura_conteudo)
        altura += self._altura_linhas(secao["linhas"], largura_conteudo)
        return altura + PADDING_SECAO

    def _altura_paragrafos(self, paragrafos, largura):
        total = 0
        for indice, texto in enumerate(paragrafos):
            total += self._altura_texto(texto, largura, 10, 5)
            if indice < len(paragrafos) - 1:
                total += 1.2
        return total

    def _estilo_card(self, card):
        if card.get("compacto"):
            return {
                "padding": 0.6,
                "rotulo": (7, 3.0),
                "valor": (9, 4.0),
                "texto": (8, 3.6),
            }
        return {
            "padding": 2.2,
            "rotulo": (8, 3.8),
            "valor": (11, 5.2),
            "texto": (9, 4.2),
        }

    def _altura_card(self, card, largura):
        estilo = self._estilo_card(card)
        padding = estilo["padding"]
        util = max(largura - (2 * padding), 8)
        altura = padding
        if card["rotulo"]:
            altura += self._altura_texto(
                card["rotulo"], util, estilo["rotulo"][0], estilo["rotulo"][1]
            )
        if card["valor"]:
            altura += self._altura_texto(
                card["valor"], util, estilo["valor"][0], estilo["valor"][1], negrito=True
            )
        if card["texto"]:
            altura += self._altura_texto(
                card["texto"], util, estilo["texto"][0], estilo["texto"][1]
            ) + 0.4
        if card["chips"]:
            altura += 6
        if card["barra"] is not None:
            altura += 3.2
        return altura + padding

    def _linhas_grade(self, cards):
        if not cards:
            return []
        if all(card.get("compacto") for card in cards):
            por_linha = len(cards) if len(cards) <= 5 else 3
            return [
                cards[indice:indice + por_linha]
                for indice in range(0, len(cards), por_linha)
            ]

        linhas = []
        indice = 0
        while indice < len(cards):
            card = cards[indice]
            if card.get("largo"):
                linhas.append([card])
                indice += 1
                continue
            if indice == len(cards) - 1:
                linhas.append([card, None])
                indice += 1
                continue
            seguinte = cards[indice + 1]
            if seguinte.get("largo"):
                linhas.append([card, None])
                indice += 1
                continue
            linhas.append([card, seguinte])
            indice += 2
        return linhas

    def _altura_linha_grade(self, linha, largura):
        cards = [card for card in linha if card is not None]
        if not cards:
            return 0
        if len(linha) == 2 and linha[1] is None and not cards[0].get("compacto"):
            largura_card = (largura - GAP_GRADE) / 2
            return self._altura_card(cards[0], largura_card)
        n = len(cards)
        largura_card = (largura - GAP_GRADE * (n - 1)) / n if n else largura
        return max(self._altura_card(card, largura_card) for card in cards)

    def _altura_grade(self, cards, largura):
        if not cards:
            return 0
        linhas = self._linhas_grade(cards)
        total = 0
        for indice, linha in enumerate(linhas):
            total += self._altura_linha_grade(linha, largura)
            if indice < len(linhas) - 1:
                total += GAP_GRADE
        return total

    def _altura_lista(self, itens, largura):
        total = 0
        for indice, item in enumerate(itens):
            total += self._altura_texto(item, largura - 6, 10, 5)
            if indice < len(itens) - 1:
                total += 1.6
        return total

    def _altura_linha_item(self, item, largura):
        if item.get("detalhes"):
            return self._altura_bloco_detalhado(item, largura)
        padding = 2.2
        util = largura - 8 - 42
        altura = padding
        altura += self._altura_texto(item["titulo"], util, 10, 4.8, negrito=True) or 4.8
        if item["subtitulo"]:
            altura += self._altura_texto(item["subtitulo"], util, 8, 3.8)
        valor_h = 0
        if item["rotulo_valor"]:
            valor_h += 3.4
        if item["valor"]:
            valor_h += self._altura_texto(item["valor"], 38, 10, 4.8, negrito=True)
        return max(altura, valor_h) + padding

    def _altura_bloco_detalhado(self, item, largura):
        padding = 2.2
        util = largura - (2 * padding)
        altura = padding
        altura += self._altura_texto(item["titulo"], util - 28, 10, 4.8, negrito=True) or 4.8
        if item["subtitulo"]:
            altura += self._altura_texto(item["subtitulo"], util, 8, 3.6)
        if item["nota"]:
            altura += self._altura_texto(item["nota"], util, 8, 3.8) + 0.6
        if item["detalhes"]:
            altura += 1.2 + self._altura_grade(item["detalhes"], util)
        return altura + padding

    def _altura_linhas(self, linhas, largura):
        total = 0
        for indice, item in enumerate(linhas):
            total += self._altura_linha_item(item, largura)
            if indice < len(linhas) - 1:
                total += GAP_PEDIDOS
        return total

    def _desenhar_secao_completa(self, secao, altura):
        x = MARGEM
        y = self.get_y()
        self._caixa(x, y, self.largura_util, altura, BRANCO, BORDA, raio=3.2)
        self._desenhar_cabecalho_secao(x, y, secao)
        cursor = y + self._altura_cabecalho(secao)
        cursor = self._desenhar_conteudo(x, cursor, secao, self.largura_util)
        self.set_y(max(cursor, y + altura) + 3.2)

    def _desenhar_secao_fluida(self, secao):
        altura_cabecalho = self._altura_cabecalho(secao)
        self._quebrar_se_preciso(altura_cabecalho + 6)
        x = MARGEM
        y = self.get_y()
        self._caixa(x, y, self.largura_util, altura_cabecalho, FUNDO_PAGINA, BORDA, raio=3)
        self._desenhar_cabecalho_secao(x, y, secao)
        self.set_y(y + altura_cabecalho + 2)
        padding = PADDING_SECAO
        largura = self.largura_util
        self._desenhar_paragrafos_fluxo(secao["paragrafos"], x, largura, padding)
        self._desenhar_grade_fluxo(secao["cards"], x, largura, padding)
        self._desenhar_lista_fluxo(secao["lista"], x, largura, padding)
        self._desenhar_linhas_fluxo(secao["linhas"], x, largura, padding)
        self.ln(2)

    def _desenhar_cabecalho_secao(self, x, y, secao):
        altura = self._altura_cabecalho(secao)
        self.set_fill_color(*FUNDO_PAGINA)
        self.rect(
            x + 0.35,
            y + 0.35,
            self.largura_util - 0.7,
            altura - 0.7,
            style="F",
        )
        self.set_draw_color(*BORDA)
        self.set_line_width(0.2)
        self.line(
            x,
            y + altura - 0.2,
            x + self.largura_util,
            y + altura - 0.2,
        )

        titulo_x = x + 4
        if secao.get("data"):
            self._fonte(8)
            self.set_text_color(*MUDO)
            self.set_xy(titulo_x, y + 1.3)
            self.cell(self.largura_util - 8, 3.4, secao["data"])
            self.set_xy(titulo_x, y + 5.2)
        else:
            self.set_xy(titulo_x, y + 2.2)

        self._fonte(8, negrito=True)
        self.set_text_color(*AZUL)
        self.cell(self.largura_util - 8, 4, secao["titulo"])

    def _desenhar_conteudo(self, x, y, secao, largura_secao):
        conteudo_x = x + PADDING_SECAO
        largura = largura_secao - (2 * PADDING_SECAO)
        cursor = y + 2
        cursor = self._desenhar_paragrafos(conteudo_x, cursor, secao["paragrafos"], largura)
        cursor = self._desenhar_grade(conteudo_x, cursor, secao["cards"], largura)
        cursor = self._desenhar_lista(conteudo_x, cursor, secao["lista"], largura)
        cursor = self._desenhar_linhas(conteudo_x, cursor, secao["linhas"], largura)
        return cursor + PADDING_SECAO - 2

    def _desenhar_paragrafos(self, x, y, paragrafos, largura):
        cursor = y
        for indice, texto in enumerate(paragrafos):
            altura = self._escrever(x, cursor, largura, texto, 10, 5, TEXTO)
            cursor += altura
            if indice < len(paragrafos) - 1:
                cursor += 1.2
        return cursor

    def _desenhar_card(self, x, y, w, h, card):
        if not card.get("compacto"):
            self._caixa(x, y, w, h, BRANCO, BORDA, raio=2.2)
        estilo = self._estilo_card(card)
        padding = estilo["padding"]
        cursor = y + padding
        util = w - (2 * padding)
        if card["rotulo"]:
            cursor += self._escrever(
                x + padding,
                cursor,
                util,
                card["rotulo"],
                estilo["rotulo"][0],
                estilo["rotulo"][1],
                MUDO,
            )
        if card["valor"]:
            cursor += self._escrever(
                x + padding,
                cursor,
                util,
                card["valor"],
                estilo["valor"][0],
                estilo["valor"][1],
                TEXTO,
                negrito=True,
            )
        if card["texto"]:
            cursor += self._escrever(
                x + padding,
                cursor + 0.3,
                util,
                card["texto"],
                estilo["texto"][0],
                estilo["texto"][1],
                SECUNDARIO,
            )
        if card["chips"]:
            chip_y = cursor + 0.8
            chip_x = x + padding
            self._fonte(8)
            for chip in card["chips"][:6]:
                largura_chip = min(self.get_string_width(chip) + 6, util)
                if chip_x + largura_chip > x + padding + util:
                    break
                self._caixa(chip_x, chip_y, largura_chip, 5.2, AZUL_CLARO, AZUL, raio=2.4)
                self._fonte(8)
                self.set_text_color(*AZUL)
                self.set_xy(chip_x, chip_y + 0.7)
                self.cell(largura_chip, 4, chip, align="C")
                chip_x += largura_chip + 2
        if card["barra"] is not None:
            barra_y = y + h - 3.4
            barra_x = x + padding
            barra_w = util
            self.set_fill_color(219, 234, 254)
            self.rect(barra_x, barra_y, barra_w, 1.3, style="F")
            preenchimento = max(0, min(100, float(card["barra"]))) / 100
            if preenchimento > 0:
                self.set_fill_color(*AZUL)
                self.rect(barra_x, barra_y, barra_w * preenchimento, 1.3, style="F")
        return h

    def _desenhar_linha_grade(self, x, y, linha, largura, gap_depois=GAP_GRADE):
        cards = [card for card in linha if card is not None]
        if not cards:
            return y
        meia_largura = (
            len(linha) == 2
            and linha[1] is None
            and not cards[0].get("compacto")
        )
        if meia_largura:
            largura_card = (largura - GAP_GRADE) / 2
            altura = self._altura_card(cards[0], largura_card)
            self._desenhar_card(x, y, largura_card, altura, cards[0])
            return y + altura + gap_depois

        n = len(cards)
        largura_card = (largura - GAP_GRADE * (n - 1)) / n
        altura = max(self._altura_card(card, largura_card) for card in cards)
        cursor_x = x
        for card in cards:
            self._desenhar_card(cursor_x, y, largura_card, altura, card)
            cursor_x += largura_card + GAP_GRADE
        return y + altura + gap_depois

    def _desenhar_grade(self, x, y, cards, largura):
        if not cards:
            return y
        cursor = y
        linhas = self._linhas_grade(cards)
        for indice, linha in enumerate(linhas):
            gap = 0 if indice == len(linhas) - 1 else GAP_GRADE
            cursor = self._desenhar_linha_grade(x, cursor, linha, largura, gap)
        return cursor

    def _desenhar_lista(self, x, y, itens, largura):
        cursor = y
        for indice, item in enumerate(itens):
            self.set_fill_color(*AZUL)
            self.ellipse(x + 0.4, cursor + 1.6, 1.3, 1.3, style="F")
            altura = self._escrever(x + 5, cursor, largura - 6, item, 10, 5, TEXTO)
            cursor += max(altura, 5)
            if indice < len(itens) - 1:
                cursor += 1.6
        return cursor

    def _desenhar_linhas(self, x, y, linhas, largura):
        cursor = y
        for indice, item in enumerate(linhas):
            altura = self._altura_linha_item(item, largura)
            if item.get("detalhes"):
                self._desenhar_bloco_detalhado(x, cursor, largura, altura, item)
            else:
                self._desenhar_linha_simples(x, cursor, largura, altura, item)
            cursor += altura
            if indice < len(linhas) - 1:
                cursor += GAP_PEDIDOS
        return cursor

    def _desenhar_linha_simples(self, x, y, w, h, item):
        self._caixa(x, y, w, h, FUNDO_PAGINA, BORDA, raio=2.2)
        padding = 2.4
        util = w - 8 - 42
        cursor = y + padding
        cursor += self._escrever(
            x + padding, cursor, util, item["titulo"], 10, 5, TEXTO, negrito=True
        )
        if item["subtitulo"]:
            self._escrever(
                x + padding, cursor, util, item["subtitulo"], 8, 4, SECUNDARIO
            )
        valor_x = x + w - padding - 40
        valor_y = y + padding
        if item["rotulo_valor"]:
            self._escrever(
                valor_x, valor_y, 40, item["rotulo_valor"], 7, 3.4, MUDO
            )
            valor_y += 3.6
        if item["valor"]:
            self.set_xy(valor_x, valor_y)
            self._fonte(10, negrito=True)
            self.set_text_color(*TEXTO)
            self.cell(40, 5, item["valor"], align="R")
        if item["selo"]:
            self._fonte(7, negrito=True)
            self.set_text_color(*AZUL)
            self.set_xy(valor_x, y + padding)
            self.cell(40, 4, item["selo"], align="R")

    def _desenhar_bloco_detalhado(self, x, y, w, h, item):
        self._caixa(x, y, w, h, FUNDO_PAGINA, BORDA, raio=2.2)
        padding = 2.2
        util = w - (2 * padding)
        cursor = y + padding
        titulo_w = util - 28
        cursor += self._escrever(
            x + padding, cursor, titulo_w, item["titulo"], 10, 4.8, TEXTO, negrito=True
        )
        if item["selo"]:
            self._fonte(7, negrito=True)
            self.set_text_color(*AZUL)
            self.set_xy(x + w - padding - 26, y + padding)
            self.cell(26, 4.8, item["selo"], align="R")
        if item["subtitulo"]:
            cursor += self._escrever(
                x + padding, cursor, util, item["subtitulo"], 8, 3.6, MUDO
            )
        if item["nota"]:
            cursor += self._escrever(
                x + padding, cursor + 0.4, util, item["nota"], 8, 3.8, SECUNDARIO
            )
        if item["detalhes"]:
            self._desenhar_grade(x + padding, cursor + 1.2, item["detalhes"], util)

    def _desenhar_paragrafos_fluxo(self, paragrafos, x, largura, padding):
        for texto in paragrafos:
            texto_h = self._altura_texto(texto, largura - 2 * padding, 10, 5)
            altura = texto_h + 4
            self._quebrar_se_preciso(altura)
            caixa_y = self.get_y()
            self._caixa(x, caixa_y, largura, altura, BRANCO, BORDA, raio=2.4)
            self._escrever(
                x + padding, caixa_y + 2, largura - 2 * padding, texto, 10, 5, TEXTO
            )
            self.set_y(caixa_y + altura + 2.5)

    def _desenhar_grade_fluxo(self, cards, x, largura, padding):
        if not cards:
            return
        util = largura - (2 * padding)
        linhas = self._linhas_grade(cards)
        for indice, linha in enumerate(linhas):
            altura = self._altura_linha_grade(linha, util)
            self._quebrar_se_preciso(altura + 4)
            gap = 0 if indice == len(linhas) - 1 else GAP_GRADE
            cursor = self._desenhar_linha_grade(
                x + padding, self.get_y(), linha, util, gap
            )
            self.set_y(cursor)

    def _desenhar_lista_fluxo(self, itens, x, largura, padding):
        if not itens:
            return
        texto_largura = largura - 2 * padding - 6
        altura = self._altura_lista(itens, texto_largura) + 4
        self._quebrar_se_preciso(min(altura, 40))
        y = self.get_y()
        self._caixa(x, y, largura, altura, BRANCO, BORDA, raio=2.4)
        self._desenhar_lista(x + padding, y + 2, itens, largura - 2 * padding)
        self.set_y(y + altura + 2.5)

    def _desenhar_linhas_fluxo(self, linhas, x, largura, padding):
        util = largura - (2 * padding)
        for indice, item in enumerate(linhas):
            altura = self._altura_linha_item(item, util)
            self._quebrar_se_preciso(altura + GAP_PEDIDOS)
            y = self.get_y()
            if item.get("detalhes"):
                self._desenhar_bloco_detalhado(x + padding, y, util, altura, item)
            else:
                self._desenhar_linha_simples(x + padding, y, util, altura, item)
            extra = GAP_PEDIDOS if indice < len(linhas) - 1 else 2
            self.set_y(y + altura + extra)


def _card_padrao(card, compacto=False):
    barra = card.get("barra")
    if barra is not None:
        try:
            barra = float(barra)
        except (TypeError, ValueError):
            barra = None
    return {
        "rotulo": _limpar_texto(card.get("rotulo", "")),
        "valor": _limpar_texto(card.get("valor", "")),
        "texto": _limpar_texto(card.get("texto", "")),
        "chips": _limpar_lista(card.get("chips", []), limite=8),
        "barra": barra,
        "largo": bool(card.get("largo")),
        "compacto": compacto,
    }


def _linha_padrao(item):
    return {
        "titulo": _limpar_texto(item.get("titulo", "")),
        "subtitulo": _limpar_texto(item.get("subtitulo", "")),
        "valor": _limpar_texto(item.get("valor", "")),
        "rotulo_valor": _limpar_texto(item.get("rotulo_valor", "")),
        "selo": _limpar_texto(item.get("selo", "")),
        "nota": _limpar_texto(item.get("nota", "")),
        "detalhes": [
            _card_padrao(detalhe, compacto=True)
            for detalhe in item.get("detalhes") or []
        ],
    }


def _hora_do_chat(data_chat, gerado):
    hora = gerado.strftime("%H:%M")
    texto = _limpar_texto(data_chat)
    if not texto:
        return hora
    for parte in reversed(texto.replace(",", " ").split()):
        if ":" in parte:
            return parte[:5]
    return hora


def _normalizar_secao(secao, data_hora_geracao=None):
    titulo = _limpar_texto(secao.get("titulo", "")).upper()
    paragrafos = _limpar_lista(secao.get("paragrafos", []))
    texto = _limpar_texto(secao.get("texto", ""))
    if texto and not paragrafos:
        paragrafos = [texto]

    data = ""
    if "RESUMO EXECUTIVO" in titulo:
        gerado = data_hora_geracao or data_hora_relatorio()
        hora = _hora_do_chat(secao.get("data", ""), gerado)
        data = f"{gerado.strftime('%d/%m/%Y')}, {hora}"

    return {
        "titulo": titulo,
        "data": data,
        "paragrafos": paragrafos,
        "cards": [_card_padrao(card) for card in secao.get("cards") or []][:20],
        "lista": _limpar_lista(secao.get("lista", [])),
        "linhas": [_linha_padrao(item) for item in secao.get("linhas") or []][:LIMITE_ITENS],
    }


def _secao_tem_conteudo(secao):
    return bool(
        secao["paragrafos"]
        or secao["cards"]
        or secao["lista"]
        or secao["linhas"]
    )


def montar_pdf_relatorio(secoes):
    if not secoes:
        raise ValueError("Não há conteúdo para gerar o relatório.")

    gerado = data_hora_relatorio()
    pdf = _novo_pdf()
    pdf.desenhar_cabecalho_documento()

    for secao in secoes[:LIMITE_SECOES]:
        pdf.desenhar_secao(secao, gerado)

    buffer = BytesIO()
    pdf.output(buffer)
    nome = f"relatorio-duaxis-{gerado.strftime('%Y%m%d-%H%M')}.pdf"
    return buffer.getvalue(), nome


def _configurar_fontes_e_familia():
    regular = _caminho_fonte(False)
    negrito = _caminho_fonte(True)
    if regular is None:
        return "Helvetica", True
    return "Relatorio", negrito is not None


def _novo_pdf():
    familia, tem_negrito = _configurar_fontes_e_familia()
    pdf = RelatorioPDF(familia, tem_negrito)
    if familia == "Relatorio":
        pdf.add_font("Relatorio", fname=str(_caminho_fonte(False)))
        caminho_negrito = _caminho_fonte(True)
        if caminho_negrito is not None:
            pdf.add_font("Relatorio", style="B", fname=str(caminho_negrito))
            pdf.tem_negrito = True
        else:
            pdf.tem_negrito = False
    pdf.add_page()
    return pdf
