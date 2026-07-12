import sys
from pathlib import Path

# Mantém a sua lógica de importação de módulos
caminho_modulos = Path(__file__).resolve().parent / "python_pasta"
if str(caminho_modulos) not in sys.path:
    sys.path.append(str(caminho_modulos))

import datetime
import flet as ft
from flet_charts import PlotlyChart  # Importante para renderizar o Plotly
import pandas as pd
import modulo_database as mod_db
import modulo_base as mod_base
import formularios as mod_form
import modulo_dbt as mod_dbt
import graficos as mod_graph
import plotly.express as px

# Inicializa banco de dados globalmente
mod_db.criar_tabelas()
engine = mod_db.conexao_banco()


def main(page: ft.Page):
    # Configurações equivalentes ao st.set_page_config
    page.title = "Financeiro Igreja"
    page.window_icon = "📊"  # Pode usar um arquivo local .ico ou .png se preferir
    page.theme_mode = ft.ThemeMode.LIGHT  # ou .DARK

    # --- CONTAINER PRINCIPAL DO CONTEÚDO ---
    # É aqui que vamos injetar o conteúdo dinâmico (Cadastro, Visualização, etc.)
    conteudo_dinamico = ft.Container(expand=True, padding=20)

    # --- FUNÇÃO PARA RERENDERIZAR A TELA (Dinamismo) ---
    def atualizar_tela():
        # Captura qual página principal está selecionada no menu lateral
        aba_principal = sidebar.selected_index

        # Se for "Menu" (Index 0)
        if aba_principal == 0:
            conteudo_dinamico.content = ft.Column(
                [ft.Text("Bem-vindo ao Sistema Financeiro da Igreja", size=24, weight="bold")]
            )

        # Se for "Cadastro" (Index 1)
        elif aba_principal == 1:
            renderizar_cadastro()

        # Se for "Visualização" (Index 2)
        elif aba_principal == 2:
            renderizar_visualizacao()

        page.update()

    # --- LÓGICA DA PÁGINA DE CADASTRO ---
    def renderizar_cadastro():
        def alternar_aba(nome_aba):
            if nome_aba == "membros":
                area_formulario.content = ft.Text("Aqui chama: mod_form.registro_membros()")
                btn_membros.style = ft.ButtonStyle(bgcolor="surfacevariant")
                btn_dizimos.style = None
            else:
                area_formulario.content = ft.Text("Aqui chama: mod_form.registro_dizimo()")
                btn_dizimos.style = ft.ButtonStyle(bgcolor="surfacevariant")
                btn_membros.style = None
            page.update()

        area_formulario = ft.Container(content=ft.Text("Carregando formulário..."), expand=True)

        # Criamos botões simples que funcionam como abas
        btn_membros = ft.TextButton("Membros", icon="people", on_click=lambda _: alternar_aba("membros"))
        btn_dizimos = ft.TextButton("Dízimos", icon="money", on_click=lambda _: alternar_aba("dizimos"))

        conteudo_dinamico.content = ft.Column([
            ft.Text("Área de Cadastro", size=22, weight="bold"),
            ft.Row([btn_membros, btn_dizimos], spacing=10), # Substitui o ft.Tabs problemático
            area_formulario
        ], expand=True)
        
        alternar_aba("membros") # Inicia na primeira aba

    # --- LÓGICA DA PÁGINA DE VISUALIZAÇÃO (Gráficos e Tabelas) ---
    def renderizar_visualizacao():
        def alternar_aba(nome_aba):
            if nome_aba == "membros":
                btn_membros.style = ft.ButtonStyle(bgcolor="surfacevariant")
                btn_dizimos.style = None
                
                # --- ABA MEMBROS ---
                pie_sexo = mod_graph.grafico_pie_sexo(engine)
                pie_cargos = mod_graph.grafico_pie_cargos(engine)
                df_membros = pd.DataFrame(mod_graph.grafico_tabela_comum("membros"))

                area_dados.content = ft.Column([
                    ft.Row([
                        ft.Container(PlotlyChart(figure=pie_sexo, expand=True), expand=True, height=350),
                        ft.Container(PlotlyChart(figure=pie_cargos, expand=True), expand=True, height=350),
                    ], spacing=20),
                    ft.Text("Tabela de Membros", size=16, weight="bold"),
                    ft.Container(
                        ft.DataTable(
                            columns=[ft.DataColumn(ft.Text(col)) for col in df_membros.columns],
                            rows=[
                                ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row])
                                for row in df_membros.values
                            ]
                        ),
                        scroll=ft.ScrollMode.ADAPTIVE
                    )
                ], scroll=ft.ScrollMode.ALWAYS, expand=True)
            else:
                btn_dizimos.style = ft.ButtonStyle(bgcolor="surfacevariant")
                btn_membros.style = None
                
                # --- ABA DÍZIMOS ---
                dizimo_membros, dizimo_obreiros = mod_graph.tabela_dizimo_membros_obreiros(engine)
                fig2 = mod_graph.grafico_saldo_mes(engine)
                fig = mod_graph.grafico_saldo_por_mesano(engine)

                area_dados.content = ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Dízimo dos Membros", weight="bold"),
                            ft.DataTable(
                                columns=[ft.DataColumn(ft.Text(col)) for col in dizimo_membros.columns],
                                rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for r in dizimo_membros.values for v in r]) if hasattr(dizimo_membros, 'values') else []] # Mantido conforme seu padrão anterior
                            )
                        ], expand=True),
                        ft.Column([
                            ft.Text("Dízimo dos Obreiros", weight="bold"),
                            ft.DataTable(
                                columns=[ft.DataColumn(ft.Text(col)) for col in dizimo_obreiros.columns],
                                rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for r in dizimo_obreiros.values for v in r]) if hasattr(dizimo_obreiros, 'values') else []]
                        , expand=True),
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
                    ft.Container(PlotlyChart(figure=fig2, expand=True), height=350),
                    ft.Container(PlotlyChart(figure=fig, expand=True), height=350),
                ], scroll=ft.ScrollMode.ALWAYS, expand=True)])
            page.update()

        area_dados = ft.Container(expand=True)
        
        btn_membros = ft.TextButton("Membros", icon="bar_chart", on_click=lambda _: alternar_aba("membros"))
        btn_dizimos = ft.TextButton("Dízimos", icon="attach_money", on_click=lambda _: alternar_aba("dizimos"))
        
        conteudo_dinamico.content = ft.Column([
            ft.Row([btn_membros, btn_dizimos], spacing=10),
            area_dados
        ], expand=True)
        
        alternar_aba("membros")

    # --- BOTÃO ATUALIZAR DADOS (Com efeito Spinner de loading) ---
    def btn_atualizar_click(e):
        btn_atualizar.disabled = True
        progress_bar.visible = True  # O Flet usa barras de progresso controladas
        page.update()
        
        # Roda suas automações de banco de dados
        mod_dbt.dbt_seed(engine)
        df = mod_dbt.dbt_run(engine)
        
        # Mostra um "Snackbar" (notificação que sobe no rodapé, substitui st.success)
        page.snack_bar = ft.SnackBar(ft.Text("Dados Atualizados com Sucesso!"))
        page.snack_bar.open = True
        
        btn_atualizar.disabled = False
        progress_bar.visible = False
        atualizar_tela() # Atualiza os gráficos com os dados novos

    btn_atualizar = ft.Button("Atualizar Dados", icon=ft.Icons.REFRESH, on_click=btn_atualizar_click)
    progress_bar = ft.ProgressBar(visible=False, width=150)

    # --- SIDEBAR (NavigationRail do Flet) ---
    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        extended=True,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME, selected_icon=ft.Icons.HOME, label="Menu"),
            ft.NavigationRailDestination(icon=ft.Icons.CREATE, selected_icon=ft.Icons.CREATE, label="Cadastro"),
            ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, selected_icon=ft.Icons.ANALYTICS, label="Visualização"),
        ],
        on_change=lambda e: atualizar_tela(),
        trailing=ft.Column([btn_atualizar, progress_bar], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # --- ESTRUTURA FINAL DA PÁGINA ---
    # Junta a barra lateral esquerda com a área de conteúdo dinâmico da direita
    page.add(
        ft.Row(
            [
                sidebar,
                ft.VerticalDivider(width=1), # Linha sutil separando o menu do app
                conteudo_dinamico
            ],
            expand=True,
        )
    )
    
    # Carrega a página inicial no primeiro boot do app
    atualizar_tela()

# Roda o app em modo desktop nativo
ft.run(main)