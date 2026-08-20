import sys
from pathlib import Path

caminho_modulos = Path(__file__).resolve().parent / "python_pasta"
sys.path.append(str(caminho_modulos))

import io
import flet as ft
import formularios as mod_form
import modulo_database as mod_db
import modulo_dbt as mod_dbt
import graficos as mod_graph
import matplotlib.pyplot as plt
import matplotlib       

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

    destinacoes = [
        ("Inicio", ft.Icons.MENU),
        ("Cadastro", ft.Icons.MENU),
        ("Visualização", ft.Icons.MENU),
    ]
    menu = [ft.NavigationRailDestination(
                label=rotulo,
                icon=icone,
                # selected_icon=icone_selecionado,
                )
            for rotulo, icone in destinacoes]


    # Função para Renderizar Página:

    def renderizar_pagina(e, main_container):
        indice = e.control.selected_index
        conexao = mod_db.ConexaoBanco()


        # MENU

        if indice == 0:
            main_container.content = ft.Text("Bem-Vindo ao Aplicativo!")

        # CADASTRO DE REGISTROS

        elif indice == 1:
            Formulario_Membros = mod_form.CadastroMembro(e.page)
            # Formulario_Cargo = mod_form.CadastroCargo(e.page)
            Formulario_Dizimo = mod_form.CadastroDizimo(e.page)

            main_container.content = ft.Column(
                [
                # Formulario_Cargo,
                Formulario_Membros,
                Formulario_Dizimo
                ]
            )


        # VISUALIZAÇÃO DE DADOS ( Membros )

        elif indice == 2:

            # Gráficos
            matplotlib.use("Agg")
            graficos = {
                "pie sexo": mod_graph.matplot_pie_sexo,
                "pie cargos": mod_graph.matplot_pie_cargos,
            }
            
            lista_graficos = []
            plt.style.use("seaborn-v0_8")

            fig, ax = plt.subplots(1, 2, figsize=(8, 5))

            for a, funcao in zip(ax, graficos.values()):
                ax_atual = funcao(conexao.engine, a)

            plt.suptitle("Gráfico de Membros", fontsize=14, fontweight='bold')

            plt.tight_layout()

            svg_buffer = io.BytesIO()
            plt.savefig(svg_buffer, format="svg", bbox_inches="tight")
        

            grafico = ft.Image(
                svg_buffer.getvalue(),
                fit="contain",
                width=700,
                height=400,
            )

            lista_graficos.append(grafico)

            # Atualização dos Dados no Sistema (DBT Like)

                mod_dbt.dbt_run(conexao.engine)

            notf = ft.SnackBar(
                ft.Text("Deu tudo certo"),
                open= False,
                duration=5000,)

            e.page.overlay.append(notf)

            notf.open = True

            # Gerenciador de Tabelas


            df = mod_graph.pesquisa_tabela_comum(conexao.engine, "membros", "nome")
            tabela_membros = mod_graph.df_para_flet(df)

            df2 = mod_graph.pesquisa_tabela_comum(conexao.engine, "fct_dizimos", "valor")
            tabela_dizimos = mod_graph.df_para_flet(df2)

            # Organizando Layout

            ft_graficos = ft.Row(
                lista_graficos,
                alignment=ft.MainAxisAlignment.CENTER
                )

            main_container.content = ft.Column(
                [ft_graficos, tabela_membros, tabela_dizimos]) 

        # elif indice == 3:

        e.page.update()


    # Objeto de Navigation Rail:

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,

        min_width=100,
        min_extended_width=200,
        extended=False,
        # expanded=True,

        destinations=menu,
        on_change= lambda e: renderizar_pagina(e, main_container)
    )

    # >>>> Primeira Página Mostrada <<<<

    main_container.content = ft.Text("Bem-Vindo ao Aplicativo!")
    row = ft.Row([
        ft.Container(rail, height=page.window.height),
        ft.VerticalDivider(),
        main_container],
        alignment = ft.MainAxisAlignment.CENTER
    )
    page.add(row)

ft.run(main)
