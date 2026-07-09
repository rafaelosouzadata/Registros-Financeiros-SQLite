import sys
from pathlib import Path

caminho_modulos = Path(__file__).resolve().parent / "python_pasta"
sys.path.append(str(caminho_modulos))

import datetime
import streamlit as st
import pandas as pd
import modulo_database as mod_db
import modulo_base as mod_base
import formularios as mod_form
import modulo_dbt as mod_dbt
import graficos as mod_graph
import plotly.express as px
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="Financeiro Igreja",       
    page_icon="📊",                        
    layout="wide",                        
    initial_sidebar_state="expanded"
)
mod_db.criar_tabelas()
engine = mod_db.conexao_banco()

with st.sidebar:
    pags = ["Menu","Cadastro", "Visualização"]
    # pagina = st.radio("Navegação", pags)

    pagina = option_menu(
        menu_title=None,                               # Título do menu (None para ficar limpo)
        options=pags,  # Opções do menu
        default_index=0,                               # Qual aba começa ativa
        orientation="vertical",                      # Transforma em abas horizontais
        )

if st.button("Atualizar Dados"):
    with st.spinner("Atualizando Dados..."):
        mod_dbt.dbt_seed(engine)
        df = mod_dbt.dbt_run(engine)
        st.success("Dados Atualizados!")
        st.rerun()

if pagina == "Cadastro":
    aba = option_menu(
        menu_title=None,                               # Título do menu (None para ficar limpo)
        options=["Membros", "Dízimos"],  # Opções do menu
        default_index=0,                               # Qual aba começa ativa
        orientation="horizontal",                      # Transforma em abas horizontais
        )
    if aba == "Membros":
        st.title(f"Cadastro de Membros")
        mod_form.registro_membros()

    if aba == "Dízimos":
        st.title(f"Cadastro de Dízimos")
        mod_form.registro_dizimo()

if pagina == "Visualização":

        aba = option_menu(
        menu_title=None,                               # Título do menu (None para ficar limpo)
        options=["Membros", "Dízimos"],  # Opções do menu
        default_index=0,                               # Qual aba começa ativa
        orientation="horizontal",                      # Transforma em abas horizontais
        )

        if aba == "Membros":

            coluna1, coluna2 = st.columns(2)

            with coluna1:
                pie_sexo = mod_graph.grafico_pie_sexo(engine)
                st.plotly_chart(pie_sexo)

            with coluna2:

                pie_cargos = mod_graph.grafico_pie_cargos(engine)   
                st.plotly_chart(pie_cargos)
                
            df = pd.DataFrame(mod_graph.grafico_tabela_comum("membros"))
            st.dataframe(df)
        
        if aba == "Dízimos":
            # df = pd.DataFrame(mod_graph.grafico_tabela_dizimos(engine))
            # st.dataframe(df)

            coluna1, coluna2 = st.columns(2)
            dizimo_membros, dizimo_obreiros = mod_graph.tabela_dizimo_membros_obreiros(engine)

            with coluna1:
                st.subheader("Dízimo dos Membros")
                st.dataframe(dizimo_membros)

            with coluna2:
                st.subheader("Dízimo dos Obreiros")
                st.dataframe(dizimo_obreiros)

            fig2 = mod_graph.grafico_saldo_mes(engine)
            st.plotly_chart(fig2)

            fig = mod_graph.grafico_saldo_por_mesano(engine)
            st.plotly_chart(fig)