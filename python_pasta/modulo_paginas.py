import flet as ft
import formularios as mod_form
import graficos as mod_graph
import modulo_dbt as mod_dbt
import modulo_database as mod_db
import matplotlib.pyplot as plt
import matplotlib       
import io

def pagina_menu():
    conteudo = ft.Text("Bem-Vindo ao Aplicativo!")
    return conteudo

def pagina_cadastro(e):
    # CADASTRO DE REGISTROS

    Formulario_Membros = mod_form.CadastroMembro(e.page)
    # Formulario_Cargo = mod_form.CadastroCargo(e.page)
    Formulario_Dizimo = mod_form.CadastroDizimo(e.page)

    coluna = ft.Column(
        [
        # Formulario_Cargo,
        Formulario_Membros,
        Formulario_Dizimo
        ]
    )

    return coluna

def pagina_visualizacao(e, conexao):
    # VISUALIZAÇÃO DE DADOS ( Membros )

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

    coluna = ft.Column(
        [ft_graficos, tabela_membros, tabela_dizimos])

    return coluna