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

    # Destinações:



    # Função para Renderizar Página:

    def renderizar_pagina(page, main_container):
        indice = page.route
        conexao = mod_db.ConexaoBanco()

        # MENU
        if indice == "/menu":
            conteudo = mod_pag.pagina_menu()

        # CADASTRO DE REGISTROS
        elif indice == "/cadastro":
            conteudo = mod_pag.pagina_cadastro(page) 


        # VISUALIZAÇÃO DE DADOS ( Membros )
        elif indice == "/visualização":
            conteudo = mod_pag.pagina_visualizacao(page, conexao) 

        main_container.content = conteudo
        page.update()


    # Objeto de Navigation Rail:
    btn_menu = ft.Button(
        "Menu",
        on_click = lambda _:ir_para("/menu")
        )
    btn_cdst = ft.Button(
        "Cadastro",
        on_click = lambda _:ir_para("/cadastro")
        )
    btn_visu = ft.Button(
        "visualização",
        on_click = lambda _:ir_para("/visualização")        
        )

    botoes = ft.Column(
        [btn_menu, btn_cdst, btn_visu],
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
        )

    page.on_route_change = lambda _: renderizar_pagina(page, main_container)

    def ir_para(rota):
        page.route = rota
        renderizar_pagina(page, main_container)

    # >>>> Primeira Página Mostrada <<<<

    main_container.content = ft.Text("Bem-Vindo ao Aplicativo!")
    row = ft.Row([
        # ft.Container(rail, height=page.window.height),
        botoes,
        ft.VerticalDivider(),
        main_container],
        alignment = ft.MainAxisAlignment.CENTER
    )

    page.add(row)
    page.route = "/menu"

ft.run(main)
