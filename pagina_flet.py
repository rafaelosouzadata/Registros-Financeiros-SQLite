import sys
from pathlib import Path

caminho_modulos = Path(__file__).resolve().parent / "python_pasta"
sys.path.append(str(caminho_modulos))

import flet as ft
import modulo_database as mod_db
import matplotlib.pyplot as plt
import matplotlib       
import modulo_paginas as mod_pag

def main(page: ft.Page):

    page.title = "Financeiro Igreja"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window.height = 600
    page.window.width = 700
    page.scroll = "auto"

    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # mod_db.criar_tabelas_orm()
    main_container = ft.Container(
                                expand = False,
                                # height = 1000,
                                # width = 500,
                                padding=20,
                                # bgcolor= "BLUE"
    )

    # ==========================
    #     MUDANÇA DE PÁGINA
    # ==========================

    # >>>> Navigation Rail: Cadastro, Visualização <<<<
    # Função para Renderizar Página:

    def renderizar_pagina(page, main_container):
        indice = page.route
        conexao = mod_db.ConexaoBanco()

        paginas = {
            "/menu": mod_pag.pagina_menu,
            "/cadastro": mod_pag.pagina_cadastro,
            "/visualização": mod_pag.pagina_visualizacao
        }

        pag = paginas.get(indice)
        conteudo = pag(page, conexao)

        main_container.content = conteudo
        page.update()


    # Objeto de Navigation Rail:

    botoes_config =[
        ["Menu", "/menu"],
        ["Cadastro", "/cadastro"],
        ["Visualização", "/visualização"],
    ]

    botoes = []
    for label, url in botoes_config:
        btn = ft.Button(
                label,
                on_click = lambda _, url=url: ir_para(url)
                )

        botoes.append(btn)


    colunas_botoes = ft.Column(
        botoes,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
        )

    page.on_route_change = lambda _: renderizar_pagina(page, main_container)

    def ir_para(rota):
        page.route = rota
        renderizar_pagina(page, main_container)

    # >>>> Primeira Página Mostrada <<<<

    row = ft.Row([
        # ft.Container(rail, height=page.window.height),
        colunas_botoes,
        ft.VerticalDivider(),
        main_container],
        alignment = ft.MainAxisAlignment.CENTER,
    )

    page.add(row)
    ir_para("/menu")

ft.run(main)
